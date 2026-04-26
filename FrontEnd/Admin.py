import tkinter as tk
from tkinter import ttk
from FrontEnd.Login import TelaLogin   
from FrontEnd.Opcoes_login import TelaOpcoesLogin

class TelaAdmin(tk.Frame):
    """Tela administrativa com opções de cadastro e configuração."""

    def __init__(self, master):
        super().__init__(master)

        # ===== Frame central =====
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # ===== Título =====
        tk.Label(
            container,
            text="Painel do Admin",
            font=("Arial", 18, "bold") 
        ).pack(pady=20)

        # ===== Botões  =====
        ttk.Button(
            container, text="Opções De Login", width=30,
            command=self.abrir_cadastro_login
        ).pack(pady=10)

        ttk.Button(
            container, text="Opções De Câmera", width=30,
            command=self.abrir_cadastro_camera
        ).pack(pady=10)

        
        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=20)

        # ===== Botão de retorno =====
        ttk.Button(
            container, text="Voltar ao Login",
            command=lambda: master.mostrar_tela(TelaLogin)
        ).pack(pady=10)

    def abrir_cadastro_login(self):
        from FrontEnd.Opcoes_login import TelaOpcoesLogin
        self.master.mostrar_tela(TelaOpcoesLogin)  

    

    def abrir_cadastro_camera(self):
        from FrontEnd.Config_Camera  import  TelaConfigCamera
      
        self.master.mostrar_tela(TelaConfigCamera)  