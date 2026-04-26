# Rastreio de Indivíduos em Diferentes Câmeras Utilizando Soft Biometrics, IA e Visão Computacional

**Autor:** Francesco Coppola  
**Curso:** Engenharia de Computação / Ciência da Computação  
**Instituição:** Universidade Presbiteriana Mackenzie  
**Data:** Abril de 2026

---

## Resumo

A crescente proliferação de sistemas de vigilância por vídeo gera volumes massivos de dados que tornam inviável a análise manual e eficiente de imagens por operadores humanos. Este trabalho apresenta o desenvolvimento de um sistema de reidentificação de pessoas em múltiplas câmeras não sobrepostas, utilizando exclusivamente **soft biometrics** — atributos físicos sutis e não identificatórios, como gênero aparente e cor predominante da vestimenta — em conformidade com os princípios da Lei Geral de Proteção de Dados (LGPD). O sistema integra quatro módulos de visão computacional e inteligência artificial: (1) detecção de pessoas via YOLOv5, que recorta automaticamente indivíduos de vídeos de vigilância; (2) classificação de gênero por rede neural baseada em OpenCV DNN com modelo Caffe; (3) segmentação e análise de cor de roupas por rede U-Net estendida (Extended U-Net); e (4) reidentificação facial incremental por similaridade de embeddings com o modelo MFA-ViT (CVPR 2024), utilizado como etapa de refinamento com validação humana. A interface gráfica desenvolvida em Tkinter permite dois perfis de acesso — administrador e operador — e guia o usuário num fluxo de busca por atributos (gênero e cor de roupa), validação visual das imagens candidatas e refinamento progressivo por similaridade facial. Os resultados demonstram a viabilidade de um protótipo funcional capaz de reduzir significativamente o escopo de busca manual em bases de vídeo, preservando a privacidade dos indivíduos ao evitar a coleta de dados biométricos primários.

**Palavras-chave:** Soft biometrics. Reidentificação de pessoas. Vigilância por vídeo. Visão computacional. YOLOv5. Segmentação de roupas. LGPD.

---

## Abstract

The growing proliferation of video surveillance systems generates massive volumes of data that make it unfeasible for human operators to analyze footage manually and efficiently. This work presents the development of a person re-identification system across multiple non-overlapping cameras, using exclusively **soft biometrics** — subtle, non-identifying physical attributes such as apparent gender and predominant clothing color — in compliance with Brazil's General Data Protection Law (LGPD). The system integrates four computer vision and artificial intelligence modules: (1) person detection via YOLOv5, which automatically crops individuals from surveillance video; (2) gender classification through an OpenCV DNN neural network with a Caffe model; (3) clothing segmentation and color analysis via Extended U-Net; and (4) incremental facial re-identification by embedding similarity with the MFA-ViT model (CVPR 2024), used as a refinement step with human validation. The graphical interface developed in Tkinter supports two access profiles — administrator and operator — and guides the user through a search flow based on attributes (gender and clothing color), visual validation of candidate images, and progressive refinement by facial similarity. The results demonstrate the feasibility of a functional prototype capable of significantly reducing the scope of manual search in video databases, while preserving individual privacy by avoiding the collection of primary biometric data.

**Keywords:** Soft biometrics. Person re-identification. Video surveillance. Computer vision. YOLOv5. Clothing segmentation. LGPD.

---

## 1. Introdução

### 1.1 Contexto e Motivação

Sistemas de vigilância por vídeo estão presentes em ambientes urbanos, comerciais e institucionais em escala crescente. A densidade de câmeras em cidades ao redor do mundo tem aumentado consideravelmente nas últimas décadas, gerando um volume de dados que supera em muito a capacidade de análise humana. Estima-se que, em grandes centros urbanos, um operador de segurança pode ser responsável por monitorar dezenas de câmeras simultaneamente — tarefa que, além de cognitivamente exaustiva, é sujeita a erros, omissões e fadiga.

Um cenário típico e recorrente é a busca por uma pessoa de interesse com base em descrição verbal: uma criança desaparecida com determinada roupa, um suspeito com características físicas específicas, ou um indivíduo que precisa ser localizado em um ambiente monitorado. Atualmente, essa busca é realizada de forma majoritariamente manual, com operadores analisando gravações de múltiplas câmeras por horas ou até dias. O processo é lento, sujeito a falhas humanas, e frequentemente não cobre toda a base de dados disponível.

