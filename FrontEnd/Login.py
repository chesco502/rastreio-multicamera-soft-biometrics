import tkinter as tk
from tkinter import ttk, messagebox


from BackEnd.Login.LoginManager import LoginManager

class TelaLogin(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(expand=True)  # 🔹 Faz o frame ocupar o centro da janela
        self.config(padx=40, pady=40)  # adiciona margem interna

        # Frame interno para centralizar vertical e horizontalmente
        centro = tk.Frame(self)
        centro.pack(expand=True)  # 🔹 Centraliza tudo dentro da tela

        # Título
        tk.Label(centro, text="Tela de Login", font=("Arial", 18, "bold")).pack(pady=20)

        # Campo de usuário
        tk.Label(centro, text="Usuário:").pack()
        self.usuario_entry = ttk.Entry(centro, width=30)
        self.usuario_entry.pack(pady=10)

        # Campo de senha
        tk.Label(centro, text="Senha:").pack()
        self.senha_entry = ttk.Entry(centro, width=30)
        self.senha_entry.pack(pady=10)

        # Botão de login
        ttk.Button(centro, text="Entrar", command=self.fazer_login).pack(pady=20)



    def fazer_login(self):

        usuario = self.usuario_entry.get()
        senha = self.senha_entry.get()
        login_level = self.verificar_login(usuario, senha)
        if login_level == 'admin' :
            messagebox.showinfo("Login", "Login realizado com sucesso!")
            from FrontEnd.Admin import  TelaAdmin
            self.master.mostrar_tela(TelaAdmin)  # muda para tela admin
        elif  login_level == 'operador' :
            messagebox.showinfo("Login", "Login realizado com sucesso!")
            from FrontEnd.Operador import  TelaOperador  
            self.master.mostrar_tela(TelaOperador)  # muda para tela operador
        else:
            messagebox.showerror("Erro", "Usuário ou senha incorretos!")


    def verificar_login(self, usuario, senha):
        lm = LoginManager()
        return lm.authenticate_user( usuario, senha) 
