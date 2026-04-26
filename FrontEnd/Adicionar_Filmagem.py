import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
from BackEnd.BackEnd_Manager import Atualizar_filmagens

class TelaAdicionarFilmagem(tk.Frame):
    """Tela para adicionar filmagens ao repositório de uma câmera."""

    def __init__(self, master):
        super().__init__(master)

        self.arquivos_selecionados = []
        self.cameras = []

        # ===== Título =====
        tk.Label(self, text="Adicionar Filmagem", font=("Arial", 18, "bold")).pack(pady=15)

        container = tk.Frame(self)
        container.pack(fill="both", expand=True, padx=30)

        # ===== Seleção de câmera =====
        tk.Label(container, text="Câmera de destino:", font=("Arial", 11)).pack(anchor="w", pady=(10, 2))

        cam_frame = tk.Frame(container)
        cam_frame.pack(fill="x")

        self.combo_camera = ttk.Combobox(cam_frame, state="readonly", width=45)
        self.combo_camera.pack(side="left", padx=(0, 8))

        ttk.Button(cam_frame, text="Atualizar", command=self._carregar_cameras).pack(side="left")

        # ===== Lista de arquivos selecionados =====
        tk.Label(container, text="Arquivos selecionados:", font=("Arial", 11)).pack(anchor="w", pady=(18, 2))

        list_frame = tk.Frame(container)
        list_frame.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical")
        self.listbox = tk.Listbox(
            list_frame, yscrollcommand=scrollbar.set,
            selectmode="extended", height=10, font=("Arial", 9)
        )
        scrollbar.config(command=self.listbox.yview)
        self.listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # ===== Botões de arquivo =====
        arq_frame = tk.Frame(container)
        arq_frame.pack(fill="x", pady=8)

        ttk.Button(arq_frame, text="Selecionar Arquivo(s)", command=self._selecionar_arquivos).pack(side="left", padx=(0, 6))
        ttk.Button(arq_frame, text="Remover Selecionado(s)", command=self._remover_selecionados).pack(side="left", padx=(0, 6))
        ttk.Button(arq_frame, text="Limpar Lista", command=self._limpar_lista).pack(side="left")

        # ===== Barra de progresso e status =====
        self.label_status = tk.Label(container, text="", font=("Arial", 9), fg="gray")
        self.label_status.pack(anchor="w", pady=(4, 0))

        self.progress = ttk.Progressbar(container, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=(2, 10))

        # ===== Botões principais =====
        ttk.Separator(container, orient="horizontal").pack(fill="x", pady=8)

        botoes = tk.Frame(container)
        botoes.pack(pady=10)

        ttk.Button(botoes, text="Adicionar ao Repositório", width=28, command=self._confirmar).pack(side="left", padx=8)
        ttk.Button(botoes, text="Voltar", width=14, command=self._voltar).pack(side="left", padx=8)

        # Carrega câmeras ao iniciar
        self._carregar_cameras()

    # ------------------------------------------------------------------
    def _carregar_cameras(self):
        """Busca as câmeras cadastradas e preenche o combobox."""
        try:
            from BackEnd.Cameras_estoque_video.Cam_Maneger import Cam_Maneger
            cm = Cam_Maneger()
            cm.carregar_cam_maneger()
            lista = cm.listar_cameras()
            self.cameras = lista

            nomes = [os.path.basename(cam["caminho"]) for cam in lista]
            self.combo_camera["values"] = nomes

            if nomes:
                self.combo_camera.current(0)
                self._set_status(f"{len(nomes)} câmera(s) encontrada(s).")
            else:
                self._set_status("Nenhuma câmera cadastrada.")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar as câmeras:\n{e}")

    def _selecionar_arquivos(self):
        """Abre diálogo para selecionar um ou mais arquivos de vídeo."""
        tipos = [
            ("Vídeos", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm"),
            ("Todos os arquivos", "*.*"),
        ]
        caminhos = filedialog.askopenfilenames(title="Selecionar filmagem(ns)", filetypes=tipos)
        for caminho in caminhos:
            if caminho not in self.arquivos_selecionados:
                self.arquivos_selecionados.append(caminho)
                self.listbox.insert(tk.END, os.path.basename(caminho))
        self._set_status(f"{len(self.arquivos_selecionados)} arquivo(s) na fila.")

    def _remover_selecionados(self):
        """Remove os itens marcados na listbox."""
        indices = list(self.listbox.curselection())[::-1]
        for i in indices:
            self.listbox.delete(i)
            self.arquivos_selecionados.pop(i)
        self._set_status(f"{len(self.arquivos_selecionados)} arquivo(s) na fila.")

    def _limpar_lista(self):
        self.listbox.delete(0, tk.END)
        self.arquivos_selecionados.clear()
        self._set_status("")
        self.progress["value"] = 0

    def _confirmar(self):
        """Copia os arquivos para a pasta input da câmera selecionada."""
        idx = self.combo_camera.current()
        if idx < 0:
            messagebox.showwarning("Aviso", "Selecione uma câmera de destino.")
            return
        if not self.arquivos_selecionados:
            messagebox.showwarning("Aviso", "Adicione ao menos um arquivo à lista.")
            return

        caminho_camera = self.cameras[idx]["caminho"]
        pasta_input = os.path.join(caminho_camera, "input")

        try:
            from BackEnd.BackEnd_Manager import adicionar_filmagens
            total = len(self.arquivos_selecionados)
            self.progress["maximum"] = total
            self.progress["value"] = 0

            copiados, ignorados = adicionar_filmagens(
                self.arquivos_selecionados,
                pasta_input
            )

            msg = f"{copiados} arquivo(s) adicionado(s) com sucesso."
            if ignorados:
                msg += f"\n{ignorados} arquivo(s) ignorado(s) (já existiam)."
            messagebox.showinfo("Concluído", msg)
            self._limpar_lista()
            Atualizar_filmagens()

        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao adicionar filmagens:\n{e}")

    def _atualizar_progresso(self, atual, nome):
        self.progress["value"] = atual
        self._set_status(f"Copiando: {nome}")
        self.update_idletasks()

    def _set_status(self, texto):
        self.label_status.config(text=texto)

    def _voltar(self):
        from FrontEnd.Operador import TelaOperador
        self.master.mostrar_tela(TelaOperador)