Surge, portanto, a necessidade de automatizar a reidentificação de indivíduos em diferentes câmeras e momentos, utilizando descrições de atributos para localizar ocorrências de uma pessoa de interesse em uma base de dados, dentro de uma área específica e em um determinado intervalo de tempo.

### 1.2 Definição do Problema

O problema central deste trabalho é a **reidentificação de pessoas em um conjunto de câmeras não sobrepostas**, sem depender de identificadores biométricos rígidos como reconhecimento facial ou impressões digitais. Em vez disso, o foco recai sobre os **soft biometrics** — atributos físicos e comportamentais sutis como vestuário, gênero, estatura e cor do cabelo (Dantcheva et al., 2016).

A delimitação do trabalho exclui técnicas de reconhecimento facial como mecanismo primário de busca, concentrando-se nos atributos visíveis que não identificam univocamente uma pessoa, mas fornecem pistas suficientes para diferenciá-la em uma multidão. Esses atributos, embora ambíguos e não permanentes (diversas pessoas podem usar camisa azul, e uma mesma pessoa pode trocar de roupa ao longo do dia), servem como evidências adicionais valiosas para reduzir a dimensão da busca.

A escolha por soft biometrics como mecanismo primário também está fundamentada em preocupações éticas e legais, especialmente no que diz respeito à privacidade e à **Lei Geral de Proteção de Dados Pessoais (LGPD)** (Brasil, 2018). Ao evitar o uso de traços que possibilitam a identificação direta e inequívoca de um indivíduo, reduz-se o risco de violações de direitos de privacidade, uma vez que se evita a coleta de informações classificadas como dados sensíveis pela legislação.

### 1.3 Objetivos

**Objetivo Geral:** Desenvolver um sistema de reidentificação de pessoas que, a partir de uma descrição semântica de atributos (gênero e cor da roupa), seja capaz de localizar e indexar imagens nas quais uma pessoa de interesse aparece, mesmo quando capturada por diferentes câmeras, utilizando soft biometrics como mecanismo primário de busca.

**Objetivos Específicos:**

1. Implementar um módulo de detecção de pessoas em vídeo utilizando o detector YOLOv5, para identificar e recortar automaticamente frames contendo pessoas.
2. Desenvolver um módulo de identificação de atributos soft biométricos, contemplando classificação de gênero aparente e detecção de cor predominante da vestimenta.
3. Integrar os módulos em um sistema unificado capaz de realizar busca por atributos e retornar candidatos ranqueados por grau de correspondência.
4. Implementar um mecanismo de refinamento incremental por similaridade facial (MFA-ViT) acionado pelo operador durante a validação manual das imagens.
5. Desenvolver uma interface gráfica intuitiva com dois perfis de acesso (administrador e operador), permitindo o gerenciamento de câmeras, ingestão de vídeos e execução de buscas.

### 1.4 Estrutura do Trabalho

O restante deste documento está organizado da seguinte forma: a **Seção 2** apresenta a fundamentação teórica sobre soft biometrics, os modelos de visão computacional utilizados e o arcabouço legal relevante. A **Seção 3** descreve a arquitetura do sistema desenvolvido, seus módulos e o fluxo de funcionamento. A **Seção 4** discute os resultados obtidos. A **Seção 5** apresenta as conclusões e trabalhos futuros. Por fim, as **Referências** listam os trabalhos citados.

---

## 2. Fundamentação Teórica

### 2.1 Soft Biometrics

Biometria refere-se ao uso de características físicas ou comportamentais mensuráveis para identificação de indivíduos. Os biométricos **rígidos** (hard biometrics), como impressões digitais, geometria da íris e padrão facial, oferecem alta precisão de identificação, mas requerem cooperação do indivíduo, equipamentos específicos e, no contexto de vigilância, levantam sérias questões de privacidade e legalidade.

Os **soft biometrics**, por outro lado, são atributos mais sutis e de granularidade menor, que por si só não identificam univocamente uma pessoa, mas que em conjunto constituem uma descrição útil para diferenciá-la em uma multidão (Dantcheva et al., 2016). Exemplos incluem:

