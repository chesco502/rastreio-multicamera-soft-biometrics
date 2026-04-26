import tkinter as tk
from tkinter import ttk, messagebox
from FrontEnd.Config_Camera import TelaConfigCamera # ajuste o caminho conforme sua estrutura


class TelaCadastroCamera(tk.Frame):
    """Tela para gerenciar câmeras: cadastro e exclusão."""

    def __init__(self, master):
        super().__init__(master)

        # ===== Frame central =====
        container = tk.Frame(self)
        container.place(relx=0.5, rely=0.5, anchor="center")

        # ===== Título =====
        tk.Label(
            container,
            text="Gerenciar Câmeras",
            font=("Arial", 18, "bold")
        ).pack(pady=20)

        # ===== Botões de ação =====
        ttk.Button(
            container, text="Cadastrar Nova Câmera", width=30,
            command=self.cadastrar_camera
        ).pack(pady=10)

        ttk.Button(
            container, text="Deletar Câmera", width=30,
            command=self.deletar_camera
        ).pack(pady=10)

        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=20)

        # ===== Botão de retorno =====
        ttk.Button(
            container, text="Voltar ao Painel do Admin",
            command=self._voltar
        ).pack(pady=10)

    def _voltar(self):
        from FrontEnd.Admin import TelaAdmin
        self.master.mostrar_tela(TelaAdmin)

    # ===== Função para abrir janela de cadastro =====
    def cadastrar_camera(self):
        """Abre uma janela para cadastrar nova câmera."""
        janela = tk.Toplevel(self)
        janela.title("Cadastrar Nova Câmera")
        janela.geometry("350x340")
        janela.grab_set()  # bloqueia interação com a tela anterior

        # ===== Frame interno =====
        frame = tk.Frame(janela, padx=20, pady=20)
        frame.pack(expand=True, fill="both")

        tk.Label(frame, text="Cadastrar Nova Câmera", font=("Arial", 14, "bold")).pack(pady=10)

        # ===== Campos =====
        tk.Label(frame, text="Nome da Câmera:",justify="center").pack(anchor="center")
        entry_nome = ttk.Entry(frame, width=35, justify="center")
        entry_nome.pack(pady=15)

        tk.Label(frame, text="Posição (Coordenadas):", justify="center").pack(anchor="center", pady=(10, 2))

        pos_frame = tk.Frame(frame)
        pos_frame.pack(pady=5)

        # Campo Latitude
        lat_frame = tk.Frame(pos_frame)
        lat_frame.pack(side="left", padx=10)
        tk.Label(lat_frame, text="Latitude:", justify="center").pack()
        entry_latitude = ttk.Entry(lat_frame, width=12, justify="center")
        entry_latitude.pack()

        # Campo Longitude
        long_frame = tk.Frame(pos_frame)
        long_frame.pack(side="left", padx=10)
        tk.Label(long_frame, text="Longitude:", justify="center").pack()
        entry_longitude = ttk.Entry(long_frame, width=12, justify="center")
        entry_longitude.pack()

        # ===== Botão salvar =====
        def salvar_camera():
            nome = entry_nome.get().strip()
            latitude = entry_latitude.get().strip()
            longitude = entry_longitude.get().strip()

            if not nome or not latitude or not longitude:
                messagebox.showwarning("Campos vazios", "Preencha todos os campos antes de salvar.")
                return

            from BackEnd.Cameras_estoque_video.Cam_Maneger import Cam_Maneger
            cam_manager = Cam_Maneger()
            cam_manager.carregar_cam_maneger()
            cam_manager.adicionar_nova_camera(latitude, longitude, nome)
            messagebox.showinfo("Sucesso", "Câmera cadastrada com sucesso!")
            janela.destroy()

        ttk.Button(frame, text="Salvar", command=salvar_camera).pack(pady=15)

    def deletar_camera(self):
        """Função chamada ao clicar em 'Deletar Câmera'."""
        print("Abrindo tela de exclusão de câmera...")
        # Você pode futuramente criar outra janela semelhante para deletar.
