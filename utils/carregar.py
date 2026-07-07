"""Leitura e limpeza dos microdados de moradores da PDAD 2024."""

import os
import pandas as pd

from utils import dicionario as dic

# Só carregamos as colunas necessárias para o Recorte A (deixa a leitura rápida).
COLUNAS = ["localidade", "idade_calculada", "E03", "escolaridade"]

# Valores sentinela usados pela PDAD (devem ser removidos antes de calcular).
SENTINELAS = (99999, 88888)  # 99999 = não se aplica; 88888 = não declarado

# Nomes dos arquivos possíveis, em ordem de preferência (completo antes do parcial).
_PASTA_DADOS = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dados")
_ARQUIVOS = ["moradores.csv", "moradores_parcial.csv"]


def caminho_dados():
    """Devolve o caminho do arquivo de dados a usar (completo, se existir; senão o parcial)."""
    for nome in _ARQUIVOS:
        caminho = os.path.join(_PASTA_DADOS, nome)
        if os.path.exists(caminho):
            return caminho
    raise FileNotFoundError(
        "Nenhum arquivo de dados encontrado em 'dados/'. "
        "Coloque 'moradores.csv' (completo) ou use 'moradores_parcial.csv'."
    )


def _contar_linhas(caminho):
    """Conta rapidamente quantas linhas de dados o arquivo tem (sem o cabeçalho)."""
    with open(caminho, encoding="utf-8-sig") as arquivo:
        total = sum(1 for _ in arquivo)
    return max(total - 1, 1)


def carregar_moradores(caminho, callback_progresso=None):
    """Lê o CSV da PDAD em blocos, informando o progresso (0 a 1) via callback."""
    total = _contar_linhas(caminho)
    blocos = []
    lidas = 0
    leitor = pd.read_csv(
        caminho,
        sep=";",                 # a PDAD usa ponto e vírgula como separador
        encoding="utf-8-sig",    # o arquivo tem BOM (marca de ordem de bytes)
        usecols=COLUNAS,
        chunksize=5000,          # lê de 5000 em 5000 linhas para atualizar a barra
    )
    for bloco in leitor:
        blocos.append(bloco)
        lidas += len(bloco)
        if callback_progresso is not None:
            callback_progresso(min(lidas / total, 1.0))
    return pd.concat(blocos, ignore_index=True)


def remover_sentinelas(df, colunas):
    """Remove linhas com valores sentinela (99999/88888) nas colunas indicadas."""
    # REQUISITO 6: sem isso, médias e contagens ficariam distorcidas.
    limpo = df
    for coluna in colunas:
        limpo = limpo[~limpo[coluna].isin(SENTINELAS)]
    return limpo


def preparar(df):
    """Limpa os sentinelas e adiciona colunas legíveis (nome da RA, sexo e se é RA do DF)."""
    df = remover_sentinelas(df, COLUNAS)
    df = df.copy()
    df["ra_nome"] = df["localidade"].map(dic.MAPA_LOCALIDADE)
    df["sexo_nome"] = df["E03"].map(dic.MAPA_SEXO)
    df["eh_df"] = df["localidade"].isin(dic.RAS_DF)
    return df