- **Gênero aparente**: masculino ou feminino, inferido a partir de características faciais e corporais.
- **Cor e tipo de vestimenta**: cor da camisa, calça, vestido; peças de roupa visíveis na câmera.
- **Estatura e porte físico**: altura e silhueta corporal estimadas.
- **Cor do cabelo e da pele**: atributos cromáticos derivados de regiões específicas da imagem.

Para fins de vigilância e reidentificação, soft biometrics apresentam vantagens importantes: podem ser extraídos automaticamente a partir de imagens de qualidade variável, não exigem cooperação do indivíduo monitorado, e geram uma representação descritiva que pode ser comparada com buscas textuais realizadas por operadores humanos.

### 2.2 Detecção de Pessoas — YOLOv5

A família de detectores **YOLO** (You Only Look Once) (Redmon et al., 2016) estabeleceu um paradigma de detecção em tempo real por meio de uma única passagem pela rede neural, e a versão YOLOv5s (Jocher et al., 2020) é utilizada neste trabalho para detectar indivíduos em frames de vídeo. O modelo, pré-treinado no dataset COCO e configurado para detectar exclusivamente a classe `person`, recorta cada detecção com confiança superior a 50% e a salva como imagem individual com o timestamp do vídeo como parte do nome do arquivo. Para evitar redundância, um intervalo mínimo de 5 segundos é mantido entre frames consecutivos salvos para a mesma câmera.

### 2.3 Classificação de Gênero — OpenCV DNN com Caffe

A classificação de gênero aparente é realizada em duas etapas: primeiro, uma rede SSD com backbone ResNet-10 (`res10_300x300_ssd_iter_140000_fp16.caffemodel`) detecta faces na imagem recortada; em seguida, para cada face encontrada, um blob de 227×227 pixels é pré-processado pela subtração de médias de canal e submetido ao classificador de gênero Caffe (Levi e Hassner, 2015), que retorna probabilidades para as classes `Male` e `Female`. Caso nenhuma face seja detectada, a função `predict_gender` retorna `None` e a imagem é desconsiderada para esse atributo. Ambos os modelos são carregados via `cv2.dnn.readNetFromCaffe` e a implementação baseia-se no repositório público de detecção de gênero e idade com OpenCV (smahesh29, 2020).

### 2.4 Segmentação e Análise de Cor de Roupas — Extended U-Net

Para determinar a cor predominante da vestimenta de um indivíduo, é necessário isolar previamente a região de roupa na imagem, descartando fundo, pele e cabelo. Este trabalho utiliza um modelo de segmentação baseado em **Extended U-Net** (Nair et al., 2021), carregado via PyTorch a partir do checkpoint `cloth_segm.pth`, que produz uma máscara binária onde pixels com valor maior que zero correspondem a vestuário. Com a máscara gerada, a função `media_cor_de_roupa` itera sobre cada pixel de roupa e aplica `color_match`, que mapeia valores RGB a cinco classes discretas (preto, branco, vermelho, verde e azul) por meio de faixas predefinidas; a cor com maior frequência (moda) é retornada como resultado. A implementação foi adaptada do repositório `wildoctopus/huggingface-cloth-segmentation`.

### 2.5 Reidentificação Facial — MFA-ViT

Como mecanismo de refinamento acionado pelo operador, o sistema integra o **MFA-ViT** (Multi-modal Flexible Attention Vision Transformer, CVPR 2024 — Tiong et al., 2024), um modelo biométrico flexível que gera embeddings faciais de alta qualidade comparáveis por similaridade cosseno. Quando o operador confirma uma imagem como positiva, a função `Detector_face_caminho` carrega o modelo MFA-ViT, computa o embedding da face de referência e o compara incrementalmente com cada candidato restante na fila: imagens com similaridade acima do threshold de 0,50 atualizam o pool de referências (refinando o centróide progressivamente), e toda a fila é reordenada da mais para a menos similar, priorizando na revisão os candidatos com maior probabilidade de ser a mesma pessoa.

### 2.6 Lei Geral de Proteção de Dados (LGPD)

A Lei nº 13.709/2018 — LGPD (Brasil, 2018) — regula o tratamento de dados pessoais no Brasil e estabelece categorias especiais de dados sensíveis, entre os quais se incluem dados biométricos que permitam a identificação direta de pessoas naturais. O uso de reconhecimento facial como mecanismo primário de vigilância massiva levanta questões legais e éticas significativas sob essa legislação.

