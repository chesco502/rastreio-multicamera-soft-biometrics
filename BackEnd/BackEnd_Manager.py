
import os
def adicionar_filmagens(lista_arquivos, pasta_destino):
    
    import shutil
    os.makedirs(pasta_destino, exist_ok=True)
    copiados = 0
    ignorados = 0
    for i, origem in enumerate(lista_arquivos, start=1):
        nome = os.path.basename(origem)
        destino = os.path.join(pasta_destino, nome)
        if os.path.exists(destino):
            ignorados += 1
        else:
            shutil.copy2(origem, destino)
            copiados += 1
        
    return copiados, ignorados


def Atualizar_filmagens():
    from BackEnd.Cameras_estoque_video.Cam_Maneger import Cam_Maneger
    cam_maneger = Cam_Maneger()
    cam_maneger.carregar_cam_maneger()
    cam_maneger.refresh_cameras()
   





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
def limita_camera():
 pass


def limita_tempo(diretorio: str, intervalo: tuple[float, float]):
    import os
    import re
    
    # Expressão regular para capturar números no início do nome (ex: "41,00_" ou "23.5_")
    padrao = re.compile(r"^(\d+(?:[.,]\d+)?)_")

    arquivos_filtrados = []

    for nome_arquivo in os.listdir(diretorio):
        correspondencia = padrao.match(nome_arquivo)
        #if correspondencia:
            #valor = float(correspondencia.group(1).replace(",", "."))
            
           
           
           #if intervalo[0] <= valor <= intervalo[1]:
        arquivos_filtrados.append(nome_arquivo)
            # Caso o modo seja 'maior' ou 'menor', mantém compatibilidade
            

    return arquivos_filtrados



    
def search(descricao, cameras=None, usar_cor=True, usar_modelo_cor=True,
           usar_genero=True, intervalo_tempo=None):
    from BackEnd.Cameras_estoque_video.Cam_Maneger import Cam_Maneger
    try:
        from Soft_biometrics_rastreio_de_pessoas.Soft_Biometrics_Manager import search_description
    except:
        from BackEnd.Soft_biometrics_rastreio_de_pessoas.Soft_Biometrics_Manager import search_description
    if cameras is None:
        cam_maneger = Cam_Maneger()
        cam_maneger.carregar_cam_maneger()
        cameras = cam_maneger.caminhos_cameras()
    return search_description(descricao, cameras, usar_cor=usar_cor,
                              usar_modelo_cor=usar_modelo_cor, usar_genero=usar_genero,
                              intervalo_tempo=intervalo_tempo)


            
def horario_para_float(data_hora_str: str) -> float:
    """
    Converte uma string no formato 'DD/MM/AAAA HH:MM' para float representando o horário.
    
    Exemplo:
        '02/11/2025 01:20' -> 1.20
        '02/11/2025 13:45' -> 13.45
    """
    try:
        # Separa data e hora
        partes = data_hora_str.strip().split(" ")
        if len(partes) != 2:
            raise ValueError("Formato inválido. Use 'DD/MM/AAAA HH:MM'")

        hora_str = partes[1]
        hora, minuto = map(int, hora_str.split(":"))

        # Converte para float no formato H.MM (sem converter minutos para base 100)
        return float(f"{hora}.{minuto:02d}")

    except Exception as e:
        raise ValueError(f"Erro ao converter horário: {e}")
