import os
import cv2
import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image
from torchvision import transforms
from concurrent.futures import ThreadPoolExecutor

from BackEnd.Soft_biometrics_rastreio_de_pessoas.Identificador_De_Face_FBR.pretrained.MFA_ViT import MFA_ViT

MODEL_PATH  = r"BackEnd\Soft_biometrics_rastreio_de_pessoas\Identificador_De_Face_FBR\pretrained\MFA-ViT.pt"
THRESHOLD   = 0.50
IMG_SIZE    = 112
INCREMENTAL = True
MAX_POOL    = 256
BATCH_SIZE  = 16    # imagens por forward pass
IO_WORKERS  = 4     # threads para leitura paralela do disco
device      = "cuda" if torch.cuda.is_available() else "cpu"

# Pesos do score combinado (devem somar 1.0)
PESO_MODELO      = 0.60  # similaridade MFA-ViT (identidade facial)
PESO_HISTOGRAMA  = 0.30  # similaridade de histograma HSV (cor da roupa)
PESO_PIXEL       = 0.10  # similaridade estrutural por pixel redimensionado


def make_transform(img_size: int):
    return transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.ToTensor(),
        transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5)),
    ])


def _load_tensor(path: str, tfm) -> torch.Tensor:
    """Carrega uma imagem e retorna tensor [1,1,3,H,W]. Retorna None se falhar."""
    try:
        x = tfm(Image.open(path).convert("RGB")).unsqueeze(0)
        return x.unsqueeze(1)
    except Exception:
        return None


def _normalize_state(state):
    if isinstance(state, dict) and "state_dict" in state:
        state = state["state_dict"]
    return {k.replace("module.", "").replace("backbone.", ""): v for k, v in state.items()}


def load_model(ckpt: str, dev: str, img_size: int):
    state = _normalize_state(torch.load(ckpt, map_location="cpu"))
    model = MFA_ViT(
        attr_size=47, img_size=img_size, patch_size=8, in_chans=3,
        embed_dim=1024, num_classes=9131, layer_depth=4, num_heads=12,
        mlp_ratio=4.0, norm_layer=None, drop_rate=0.0, attn_drop_rate=0.0,
        drop_path_rate=0.0, prompt_mode="deep", prompt_tokens=32, head_strategy="prm",
    )
    model.load_state_dict(state, strict=False)
    return model.to(dev).eval()


@torch.inference_mode()
def face_embedding(model, dev, face_tensor: torch.Tensor) -> torch.Tensor:
    face_tensor = face_tensor.to(dev)
    x = model.tokenize(face_tensor, mode="face")
    feat = model.forward_features(x, mode="face")
    if hasattr(feat, "dim") and feat.dim() > 2:
        feat = feat.flatten(1)
    return F.normalize(feat, dim=1)


def _centroid(pool: list) -> torch.Tensor:
    S = torch.stack(pool, dim=0)
    return F.normalize(S.mean(dim=0, keepdim=True), dim=1).squeeze(0)


def _load_tensors_parallel(paths: list, tfm) -> list:
    """Lê imagens do disco em paralelo; mantém ordem e substitui falhas por None."""
    with ThreadPoolExecutor(max_workers=IO_WORKERS) as ex:
        return list(ex.map(lambda p: _load_tensor(p, tfm), paths))


@torch.inference_mode()
def _batch_embeddings(model, dev, tensors: list) -> list:
    """
    Recebe lista de tensores [1,1,3,H,W] (None ignorado) e retorna lista de
    embeddings [1,D] na mesma ordem (None onde o tensor era None).
    Processa em mini-batches de BATCH_SIZE para controlar memória.
    """
    result = [None] * len(tensors)
    valid_idx = [i for i, t in enumerate(tensors) if t is not None]

    for start in range(0, len(valid_idx), BATCH_SIZE):
        batch_idx = valid_idx[start:start + BATCH_SIZE]
        batch = torch.cat([tensors[i] for i in batch_idx], dim=0)  # [B,1,3,H,W]
        embs = face_embedding(model, dev, batch)                    # [B,D]
        for k, i in enumerate(batch_idx):
            result[i] = embs[k:k+1]  # [1,D]

    return result


def _hsv_hist(path: str):
    """Retorna histograma HSV normalizado (canais H e S) ou None se falhar."""
    img = cv2.imread(path)
    if img is None:
        return None
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
    cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)
    return hist


def _pixel_vec(path: str, size: int = 16):
    """Redimensiona para size×size em escala de cinza e retorna vetor normalizado ou None."""
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        return None
    resized = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA).flatten().astype(np.float32)
    norm = np.linalg.norm(resized)
    return resized / norm if norm > 0 else resized


