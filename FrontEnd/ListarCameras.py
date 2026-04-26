import tkinter as tk
from tkinter import ttk, messagebox
import os
from BackEnd.Cameras_estoque_video.Cam_Maneger import Cam_Maneger


class TelaListarCameras(tk.Frame):
    

    def __init__(self, master):
        super().__init__(master)

        # ====== Configuração visual ======
        tk.Label(self, text="Câmeras Cadastradas", font=("Arial", 18, "bold")).pack(pady=15)

        # Frame de botões
        botoes_frame = tk.Frame(self)
        botoes_frame.pack(pady=5)

        
        ttk.Button(botoes_frame, text="Voltar", command=self.voltar).pack(side="left", padx=5)

        # ====== Treeview para exibir as câmeras ======
        colunas = ("Nome", "Latitude", "Longitude", "Caminho")
        self.tree = ttk.Treeview(self, columns=colunas, show="headings", height=10)

        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.tree.pack(padx=20, pady=10, fill="both", expand=True)

        # ====== Inicializa o gerenciador ======
        self.cam_manager = Cam_Maneger()
        try:
            self.cam_manager.carregar_cam_maneger()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar gerenciador: {e}")

        # Carrega lista inicial
        self.atualizar_lista()

    def atualizar_lista(self):
        """Recarrega e exibe todas as câmeras cadastradas."""
        for i in self.tree.get_children():
            self.tree.delete(i)

        try:
            self.cam_manager.carregar_cam_maneger()
            lista_cameras = self.cam_manager.listar_cameras()
            if not lista_cameras:
                messagebox.showinfo("Info", "Nenhuma câmera cadastrada ainda.")
                return

            for cam in lista_cameras:
                nome = os.path.basename(cam["caminho"])
                self.tree.insert("", "end", values=(nome, cam["latitude"], cam["longitude"], cam["caminho"]))
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao atualizar lista: {e}")

    def voltar(self):
        self.master.mostrar_tela_anterior()
