"""Cálculos de escolaridade: filtros, distribuição, estatísticas e ranking das RAs."""

from utils import dicionario as dic


def filtrar(df, localidade=None, faixa=None, sexo=None):
    """Aplica filtros de localidade, faixa etária e sexo ao DataFrame."""
    resultado = df
    if localidade is not None:
        resultado = resultado[resultado["localidade"] == localidade]
    if faixa is not None:
        minimo, maximo = faixa
        resultado = resultado[(resultado["idade_calculada"] >= minimo) &
                              (resultado["idade_calculada"] <= maximo)]
    if sexo is not None:
        resultado = resultado[resultado["E03"] == sexo]
    return resultado


def apenas_df(df):
    """Mantém apenas moradores das Regiões Administrativas do DF (exclui municípios de GO)."""
    return df[df["eh_df"]]


def somente_classificados(df):
    """Mantém apenas quem tem escolaridade classificada (níveis 1 a 7)."""
    # O código 8 ("Sem classificação") é tratado como não informado e fica de fora.
    return df[df["escolaridade"].isin(dic.NIVEIS_ESCOLARIDADE)]


def _percentual(df, codigos):
    """Percentual de pessoas classificadas cuja escolaridade está em 'codigos'."""
    classificados = somente_classificados(df)
    if len(classificados) == 0:
        return 0.0
    return 100.0 * classificados["escolaridade"].isin(codigos).mean()


def distribuicao_escolaridade(df):
    """Retorna a distribuição (contagem e %) por nível de escolaridade, de 1 a 7."""
    classificados = somente_classificados(df)
    total = len(classificados)
    contagens = classificados["escolaridade"].value_counts()
    linhas = []
    for codigo in dic.NIVEIS_ESCOLARIDADE:
        n = int(contagens.get(codigo, 0))
        pct = (100.0 * n / total) if total > 0 else 0.0
        linhas.append({
            "codigo": codigo,
            "nome": dic.MAPA_ESCOLARIDADE[codigo],
            "contagem": n,
            "percentual": pct,
        })
    return linhas


def estatisticas(df):
    """Calcula estatísticas descritivas de escolaridade para o recorte filtrado."""
    classificados = somente_classificados(df)
    total = len(classificados)
    sem_classe = len(df) - total
    if total == 0:
        return {"n": 0, "n_sem_classe": sem_classe, "pct_superior": 0.0,
                "pct_ao_menos_medio": 0.0, "pct_sem_instrucao": 0.0,
                "moda_nome": "-", "media_anos": 0.0}
    moda_codigo = int(classificados["escolaridade"].mode().iloc[0])
    media_anos = classificados["escolaridade"].map(dic.ANOS_ESTUDO).mean()
    return {
        "n": total,
        "n_sem_classe": sem_classe,
        "pct_superior": _percentual(df, [dic.SUPERIOR_COMPLETO]),
        "pct_ao_menos_medio": _percentual(df, list(dic.AO_MENOS_MEDIO)),
        "pct_sem_instrucao": _percentual(df, [dic.SEM_INSTRUCAO]),
        "moda_nome": dic.MAPA_ESCOLARIDADE[moda_codigo],
        "media_anos": float(media_anos),
    }


def ordenar_por_selecao(lista, chave, decrescente=True):
    """Ordena a lista pelo valor de 'chave' usando Selection Sort feito à mão (D4)."""
    # DIFERENCIAL D4: ordenação implementada manualmente, sem usar sort()/sort_values().
    itens = list(lista)
    n = len(itens)
    for i in range(n):
        indice_alvo = i  # posição do maior (ou menor) valor encontrado a partir de i
        for j in range(i + 1, n):
            if decrescente and chave(itens[j]) > chave(itens[indice_alvo]):
                indice_alvo = j
            elif not decrescente and chave(itens[j]) < chave(itens[indice_alvo]):
                indice_alvo = j
        itens[i], itens[indice_alvo] = itens[indice_alvo], itens[i]
    return itens


def ranking_ras(df, faixa=None, sexo=None, minimo_pessoas=20):
    """Monta o ranking das RAs do DF por % com superior completo (ordenado à mão)."""
    base = filtrar(apenas_df(df), faixa=faixa, sexo=sexo)
    ranking = []
    for codigo, grupo in base.groupby("localidade"):
        classificados = somente_classificados(grupo)
        if len(classificados) < minimo_pessoas:
            continue  # ignora RAs com amostra pequena demais (percentual instável)
        ranking.append({
            "codigo": int(codigo),
            "nome": dic.nome_localidade(int(codigo)),
            "pct_superior": _percentual(grupo, [dic.SUPERIOR_COMPLETO]),
            "n": len(classificados),
        })
    return ordenar_por_selecao(ranking, chave=lambda item: item["pct_superior"])


def serie_por_faixa(df, faixas, localidade=None, sexo=None):
    """Calcula o % com superior completo por faixa etária (para o gráfico de linha)."""
    base = apenas_df(df) if localidade is None else df[df["localidade"] == localidade]
    if sexo is not None:
        base = base[base["E03"] == sexo]
    serie = []
    for rotulo, (minimo, maximo) in faixas:
        recorte = base[(base["idade_calculada"] >= minimo) &
                       (base["idade_calculada"] <= maximo)]
        serie.append({
            "faixa": rotulo,
            "pct_superior": _percentual(recorte, [dic.SUPERIOR_COMPLETO]),
            "n": len(somente_classificados(recorte)),
        })
    return serie
