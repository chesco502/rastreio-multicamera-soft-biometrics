import tkinter as tk
from tkinter import ttk, messagebox
import os
from BackEnd.Cameras_estoque_video.Cam_Maneger import Cam_Maneger



class TelaCaminho_Min(tk.Frame):
    """Tela que permite selecionar duas câmeras e definir o tempo mínimo entre elas."""

    def __init__(self, master):
        super().__init__(master)

        # 🔹 Define o tamanho da janela principal
        master.geometry("1000x700")

        tk.Label(self, text="Definir Tempo Mínimo Entre Câmeras", font=("Arial", 18, "bold")).pack(pady=15)

        # ====== Frame principal ======
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill="both", expand=True)

        # ====== Inicializa o gerenciador de câmeras ======
        self.cam_manager = Cam_Maneger()
        try:
            self.cam_manager.carregar_cam_maneger()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar gerenciador: {e}")

        # ====== Frames laterais ======
        frame_esq = tk.LabelFrame(main_frame, text="Câmera 1", padx=10, pady=10)
        frame_esq.pack(side="left", expand=True, fill="both", padx=5)

        frame_dir = tk.LabelFrame(main_frame, text="Câmera 2", padx=10, pady=10)
        frame_dir.pack(side="right", expand=True, fill="both", padx=5)

        # ====== Colunas da tabela ======
        colunas = ("Nome", "Latitude", "Longitude")
        self.tree1 = ttk.Treeview(frame_esq, columns=colunas, show="headings", height=8)
        self.tree2 = ttk.Treeview(frame_dir, columns=colunas, show="headings", height=8)

        for tree in (self.tree1, self.tree2):
            for col in colunas:
                tree.heading(col, text=col)
                tree.column(col, anchor="center", width=120)
            tree.pack(expand=True, fill="both")

        # ====== Campo de tempo ======
        frame_tempo = tk.LabelFrame(self, text="Tempo mínimo entre as câmeras", padx=10, pady=10)
        frame_tempo.pack(pady=15)

        # Campos lado a lado (horas, minutos, segundos)
        tk.Label(frame_tempo, text="Horas:").grid(row=0, column=0, padx=5, pady=5)
        self.entry_horas = ttk.Entry(frame_tempo, width=6)
        self.entry_horas.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_tempo, text="Minutos:").grid(row=0, column=2, padx=5, pady=5)
        self.entry_minutos = ttk.Entry(frame_tempo, width=6)
        self.entry_minutos.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(frame_tempo, text="Segundos:").grid(row=0, column=4, padx=5, pady=5)
        self.entry_segundos = ttk.Entry(frame_tempo, width=6)
        self.entry_segundos.grid(row=0, column=5, padx=5, pady=5)

        # ====== Frame de botões ======
        botoes_frame = tk.Frame(self)
        botoes_frame.pack(pady=10)

        ttk.Button(
            botoes_frame,
            text="Adicionar Tempo Mínimo Entre Câmeras",
            command=self.acao_adicionar_tempo,
            width=40
        ).pack(side="left", padx=5)
        
        ttk.Button(
            botoes_frame,
            text="Mostrar Conexões",
            command=self.mostrar_conexoes,
            width=20
        ).pack(side="left", padx=5)
        
        ttk.Button(
            botoes_frame,
            text="Atualizar",
            command=self.atualizar_listas,
            width=15
        ).pack(side="left", padx=5)

        ttk.Button(
            botoes_frame,
            text="Voltar",
            command=self.voltar,
            width=15
        ).pack(side="left", padx=5)

        # ====== Popula as tabelas ======
        self.atualizar_listas()

    # ==========================================================
    # Recarrega as listas de câmeras
    # ==========================================================
    def atualizar_listas(self):
        """Recarrega as listas de câmeras."""
        for tree in (self.tree1, self.tree2):
            for i in tree.get_children():
                tree.delete(i)

        try:
            self.cam_manager.carregar_cam_maneger()
            lista_cameras = self.cam_manager.listar_cameras()

            if not lista_cameras:
                messagebox.showinfo("Info", "Nenhuma câmera cadastrada ainda.")
                return

            for cam in lista_cameras:
                nome = os.path.basename(cam["caminho"])
                valores = (nome, cam["latitude"], cam["longitude"])
                self.tree1.insert("", "end", values=valores)
                self.tree2.insert("", "end", values=valores)

            print("🔄 Listas atualizadas com sucesso.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar listas: {e}")

    # ==========================================================
    # Botão principal
    # ==========================================================
    def acao_adicionar_tempo(self):
        """Obtém as câmeras selecionadas e o tempo digitado."""
        selecao1 = self.tree1.selection()
        selecao2 = self.tree2.selection()

        # 🔸 Valida seleção
        if not selecao1 or not selecao2:
            messagebox.showwarning("Seleção inválida", "Selecione uma câmera em cada lista.")
            return

        valores1 = self.tree1.item(selecao1[0], "values")
        valores2 = self.tree2.item(selecao2[0], "values")
        cam1 = valores1[0]
        cam2 = valores2[0]

        if cam1 == cam2:
            messagebox.showwarning("Seleção inválida", "As câmeras selecionadas devem ser diferentes.")
            return

        # 🔸 Lê os campos de tempo
        horas = self.entry_horas.get().strip() or "0"
        minutos = self.entry_minutos.get().strip() or "0"
        segundos = self.entry_segundos.get().strip() or "0"

        # 🔸 Validação
        if not horas.isdigit() or not minutos.isdigit() or not segundos.isdigit():
            messagebox.showwarning("Tempo inválido", "Insira apenas números inteiros.")
            return

        h, m, s = int(horas), int(minutos), int(segundos)
        tempo_total = h * 3600 + m * 60 + s

        if tempo_total <= 0:
            messagebox.showwarning("Tempo inválido", "O tempo mínimo deve ser maior que zero.")
            return

        
        from BackEnd.Caminho_Possivel.Caminho_Possivel_Manager import Caminho_Possivel
        caminho_possivel_manager = Caminho_Possivel()
        caminho_possivel_manager.carregar_grafo()
        caminho_possivel_manager.conectar_cameras(cam1,cam2,tempo_total)
       
    def mostrar_conexoes(self):
        """Abre a tela de visualização do grafo de conexões."""
        from FrontEnd.Mostra_Caminhos import TelaMostrarCaminhos
        self.master.mostrar_tela(TelaMostrarCaminhos) 

    # ==========================================================
    def voltar(self):
        from FrontEnd.Config_Camera import TelaConfigCamera
        self.master.mostrar_tela(TelaConfigCamera)