A abordagem deste trabalho foi desenvolvida de forma consciente para minimizar os riscos regulatórios:

- **Soft biometrics como mecanismo primário**: gênero aparente e cor de roupa são atributos descritivos que não permitem identificação inequívoca de um indivíduo.
- **Reconhecimento facial como refinamento voluntário**: o MFA-ViT só é acionado quando o operador confirma manualmente uma imagem, usando-a como referência para busca de similaridade — não há varredura facial automática da base completa.
- **Validação humana obrigatória**: toda imagem retornada pelo sistema passa por confirmação explícita do operador antes de ser considerada uma correspondência positiva.
- **Sem armazenamento de embeddings biométricos**: o sistema não persiste os vetores faciais gerados; eles são calculados em memória durante a sessão de busca.

---

## 3. Desenvolvimento

### 3.1 Visão Geral da Arquitetura

O sistema é composto por três camadas principais:

```
┌─────────────────────────────────────────────────────────────────┐
│                        FRONTEND (Tkinter)                        │
│  Login → Admin/Operador → Busca → Revisão → Resultado Final      │
└──────────────────────────┬──────────────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────────────┐
│                    BACKEND MANAGER                               │
│  start() · search() · adicionar_filmagens() · Atualizar_filmagens()│
└──────┬───────────────┬──────────────────────┬───────────────────┘
       │               │                      │
┌──────▼──────┐ ┌──────▼──────┐ ┌─────────────▼──────────────────┐
│  Detecção   │ │  Câmeras    │ │       Soft Biometrics           │
│  YOLOv5    │ │  Estoque    │ │  ┌─────────────┐ ┌───────────┐  │
│  (yolo_    │ │  (Cam_      │ │  │   Gênero   │ │   Cor     │  │
│ processor) │ │  Maneger)   │ │  │  (OpenCV)  │ │  Roupa    │  │
└─────────────┘ └─────────────┘ │  └─────────────┘ │(U-Net)    │  │
                                │                   └───────────┘  │
                                │  ┌───────────────────────────┐  │
                                │  │  Reidentificação Facial   │  │
                                │  │       (MFA-ViT)            │  │
                                │  └───────────────────────────┘  │
                                └────────────────────────────────┘
```

### 3.2 Estrutura de Diretórios

```
tcc/
├── main.py                          # Ponto de entrada da aplicação
├── requirements.txt                  # Dependências principais
├── requirements2.txt                 # Dependências PyTorch + CUDA
├── BackEnd/
│   ├── BackEnd_Manager.py           # Orquestrador do backend
│   ├── Login/
│   │   ├── LoginManager.py          # Autenticação (SQLite + bcrypt)
│   │   └── users.db                 # Banco de dados de usuários
│   ├── Cameras_estoque_video/
│   │   └── Cam_Maneger.py           # Gerenciamento de câmeras
│   ├── Deteccao_pessoas_Yolov5/
│   │   ├── yolo_processor.py        # Detecção de pessoas em vídeo
│   │   ├── utils_io.py              # Utilitários de I/O
│   │   ├── yolov5s.pt               # Pesos YOLOv5s (download separado)
│   │   └── models/ + utils/         # Código-fonte YOLOv5
│   ├── Yolo_Dec_Pessoas/
│   │   └── yolo_processor.py        # Versão de processamento de diretório
│   └── Soft_biometrics_rastreio_de_pessoas/
│       ├── Soft_Biometrics_Manager.py   # Orquestrador de soft biometrics
│       ├── Identificador_De_Genero_Open_CV/
│       │   ├── Identificador_Genero.py  # Classificação de gênero
│       │   └── Modelos/
│       │       ├── Identificador_De_Genero/  # Modelo + pesos gênero Caffe
│       │       └── Localizador_face/          # Modelo + pesos face SSD
│       ├── cloth_segmentation/
│       │   ├── app.py               # Interface e função media_cor_de_roupa
│       │   ├── process.py           # Pipeline de segmentação U-Net
│       │   └── model/
│       │       └── cloth_segm.pth   # Pesos U-Net (download separado)
│       └── Identificador_De_Face_FBR/
│           ├── Detector_de_face.py  # Reidentificação facial MFA-ViT
│           └── pretrained/
│               └── MFA-ViT.pt       # Pesos MFA-ViT (download separado)
└── FrontEnd/
    ├── Login.py                     # Tela de login
    ├── Admin.py                     # Painel do administrador
    ├── Operador.py                  # Painel do operador
    ├── Busca.py                     # Formulário de busca por atributos
    ├── Mostra_pessoa.py             # Revisão e validação de imagens
    ├── Resultado_Final.py           # Exibição dos resultados confirmados
    ├── Config_Camera.py             # Configuração de câmeras
    ├── Cadastro_Camera.py           # Cadastro de câmeras
    ├── Deletar_Camera.py            # Exclusão de câmeras
    ├── ListarCameras.py             # Listagem de câmeras
    ├── Adicionar_Filmagem.py        # Upload de vídeos/imagens
    ├── Usuarios_display.py          # Gestão de usuários
    └── Opcoes_login.py              # Opções de autenticação
```

