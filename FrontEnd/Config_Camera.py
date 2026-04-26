import tkinter as tk
from tkinter import ttk

class TelaConfigCamera(tk.Frame):
    """Tela de configuração geral das câmeras."""

    def __init__(self, master):
        super().__init__(master)

        # ====== Título ======
        tk.Label(
            self,
            text="Configuração de Câmeras",
            font=("Arial", 18, "bold")
        ).pack(pady=25)

        # ====== Container central ======
        container = tk.Frame(self)
        container.pack(expand=True)

        # ====== Botões principais ======
        ttk.Button(
            container, text="Adicionar Nova Câmera", width=30,
            command=self.cadastro_camera  # função ainda será implementada
        ).pack(pady=10)

        ttk.Button(
            container, text="Deletar Câmera", width=30,
            command=self.tela_deletar  # função ainda será implementada
        ).pack(pady=10)

        ttk.Button(
            container, text="Configurar Tempo Mínimo", width=30,
            command=self.tela_configurar_caminhos
        ).pack(pady=10)

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=20)

        # ====== Botão de retorno ======
        ttk.Button(
            container, text="Voltar",
            command=self.voltar
        ).pack(pady=10)

    def voltar(self):
        from FrontEnd.Admin import TelaAdmin
        self.master.mostrar_tela(TelaAdmin)

    # ====== Funções placeholder (sem lógica por enquanto) ======
    def cadastro_camera(self):
        from FrontEnd.Cadastro_Camera  import  TelaCadastroCamera

        self.master.mostrar_tela(TelaCadastroCamera)  

    def tela_deletar(self):
        from FrontEnd.Deletar_Camera  import  TelaDeletarCamera
        self.master.mostrar_tela(TelaDeletarCamera)  

    def tela_configurar_caminhos(self):
        from FrontEnd.Config_Caminho_Min import TelaCaminho_Min
        self.master.mostrar_tela(TelaCaminho_Min)  
       
