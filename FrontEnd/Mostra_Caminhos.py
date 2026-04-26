import tkinter as tk
from tkinter import ttk, messagebox
from BackEnd.Caminho_Possivel.Caminho_Possivel_Manager import Caminho_Possivel


class TelaMostrarCaminhos(tk.Frame):
    """Tela para listar e gerenciar as conexões (caminhos possíveis) entre câmeras."""

    def __init__(self, master):
        super().__init__(master)

        master.geometry("900x600")
        tk.Label(self, text="Conexões Entre Câmeras", font=("Arial", 18, "bold")).pack(pady=15)

        # ===== Inicializa gerenciador de caminhos =====
        self.grafo_manager = Caminho_Possivel()
        try:
            self.grafo_manager.carregar_grafo()
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao carregar o grafo: {e}")

        # ===== Frame principal =====
        frame_main = tk.Frame(self)
        frame_main.pack(fill="both", expand=True, padx=20, pady=10)

        # ===== Tabela de conexões =====
        colunas = ("Origem", "Destino", "Tempo (s)")
        self.tree = ttk.Treeview(frame_main, columns=colunas, show="headings", height=15)
        for col in colunas:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=200)
        self.tree.pack(expand=True, fill="both")

        # ===== Frame de botões =====
        botoes_frame = tk.Frame(self)
        botoes_frame.pack(pady=10)

        ttk.Button(botoes_frame, text="Atualizar", command=self.atualizar_tabela, width=15).pack(side="left", padx=5)
        ttk.Button(botoes_frame, text="Deletar Conexão Selecionada", command=self.deletar_conexao, width=30).pack(side="left", padx=5)
        ttk.Button(botoes_frame, text="Voltar", command=self.voltar, width=15).pack(side="left", padx=5)

        # ===== Carrega conexões =====
        self.atualizar_tabela()

    # ==========================================================
    def atualizar_tabela(self):
        """Atualiza a tabela com as conexões existentes."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            conexoes = self.grafo_manager.mostrar_conexoes()
            if not conexoes:
                messagebox.showinfo("Info", "Nenhuma conexão cadastrada.")
                return

            for origem, destino, tempo in conexoes:
                self.tree.insert("", "end", values=(origem, destino, tempo))

            print("🔄 Tabela de conexões atualizada.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar conexões: {e}")

    # ==========================================================
    def deletar_conexao(self):
        selecao = self.tree.selection()
        valores = self.tree.item(selecao[0], "values")
        origem, destino, _ = valores
        caminho_possivel_manager = Caminho_Possivel()
        caminho_possivel_manager.carregar_grafo()
        caminho_possivel_manager.remover_conexao(origem, destino,)
        
    # ==========================================================
    def voltar(self):
        self.master.mostrar_tela_anterior()