### 3.3 Fluxo de Dados Principal

O fluxo completo do sistema é dividido em duas fases: **ingestão** e **busca**.

#### Fase 1 — Ingestão de Vídeo

```
Administrador
    │
    ├─→ Cadastra câmera (nome, latitude, longitude, ângulo)
    │       └─→ Cria estrutura: cameras/<nome>/input/ e cameras/<nome>/output/
    │
    ├─→ Adiciona vídeo à pasta input/ da câmera
    │
    └─→ Dispara "Atualizar Filmagens"
            └─→ Cam_Maneger.refresh_cameras()
                    └─→ Para cada câmera:
                            └─→ processar_diretorio(input/, output/)
                                    └─→ YOLOv5: detecta pessoas frame a frame
                                            └─→ Salva recortes em output/
                                                (nome: <timestamp>_<x1>_<y1>.jpg)
```

#### Fase 2 — Busca por Atributos

```
Operador
    │
    ├─→ Seleciona critérios: gênero (Male/Female) + cor da roupa
    │
    └─→ Executa busca → BackEnd_Manager.search(descricao)
            └─→ Soft_Biometrics_Manager.search_description(descricao, cameras)
                    │
                    ├─→ Para cada câmera → para cada imagem em output/:
                    │       ├─→ predict_gender(imagem) → positivo_genero[]
                    │       └─→ media_cor_de_roupa(imagem) → positivo_cor[]
                    │
                    └─→ combinar_listas(positivo_cor, positivo_genero)
                            └─→ Imagens em ambas listas primeiro,
                                depois as que estão em apenas uma lista
                                    │
                                    └─→ TelaRevisarImagens
                                            │
                                            ├─→ Operador: "Sim" (confirma)
                                            │       └─→ MFA-ViT reordena fila
                                            │           por similaridade facial
                                            │
                                            └─→ Operador: "Não" (descarta)
                                                    └─→ Próxima imagem

```

### 3.4 Módulo de Gerenciamento de Câmeras (`Cam_Maneger`)

O `Cam_Maneger` é responsável pelo ciclo de vida das câmeras cadastradas no sistema. Cada câmera é representada por um objeto `Camera` que persiste suas configurações (latitude, longitude, ângulo e caminho) em arquivo `config.pkl` via serialização Python (pickle). O gerenciador de câmeras é persistido em `config_maneger.pkl`.

**Atributos de uma câmera:**
| Atributo | Tipo | Descrição |
|---|---|---|
| `latitude` | float | Coordenada geográfica |
| `longitude` | float | Coordenada geográfica |
| `angle` | float | Ângulo de visão da câmera |
| `caminho_camera` | str | Caminho absoluto da pasta da câmera |

**Operações suportadas:**
- `adicionar_nova_camera(lat, lon, angle, nome)`: registra câmera e cria estrutura de pastas.
- `listar_cameras()`: retorna lista de dicionários com informações de todas as câmeras.
- `deletar_camera(nome)`: remove câmera, apaga arquivos e atualiza o grafo de caminhos possíveis.
- `refresh_cameras()`: processa vídeos pendentes em todas as pastas `input/`.

### 3.5 Módulo de Detecção de Pessoas (`yolo_processor`)

