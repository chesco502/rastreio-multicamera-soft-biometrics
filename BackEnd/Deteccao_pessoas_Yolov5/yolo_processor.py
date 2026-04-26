import cv2
import torch
import time
from pathlib import Path
from .utils_io import criar_pastas, salvar_txt, salvar_imagem
import os

# -------- CONFIGURAÇÕES --------
CLASSES_DESEJADAS = ["person"]
INTERVALO_SALVAR_TXT = 10
INTERVALO_SALVAR_IMG = 5.0

# -------- CARREGAR MODELO YOLOv5 OFFLINE --------
REPO_DIR = r"BackEnd\Deteccao_pessoas_Yolov5"
WEIGHTS_PATH = r"BackEnd\Deteccao_pessoas_Yolov5\yolov5s.pt"


model = torch.hub.load(str(REPO_DIR), "custom", path=str(WEIGHTS_PATH), source="local")




def abrir_video(video_path):
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise ValueError(f"Não foi possível abrir {video_path}")
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    return cap, fps

def detectar(frame):
    results = model(frame)
    detections = []

    for *xyxy, conf, cls in results.xyxy[0]:
        label = model.names[int(cls)]

       
        if label in CLASSES_DESEJADAS and conf.item() > 0.5:
            x1, y1, x2, y2 = map(int, xyxy)
            detections.append((label, conf.item(), (x1, y1, x2, y2)))

    return detections

def adicionar_ao_buffer(buffer, frame, detections, tempo, ultimo_frame_img):
    if detections and (ultimo_frame_img is None or tempo - ultimo_frame_img >= INTERVALO_SALVAR_IMG):
        for label, conf, (x1, y1, x2, y2) in detections:
            corte = frame[y1:y2, x1:x2].copy()
            buffer.append((tempo, label, conf, x1, y1, x2, y2, corte))
        return tempo
    return ultimo_frame_img

def salvar_buffer(buffer, output_dir, txt_path):
    criar_pastas([output_dir ])
    for t, label, conf, x1, y1, x2, y2, img in buffer:
        salvar_txt(txt_path, f"{t:.2f}s,)\n")
        salvar_imagem(output_dir,x1, y1,t, img)
    buffer.clear()

# ======================================================
# FUNÇÃO PRINCIPAL
# ======================================================
def processar_video(video_path, output_dir):
    """
    Processa um vídeo e salva resultados em output_dir.
    output_dir: pasta onde serão salvos imagens, TXT e cópia do vídeo
    """
    video_path = Path(video_path)
    output_dir = Path(output_dir)
    criar_pastas([output_dir, output_dir / "imagens"])

    resultados_txt = output_dir / "resultados.txt"
   

    print(f"[INFO] Processando vídeo {video_path.name}...")

    cap, fps = abrir_video(video_path)
    buffer = []
    ultimo_frame_img = None
    ultimo_salvamento_txt = time.time()
    frame_idx = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_idx += 1
        tempo = frame_idx / fps

        detections = detectar(frame)
        ultimo_frame_img = adicionar_ao_buffer(buffer, frame, detections, tempo, ultimo_frame_img)

        if time.time() - ultimo_salvamento_txt >= INTERVALO_SALVAR_TXT and buffer:
            salvar_buffer(buffer, output_dir, resultados_txt)
            ultimo_salvamento_txt = time.time()

    if buffer:
        salvar_buffer(buffer, output_dir, resultados_txt)

    cap.release()
    print(f"[OK] Processamento finalizado para {video_path.name} em {output_dir}")
    os.remove(video_path)


def obter_videos_na_pasta(pasta):
    """Retorna apenas arquivos de vídeo na pasta."""
    extensoes_validas = {".mp4", ".avi", ".mov", ".mkv"}
    return [
        arq for arq in Path(pasta).iterdir()
        if arq.is_file() and arq.suffix.lower() in extensoes_validas
    ]

def remover_video_processado(caminho_video):
    """
    Remove o vídeo original após o processamento.
    Recebe o caminho completo do arquivo.
    """
    try:
        if os.path.exists(caminho_video):
            os.remove(caminho_video)
            print(f"[INFO] Vídeo removido: {caminho_video}")
        else:
            print(f"[AVISO] Vídeo não encontrado para remoção: {caminho_video}")
    except Exception as e:
        print(f"[ERRO] Não foi possível remover o vídeo {caminho_video}: {e}")