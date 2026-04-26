import sys
import os

sys.path.insert(0, os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..")))

from BackEnd.Cameras_estoque_video.Cam_Maneger import Cam_Maneger

if __name__ == "__main__":
    cm = Cam_Maneger()
    cm.carregar_cam_maneger()
    cameras = cm.listar_cameras()
    if not cameras:
        print("Nenhuma câmera cadastrada.")
        sys.exit(0)

    print(f"{len(cameras)} câmera(s) encontrada(s):")
    for cam in cameras:
        print(f"  - {os.path.basename(cam['caminho'])}")

    resposta = input("\nDeseja limpar o conteúdo de todas as câmeras? (s/N): ").strip().lower()
    if resposta != "s":
        print("Operação cancelada.")
        sys.exit(0)

    cm.limpar_cameras()
    print("Conteúdo das câmeras limpo com sucesso.")
