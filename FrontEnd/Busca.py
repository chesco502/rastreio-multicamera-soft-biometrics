import os
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime



class TelaBuscaPessoas(tk.Frame):
    def __init__(self, master):
        super().__init__(master)

        self._cameras = []       # lista de dicts com info das câmeras
        self._check_vars = []    # BooleanVar para cada checkbox de câmera

        tk.Label(self, text="Busca de Pessoas", font=("Arial", 18, "bold")).pack(pady=15)

        frame = tk.Frame(self)
        frame.pack(pady=10)

        # ===== Cor =====
        CORES = [
            ("Preto",    "preto",    "#1a1a1a"),
            ("Branco",   "branco",   "#f5f5f5"),
            ("Cinza",    "cinza",    "#808080"),
            ("Vermelho", "vermelho", "#cc2200"),
            ("Verde",    "verde",    "#1a8a1a"),
            ("Azul",     "azul",     "#1a1acc"),
        ]
        self._cor_vars = {valor: tk.BooleanVar(value=False) for _, valor, _ in CORES}

        tk.Label(frame, text="Cor da Roupa:").grid(row=0, column=0, columnspan=4, pady=(10, 4))
        cor_frame = tk.Frame(frame)
        cor_frame.grid(row=1, column=0, columnspan=4, pady=(0, 4))
        for label, valor, hex_cor in CORES:
            cb_frame = tk.Frame(cor_frame)
            cb_frame.pack(side="left", padx=4)
            tk.Label(cb_frame, bg=hex_cor, width=2, height=1, relief="solid").pack()
            tk.Checkbutton(cb_frame, text=label, variable=self._cor_vars[valor],
                           font=("Arial", 9)).pack()

        # ===== Gênero =====
        tk.Label(frame, text="Gênero:").grid(row=2, column=0, pady=(15, 5), sticky="e")
        self.combo_genero = ttk.Combobox(frame, values=["Male", "Female"], width=15, state="readonly")
        self.combo_genero.grid(row=2, column=1)
        self.combo_genero.set("Male")

        # ===== Câmeras =====
        cam_outer = tk.LabelFrame(self, text="Câmeras para busca", padx=8, pady=6)
        cam_outer.pack(fill="x", padx=30, pady=(10, 0))

        # área rolável para os checkboxes
        scroll_canvas = tk.Canvas(cam_outer, height=120, highlightthickness=0)
        scrollbar = ttk.Scrollbar(cam_outer, orient="vertical", command=scroll_canvas.yview)
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        scroll_canvas.pack(side="left", fill="both", expand=True)

        self._check_frame = tk.Frame(scroll_canvas)
        self._canvas_window = scroll_canvas.create_window((0, 0), window=self._check_frame, anchor="nw")

        self._check_frame.bind(
            "<Configure>",
            lambda _: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )
        scroll_canvas.bind(
            "<Configure>",
            lambda e: scroll_canvas.itemconfig(self._canvas_window, width=e.width)  # noqa: E731
        )
        scroll_canvas.bind_all(
            "<MouseWheel>",
            lambda e: scroll_canvas.yview_scroll(-1 * (e.delta // 120), "units")
        )

        cam_btns = tk.Frame(cam_outer)
        cam_btns.pack(fill="x", pady=(6, 0))
        ttk.Button(cam_btns, text="Marcar Todas",   command=self._marcar_todas).pack(side="left", padx=4)
        ttk.Button(cam_btns, text="Desmarcar Todas", command=self._desmarcar_todas).pack(side="left", padx=4)
        ttk.Button(cam_btns, text="Atualizar Lista", command=self._carregar_cameras).pack(side="left", padx=4)

        # ===== Filtro de horário =====
        filtro_outer = tk.LabelFrame(self, text="Filtro de horário", padx=8, pady=6)
        filtro_outer.pack(fill="x", padx=30, pady=(10, 0))

        self.usar_filtro_tempo = tk.BooleanVar(value=False)
        tk.Checkbutton(
            filtro_outer, text="Ativar filtro de horário",
            variable=self.usar_filtro_tempo,
            command=self._toggle_filtro_tempo, font=("Arial", 9)
        ).pack(anchor="w")

        campos = tk.Frame(filtro_outer)
        campos.pack(anchor="w", pady=(4, 0))

        tk.Label(campos, text="De:", font=("Arial", 9)).grid(row=0, column=0, sticky="e", padx=(0, 4))
        self.entry_inicio = ttk.Entry(campos, width=18, state="disabled")
        self.entry_inicio.grid(row=0, column=1, padx=(0, 16))
        self.entry_inicio.insert(0, "DD/MM/AAAA HH:MM")

        tk.Label(campos, text="Até:", font=("Arial", 9)).grid(row=0, column=2, sticky="e", padx=(0, 4))
        self.entry_fim = ttk.Entry(campos, width=18, state="disabled")
        self.entry_fim.grid(row=0, column=3)
        self.entry_fim.insert(0, "DD/MM/AAAA HH:MM")

        # ===== Modelos =====
        modelos_outer = tk.LabelFrame(self, text="Modelos a utilizar", padx=8, pady=6)
        modelos_outer.pack(fill="x", padx=30, pady=(10, 0))

        self.modo_modelo = tk.StringVar(value="ambos")
        rb_frame = tk.Frame(modelos_outer)
        rb_frame.pack(anchor="w")
        for texto, valor in [("Ambos", "ambos"), ("Apenas Cor", "cor"), ("Apenas Gênero", "genero")]:
            tk.Radiobutton(
                rb_frame, text=texto, variable=self.modo_modelo, value=valor,
                command=self._atualizar_modo_modelo, font=("Arial", 9)
            ).pack(side="left", padx=8)

        self.usar_modelo_cor = tk.BooleanVar(value=True)
        self.chk_unet = tk.Checkbutton(
            modelos_outer, text="Usar segmentação de roupa (U-Net) na análise de cor",
            variable=self.usar_modelo_cor, font=("Arial", 9)
        )
        self.chk_unet.pack(anchor="w", pady=(4, 0))

        # ===== Botões principais =====
        botoes = tk.Frame(self)
        botoes.pack(pady=12)
        ttk.Button(botoes, text="Confirmar", command=self.confirmar).pack(side="left", padx=10)
        ttk.Button(botoes, text="Voltar",    command=self.voltar).pack(side="left", padx=10)

        self._carregar_cameras()

    # ------------------------------------------------------------------
    # Câmeras
    # ------------------------------------------------------------------

    def _carregar_cameras(self):
        try:
            from BackEnd.Cameras_estoque_video.Cam_Maneger import Cam_Maneger
            cm = Cam_Maneger()
            cm.carregar_cam_maneger()
            self._cameras = cm.listar_cameras()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível carregar câmeras:\n{e}")
            self._cameras = []

        # remove checkboxes anteriores
        for w in self._check_frame.winfo_children():
            w.destroy()
        self._check_vars.clear()

        for cam in self._cameras:
            var = tk.BooleanVar(value=True)
            self._check_vars.append(var)
            nome = os.path.basename(cam["caminho"])
            tk.Checkbutton(
                self._check_frame, text=nome, variable=var,
                anchor="w", font=("Arial", 10)
            ).pack(fill="x", padx=4, pady=1)

    def _atualizar_modo_modelo(self):
        usar_cor = self.modo_modelo.get() in ("ambos", "cor")
        self.chk_unet.config(state="normal" if usar_cor else "disabled")

    def _toggle_filtro_tempo(self):
        state = "normal" if self.usar_filtro_tempo.get() else "disabled"
        self.entry_inicio.config(state=state)
        self.entry_fim.config(state=state)

    def _marcar_todas(self):
        for var in self._check_vars:
            var.set(True)

    def _desmarcar_todas(self):
        for var in self._check_vars:
            var.set(False)

    def _cameras_selecionadas(self):
        return [
            self._cameras[i]["caminho"]
            for i, var in enumerate(self._check_vars)
            if var.get()
        ]

    # ------------------------------------------------------------------
    # Ações
    # ------------------------------------------------------------------

    def confirmar(self):
        try:
            genero = self.combo_genero.get()
            cores  = [v for v, var in self._cor_vars.items() if var.get()]

            modo = self.modo_modelo.get()
            usar_cor    = modo in ("ambos", "cor")
            usar_genero = modo in ("ambos", "genero")

            if usar_cor and not cores:
                messagebox.showwarning("Aviso", "Selecione ao menos uma cor.")
                return

            cameras = self._cameras_selecionadas()
            if not cameras:
                messagebox.showwarning("Aviso", "Selecione ao menos uma câmera.")
                return

            intervalo_tempo = None
            if self.usar_filtro_tempo.get():
                fmt = "%d/%m/%Y %H:%M"
                try:
                    inicio = datetime.strptime(self.entry_inicio.get().strip(), fmt)
                    fim    = datetime.strptime(self.entry_fim.get().strip(), fmt)
                except ValueError:
                    messagebox.showerror("Erro", "Formato de horário inválido.\nUse DD/MM/AAAA HH:MM")
                    return
                if inicio > fim:
                    messagebox.showwarning("Aviso", "O horário inicial deve ser anterior ao final.")
                    return
                intervalo_tempo = (inicio, fim)

            from BackEnd.BackEnd_Manager import search
            imagems = search(
                [genero, cores],
                cameras=cameras,
                usar_cor=usar_cor,
                usar_modelo_cor=self.usar_modelo_cor.get() if usar_cor else False,
                usar_genero=usar_genero,
                intervalo_tempo=intervalo_tempo,
            )
            from FrontEnd.Revisar_imagens import TelaRevisarImagens
            self.master.mostrar_tela(TelaRevisarImagens, imagems)

        except Exception as e:
            messagebox.showerror("Erro", f"Erro na busca: {e}")

    def voltar(self):
        from FrontEnd.Operador import TelaOperador
        self.master.mostrar_tela(TelaOperador)