O processamento de vídeos é realizado pela função `processar_video(video_path, output_dir)`:

1. O vídeo é aberto com OpenCV (`cv2.VideoCapture`) e percorrido frame a frame.
2. Cada frame é submetido ao modelo YOLOv5 via `torch.hub.load` (modo offline, com pesos locais).
3. Detecções da classe `person` com confiança > 50% são retidas.
4. Um mecanismo de **throttling temporal** (intervalo mínimo de 5 segundos entre imagens salvas) evita frames redundantes do mesmo indivíduo em posições muito próximas.
5. Os recortes são salvos em `output/` com nome `<timestamp>_<x1>_<y1>.jpg`, onde o timestamp corresponde ao tempo em segundos dentro do vídeo — informação útil para contextualização temporal.
6. Após o processamento, o arquivo de vídeo original é **removido** (`os.remove(video_path)`), mantendo apenas os recortes.

### 3.6 Módulo de Soft Biometrics (`Soft_Biometrics_Manager`)

A função `search_description(descricao, cameras)` é o coração da busca:

```python
def search_description(descricao, cameras):
    genero_alvo, cor_de_roupa_alvo = descricao
    positivo_genero = []
    positivo_cor_de_roupa = []
    
    for caminho in cameras:
        imagens_diretorio = os.path.join(caminho, "output")
        for foto in os.listdir(imagens_diretorio):
            caminho_foto = os.path.join(imagens_diretorio, foto)
            
            genero = predict_gender(caminho_foto)
            cor = media_cor_de_roupa(caminho_foto)
            
            if cor == cor_de_roupa_alvo:
                positivo_cor_de_roupa.append([caminho_foto])
            if genero is not None and genero[0] == genero_alvo:
                positivo_genero.append([caminho_foto])
    
    return combinar_listas(positivo_cor_de_roupa, positivo_genero)
```

A função `combinar_listas` implementa uma estratégia de **ranqueamento por correspondência múltipla**: imagens que satisfazem ambos os critérios (cor E gênero) aparecem primeiro; em seguida, aparecem imagens que satisfazem apenas um dos critérios. Este ranqueamento garante que os candidatos mais prováveis sejam revisados primeiro pelo operador.

### 3.7 Módulo de Reidentificação Facial (`Detector_de_face`)

Após o operador confirmar a primeira imagem positiva na tela de revisão, o sistema aciona o módulo MFA-ViT para reordenar a fila de candidatos restantes. A função `Detector_face_caminho(imagem_referencia, candidatos)`:

1. Carrega o modelo MFA-ViT com os pesos pré-treinados (`MFA-ViT.pt`).
2. Transforma a imagem de referência e cada candidato em tensores `[1, 1, 3, H, W]` (formato esperado pelo modelo).
3. Gera embeddings normalizados para cada imagem via `face_embedding()`.
4. Calcula similaridade cosseno entre cada candidato e o centróide do pool de referências.
5. Imagens confirmadas como correspondência (`score >= 0.50`) atualizam o pool, refinando o centróide progressivamente.
6. Retorna a lista de candidatos reordenada por score decrescente.

### 3.8 Sistema de Autenticação (`LoginManager`)

A autenticação é implementada com **SQLite** como banco de dados e **bcrypt** para hashing de senhas. A tabela `users` possui três colunas:

| Coluna | Tipo | Restrição |
|---|---|---|
| `username` | TEXT | PRIMARY KEY |
| `password_hash` | BLOB | NOT NULL |
| `role` | TEXT | CHECK(role IN ('admin', 'operador')) |

Dois perfis de acesso são suportados:

**Administrador (`admin`):**
- Gerenciar usuários (cadastrar, listar, deletar)
- Configurar câmeras (adicionar, editar, deletar)
- Carregar vídeos e disparar processamento YOLO

**Operador (`operador`):**
- Listar câmeras cadastradas
- Adicionar filmagens via interface
- Realizar buscas por atributos
- Validar imagens candidatas

### 3.9 Interface Gráfica (`FrontEnd`)

A interface é desenvolvida em **Tkinter**, a biblioteca padrão de GUI do Python, utilizando o padrão de múltiplos frames sobre uma única janela (`tk.Tk`). A classe `FrontManager` (em `main.py`) gerencia a navegação entre telas por meio do método `mostrar_tela(tela_classe)`, que eleva (`tkraise`) o frame correspondente sem recriá-lo.