def _similaridades_matematicas(ref_path: str, paths: list) -> dict:
    """
    Calcula similaridade de histograma HSV e de pixel para cada candidato.
    Retorna {path: (hist_score, pixel_score)} com valores em [0, 1].
    """
    ref_hist = _hsv_hist(ref_path)
    ref_pix  = _pixel_vec(ref_path)

    resultados = {}
    for path in paths:
        # histograma HSV — correlação clipada em [0, 1]
        hist = _hsv_hist(path)
        if ref_hist is not None and hist is not None:
            h_score = max(0.0, float(cv2.compareHist(ref_hist, hist, cv2.HISTCMP_CORREL)))
        else:
            h_score = 0.0

        # similaridade de pixel — produto escalar de vetores normalizados
        pix = _pixel_vec(path)
        if ref_pix is not None and pix is not None:
            p_score = max(0.0, float(np.dot(ref_pix, pix)))
        else:
            p_score = 0.0

        resultados[path] = (h_score, p_score)
    return resultados


def imagems_comparacao(folder: str) -> list:
    extensoes = ('.png', '.jpg', '.jpeg')
    imagens = []
    for root, _, files in os.walk(folder):
        for f in files:
            if f.lower().endswith(extensoes):
                imagens.append(os.path.join(root, f))
    return imagens


def _score_incremental(ref_pool: list, embs: list, paths: list,
                       math_scores: dict) -> list:
    """
    Scoring incremental com centróide MFA-ViT combinado com
    similaridade matemática (histograma HSV + pixel).
    score_final = PESO_MODELO × modelo + PESO_HISTOGRAMA × hist + PESO_PIXEL × pixel
    """
    results = []
    for path, emb in zip(paths, embs):
        if emb is None:
            continue
        cur_centroid = _centroid(ref_pool)
        modelo_score = F.cosine_similarity(cur_centroid.unsqueeze(0), emb).item()

        hist_score, pixel_score = math_scores.get(path, (0.0, 0.0))

        combined = (PESO_MODELO     * modelo_score +
                    PESO_HISTOGRAMA * hist_score   +
                    PESO_PIXEL      * pixel_score)

        is_same = combined >= THRESHOLD
        results.append((path, float(combined), is_same))
        if INCREMENTAL and is_same and len(ref_pool) < MAX_POOL:
            ref_pool.append(emb[0].detach())
    return results


@torch.inference_mode()
def Detector_face(QUERY_IMG: str, FOLDER_DIR: str) -> list:
    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(f"Modelo não encontrado: {MODEL_PATH}")
    if not os.path.isfile(QUERY_IMG):
        raise FileNotFoundError(f"Imagem de consulta não encontrada: {QUERY_IMG}")
    if not os.path.isdir(FOLDER_DIR):
        raise NotADirectoryError(f"Pasta não encontrada: {FOLDER_DIR}")

    tfm   = make_transform(IMG_SIZE)
    model = load_model(MODEL_PATH, device, IMG_SIZE)

    q_emb    = face_embedding(model, device, _load_tensor(QUERY_IMG, tfm))
    ref_pool = [q_emb[0].to(device)]

    candidates = imagems_comparacao(os.path.abspath(FOLDER_DIR))
    if not candidates:
        return []

    print(f"[info] {len(candidates)} imagem(ns) para comparar")
    math_scores = _similaridades_matematicas(QUERY_IMG, candidates)
    tensors     = _load_tensors_parallel(candidates, tfm)
    embs        = _batch_embeddings(model, device, tensors)
    results     = _score_incremental(ref_pool, embs, candidates, math_scores)

    return sorted(results, key=lambda x: x[1], reverse=True)


@torch.inference_mode()
def Detector_face_caminho(QUERY_IMG: str, candidates: list) -> list:
    if not os.path.isfile(MODEL_PATH):
        raise FileNotFoundError(f"Modelo não encontrado: {MODEL_PATH}")
    if not os.path.isfile(QUERY_IMG):
        raise FileNotFoundError(f"Imagem de consulta não encontrada: {QUERY_IMG}")
    if not candidates:
        return []

    tfm   = make_transform(IMG_SIZE)
    model = load_model(MODEL_PATH, device, IMG_SIZE)

    q_emb    = face_embedding(model, device, _load_tensor(QUERY_IMG, tfm))
    ref_pool = [q_emb[0].to(device)]

    paths   = [p[0] for p in candidates]
    print(f"[info] {len(paths)} imagem(ns) para comparar")
    math_scores = _similaridades_matematicas(QUERY_IMG, paths)
    tensors     = _load_tensors_parallel(paths, tfm)
    embs        = _batch_embeddings(model, device, tensors)
    results     = _score_incremental(ref_pool, embs, paths, math_scores)

    return sorted(results, key=lambda x: x[1], reverse=True)
