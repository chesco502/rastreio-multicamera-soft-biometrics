import tkinter as tk
from tkinter import ttk
from FrontEnd.Opcoes_login import TelaOpcoesLogin


class TelaListarUsuarios(tk.Frame):
    """Tela que exibe todos os usuários e seus papéis (roles)."""

    def __init__(self, master):
        super().__init__(master)
        self.master = master
        
        from BackEnd.Login.LoginManager import LoginManager
        lm = LoginManager()
        self.usuarios = lm.listar_logins() # lista [{'username': u, 'role': r}]

        # ===== Frame principal =====
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # ===== Título =====
        tk.Label(
            container,
            text="Lista de Usuários",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        # ===== Frame de listagem =====
        frame_lista = tk.Frame(container)
        frame_lista.pack(pady=10)

        # Se a lista estiver vazia
        if not self.usuarios:
            tk.Label(frame_lista, text="Nenhum usuário encontrado.").pack()
        else:
            for user in self.usuarios:
                linha = tk.Frame(frame_lista)
                linha.pack(fill="x", pady=4)

                # Nome e role
                tk.Label(
                    linha,
                    text=f"{user['username']} ({user['role']})",
                    font=("Arial", 12)
                ).pack(side="left", padx=10)

        # ===== Separador =====
        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=20)

        # ===== Botão de retorno =====
        ttk.Button(
            container, text="Retornar",
            command=lambda: master.mostrar_tela(TelaOpcoesLogin)
        ).pack(pady=10)