**Fluxo de telas:**

```
TelaLogin
    ├─→ TelaAdmin
    │       ├─→ TelaOpcoesLogin (gerenciar usuários)
    │       └─→ TelaConfigCamera → TelaCadastroCamera / TelaDeletarCamera
    │
    └─→ TelaOperador
            ├─→ TelaListarCameras
            ├─→ TelaAdicionarFilmagem
            └─→ TelaBuscaPessoas
                    └─→ TelaRevisarImagens
                            └─→ TelaResultadoFinal
```

**Tela de Busca (`TelaBuscaPessoas`):** Permite ao operador selecionar gênero (Male/Female) via combobox e cor da roupa via seletor de cor RGB (colorchooser). O valor RGB selecionado é convertido para o nome de cor discreto mais próximo pela função `color_match`.

**Tela de Revisão (`TelaRevisarImagens`):** Exibe imagens candidatas uma a uma, permitindo ao operador confirmar ("Sim") ou descartar ("Não"). Ao confirmar uma imagem, o MFA-ViT reordena a fila remanescente por similaridade facial com a imagem confirmada.

**Tela de Resultado Final (`TelaResultadoFinal`):** Agrupa as imagens confirmadas por câmera de origem, exibindo miniaturas organizadas em grade. O nome da câmera é inferido a partir do caminho do arquivo (estrutura `.../nome_camera/output/arquivo.jpg`).

---

## 4. Tecnologias e Dependências

| Biblioteca | Versão | Finalidade |
|---|---|---|
| Python | 3.10 | Linguagem principal |
| PyTorch | 1.13.1+cu117 | Inferência YOLO e MFA-ViT (GPU CUDA 11.7) |
| OpenCV (`opencv-python`) | ≥ 4.x | Leitura de vídeo, processamento de imagem, inferência Caffe |
| Pillow | ≥ 9.0.0 | Carregamento e exibição de imagens |
| NumPy | ≥ 1.23.0 | Operações matriciais |
| Tkinter | (stdlib) | Interface gráfica |
| bcrypt | latest | Hash seguro de senhas |
| sqlite3 | (stdlib) | Banco de dados de usuários |
| gradio | latest | (Interface alternativa para cloth segmentation — não utilizado na UI principal) |
| torchvision | (transitivo) | Transforms para MFA-ViT |

**Hardware recomendado:**
- GPU NVIDIA com suporte a CUDA 11.7 (para inferência acelerada de YOLO e MFA-ViT)
- Mínimo 8 GB de RAM; recomendado 16 GB

---

## 5. Resultados e Discussão

> *(Esta seção deverá ser preenchida com os resultados dos experimentos realizados, incluindo: métricas de precisão e recall do módulo de gênero, acurácia da detecção de cor de roupa, tempo médio de processamento por câmera, e análise qualitativa do refinamento por similaridade facial.)*

### 5.1 Desempenho da Detecção de Pessoas (YOLOv5s)

*(A ser preenchido com dados experimentais)*

Parâmetros a reportar:
- Taxa de detecção por frame
- Velocidade de processamento (frames/segundo)
- Taxa de falsos negativos em condições variadas de iluminação e oclusão

### 5.2 Acurácia do Classificador de Gênero

*(A ser preenchido com dados experimentais)*

Parâmetros a reportar:
- Precisão e recall por classe (Male/Female)
- Comportamento em imagens com face não detectada

### 5.3 Desempenho da Segmentação de Cor de Roupa

*(A ser preenchido com dados experimentais)*

Parâmetros a reportar:
- Taxa de acerto da cor mais frequente em comparação com anotação manual
- Cobertura das 5 classes de cor implementadas

### 5.4 Eficácia do Refinamento por MFA-ViT

*(A ser preenchido com dados experimentais)*

Parâmetros a reportar:
- Posição média da imagem correta na fila reordenada
- Redução percentual no número de imagens revisadas até encontrar correspondência

---

## 6. Conclusão

