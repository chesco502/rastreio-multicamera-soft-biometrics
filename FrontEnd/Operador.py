import tkinter as tk
from tkinter import ttk
from FrontEnd.Login import TelaLogin 



class TelaOperador(tk.Frame):
    """Tela do operador com opções principais."""

    def __init__(self, master):
        super().__init__(master)

        # ===== Frame central =====
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # ===== Cabeçalho =====
        tk.Label(
            container,
            text="Painel do Operador",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        # ===== Botões de opções =====
        ttk.Button(
            container, text="Listar Câmeras", width=30, command=self.listar_cameras
        ).pack(pady=10)
        
        ttk.Button(
            container, text="Adicionar Filmagem", width=30, command=self.adicionar_filmagem
        ).pack(pady=10)
        ttk.Button(
            container, text="Mostrar Mapa", width=30, command=self.mostrar_mapa
        ).pack(pady=10)

        ttk.Button(
            container, text="Realizar Busca", width=30, command=self.realizar_busca
        ).pack(pady=10)

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=20)

        # ===== Botão de retorno ===== #
        ttk.Button(
            container, text="Deslogar",
            command=lambda: master.mostrar_tela(TelaLogin)
        ).pack(pady=10)

    # ====== Funções  ====== #
    def listar_cameras(self):
        from FrontEnd.ListarCameras import TelaListarCameras
        self.master.mostrar_tela(TelaListarCameras)  
    def mostrar_mapa(self):
        from FrontEnd.ListarCameras import TelaListarCameras
        self.master.mostrar_tela(TelaListarCameras)  

    def adicionar_filmagem(self):
        from FrontEnd.Adicionar_Filmagem import TelaAdicionarFilmagem
        self.master.mostrar_tela(TelaAdicionarFilmagem)

    def realizar_busca(self):
        from FrontEnd.Busca import TelaBuscaPessoas
        self.master.mostrar_tela(TelaBuscaPessoas)
        