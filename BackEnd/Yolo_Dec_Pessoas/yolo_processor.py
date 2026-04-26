import sys
import cv2
import os
import time
import torch
from pathlib import Path

# -------- CONFIGURAÇÕES --------
CONF_THRESHOLD = 0.5
INTERVALO_VIDEO_SEG = 5.0  # segundos entre frames amostrados em vídeos

EXTENSOES_VIDEO = {".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm"}
EXTENSOES_IMAGEM = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"}

REPO_DIR = Path(__file__).parent
WEIGHTS_PATH = REPO_DIR / "yolov5s.pt"

# Garante que utils/ e models/ do repositório local sejam encontrados
if str(REPO_DIR) not in sys.path:
    sys.path.insert(0, str(REPO_DIR))

from utils.general import non_max_suppression  # noqa: E402

model = torch.hub.load(str(REPO_DIR), "custom", path=str(WEIGHTS_PATH), source="local")
model.eval()


# -------- HELPERS INTERNOS --------

def _preparar_tensor(frame):
    """
    Converte frame BGR original para tensor NCHW [0,1] com dimensões múltiplas de 32.
    Retorna (tensor, escala_x, escala_y) para reescalar as coordenadas de volta.
    """
    import numpy as np
    h_orig, w_orig = frame.shape[:2]
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    tamanho = 640
    escala = tamanho / max(h_orig, w_orig)
    nh = (int(h_orig * escala) + 31) // 32 * 32
    nw = (int(w_orig * escala) + 31) // 32 * 32
    frame_res = cv2.resize(frame_rgb, (nw, nh), interpolation=cv2.INTER_LINEAR)

    tensor = torch.from_numpy(np.ascontiguousarray(frame_res))
    tensor = tensor.permute(2, 0, 1).float().unsqueeze(0) / 255.0
    tensor = tensor.to(next(model.parameters()).device)

    # fatores para mapear coords do frame redimensionado → frame original
    escala_x = w_orig / nw
    escala_y = h_orig / nh
    return tensor, escala_x, escala_y


def _detectar_pessoas(frame) -> list:
    tensor, escala_x, escala_y = _preparar_tensor(frame)

    with torch.no_grad():
        pred = model(tensor)

    # AutoShape com tensor retorna saída raw (tuple); pega o tensor de predições
    if isinstance(pred, (list, tuple)):
        pred = pred[0]

    deteccoes = non_max_suppression(pred, conf_thres=CONF_THRESHOLD, iou_thres=0.45)[0]

    pessoas = []
    for *xyxy, conf, cls in deteccoes:
        if model.names[int(cls)] == "person":
            x1 = int(xyxy[0].item() * escala_x)
            y1 = int(xyxy[1].item() * escala_y)
            x2 = int(xyxy[2].item() * escala_x)
            y2 = int(xyxy[3].item() * escala_y)
            pessoas.append((x1, y1, x2, y2, conf.item()))
    return pessoas


def _salvar_recortes(frame, pessoas: list, pasta_saida: Path, prefixo: str):
    pasta_saida.mkdir(parents=True, exist_ok=True)
    for i, (x1, y1, x2, y2, conf) in enumerate(pessoas):
        recorte = frame[y1:y2, x1:x2]
        if recorte.size == 0:
            continue
        nome = f"{prefixo}_p{i:02d}.jpg"
        cv2.imwrite(str(pasta_saida / nome), recorte)


def _processar_imagem(caminho: Path, pasta_saida: Path):
    frame = cv2.imread(str(caminho))
    if frame is None:
        print(f"[ERRO] Não foi possível abrir: {caminho.name}")
        return

    pessoas = _detectar_pessoas(frame)
    if pessoas:
        _salvar_recortes(frame, pessoas, pasta_saida, prefixo=caminho.stem)
        print(f"[OK] {caminho.name} → {len(pessoas)} pessoa(s)")
    else:
        print(f"[SKIP] Nenhuma pessoa em: {caminho.name}")

    os.remove(caminho)


def _processar_video(caminho: Path, pasta_saida: Path):
    cap = cv2.VideoCapture(str(caminho))
    if not cap.isOpened():
        print(f"[ERRO] Não foi possível abrir: {caminho.name}")
        return

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    frame_idx = 0
    ultimo_tempo_salvo = -INTERVALO_VIDEO_SEG
    total_recortes = 0

    print(f"[INFO] Processando vídeo: {caminho.name}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        tempo_seg = frame_idx / fps

        if tempo_seg - ultimo_tempo_salvo < INTERVALO_VIDEO_SEG:
            continue

        ultimo_tempo_salvo = tempo_seg
        pessoas = _detectar_pessoas(frame)
        if pessoas:
            h = int(tempo_seg) // 3600
            m = (int(tempo_seg) % 3600) // 60
            s = int(tempo_seg) % 60
            _salvar_recortes(frame, pessoas, pasta_saida,
                             prefixo=f"t{h:02d}_{m:02d}_{s:02d}")
            total_recortes += len(pessoas)

    cap.release()
    print(f"[OK] {caminho.name} → {total_recortes} recorte(s)")
    os.remove(caminho)


# -------- FUNÇÃO PRINCIPAL --------

def processar_diretorio(entrada: str, saida: str):
    """
    Lê todos os vídeos e imagens em `entrada`, detecta e isola cada pessoa
    encontrada, salva os recortes em `saida` e deleta os arquivos processados.
    """
    dir_entrada = Path(entrada)
    dir_saida = Path(saida)

    if not dir_entrada.is_dir():
        print(f"[ERRO] Diretório inválido: {dir_entrada}")
        return

    dir_saida.mkdir(parents=True, exist_ok=True)

    arquivos = sorted(dir_entrada.iterdir())
    imagens = [f for f in arquivos if f.is_file() and f.suffix.lower() in EXTENSOES_IMAGEM]
    videos  = [f for f in arquivos if f.is_file() and f.suffix.lower() in EXTENSOES_VIDEO]

    total = len(imagens) + len(videos)
    if total == 0:
        print("[AVISO] Nenhum arquivo de imagem ou vídeo encontrado.")
        return

    print(f"[INFO] {len(imagens)} imagem(ns), {len(videos)} vídeo(s) encontrados.")

    inicio = time.time()
    for img in imagens:
        _processar_imagem(img, dir_saida)
    for vid in videos:
        _processar_video(vid, dir_saida)

    print(f"[CONCLUÍDO] {total} arquivo(s) em {time.time() - inicio:.1f}s → {dir_saida}")