Este trabalho apresentou o desenvolvimento de um sistema de reidentificação de pessoas em múltiplas câmeras de vigilância baseado em soft biometrics. O sistema integra módulos de detecção de pessoas (YOLOv5s), classificação de gênero (OpenCV DNN), segmentação de roupas e análise de cor (Extended U-Net) e reidentificação facial incremental (MFA-ViT), orquestrados por uma interface gráfica Tkinter com dois perfis de acesso.

As principais contribuições do trabalho são:

1. **Prototipo funcional** de sistema de vigilância inteligente capaz de realizar reidentificação por descrição semântica de atributos, sem depender de reconhecimento facial como mecanismo primário.

2. **Abordagem privacy-by-design**, alinhada com a LGPD, que utiliza soft biometrics como critério de busca principal e mantém validação humana obrigatória em todo o fluxo.

3. **Refinamento incremental** por similaridade facial (MFA-ViT), que melhora progressivamente a ordenação da fila de candidatos à medida que o operador confirma imagens, reduzindo o esforço humano de revisão.

4. **Arquitetura modular e extensível**, que permite a adição de novos atributos soft biométricos (estatura, cor de cabelo, etc.) sem alteração da estrutura principal do sistema.

### 6.1 Limitações

- O sistema funciona em modo **offline** (vídeos pré-gravados), não em tempo real.
- O número de cores de roupa reconhecidas é limitado a 5 classes discretas (preto, branco, vermelho, verde, azul).
- A classificação de gênero depende da detecção de face, tornando-a indisponível para imagens de costas ou com oclusão facial.
- O processamento sem GPU é significativamente mais lento, especialmente nos módulos YOLOv5 e MFA-ViT.

### 6.2 Trabalhos Futuros

- Ampliar o vocabulário de cores de roupas, adicionando tons como cinza, amarelo, laranja e rosa.
- Implementar estimativa de estatura e cor de pele como atributos adicionais de busca.
- Adicionar suporte ao grafo de caminhos possíveis entre câmeras (módulo em desenvolvimento) para filtragem por viabilidade temporal de deslocamento.
- Avaliar o sistema em bases de dados públicas anotadas (e.g., RAP, AVSS 2018 Challenge II) para validação quantitativa rigorosa.
- Migrar para processamento em tempo real utilizando filas de mensagens e workers paralelos.

---

## Referências

BRASIL. **Lei nº 13.709, de 14 de agosto de 2018.** Lei Geral de Proteção de Dados Pessoais (LGPD). Diário Oficial da União, Brasília, DF, 15 ago. 2018.

DANTCHEVA, A.; ELIA, P.; ROSS, A. What else does your biometric data reveal? A survey on soft biometrics. **IEEE Transactions on Information Forensics and Security**, v. 11, n. 3, p. 441–467, 2016.

JOCHER, G. et al. **YOLOv5 by Ultralytics** (v7.0). Zenodo, 2020. Disponível em: https://github.com/ultralytics/yolov5. Acesso em: 2025.

LEVI, G.; HASSNER, T. Age and gender classification using convolutional neural networks. In: **IEEE Conference on Computer Vision and Pattern Recognition Workshops (CVPRW)**, 2015.

NAIR, A. et al. ClothingParsing using Extended U-Net. In: **Proceedings of the 16th International Joint Conference on Computer Vision, Imaging and Computer Graphics Theory and Applications (SCITEPRESS)**, 2021. Disponível em: https://www.scitepress.org/Papers/2021/101777/101777.pdf.

REDMON, J. et al. You Only Look Once: Unified, Real-Time Object Detection. In: **IEEE Conference on Computer Vision and Pattern Recognition (CVPR)**, 2016.

TIONG, L. C. O. et al. Flexible Biometrics Recognition: Bridging the Multimodality Gap through Attention Alignment. In: **IEEE/CVF Conference on Computer Vision and Pattern Recognition (CVPR)**, 2024. Disponível em: https://openaccess.thecvf.com/content/CVPR2024/papers/Tiong_Flexible_Biometrics_Recognition_Bridging_the_Multimodality_Gap_through_Attention_Alignment_CVPR_2024_paper.pdf.

XIN, X. et al. U²-Net: Going deeper with nested U-structure for salient object detection. **Pattern Recognition**, v. 106, 2020.

---

*Documento gerado em: Abril de 2026*  
*Status: Rascunho Inicial — Seção 5 (Resultados) pendente de dados experimentais*
