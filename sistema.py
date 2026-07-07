"""Sistema de Exploração do Perfil Educacional por Região Administrativa — PDAD 2024.

Recorte A: como varia o nível de escolaridade da população adulta entre as RAs do DF?
Execute com:  python sistema.py
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import matplotlib
matplotlib.use("TkAgg")  # backend do matplotlib que conversa com o Tkinter
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from utils import carregar, calcular, exportar
from utils import dicionario as dic

# --- Opções fixas dos filtros -----------------------------------------------
FAIXAS = [
    ("Adultos (18+)", (18, 200)),
    ("18 a 24 anos", (18, 24)),
    ("25 a 39 anos", (25, 39)),
    ("40 a 59 anos", (40, 59)),
    ("60 anos ou mais", (60, 200)),
    ("Todas as idades", (0, 200)),
]
FAIXAS_DICT = dict(FAIXAS)
SEXOS = [("Todos", None), ("Masculino", 1), ("Feminino", 2)]
SEXOS_DICT = dict(SEXOS)
# Faixas usadas no gráfico de linha (escolaridade x idade).
FAIXAS_LINHA = [("18-24", (18, 24)), ("25-39", (25, 39)),
                ("40-59", (40, 59)), ("60+", (60, 200))]

# Rótulos curtos dos níveis de escolaridade (para caber no eixo dos gráficos).
ESCOLARIDADE_CURTA = ["Sem\ninstr.", "Fund.\ninc.", "Fund.\ncomp.", "Médio\ninc.",
                      "Médio\ncomp.", "Sup.\ninc.", "Sup.\ncomp."]

# Nome -> código (todos os nomes de localidade são únicos).
CODIGO_POR_NOME = {nome: cod for cod, nome in dic.MAPA_LOCALIDADE.items()}
NOMES_RAS_DF = sorted(dic.RAS_DF.values())
NOMES_TODAS = NOMES_RAS_DF + sorted(dic.MUNICIPIOS_GO.values())

COR_RA = "#2b6cb0"   # azul
COR_DF = "#dd6b20"   # laranja
COR_B = "#38a169"    # verde (2ª RA na comparação)

# Dados carregados (preenchido no início) e estado da aba 1 (para exportação).
dados = None
estado_aba1 = {}


# ---------------------------------------------------------------------------
# Funções auxiliares de interface
# ---------------------------------------------------------------------------
def criar_filtro(pai, rotulo, valores, inicial, ao_mudar):
    """Cria um par rótulo + Combobox (somente leitura) e devolve o Combobox."""
    tk.Label(pai, text=rotulo).pack(side="left", padx=(10, 3))
    combo = ttk.Combobox(pai, values=valores, state="readonly", width=max(len(inicial), 14))
    combo.set(inicial)
    combo.bind("<<ComboboxSelected>>", lambda *_: ao_mudar())
    combo.pack(side="left")
    return combo


def novo_grafico(pai):
    """Cria uma figura matplotlib embutida no Tkinter e devolve (figura, eixo, canvas)."""
    figura = Figure(figsize=(6.5, 4.2), dpi=95)
    eixo = figura.add_subplot(111)
    canvas = FigureCanvasTkAgg(figura, master=pai)
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=6, pady=6)
    return figura, eixo, canvas


# ---------------------------------------------------------------------------
# Aba 1 — Distribuição por RA (gráfico obrigatório de barras + estatísticas)
# ---------------------------------------------------------------------------
def construir_aba_distribuicao(notebook):
    """Monta a aba com a distribuição de escolaridade de uma RA comparada ao DF."""
    aba = tk.Frame(notebook)
    notebook.add(aba, text="Distribuição por RA")

    controles = tk.Frame(aba)
    controles.pack(fill="x", pady=6)

    figura, eixo, canvas = novo_grafico(aba)

    painel_stats = tk.LabelFrame(aba, text="Estatísticas descritivas", padx=8, pady=6)
    painel_stats.pack(fill="x", padx=8, pady=(0, 8))
    rotulos = {}
    for chave in ("n", "superior", "medio", "sem", "moda", "anos"):
        rotulos[chave] = tk.Label(painel_stats, text="", anchor="w", font=("Segoe UI", 9))
        rotulos[chave].pack(fill="x")

    def atualizar():
        """Redesenha o gráfico e as estatísticas da RA selecionada."""
        codigo = CODIGO_POR_NOME[combo_ra.get()]
        faixa = FAIXAS_DICT[combo_faixa.get()]
        sexo = SEXOS_DICT[combo_sexo.get()]
        df_ra = calcular.filtrar(dados, localidade=codigo, faixa=faixa, sexo=sexo)
        df_baseline = calcular.filtrar(calcular.apenas_df(dados), faixa=faixa, sexo=sexo)
        dist_ra = calcular.distribuicao_escolaridade(df_ra)
        dist_df = calcular.distribuicao_escolaridade(df_baseline)

        eixo.clear()
        posicoes = list(range(len(ESCOLARIDADE_CURTA)))
        largura = 0.4
        eixo.bar([p - largura / 2 for p in posicoes], [d["percentual"] for d in dist_ra],
                 largura, label=combo_ra.get(), color=COR_RA)
        eixo.bar([p + largura / 2 for p in posicoes], [d["percentual"] for d in dist_df],
                 largura, label="Média do DF", color=COR_DF)
        eixo.set_xticks(posicoes)
        eixo.set_xticklabels(ESCOLARIDADE_CURTA, fontsize=8)
        eixo.set_ylabel("% das pessoas")
        eixo.set_xlabel("Nível de escolaridade")
        eixo.set_title(f"Escolaridade — {combo_ra.get()} vs média do DF")
        eixo.legend(fontsize=8)
        figura.tight_layout()
        canvas.draw()

        est = calcular.estatisticas(df_ra)
        rotulos["n"].config(text=f"Pessoas consideradas: {est['n']}   "
                                 f"(excluídas por 'sem classificação': {est['n_sem_classe']})")
        rotulos["superior"].config(text=f"% com superior completo: {est['pct_superior']:.1f}%")
        rotulos["medio"].config(text=f"% com ao menos ensino médio: {est['pct_ao_menos_medio']:.1f}%")
        rotulos["sem"].config(text=f"% sem instrução: {est['pct_sem_instrucao']:.1f}%")
        rotulos["moda"].config(text=f"Escolaridade mais comum: {est['moda_nome']}")
        rotulos["anos"].config(text=f"Média aproximada de anos de estudo: {est['media_anos']:.1f}")

        # guarda o estado atual para a exportação
        estado_aba1["titulo"] = f"{combo_ra.get()} | {combo_faixa.get()} | {combo_sexo.get()}"
        estado_aba1["est"] = est
        estado_aba1["dist"] = dist_ra

    combo_ra = criar_filtro(controles, "Região Administrativa:", NOMES_TODAS, "Ceilândia", atualizar)
    combo_faixa = criar_filtro(controles, "Faixa etária:", [f[0] for f in FAIXAS], FAIXAS[0][0], atualizar)
    combo_sexo = criar_filtro(controles, "Sexo:", [s[0] for s in SEXOS], SEXOS[0][0], atualizar)
    tk.Button(controles, text="Exportar…", command=acao_exportar).pack(side="right", padx=10)

    atualizar()


def acao_exportar():
    """Abre um diálogo e exporta as estatísticas da aba 1 para .txt ou .csv."""
    if not estado_aba1:
        return
    caminho = filedialog.asksaveasfilename(
        title="Exportar estatísticas",
        defaultextension=".txt",
        initialfile="saida_escolaridade",
        filetypes=[("Arquivo de texto", "*.txt"), ("Planilha CSV", "*.csv")],
    )
    if not caminho:
        return  # usuário cancelou
    try:
        exportar.exportar_estatisticas(caminho, estado_aba1["titulo"],
                                       estado_aba1["est"], estado_aba1["dist"])
        messagebox.showinfo("Exportação concluída", f"Arquivo salvo em:\n{caminho}")
    except OSError as erro:
        messagebox.showerror("Erro ao exportar", str(erro))


# ---------------------------------------------------------------------------
# Aba 2 — Comparar duas RAs lado a lado (Diferencial D2)
# ---------------------------------------------------------------------------
def construir_aba_comparacao(notebook):
    """Monta a aba que compara a distribuição de escolaridade de duas RAs (D2)."""
    aba = tk.Frame(notebook)
    notebook.add(aba, text="Comparar RAs")

    controles = tk.Frame(aba)
    controles.pack(fill="x", pady=6)
    figura, eixo, canvas = novo_grafico(aba)

    def atualizar():
        """Redesenha o gráfico de barras comparando as duas RAs escolhidas."""
        cod_a = CODIGO_POR_NOME[combo_a.get()]
        cod_b = CODIGO_POR_NOME[combo_b.get()]
        faixa = FAIXAS_DICT[combo_faixa.get()]
        sexo = SEXOS_DICT[combo_sexo.get()]
        dist_a = calcular.distribuicao_escolaridade(
            calcular.filtrar(dados, localidade=cod_a, faixa=faixa, sexo=sexo))
        dist_b = calcular.distribuicao_escolaridade(
            calcular.filtrar(dados, localidade=cod_b, faixa=faixa, sexo=sexo))

        eixo.clear()
        posicoes = list(range(len(ESCOLARIDADE_CURTA)))
        largura = 0.4
        eixo.bar([p - largura / 2 for p in posicoes], [d["percentual"] for d in dist_a],
                 largura, label=combo_a.get(), color=COR_RA)
        eixo.bar([p + largura / 2 for p in posicoes], [d["percentual"] for d in dist_b],
                 largura, label=combo_b.get(), color=COR_B)
        eixo.set_xticks(posicoes)
        eixo.set_xticklabels(ESCOLARIDADE_CURTA, fontsize=8)
        eixo.set_ylabel("% das pessoas")
        eixo.set_xlabel("Nível de escolaridade")
        eixo.set_title(f"{combo_a.get()} vs {combo_b.get()}  ({combo_faixa.get()})")
        eixo.legend(fontsize=8)
        figura.tight_layout()
        canvas.draw()

    combo_a = criar_filtro(controles, "RA A:", NOMES_TODAS, "Ceilândia", atualizar)
    combo_b = criar_filtro(controles, "RA B:", NOMES_TODAS, "Plano Piloto", atualizar)
    combo_faixa = criar_filtro(controles, "Faixa:", [f[0] for f in FAIXAS], FAIXAS[0][0], atualizar)
    combo_sexo = criar_filtro(controles, "Sexo:", [s[0] for s in SEXOS], SEXOS[0][0], atualizar)
    atualizar()


# ---------------------------------------------------------------------------
# Aba 3 — Ranking das RAs (ordenação manual — Diferencial D4)
# ---------------------------------------------------------------------------
def construir_aba_ranking(notebook):
    """Monta a aba com o ranking das RAs do DF por % com superior completo (D4)."""
    aba = tk.Frame(notebook)
    notebook.add(aba, text="Ranking das RAs")

    controles = tk.Frame(aba)
    controles.pack(fill="x", pady=6)
    tk.Label(controles, text="Ranking por % com superior completo "
                             "(ordenação manual — Selection Sort)").pack(side="left", padx=10)

    corpo = tk.Frame(aba)
    corpo.pack(fill="both", expand=True)

    tabela = ttk.Treeview(corpo, columns=("pos", "ra", "pct", "n"),
                          show="headings", height=18)
    for coluna, titulo, largura in [("pos", "#", 40), ("ra", "Região Administrativa", 190),
                                    ("pct", "% superior", 90), ("n", "Pessoas", 80)]:
        tabela.heading(coluna, text=titulo)
        tabela.column(coluna, width=largura, anchor="center")
    tabela.column("ra", anchor="w")
    tabela.pack(side="left", fill="y", padx=(8, 4), pady=6)

    figura, eixo, canvas = novo_grafico(corpo)

    def atualizar():
        """Recalcula o ranking (ordenado à mão) e atualiza a tabela e o gráfico."""
        faixa = FAIXAS_DICT[combo_faixa.get()]
        sexo = SEXOS_DICT[combo_sexo.get()]
        ranking = calcular.ranking_ras(dados, faixa=faixa, sexo=sexo)

        tabela.delete(*tabela.get_children())
        for posicao, item in enumerate(ranking, start=1):
            tabela.insert("", "end", values=(posicao, item["nome"],
                                             f"{item['pct_superior']:.1f}%", item["n"]))

        eixo.clear()
        nomes = [item["nome"] for item in ranking]
        valores = [item["pct_superior"] for item in ranking]
        posicoes = list(range(len(ranking)))
        eixo.barh(posicoes, valores, color=COR_RA)
        eixo.set_yticks(posicoes)
        eixo.set_yticklabels(nomes, fontsize=6)
        eixo.invert_yaxis()  # a RA com maior % fica no topo
        eixo.set_xlabel("% com superior completo")
        eixo.set_title(f"Ranking das RAs do DF ({combo_faixa.get()})")
        figura.tight_layout()
        canvas.draw()

    combo_faixa = criar_filtro(controles, "Faixa:", [f[0] for f in FAIXAS], FAIXAS[0][0], atualizar)
    combo_sexo = criar_filtro(controles, "Sexo:", [s[0] for s in SEXOS], SEXOS[0][0], atualizar)
    atualizar()


# ---------------------------------------------------------------------------
# Aba 4 — Escolaridade x Idade (2º gráfico, de linha — Diferencial D1)
# ---------------------------------------------------------------------------
def construir_aba_idade(notebook):
    """Monta a aba com o gráfico de linha do % com superior por faixa etária (D1)."""
    aba = tk.Frame(notebook)
    notebook.add(aba, text="Escolaridade × Idade")

    controles = tk.Frame(aba)
    controles.pack(fill="x", pady=6)
    figura, eixo, canvas = novo_grafico(aba)

    def atualizar():
        """Redesenha o gráfico de linha comparando a RA com a média do DF por idade."""
        codigo = CODIGO_POR_NOME[combo_ra.get()]
        sexo = SEXOS_DICT[combo_sexo.get()]
        serie_ra = calcular.serie_por_faixa(dados, FAIXAS_LINHA, localidade=codigo, sexo=sexo)
        serie_df = calcular.serie_por_faixa(dados, FAIXAS_LINHA, localidade=None, sexo=sexo)

        eixo.clear()
        faixas = [s["faixa"] for s in serie_ra]
        eixo.plot(faixas, [s["pct_superior"] for s in serie_ra],
                  marker="o", color=COR_RA, linewidth=2, label=combo_ra.get())
        eixo.plot(faixas, [s["pct_superior"] for s in serie_df],
                  marker="s", color=COR_DF, linewidth=2, label="Média do DF")
        eixo.set_ylabel("% com superior completo")
        eixo.set_xlabel("Faixa etária")
        eixo.set_title(f"Escolaridade superior por idade — {combo_ra.get()}")
        eixo.grid(True, alpha=0.3)
        eixo.legend(fontsize=8)
        figura.tight_layout()
        canvas.draw()

    combo_ra = criar_filtro(controles, "Região Administrativa:", NOMES_TODAS, "Plano Piloto", atualizar)
    combo_sexo = criar_filtro(controles, "Sexo:", [s[0] for s in SEXOS], SEXOS[0][0], atualizar)
    atualizar()


# ---------------------------------------------------------------------------
# Montagem geral da janela
# ---------------------------------------------------------------------------
def construir_cabecalho(janela):
    """Monta o título, a descrição do recorte e a contagem de registros carregados."""
    cabecalho = tk.Frame(janela, bg="#1a365d")
    cabecalho.pack(fill="x")
    tk.Label(cabecalho, text="TRABALHO FINAL · APC 2026/1",
             fg="#90cdf4", bg="#1a365d", font=("Segoe UI", 8, "bold")).pack(anchor="w", padx=12, pady=(8, 0))
    tk.Label(cabecalho, text="Perfil Educacional por Região Administrativa — PDAD 2024",
             fg="white", bg="#1a365d", font=("Segoe UI", 13, "bold")).pack(anchor="w", padx=12)
    tk.Label(cabecalho, text="Como varia a escolaridade da população adulta entre as RAs do DF?",
             fg="#cbd5e0", bg="#1a365d", font=("Segoe UI", 9)).pack(anchor="w", padx=12)

    total = len(dados)
    adultos = int((dados["idade_calculada"] >= 18).sum())
    n_ras = calcular.apenas_df(dados)["localidade"].nunique()
    tk.Label(cabecalho,
             text=f"{total:,} moradores carregados  ·  {adultos:,} adultos (18+)  ·  {n_ras} RAs do DF"
                  .replace(",", "."),
             fg="white", bg="#1a365d", font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=12, pady=(0, 8))


def construir_interface(janela):
    """Constrói o cabeçalho e as abas depois que os dados foram carregados."""
    construir_cabecalho(janela)
    notebook = ttk.Notebook(janela)
    notebook.pack(fill="both", expand=True)
    construir_aba_distribuicao(notebook)
    construir_aba_comparacao(notebook)
    construir_aba_ranking(notebook)
    construir_aba_idade(notebook)


def carregar_com_progresso(janela):
    """Mostra uma barra de progresso enquanto lê os microdados (Diferencial D6)."""
    tela = tk.Frame(janela)
    tela.pack(expand=True)
    tk.Label(tela, text="Carregando microdados da PDAD 2024…",
             font=("Segoe UI", 11)).pack(pady=12)
    barra = ttk.Progressbar(tela, length=420, maximum=100)
    barra.pack(pady=8)
    rotulo = tk.Label(tela, text="0%", font=("Segoe UI", 9))
    rotulo.pack()
    janela.update()

    def progresso(fracao):
        barra["value"] = fracao * 100
        rotulo.config(text=f"{int(fracao * 100)}%")
        janela.update()

    df = carregar.carregar_moradores(carregar.caminho_dados(), progresso)
    tela.destroy()
    return carregar.preparar(df)


def main():
    """Inicia a janela, carrega os dados e entra no laço principal do Tkinter."""
    global dados
    janela = tk.Tk()
    janela.title("Trabalho Final · APC 2026/1 — Perfil Educacional por RA (PDAD 2024)")
    janela.geometry("960x720")
    try:
        dados = carregar_com_progresso(janela)
    except FileNotFoundError as erro:
        messagebox.showerror("Dados não encontrados", str(erro))
        janela.destroy()
        return
    construir_interface(janela)
    janela.mainloop()


if __name__ == "__main__":
    main()
