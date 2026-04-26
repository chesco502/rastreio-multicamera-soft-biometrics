# Rastreio de pessoas em diferentes câmeras utilizando soft biometrics, IA e visão computacional
###

### 0. Clonar o Repositório

```bash
git clone --recurse-submodules http://mackcloud.mackenzie.br/gitlab/living-lab/projects/video-analitico/soft-biometrics/tcc.git
cd tcc
```

---


### 0.1 O Programa Depende de Python **3.10**  é recomendado a criação de um ambiente virtual (Criar na pasta TCC)

#### Download do Python 3.10

**Opção 1 — via winget (recomendado no Windows):**
```bash
winget install Python.Python.3.10
```

**Opção 2 — via site oficial:**
- Acesse [python.org/downloads/release/python-31011](https://www.python.org/downloads/release/python-31011/)
- Baixe o instalador **Windows installer (64-bit)**
- Durante a instalação, marque a opção **"Add Python to PATH"**

---

   - **Guia Sobre Ambientes Virtuais** [python.org](https://docs.python.org/3/library/venv.html)  
   **Lista de Commandos**
    py -3.10 -m venv .venv

    .\.venv\Scripts\Activate
---

## Modelos Utilizados

### 1. YOLOv5 — Detecção de Pessoas
- **Repositório:** [ultralytics/yolov5](https://github.com/ultralytics/yolov5/releases/download/v7.0/yolov5s.pt)
- **Variante utilizada:** YOLOv5s 
- **Caminho de onde deve ser armazenado**("TCC\BackEnd\Deteccao_pessoas_Yolov5\yolov5s.pt")


---

### 2. Modelo de Gênero (OpenCV)
- **Modelo:** [Download via Google Drive](https://drive.google.com/open?id=1AW3WduLk1haTVAxHOkVS_BEzel1WXQHP)(ja incluso)
**Caminho**(TCC\BackEnd\Soft_biometrics_rastreio_de_pessoas\Identificador_De_Genero_Open_CV\Modelos\Identificador_De_Genero\Modelo_genero.prototxt)

- **Peso:** [Download via Google Drive](https://drive.google.com/open?id=1W_moLzMlGiELyPxWiYQJ9KFaXroQ_NFQ)

 **Caminho**(TCC\BackEnd\Soft_biometrics_rastreio_de_pessoas\Identificador_De_Genero_Open_CV\Modelos\Identificador_De_Genero\Pesos_genero.caffemodel)

- **Modelo2** [Download Via Repositorio Github](dowload em https://github.com/opencv/opencv/blob/4.x/samples/dnn/face_detector/deploy.prototxt)

 **Caminho**(BackEnd/Soft_biometrics_rastreio_de_pessoas/Identificador_De_Genero_Open_CV/Modelos/Localizador_face/Modelo_face.txt)


- **Pesos2** [Download Via Repositorio Github]( https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20180205_fp16/res10_300x300_ssd_iter_140000_fp16.caffemodel)

**Caminho**(TCC\BackEnd\Soft_biometrics_rastreio_de_pessoas\Identificador_De_Genero_Open_CV\Modelos\Localizador_face\Pesos_face.caffemodel")


- **Fonte:** [Gender-and-Age-Detection (smahesh29)](https://github.com/smahesh29/Gender-and-Age-Detection)
-
---

### 3. Modelo de Reconhecimento Facial — MFA-ViT
- **Modelo:** [Download via Google Drive](https://drive.google.com/file/d/1miBvWW16p6axtBBmk4KcXiFeKZJxqklv/view?usp=drive_link)

**Caminho**("TCC\BackEnd\Soft_biometrics_rastreio_de_pessoas\Identificador_De_Face_FBR\pretrained\MFA-ViT.pt")

- **Artigo:** [Flexible Biometrics Recognition — CVPR 2024](https://openaccess.thecvf.com/content/CVPR2024/papers/Tiong_Flexible_Biometrics_Recognition_Bridging_the_Multimodality_Gap_through_Attention_Alignment_CVPR_2024_paper.pdf)


---
### 4. Modelo de Analise de Cor de Roupa
- **Modelo:** [Download via Google Drive](https://drive.google.com/file/d/1eAT772TcR4y9pAyj23QzaAZYPMuV8W47/view?usp=drive_link)

**Caminho**(TCC\BackEnd\Soft_biometrics_rastreio_de_pessoas\cloth_segmentation\model\cloth_segm.pth)

-**Fonte** [ClothingParsing using Extended U-Net](https://www.scitepress.org/Papers/2021/101777/101777.pdf)

-**Codigo Usado Como Referencia** [Download via Github](https://github.com/wildoctopus/huggingface-cloth-segmentation)




## Download dos Modelos

Antes de executar o sistema, faça o download dos pesos e modelos listados acima e coloque-os nos diretórios esperados pela aplicação.


------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

## Instalação de Dependências

Certifique-se de ter o **Python 3.8+** e o **pip** instalados. Em seguida, execute:

```bash
pip install -r requirements.txt
pip install -r requirements2.txt
```

**Atenção:** O projeto utiliza **PyTorch com suporte a CUDA 11.7** (`torch==1.13.1+cu117`). Certifique-se de que sua máquina possui uma GPU NVIDIA compatível e os drivers CUDA instalados.

## Executando o programa:

```bash
python main.py
```
------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




## Como Usar o Sistema

### Acesso como Administrador

**Login:** `admin`  
**Senha:** `123`

Como administrador, você pode:
- **Adicionar cameras:** cria o diretorio com o nome dado a camera para o input e output das imagens 
- **Processar vídeos:** Adicione o arquivo de vídeo na pasta `input` da câmera correspondente. O sistema irá processá-lo automaticamente.
- **Adicionar imagens já processadas:** Adicione as imagens diretamente na pasta `"TCC\BackEnd\Cameras_estoque_video\Nome_da_camera\output"`.

**Atenção:** a pasta de cameras somente sera criada apos a funcao **Adicionar cameras:** ser executada
----

----
### Acesso como Operador

**Login:** `operador`  
**Senha:** `123`

**Passos para realizar uma busca:**
1. Faça login como operador
2. Selecione a opção **"Realizar Busca"**
3. Escolha uma **cor** e um **gênero**
4. Execute a busca

------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

**Erros Frequentes** 

ModuleNotFoundError: No module named 'tkinter'

solucao: Reinstalar Python usando o seguinte comando  winget install Python.Python.3.10 



