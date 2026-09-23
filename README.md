# Rastreio de Pessoas em Múltiplas Câmeras com Soft Biometrics

> Trabalho de Conclusão de Curso em Ciência da Computação (Universidade Presbiteriana Mackenzie): *"Rastreio de Indivíduos em Múltiplas Câmeras Utilizando Soft Biometrics, Inteligência Artificial e Visão Computacional"*.

Sistema que processa vídeos de várias câmeras e permite **buscar uma pessoa por características visuais**, como gênero e cor da roupa, em vez de depender só de reconhecimento facial. É útil em cenários de segurança em que o rosto nem sempre aparece com qualidade.

<!-- Adicione aqui um GIF ou print da tela de busca, por exemplo: ![Demo](docs/demo.gif) -->

## Como funciona

```
Vídeo da câmera ─► Detecção de pessoas ─► Extração de soft biometrics ─► Base indexada ─► Busca pelo operador
                     (YOLOv5s)              • Gênero (OpenCV DNN)          por câmera       (cor + gênero)
                                            • Cor da roupa (U-Net)
                                            • Face (MFA-ViT)
```

1. **Ingestão:** o administrador cadastra câmeras. Cada uma ganha uma pasta de entrada, e os vídeos colocados ali são processados automaticamente.
2. **Detecção:** o **YOLOv5s** localiza as pessoas em cada quadro e recorta cada detecção.
3. **Soft biometrics:** cada recorte passa por três modelos:
   - **Gênero:** localizador de face + classificador Caffe via OpenCV DNN;
   - **Cor da roupa:** segmentação de vestimenta com U-Net estendida e extração da cor predominante;
   - **Face:** embeddings com **MFA-ViT** (*Flexible Biometrics Recognition*, CVPR 2024).
4. **Busca:** o operador escolhe gênero e cor, e o sistema devolve as ocorrências encontradas em cada câmera.

## Destaques técnicos

- Pipeline modular: cada biometria é um módulo independente orquestrado pelo `Soft_Biometrics_Manager`.
- Integração de modelos de fontes diferentes (PyTorch, Caffe/OpenCV DNN) em um único fluxo.
- Interface desktop em **Tkinter** com dois perfis de acesso (administrador e operador) e senhas com hash **bcrypt**.
- Inferência em GPU com **PyTorch + CUDA**.

## Tecnologias

Python 3.10 · PyTorch · OpenCV · YOLOv5 · Vision Transformers (MFA-ViT) · U-Net · Tkinter · SQLite · bcrypt

## Estrutura

```
├── main.py                         # ponto de entrada (interface)
├── FrontEnd/                       # telas: login, administrador, operador
└── BackEnd/
    ├── BackEnd_Manager.py          # orquestra o processamento
    ├── Cameras_estoque_video/      # gestão de câmeras e vídeos
    ├── Deteccao_pessoas_Yolov5/    # detecção de pessoas
    ├── Soft_biometrics_rastreio_de_pessoas/
    │   ├── Identificador_De_Genero_Open_CV/
    │   ├── Identificador_De_Face_FBR/   # MFA-ViT
    │   └── cloth_segmentation/          # cor da roupa
    └── Login/                      # autenticação
```

## Próximos passos

Estou evoluindo o projeto de MVP acadêmico para uma aplicação completa:

- [ ] **Trajetória entre câmeras:** reconstruir o caminho provável de uma pessoa (módulo `Caminho_Possivel`, em desenvolvimento)
- [ ] Interface web no lugar da interface desktop
- [ ] Métricas de avaliação (precisão da busca por atributo)

---

## Executando localmente

### Requisitos

- Python **3.10**
- GPU NVIDIA com CUDA 11.7 (o projeto usa `torch==1.13.1+cu117`)

```bash
git clone https://github.com/chesco502/rastreio-multicamera-soft-biometrics.git
cd rastreio-multicamera-soft-biometrics

python3.10 -m venv .venv
# Windows: .\.venv\Scripts\activate  |  Linux/Mac: source .venv/bin/activate

pip install -r requirements.txt
pip install -r requirements2.txt
```

### Pesos dos modelos

Os pesos não estão no repositório por causa do tamanho. Baixe e coloque em:

| Modelo | Destino | Fonte |
|---|---|---|
| YOLOv5s | `BackEnd/Deteccao_pessoas_Yolov5/yolov5s.pt` | [ultralytics/yolov5](https://github.com/ultralytics/yolov5) |
| Gênero (Caffe) | `BackEnd/Soft_biometrics_rastreio_de_pessoas/Identificador_De_Genero_Open_CV/Modelos/Identificador_De_Genero/Pesos_genero.caffemodel` | [Gender-and-Age-Detection](https://github.com/smahesh29/Gender-and-Age-Detection) |
| Localizador de face | `.../Identificador_De_Genero_Open_CV/Modelos/Localizador_face/Pesos_face.caffemodel` | [OpenCV face_detector](https://github.com/opencv/opencv/tree/4.x/samples/dnn/face_detector) |
| MFA-ViT | `BackEnd/Soft_biometrics_rastreio_de_pessoas/Identificador_De_Face_FBR/pretrained/MFA-ViT.pt` | Flexible Biometrics Recognition (CVPR 2024) |
| Segmentação de roupa | `BackEnd/Soft_biometrics_rastreio_de_pessoas/cloth_segmentation/model/cloth_segm.pth` | ClothingParsing (Extended U-Net) |

### Uso

```bash
python main.py
```

- **Administrador:** cadastra câmeras e coloca vídeos em `BackEnd/Cameras_estoque_video/<camera>/input`.
- **Operador:** em *Realizar Busca*, escolhe cor e gênero e executa a busca.

Na primeira execução existem usuários de demonstração (`admin` e `operador`). Troque as senhas antes de qualquer uso real.

**Erro comum:** `ModuleNotFoundError: No module named 'tkinter'`. Reinstale o Python 3.10 pelo instalador oficial ou com `winget install Python.Python.3.10`.

## Autor

**Francesco Zangrandi Coppola** · [GitHub](https://github.com/chesco502)
