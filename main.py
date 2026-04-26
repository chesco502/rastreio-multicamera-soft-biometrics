import tkinter as tk
from FrontEnd.Admin import TelaAdmin
from FrontEnd.Login import TelaLogin
from FrontEnd.Operador import TelaOperador
from FrontEnd.Opcoes_login import TelaOpcoesLogin
from FrontEnd.Usuarios_display import TelaListarUsuarios
#from BackEnd.BackEnd_Manager import start


class FrontManager(tk.Tk):
    
    def __init__(self):
        super().__init__()

        # Configurações básicas da janela
        self.title("Sistema de Login")
        self.geometry("600x800")
        self.resizable(False, False)

        # 🔹 Garante que o frame principal se expanda e centralize
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.frames = {}

        # 🔹 Dicionário com todas as telas
        for F in (TelaLogin, TelaAdmin, TelaOperador,TelaOpcoesLogin,TelaListarUsuarios):
            frame = F(self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")  # ocupa todo o espaço

        # Exibe a primeira tela (login)
        self.mostrar_tela(TelaLogin)


    def mostrar_tela(self, tela_classe, *args, **kwargs):
        # Telas que recebem dados dinâmicos são sempre recriadas
        if args or kwargs:
            if tela_classe in self.frames:
                self.frames[tela_classe].destroy()
                del self.frames[tela_classe]

        if tela_classe not in self.frames:
            frame = tela_classe(self, *args, **kwargs)
            self.frames[tela_classe] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.frames[tela_classe].tkraise()

if __name__ == "__main__":
    
    #resultado=search_description(["Male","cinza"],[22,42],"camera1")
    
    
    
    
    #start()
    
    
    app = FrontManager()
    app.mainloop()
