import os
import re
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk


def _tempo_display(caminho: str) -> str:
    nome = os.path.basename(caminho)
    m = re.search(r'\bt(\d{2})_(\d{2})_(\d{2})', nome)
    if m:
        return f"{m.group(1)}:{m.group(2)}:{m.group(3)}"
    try:
        return datetime.fromtimestamp(os.path.getmtime(caminho)).strftime("%H:%M:%S")
    except Exception:
        return ""


class TelaRevisarImagens(tk.Frame):
    """
    Exibe imagens para validação (Sim/Não).
    Ao confirmar uma imagem, a fila restante é reordenada pelo índice de
    similaridade retornado por Detector_face_caminho — imagens mais prováveis
    sobem na lista. Imagens já avaliadas nunca voltam a aparecer.
    """

    def __init__(self, master, lista_caminhos_imagens):
        super().__init__(master)
        self.master = master

        # fila mutável de itens ainda não avaliados (cada item é [path_str])
        self.fila = list(lista_caminhos_imagens)
        # caminhos já avaliados — garante que não reapareçam após reordenação
        self.revisados = set()
        # resultado final: lista de (caminho_str, bool)
        self.resultados = []

        # ===== UI =====
        tk.Label(self, text="Validação de Imagens", font=("Arial", 18, "bold")).pack(pady=15)

        self.image_label = tk.Label(self, bg="gray", width=600, height=400)
        self.image_label.pack(pady=10)

        self.label_camera = tk.Label(self, text="", font=("Arial", 10, "bold"), fg="#333")
        self.label_camera.pack()

        self.label_tempo = tk.Label(self, text="", font=("Arial", 10), fg="#555")
        self.label_tempo.pack()

        botoes_frame = tk.Frame(self)
        botoes_frame.pack(pady=10)

        self.btn_sim = ttk.Button(botoes_frame, text="✅ Sim", command=lambda: self.registrar_resposta(True))
        self.btn_nao = ttk.Button(botoes_frame, text="❌ Não", command=lambda: self.registrar_resposta(False))
        ttk.Button(botoes_frame, text="Voltar", command=self.voltar).pack(side="right", padx=10)
        ttk.Button(botoes_frame, text="Encerrar Revisão", command=self._encerrar_antecipado).pack(side="right", padx=10)
        self.btn_sim.pack(side="left", padx=10)
        self.btn_nao.pack(side="left", padx=10)

        filtro_frame = tk.Frame(self)
        filtro_frame.pack(pady=(0, 4))
        self.btn_aprovar_similares = ttk.Button(
            filtro_frame, text="Aprovar Parecidas",
            command=self._aprovar_similares
        )
        self.btn_aprovar_similares.pack(side="left", padx=6)
        self.btn_remover_similares = ttk.Button(
            filtro_frame, text="Remover Similares",
            command=self._remover_similares
        )
        self.btn_remover_similares.pack(side="left", padx=6)

        self.label_progresso = tk.Label(self, text="")
        self.label_progresso.pack(pady=5)

        self.label_status = tk.Label(self, text="", font=("Arial", 9), fg="gray")
        self.label_status.pack(pady=2)

        if self.fila:
            self._mostrar_topo()
        else:
            messagebox.showinfo("Info", "Nenhuma imagem encontrada.")

    # ------------------------------------------------------------------
    # Exibição
    # ------------------------------------------------------------------

    def _caminho(self, item):
        """Extrai o caminho string de um item da fila (pode ser str ou [str])."""
        return item[0] if isinstance(item, list) else item

    def _mostrar_topo(self):
        """Mostra a imagem no topo da fila."""
        if not self.fila:
            return
        caminho = self._caminho(self.fila[0])
        try:
            imagem = Image.open(caminho)
            imagem.thumbnail((600, 400))
            self.tk_image = ImageTk.PhotoImage(imagem)
            self.image_label.config(image=self.tk_image, text="")
        except Exception as e:
            self.image_label.config(text=f"Erro ao abrir imagem:\n{caminho}", image="", bg="gray")
            print(f"Erro ao carregar imagem {caminho}: {e}")

        nome_camera = os.path.basename(os.path.dirname(os.path.dirname(caminho)))
        self.label_camera.config(text=f"Câmera: {nome_camera}")
        self.label_tempo.config(text=_tempo_display(caminho))

        self.label_progresso.config(
            text=f"Na fila: {len(self.fila)}  |  Revisadas: {len(self.revisados)}"
        )
        self.label_status.config(text="")

    # ------------------------------------------------------------------
    # Avaliação
    # ------------------------------------------------------------------

    def registrar_resposta(self, resposta):
        """Registra a resposta e avança para a próxima imagem da fila."""
        if not self.fila:
            return

        item_atual = self.fila.pop(0)
        caminho_atual = self._caminho(item_atual)

        self.resultados.append((caminho_atual, resposta))
        self.revisados.add(caminho_atual)

        if resposta and self.fila:
            # Reordena o restante da fila por similaridade com a imagem confirmada
            self.label_status.config(text="Reordenando fila por similaridade...")
            self.update_idletasks()
            self._reordenar_fila(caminho_atual)

        if self.fila:
            self._mostrar_topo()
        else:
            self.finalizar()

    def _reordenar_fila(self, imagem_referencia):
        """
        Chama Detector_face_caminho para calcular a similaridade de cada
        imagem restante com a referência confirmada e reordena a fila do
        mais similar para o menos similar. Itens já revisados são descartados.
        """
        try:
            from BackEnd.Soft_biometrics_rastreio_de_pessoas.Identificador_De_Face_FBR.Detector_de_face import Detector_face_caminho
            resultados = Detector_face_caminho(imagem_referencia, self.fila)
            # resultados: [(path_str, score_float, is_same_bool), ...] ordenado por score desc
            nova_fila = [
                [path_str]
                for path_str, score, *_ in resultados
                if path_str not in self.revisados and score >= 0.20
            ]
            self.fila = nova_fila
        except Exception as e:
            print(f"Aviso: não foi possível reordenar a fila — {e}")
            # Mantém a ordem atual em caso de erro, apenas remove revisados
            self.fila = [
                item for item in self.fila
                if self._caminho(item) not in self.revisados
            ]

    def _remover_similares(self):
        """
        Compara a imagem atual com o restante da fila usando Detector_face_caminho.
        Remove da fila todas as imagens com similaridade > 60% em relação à atual.
        """
        if len(self.fila) < 2:
            self.label_status.config(text="Nenhuma imagem na fila para comparar.")
            return

        caminho_ref = self._caminho(self.fila[0])
        candidatos = self.fila[1:]

        self.btn_remover_similares.config(state="disabled")
        self.label_status.config(text="Calculando similaridade...")
        self.update_idletasks()

        try:
            from BackEnd.Soft_biometrics_rastreio_de_pessoas.Identificador_De_Face_FBR.Detector_de_face import Detector_face_caminho
            resultados = Detector_face_caminho(caminho_ref, candidatos)

            similares = {path for path, score, _ in resultados if score > 0.73}

            # recusa a imagem atual
            self.fila.pop(0)
            self.resultados.append((caminho_ref, False))
            self.revisados.add(caminho_ref)

            antes = len(self.fila)
            self.fila = [
                item for item in candidatos
                if self._caminho(item) not in similares
            ]
            removidos = antes - len(self.fila)
            self.label_status.config(
                text=f"Imagem recusada. {removidos} similar(es) removida(s) da fila."
            )
        except Exception as e:
            self.label_status.config(text=f"Erro ao calcular similaridade: {e}")
        finally:
            self.btn_remover_similares.config(state="normal")
            if self.fila:
                self._mostrar_topo()
            else:
                self.finalizar()

    def _aprovar_similares(self):
        """
        Compara a imagem atual com o restante da fila.
        Qualquer imagem com similaridade >= 80% é automaticamente aprovada
        e removida da fila sem precisar de revisão manual.
        """
        if len(self.fila) < 2:
            self.label_status.config(text="Nenhuma imagem na fila para comparar.")
            return

        caminho_ref = self._caminho(self.fila[0])
        candidatos = self.fila[1:]

        self.btn_aprovar_similares.config(state="disabled")
        self.btn_remover_similares.config(state="disabled")
        self.label_status.config(text="Calculando similaridade...")
        self.update_idletasks()

        try:
            from BackEnd.Soft_biometrics_rastreio_de_pessoas.Identificador_De_Face_FBR.Detector_de_face import Detector_face_caminho
            resultados = Detector_face_caminho(caminho_ref, candidatos)

            aprovados = {path for path, score, _ in resultados if score >= 0.75}

            # aprova a imagem atual
            self.fila.pop(0)
            self.resultados.append((caminho_ref, True))
            self.revisados.add(caminho_ref)

            nova_fila = []
            aprovados_count = 1
            for item in candidatos:
                path = self._caminho(item)
                if path in aprovados:
                    self.resultados.append((path, True))
                    self.revisados.add(path)
                    aprovados_count += 1
                else:
                    nova_fila.append(item)

            self.fila = nova_fila
            self.label_status.config(
                text=f"{aprovados_count} imagem(ns) aprovada(s) automaticamente."
            )
        except Exception as e:
            self.label_status.config(text=f"Erro ao calcular similaridade: {e}")
        finally:
            self.btn_aprovar_similares.config(state="normal")
            self.btn_remover_similares.config(state="normal")
            if self.fila:
                self._mostrar_topo()
            else:
                self.finalizar()

    # ------------------------------------------------------------------
    # Conclusão e navegação
    # ------------------------------------------------------------------

    def _encerrar_antecipado(self):
        if not self.resultados:
            messagebox.showwarning("Aviso", "Nenhuma imagem foi avaliada ainda.")
            return
        self.finalizar()

    def voltar(self):
        from FrontEnd.Busca import TelaBuscaPessoas
        self.master.mostrar_tela(TelaBuscaPessoas)

    def finalizar(self):
        from FrontEnd.Linha_do_Tempo import TelaLinhaDeTempo
        if hasattr(self.master, "mostrar_tela"):
            self.master.mostrar_tela(TelaLinhaDeTempo, self.resultados)
        else:
            self.voltar()
