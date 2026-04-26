from pathlib import Path
import cv2

def criar_pastas(lista_pastas):
    for pasta in lista_pastas:
        Path(pasta).mkdir(parents=True, exist_ok=True)

def obter_videos_na_pasta(nome_pasta):
    pasta = Path(nome_pasta)
    return list(pasta.glob("*.mp4")) + list(pasta.glob("*.avi")) + list(pasta.glob("*.mov"))

def salvar_txt(caminho, conteudo):
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with open(caminho, "a", encoding="utf-8") as f:
        f.write(conteudo)

def salvar_imagem(pasta_imgs,x1,y1 ,tempo,  img):
    import os
    Path(pasta_imgs).mkdir(parents=True, exist_ok=True)
    arquivo_config_manager = os.path.join(pasta_imgs, r"imagens")
    nome = f"{tempo:.2f}"+str(x1)+str(y1)+".jpg"
    cv2.imwrite(str(Path(pasta_imgs) / nome), img)
