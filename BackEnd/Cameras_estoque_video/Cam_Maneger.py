import os
import pickle



#Util
def listar_arquivos(diretorio):
    """Retorna uma lista com o caminho completo de todos os arquivos do diretório informado."""
    if not os.path.exists(diretorio):
        raise FileNotFoundError(f"O diretório '{diretorio}' não foi encontrado.")

    arquivos = []
    for nome in os.listdir(diretorio):
        caminho = os.path.join(diretorio, nome)
        if os.path.isfile(caminho):
            arquivos.append(os.path.normpath(caminho))

    return arquivos



class Cam_Maneger:
    def __init__(self):
        self.diretorio = None
        self.cameras = []
    
    def set_up(self, diretorio):
        """Define o diretório principal onde as câmeras serão salvas."""
        self.diretorio = diretorio
    
    
    def caminhos_cameras(self):
        """
        Retorna uma lista com os caminhos completos de todas as câmeras.
        """
        if not self.cameras:
            return []

        return [cam.caminho_camera for cam in self.cameras]
    
    def carregar_cam_maneger(self):
        """Carrega o gerenciador de câmeras salvo em um arquivo pickle."""
        diretorio_atual = os.path.normpath(os.path.dirname(os.path.abspath(__file__)))
        arquivo_config_manager = os.path.join(diretorio_atual, "config_maneger.pkl")

        if not os.path.exists(arquivo_config_manager):
            self.diretorio = diretorio_atual
            with open(arquivo_config_manager, 'wb') as arquivo:
                pickle.dump(self, arquivo)
        else:
            with open(arquivo_config_manager, 'rb') as arquivo:
                maneger = pickle.load(arquivo)
                self.__dict__.update(maneger.__dict__)

            # Se o projeto foi movido, recalcula todos os caminhos absolutos
            if os.path.normpath(self.diretorio) != diretorio_atual:
                for cam in self.cameras:
                    nome_pasta = os.path.basename(cam.caminho_camera)
                    cam.caminho_camera = os.path.join(diretorio_atual, nome_pasta)
                self.diretorio = diretorio_atual
                self.salvar()
    
    def salvar(self):
        arquivo_config_manager = os.path.join(self.diretorio, r"config_maneger.pkl")
        with open(arquivo_config_manager, 'wb') as arquivo:
            pickle.dump(self, arquivo)

    def caminho_camera(self, nome_camera):
        """
        Retorna o caminho completo de uma câmera pelo nome da pasta.
        Lança FileNotFoundError se a câmera não existir.
        """
        lista = self.listar_cameras()

        for cam in lista:
            nome_pasta = os.path.basename(cam["caminho"])
            if nome_pasta == nome_camera:
                return  os.path.join(self.diretorio, cam["caminho"])


    def adicionar_nova_camera(self, latitude, longitude, caminho_camera):
        """
        Cria e adiciona uma nova câmera ao gerenciador.
        - latitude: coordenada latitude (float ou str)
        - longitude: coordenada longitude (float ou str)
        - caminho_camera: caminho onde os dados da câmera serão salvos
        """
        cam = Camera()
        caminho_camera = os.path.join(self.diretorio,caminho_camera)
        cam.set_up(latitude, longitude, caminho_camera)
        self.cameras.append(cam)
        self.salvar()

    def listar_cameras(self):
        """
        Retorna uma lista com informações de todas as câmeras cadastradas.
        """
        if not self.cameras:
        
            return []
        return [cam.get_info() for cam in self.cameras]

    def deletar_camera(self, nome_camera):
        
        
        lista = self.listar_cameras()
        camera_encontrada = None

        # Localiza a câmera pelo nome da pasta
        for cam in lista:
            nome_pasta = os.path.basename(cam["caminho"])
            if nome_pasta == nome_camera:
                camera_encontrada = cam
                break

        if not camera_encontrada:
            raise FileNotFoundError(f"❌ Câmera '{nome_camera}' não encontrada.")

        caminho = camera_encontrada["caminho"]

        # Remove todos os arquivos e subpastas
        if os.path.exists(caminho):
            for root, dirs, files in os.walk(caminho, topdown=False):
                for arquivo in files:
                    try:
                        os.remove(os.path.join(root, arquivo))
                    except Exception as e:
                        print(f"⚠️ Erro ao remover arquivo {arquivo}: {e}")

                for pasta in dirs:
                    try:
                        os.rmdir(os.path.join(root, pasta))
                    except Exception as e:
                        print(f"⚠️ Erro ao remover pasta {pasta}: {e}")

            # Remove o diretório principal da câmera
            try:
                os.rmdir(caminho)
            except Exception as e:
               pass

        # Remove também do gerenciador de objetos
        self.cameras = [c for c in self.cameras if os.path.basename(c.caminho_camera) != nome_camera]
        self.salvar()
        from BackEnd.Caminho_Possivel.Caminho_Possivel_Manager import Caminho_Possivel
        caminho_possivel_manager = Caminho_Possivel()
        caminho_possivel_manager.carregar_grafo()
        caminho_possivel_manager.deletar_camera(nome_camera)
        return True
    

    def limpar_cameras(self):
        """Remove todos os arquivos de input e output de todas as câmeras,
        mantendo a estrutura de pastas intacta."""
        for cam in self.cameras:
            for subpasta in ("input", "output"):
                pasta = os.path.join(cam.caminho_camera, subpasta)
                if not os.path.isdir(pasta):
                    continue
                for nome in os.listdir(pasta):
                    caminho = os.path.join(pasta, nome)
                    try:
                        if os.path.isfile(caminho):
                            os.remove(caminho)
                    except Exception as e:
                        print(f"Erro ao remover {caminho}: {e}")

    def refresh_cameras(self):
        from BackEnd.Yolo_Dec_Pessoas.yolo_processor import processar_diretorio
        cam = self.listar_cameras()
        for camera in cam:
            pasta_input = os.path.join(camera["caminho"], "input")
            pasta_output = os.path.join(camera["caminho"], "output")
            if not os.path.exists(pasta_input):
                continue
            processar_diretorio(pasta_input, pasta_output)


class Camera:
    def __init__(self):
        self.latitude = None
        self.longitude = None
        self.caminho_camera = None

    def set_up(self, latitude, longitude, caminho_camera):
        """Inicializa e salva a câmera."""
        self.latitude = latitude
        self.longitude = longitude
        self.caminho_camera = caminho_camera
        self.salvar_camera()

    def salvar_camera(self):
        """Salva a configuração da câmera em um arquivo pickle."""
        
        os.makedirs(self.caminho_camera, exist_ok=True)
        os.makedirs(os.path.join(self.caminho_camera,"input"))
        os.makedirs(os.path.join(self.caminho_camera,"output"))
        arquivo_config = os.path.join(self.caminho_camera, "config.pkl")
        with open(arquivo_config, 'wb') as arquivo:
            pickle.dump(self, arquivo)
    
    def carregar_Camera(self, caminho_config_camera):
        """Carrega os dados da câmera de um arquivo pickle."""
        if not os.path.exists(caminho_config_camera):
            raise FileNotFoundError(f"❌ O arquivo '{caminho_config_camera}' não foi encontrado.")
        with open(caminho_config_camera, 'rb') as arquivo:
            camera = pickle.load(arquivo)
            self.__dict__.update(camera.__dict__)
        return self.caminho_camera
    def get_info(self):
        """
        Retorna as propriedades da câmera em formato de dicionário.
        """
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "caminho": self.caminho_camera
        }