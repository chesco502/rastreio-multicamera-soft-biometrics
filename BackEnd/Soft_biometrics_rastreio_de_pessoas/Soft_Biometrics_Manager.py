import os


def combinar_listas(lista1, lista2):
    """
    Retorna uma lista com:
    1. As strings que aparecem em ambas as listas.
    2. Seguidas das demais strings únicas.
    """
    # Interseção (presentes nas duas)
    intersecao = [x for x in lista1 if x in lista2]
    
    # Restantes (que não estão na interseção)
    restantes = [x for x in lista1 + lista2 if x not in intersecao] #caso queira adicionar qualquer positivo
    
    # Junta as duas partes
    return intersecao + restantes  #// caso queira adicionar qualquer positivo






def _extrair_timestamp(caminho):
    import re
    from datetime import datetime, timedelta
    nome = os.path.basename(caminho)
    m = re.search(r'(\d{8}_\d{6})', nome)
    if m:
        try:
            return datetime.strptime(m.group(1), "%Y%m%d_%H%M%S")
        except ValueError:
            pass
    m = re.search(r'\bt(\d{2})_(\d{2})_(\d{2})', nome)
    if m:
        try:
            offset = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            return datetime.fromtimestamp(os.path.getmtime(caminho)) - timedelta(seconds=offset)
        except Exception:
            pass
    try:
        return datetime.fromtimestamp(os.path.getmtime(caminho))
    except Exception:
        return None


def search_description(descricao, cameras, usar_cor=True, usar_modelo_cor=True,
                       usar_genero=True, intervalo_tempo=None):
    genero_alvo, cores_alvo = descricao
    if isinstance(cores_alvo, str):
        cores_alvo = [cores_alvo]

    # coleta todos os caminhos e aplica filtro de horário
    all_images = []
    for caminho_camera in cameras:
        imagens_diretorio = os.path.join(caminho_camera, "output")
        if not os.path.isdir(imagens_diretorio):
            continue
        for foto in os.listdir(imagens_diretorio):
            caminho = os.path.join(imagens_diretorio, foto)
            if intervalo_tempo is not None:
                ts = _extrair_timestamp(caminho)
                inicio, fim = intervalo_tempo
                if ts is None or not (inicio <= ts <= fim):
                    continue
            all_images.append(caminho)

    positivo_genero = []
    positivo_cor_de_roupa = []

    if usar_genero:
        from BackEnd.Soft_biometrics_rastreio_de_pessoas.Identificador_De_Genero_Open_CV.Identificador_Genero import predict_gender_batch
        generos = predict_gender_batch(all_images)
        for caminho in all_images:
            genero = generos.get(caminho)
            if genero is not None and genero[0] == genero_alvo:
                positivo_genero.append([caminho])

    if usar_cor:
        from BackEnd.Soft_biometrics_rastreio_de_pessoas.cloth_segmentation.app import media_cor_de_roupa_batch
        cores = media_cor_de_roupa_batch(all_images, usar_modelo=usar_modelo_cor)
        for caminho in all_images:
            cor = cores.get(caminho)
            if cor and cor in cores_alvo:
                positivo_cor_de_roupa.append([caminho])

    return combinar_listas(positivo_cor_de_roupa, positivo_genero)