"""Exportação das estatísticas e da distribuição para arquivo .txt ou .csv."""


def _bloco_resumo(estatisticas):
    """Devolve pares (rótulo, valor) com o resumo estatístico, prontos para gravar."""
    e = estatisticas
    return [
        ("Pessoas consideradas", f"{e['n']}"),
        ("Sem classificacao (excluidas)", f"{e['n_sem_classe']}"),
        ("% com superior completo", f"{e['pct_superior']:.1f}%"),
        ("% com ao menos ensino medio", f"{e['pct_ao_menos_medio']:.1f}%"),
        ("% sem instrucao", f"{e['pct_sem_instrucao']:.1f}%"),
        ("Escolaridade mais comum", e["moda_nome"]),
        ("Media aproximada de anos de estudo", f"{e['media_anos']:.1f}"),
    ]


def _exportar_txt(caminho, titulo, estatisticas, distribuicao):
    """Grava um relatório de texto legível (.txt)."""
    linhas = []
    linhas.append("PDAD 2024 - Perfil educacional por Regiao Administrativa")
    linhas.append(f"Recorte: {titulo}")
    linhas.append("=" * 60)
    linhas.append("")
    linhas.append("RESUMO")
    for rotulo, valor in _bloco_resumo(estatisticas):
        linhas.append(f"  {rotulo:.<40} {valor}")
    linhas.append("")
    linhas.append("DISTRIBUICAO POR NIVEL DE ESCOLARIDADE")
    linhas.append(f"  {'Nivel':<24}{'Contagem':>10}{'%':>10}")
    for item in distribuicao:
        linhas.append(f"  {item['nome']:<24}{item['contagem']:>10}{item['percentual']:>9.1f}%")
    with open(caminho, "w", encoding="utf-8") as arquivo:
        arquivo.write("\n".join(linhas) + "\n")


def _exportar_csv(caminho, titulo, estatisticas, distribuicao):
    """Grava os dados em formato de tabela (.csv), separado por ponto e vírgula."""
    linhas = []
    linhas.append(f"Recorte;{titulo}")
    linhas.append("")
    linhas.append("Indicador;Valor")
    for rotulo, valor in _bloco_resumo(estatisticas):
        linhas.append(f"{rotulo};{valor}")
    linhas.append("")
    linhas.append("Nivel de escolaridade;Contagem;Percentual")
    for item in distribuicao:
        linhas.append(f"{item['nome']};{item['contagem']};{item['percentual']:.1f}")
    with open(caminho, "w", encoding="utf-8-sig") as arquivo:
        arquivo.write("\n".join(linhas) + "\n")


def exportar_estatisticas(caminho, titulo, estatisticas, distribuicao):
    """Grava o relatório em .csv (tabela) ou .txt (texto) conforme a extensão do caminho."""
    if caminho.lower().endswith(".csv"):
        _exportar_csv(caminho, titulo, estatisticas, distribuicao)
    else:
        _exportar_txt(caminho, titulo, estatisticas, distribuicao)
