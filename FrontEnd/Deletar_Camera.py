import tkinter as tk
from tkinter import ttk, messagebox
import os
from BackEnd.Cameras_estoque_video.Cam_Maneger import Cam_Maneger


class TelaDeletarCamera(tk.Frame):
    """Tela que exibe todas as câmeras e permite selecionar uma para deletar (lógica ainda será implementada)."""

    def __init__(self, master):
        super().__init__(master)

        # ====== Título ======
        tk.Label(self, text="Deletar Câmeras", font=("Arial", 18, "bold")).pack(pady=15)

        # ====== Frame de botões ======
        botoes_frame = tk.Frame(self)
        botoes_frame.pack(pady=5)

        ttk.Button(botoes_frame, text="Atualizar Lista", command=self.atualizar_lista).pack(side="left", padx=5)
        ttk.Button(botoes_frame, text="Deletar Selecionada", command=self.deletar_camera).pack(side="left", padx=5)
        ttk.Button(botoes_frame, text="Voltar", command=self.voltar).pack(side="left", padx=5)

        # ====== Treeview ======
        colunas = ("Nome", "Latitude", "Longitude", "Caminho")
        self.tree = ttk.Treeview(self, columns=colunas, show="headings", height=10)

        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")

        self.tree.pack(padx=20, pady=10, fill="both", expand=True)

        # ====== Inicializa gerenciador ======
        self.cam_manager = Cam_Maneger()
        try:
            self.cam_manager.carregar_cam_maneger()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar gerenciador: {e}")

        # ====== Carrega lista inicial ======
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

    def deletar_camera(self):
        
        selecionado = self.tree.selection()
        valores = self.tree.item(selecionado[0], "values")
        nome_camera = valores[0]
        from BackEnd.Cameras_estoque_video.Cam_Maneger import Cam_Maneger
        cam_maneger = Cam_Maneger()
        cam_maneger.carregar_cam_maneger()
        cam_maneger.deletar_camera(nome_camera)
        
        messagebox.showinfo("Selecionado", f"Camera : {nome_camera} Deletada")
        self.atualizar_lista()

    def voltar(self):
        self.master.mostrar_tela_anterior()
