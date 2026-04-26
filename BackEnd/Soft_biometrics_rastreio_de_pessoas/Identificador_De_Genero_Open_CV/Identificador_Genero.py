import cv2
import numpy as np
import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

_DIR = os.path.dirname(os.path.abspath(__file__))
_FACE_PROTO  = os.path.join(_DIR, r"Modelos\Localizador_face\Modelo_face.txt")
_FACE_MODEL  = os.path.join(_DIR, r"Modelos\Localizador_face\Pesos_face.caffemodel")
_GENDER_PROTO = os.path.join(_DIR, r"Modelos\Identificador_De_Genero\Modelo_genero.prototxt")
_GENDER_MODEL = os.path.join(_DIR, r"Modelos\Identificador_De_Genero\Pesos_genero.caffemodel")

MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
GENDER_LIST = ['Male', 'Female']
MAX_WIDTH = 1280

_gender_call_count = 0
_gender_lock = threading.Lock()

# Cada thread carrega suas próprias redes uma única vez — cv2.dnn.Net não é thread-safe.
_thread_local = threading.local()


def _get_nets():
    if not hasattr(_thread_local, 'face_net'):
        _thread_local.face_net = cv2.dnn.readNetFromCaffe(_FACE_PROTO, _FACE_MODEL)
        _thread_local.gender_net = cv2.dnn.readNetFromCaffe(_GENDER_PROTO, _GENDER_MODEL)
    return _thread_local.face_net, _thread_local.gender_net


def _get_faces(frame, confidence_threshold=0.5):
    face_net, _ = _get_nets()
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177.0, 123.0))
    face_net.setInput(blob)
    output = np.squeeze(face_net.forward())
    h, w = frame.shape[:2]
    faces = []
    for i in range(output.shape[0]):
        if output[i, 2] > confidence_threshold:
            box = output[i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype(int)
            x1, y1 = max(x1 - 10, 0), max(y1 - 10, 0)
            x2, y2 = max(x2 + 10, 0), max(y2 + 10, 0)
            faces.append((x1, y1, x2, y2))
    return faces


def _resize_to_max_width(frame):
    h, w = frame.shape[:2]
    if w <= MAX_WIDTH:
        return frame
    return cv2.resize(frame, (MAX_WIDTH, int(h * MAX_WIDTH / w)), interpolation=cv2.INTER_AREA)


def predict_gender(input_path: str):
    global _gender_call_count
    with _gender_lock:
        _gender_call_count += 1
        count = _gender_call_count
    print(f"[genero] chamada #{count}")

    img = cv2.imread(input_path)
    if img is None:
        return None
    _, gender_net = _get_nets()
    frame = _resize_to_max_width(img)
    for x1, y1, x2, y2 in _get_faces(frame):
        face_img = frame[y1:y2, x1:x2]
        blob = cv2.dnn.blobFromImage(
            face_img, 1.0, (227, 227), MODEL_MEAN_VALUES, swapRB=False, crop=False
        )
        gender_net.setInput(blob)
        preds = gender_net.forward()
        idx = preds[0].argmax()
        return GENDER_LIST[idx], float(preds[0][idx])
    return None


def predict_gender_batch(paths: list, max_workers: int = None) -> dict:
    """
    Executa predict_gender em paralelo para uma lista de caminhos.
    Retorna {caminho: (genero, confiança) | None}.
    Cada worker thread carrega sua própria cópia das redes.
    """
    if max_workers is None:
        max_workers = min(4, os.cpu_count() or 1)

    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_path = {executor.submit(predict_gender, p): p for p in paths}
        for future in as_completed(future_to_path):
            path = future_to_path[future]
            try:
                results[path] = future.result()
            except Exception:
                results[path] = None
    return results
