import os
import re
import shutil
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from pathlib import Path
from PIL import Image, ImageTk

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def _tempo_display(caminho: str) -> str:
    nome = os.path.basename(caminho)
    m = re.search(r'\bt(\d{2})_(\d{2})_(\d{2})', nome)
    if m:
        return f"{m.group(1)}:{m.group(2)}:{m.group(3)}"
    try:
        return datetime.fromtimestamp(os.path.getmtime(caminho)).strftime("%H:%M:%S")
    except Exception:
        return ""


def _sort_key(caminho: str) -> float:
    nome = os.path.basename(caminho)
    m = re.search(r'\bt(\d{2})_(\d{2})_(\d{2})', nome)
    if m:
        return int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
    try:
        return os.path.getmtime(caminho)
    except Exception:
        return 0.0


class TelaResultadoFinal(tk.Frame):
    """
    Exibe todas as imagens confirmadas agrupadas por câmera.
    O salvamento é feito manualmente pelo botão "Salvar Resultados".
    """

    THUMB_W = 160
    THUMB_H = 160
    COLUNAS = 4

    def __init__(self, master, resultados: list):
        super().__init__(master)
        self._resultados = resultados

        self._positivos = [path for path, ok in resultados if ok]

        tk.Label(self, text="Resultados Confirmados",
                 font=("Arial", 18, "bold")).pack(pady=(15, 5))
        tk.Label(self,
                 text=f"{len(self._positivos)} imagem(ns) positiva(s) encontrada(s)",
                 font=("Arial", 10), fg="gray").pack(pady=(0, 10))

        # ── área rolável ──────────────────────────────────────────────
        container = tk.Frame(self)
        container.pack(fill="both", expand=True, padx=10)

        canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self.inner = tk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=self.inner, anchor="nw")
        self.inner.bind("<Configure>",
                        lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>",
                    lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # ── agrupa por câmera ─────────────────────────────────────────
        grupos: dict[str, list[str]] = {}
        for path in self._positivos:
            cam = self._extrair_camera(path)
            grupos.setdefault(cam, []).append(path)

        self._refs = []

        if not self._positivos:
            tk.Label(self.inner, text="Nenhuma imagem foi confirmada.",
                     font=("Arial", 12), fg="gray").pack(pady=40)
        else:
            for cam_nome, caminhos in grupos.items():
                self._renderizar_grupo(cam_nome, caminhos)

        # ── botões ────────────────────────────────────────────────────
        rodape = tk.Frame(self)
        rodape.pack(pady=12)
        ttk.Button(rodape, text="Salvar Resultados",
                   command=self._salvar).pack(side="left", padx=10)
        ttk.Button(rodape, text="Voltar",
                   command=self.voltar).pack(side="left", padx=10)

    # ------------------------------------------------------------------

    def _extrair_camera(self, caminho: str) -> str:
        partes = os.path.normpath(caminho).split(os.sep)
        try:
            idx = partes.index("output")
            return partes[idx - 1]
        except ValueError:
            return os.path.basename(os.path.dirname(caminho))

    def _renderizar_grupo(self, titulo: str, caminhos: list[str]):
        header = tk.Frame(self.inner, bg="#e8e8e8")
        header.pack(fill="x", pady=(14, 4), padx=4)
        tk.Label(header, text=f"📷  {titulo}  —  {len(caminhos)} foto(s)",
                 font=("Arial", 11, "bold"), bg="#e8e8e8",
                 anchor="w").pack(padx=8, pady=4, fill="x")

        grade = tk.Frame(self.inner)
        grade.pack(fill="x", padx=8, pady=4)

        for i, caminho in enumerate(sorted(caminhos, key=_sort_key)):
            self._adicionar_thumb(grade, caminho, i // self.COLUNAS, i % self.COLUNAS)

    def _adicionar_thumb(self, pai, caminho: str, row: int, col: int):
        cell = tk.Frame(pai, bd=1, relief="solid", padx=2, pady=2)
        cell.grid(row=row, column=col, padx=6, pady=6, sticky="n")

        try:
            img = Image.open(caminho)
            img.thumbnail((self.THUMB_W, self.THUMB_H))
            tk_img = ImageTk.PhotoImage(img)
            self._refs.append(tk_img)
            tk.Label(cell, image=tk_img).pack()
        except Exception:
            tk.Label(cell, text="[erro]", width=14, height=6, bg="lightgray").pack()

        tk.Label(cell, text=_tempo_display(caminho),
                 font=("Arial", 9), justify="center").pack()

    # ------------------------------------------------------------------

    def _salvar(self):
        if not self._positivos:
            messagebox.showinfo("Aviso", "Não há imagens confirmadas para salvar.")
            return

        try:
            ts_base = datetime.now().strftime("%Y%m%d_%H%M%S")
            pasta = OUTPUT_DIR / ts_base
            pasta.mkdir(parents=True, exist_ok=True)

            salvos = 0
            for origem in self._positivos:
                destino = pasta / Path(origem).name
                if not destino.exists():
                    shutil.copy2(origem, destino)
                salvos += 1

            messagebox.showinfo(
                "Salvo",
                f"{salvos} imagem(ns) salva(s) em:\noutput/{ts_base}/"
            )
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível salvar:\n{e}")

    def voltar(self):
        from FrontEnd.Busca import TelaBuscaPessoas
        self.master.mostrar_tela(TelaBuscaPessoas)
