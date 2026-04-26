import tkinter as tk
from tkinter import ttk
 # supondo que a tela de login já exista


class TelaOpcoesLogin(tk.Frame):
    """Tela para gerenciamento de logins (listar, criar e deletar)."""

    def __init__(self, master):
        super().__init__(master)

        # ===== Frame central =====
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # ===== Título =====
        tk.Label(
            container,
            text="Gerenciamento de Logins",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        # ===== Botões principais =====
        ttk.Button(
            container, text="Listar Logins", width=30,
            command=self.listar_logins
        ).pack(pady=10)

        ttk.Button(
            container, text="Criar Login", width=30,
            command=self.criar_login
        ).pack(pady=10)

        ttk.Button(
            container, text="Deletar Login", width=30,
            command=self.deletar_login
        ).pack(pady=10)

        # ===== Separador =====
        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=20)

        # ===== Botão de retorno =====
        ttk.Button(
            container, text="Voltar", width=30,
            command=self.Voltar
        ).pack(pady=10)
    
    
    
    # ===== Métodos simulando ações =====
    def listar_logins(self):
        from BackEnd.Login.LoginManager import LoginManager
        from FrontEnd.Usuarios_display import TelaListarUsuarios
        lm = LoginManager()
        
        self.master.mostrar_tela(TelaListarUsuarios)  
        
    
    def Voltar(self):
        from FrontEnd.Admin import TelaAdmin
        self.master.mostrar_tela(TelaAdmin)  
        


    def criar_login(self):
        print("Abrindo tela de criação de login...")

    def deletar_login(self):
        print("Abrindo tela de deleção de login...")
