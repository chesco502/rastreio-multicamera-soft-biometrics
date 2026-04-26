import os
import re
import shutil
import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
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


class TelaLinhaDeTempo(tk.Frame):
    """
    Exibe imagens confirmadas em ordem cronológica.
    Cada entrada tem botão de remoção individual.
    O salvamento é feito manualmente via botão em TelaResultadoFinal.
    """

    THUMB_W = 90
    THUMB_H = 70

    def __init__(self, master, resultados: list):
        super().__init__(master)
        self.master = master
        self._refs = []
        # cópia mutável: (caminho, confirmado)
        self._resultados = list(resultados)

        itens = self._parsear_e_ordenar(self._resultados)

        tk.Label(self, text="Linha do Tempo", font=("Arial", 18, "bold")).pack(pady=(15, 2))
        self._label_resumo = tk.Label(self, font=("Arial", 10), fg="gray")
        self._label_resumo.pack(pady=(0, 8))
        self._atualizar_resumo()

        # ── área rolável ──────────────────────────────────────────────────
        container = tk.Frame(self)
        container.pack(fill="both", expand=True, padx=10)

        self._canvas = tk.Canvas(container, highlightthickness=0)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        self._inner = tk.Frame(self._canvas)
        win = self._canvas.create_window((0, 0), window=self._inner, anchor="nw")
        self._inner.bind("<Configure>", lambda _: self._canvas.configure(
            scrollregion=self._canvas.bbox("all")))
        self._canvas.bind("<Configure>",
                          lambda e: self._canvas.itemconfig(win, width=e.width))
        self._canvas.bind_all("<MouseWheel>",
                              lambda e: self._canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        self._popular(self._inner, itens)

        # ── botões ────────────────────────────────────────────────────────
        rodape = tk.Frame(self)
        rodape.pack(pady=10)
        ttk.Button(rodape, text="Ver Resumo",
                   command=self._ver_resumo).pack(side="left", padx=10)
        ttk.Button(rodape, text="Voltar à Busca",
                   command=self.voltar).pack(side="left", padx=10)

    # ── resumo ────────────────────────────────────────────────────────────

    def _atualizar_resumo(self):
        n = sum(1 for _, ok in self._resultados if ok)
        self._label_resumo.config(text=f"{n} imagem(ns) confirmada(s)")

    # ── parsing ───────────────────────────────────────────────────────────

    def _extrair_timestamp(self, caminho: str) -> datetime:
        nome = os.path.basename(caminho)
        m = re.search(r'\bt(\d{2})_(\d{2})_(\d{2})', nome)
        if m:
            try:
                h, mi, s = int(m.group(1)), int(m.group(2)), int(m.group(3))
                return datetime.min + timedelta(hours=h, minutes=mi, seconds=s)
            except Exception:
                pass
        try:
            dt = datetime.fromtimestamp(os.path.getmtime(caminho))
            return datetime.min + timedelta(hours=dt.hour, minutes=dt.minute, seconds=dt.second)
        except Exception:
            return datetime.min

    def _parsear_e_ordenar(self, resultados: list) -> list:
        itens = []
        for caminho, confirmado in resultados:
            if not confirmado:
                continue
            ts = self._extrair_timestamp(caminho)
            camera = self._extrair_camera(caminho)
            try:
                dia = datetime.fromtimestamp(os.path.getmtime(caminho)).strftime("%d/%m/%Y")
            except Exception:
                dia = "—"
            itens.append((ts, caminho, camera, confirmado, dia))
        itens.sort(key=lambda x: (x[0], os.path.basename(x[1])))
        return itens

    @staticmethod
    def _extrair_camera(caminho: str) -> str:
        partes = os.path.normpath(caminho).split(os.sep)
        try:
            idx = partes.index("output")
            return partes[idx - 1]
        except ValueError:
            return os.path.basename(os.path.dirname(caminho))

    # ── renderização ──────────────────────────────────────────────────────

    def _popular(self, frame: tk.Frame, itens: list):
        if not itens:
            tk.Label(frame, text="Nenhuma imagem para exibir.",
                     font=("Arial", 11), fg="gray").pack(pady=40)
            return

        ultimo_dia = None
        for ts, caminho, camera, confirmado, dia_str in itens:
            if dia_str != ultimo_dia:
                ultimo_dia = dia_str
                sep = tk.Frame(frame, bg="#d0d0d0", height=1)
                sep.pack(fill="x", padx=8, pady=(14, 0))
                tk.Label(frame, text=f"  {dia_str}",
                         font=("Arial", 10, "bold"), fg="#444",
                         anchor="w").pack(fill="x", padx=8, pady=(2, 6))

            self._adicionar_entrada(frame, caminho, camera)

    def _adicionar_entrada(self, pai, caminho: str, camera: str):
        linha = tk.Frame(pai, bd=1, relief="groove")
        linha.pack(fill="x", padx=8, pady=3)

        # faixa colorida lateral
        tk.Frame(linha, bg="#2a9d2a", width=6).pack(side="left", fill="y")

        # thumbnail (clicável para zoom)
        thumb_frame = tk.Frame(linha, bg="white",
                               width=self.THUMB_W + 4, height=self.THUMB_H + 4,
                               cursor="hand2")
        thumb_frame.pack(side="left", padx=4, pady=4)
        thumb_frame.pack_propagate(False)
        try:
            img = Image.open(caminho)
            img.thumbnail((self.THUMB_W, self.THUMB_H))
            tk_img = ImageTk.PhotoImage(img)
            self._refs.append(tk_img)
            lbl = tk.Label(thumb_frame, image=tk_img, bg="white", cursor="hand2")
            lbl.pack(expand=True, fill="both")
            lbl.bind("<Button-1>", lambda _: self._abrir_zoom(caminho))
        except Exception:
            tk.Label(thumb_frame, text="[?]", bg="#ddd").pack(expand=True, fill="both")

        # horário
        hora_frame = tk.Frame(linha, width=75)
        hora_frame.pack(side="left", fill="y", padx=(6, 0))
        hora_frame.pack_propagate(False)
        tk.Label(hora_frame, text=_tempo_display(caminho),
                 font=("Arial", 14, "bold"), anchor="center").pack(expand=True, fill="both")

        # divisor vertical
        tk.Frame(linha, bg="#d0d0d0", width=1).pack(side="left", fill="y", padx=4)

        # metadados
        info = tk.Frame(linha)
        info.pack(side="left", fill="both", expand=True, padx=6, pady=4)
        tk.Label(info, text=camera, font=("Arial", 10, "bold"), anchor="w", fg="#222").pack(fill="x")
        tk.Label(info, text=os.path.basename(caminho),
                 font=("Arial", 8), anchor="w", fg="#777", wraplength=300).pack(fill="x")

        # botão remover (lado direito)
        ttk.Button(
            linha, text="Remover",
            command=lambda l=linha, c=caminho: self._remover_entrada(l, c)
        ).pack(side="right", padx=8, pady=6)

    def _remover_entrada(self, linha: tk.Frame, caminho: str):
        # Marca como não confirmado em _resultados
        for i, (c, ok) in enumerate(self._resultados):
            if c == caminho and ok:
                self._resultados[i] = (c, False)
                break
        linha.destroy()
        self._atualizar_resumo()

    # ── zoom ──────────────────────────────────────────────────────────────

    def _abrir_zoom(self, caminho: str):
        popup = tk.Toplevel(self)
        popup.title(os.path.basename(caminho))
        popup.grab_set()

        sw = popup.winfo_screenwidth()
        sh = popup.winfo_screenheight()
        max_w, max_h = int(sw * 0.85), int(sh * 0.85)

        try:
            img = Image.open(caminho)
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(img)
            lbl = tk.Label(popup, image=tk_img, cursor="hand2")
            lbl.image = tk_img
            lbl.pack()
            lbl.bind("<Button-1>", lambda _: popup.destroy())
        except Exception as e:
            tk.Label(popup, text=f"Erro ao abrir imagem:\n{e}", padx=20, pady=20).pack()

        popup.bind("<Escape>", lambda _: popup.destroy())
        popup.bind("<Button-3>", lambda _: popup.destroy())
        popup.update_idletasks()
        x = (sw - popup.winfo_width()) // 2
        y = (sh - popup.winfo_height()) // 2
        popup.geometry(f"+{x}+{y}")

    # ── navegação ─────────────────────────────────────────────────────────

    def _ver_resumo(self):
        from FrontEnd.Resultado_Final import TelaResultadoFinal
        self.master.mostrar_tela(TelaResultadoFinal, self._resultados)

    def voltar(self):
        from FrontEnd.Busca import TelaBuscaPessoas
        self.master.mostrar_tela(TelaBuscaPessoas)
