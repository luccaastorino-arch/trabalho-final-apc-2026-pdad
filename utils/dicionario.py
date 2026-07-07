"""Mapeamentos de códigos para rótulos, extraídos do dicionário oficial da PDAD 2024.

Fonte: dados/dicionario_de_variaveis_pdad_2024.xlsx
  - localidade  -> aba "anexo_1"
  - escolaridade, id_genero, E03 (sexo) -> aba "moradores"
Manter os valores aqui (em vez de ler o .xlsx em tempo de execução) deixa o
sistema mais simples e sem dependências extras para rodar.
"""

# --- Regiões Administrativas do DF (localidade 5301..5336) -------------------
# O código é "53" (UF do DF) + o número da RA. 5336 = "Área Rural" é um
# agregado novo em 2024 (primeira edição da PDAD a cobrir a zona rural).
RAS_DF = {
    5301: "Plano Piloto",
    5302: "Gama",
    5303: "Taguatinga",
    5304: "Brazlândia",
    5305: "Sobradinho",
    5306: "Planaltina",
    5307: "Paranoá",
    5308: "Núcleo Bandeirante",
    5309: "Ceilândia",
    5310: "Guará",
    5311: "Cruzeiro",
    5312: "Samambaia",
    5313: "Santa Maria",
    5314: "São Sebastião",
    5315: "Recanto das Emas",
    5316: "Lago Sul",
    5317: "Riacho Fundo",
    5318: "Lago Norte",
    5319: "Candangolândia",
    5320: "Águas Claras",
    5321: "Riacho Fundo II",
    5322: "Sudoeste e Octogonal",
    5323: "Varjão",
    5324: "Park Way",
    5325: "SCIA",
    5326: "Sobradinho II",
    5327: "Jardim Botânico",
    5328: "Itapoã",
    5329: "SIA",
    5330: "Vicente Pires",
    5331: "Fercal",
    5332: "Sol Nascente / Pôr do Sol",
    5333: "Arniqueira",
    5334: "Arapoanga",
    5335: "Água Quente",
    5336: "Área Rural",
}

# --- Municípios de Goiás no entorno (localidade 5241..5252) ------------------
# Fazem parte da amostra "Ampliada" da PDAD, mas NÃO são Regiões
# Administrativas do DF. Por isso ficam separados das RAs.
MUNICIPIOS_GO = {
    5241: "Águas Lindas de Goiás (GO)",
    5242: "Alexânia (GO)",
    5243: "Cidade Ocidental (GO)",
    5244: "Cristalina (GO)",
    5245: "Cocalzinho de Goiás (GO)",
    5246: "Formosa (GO)",
    5247: "Luziânia (GO)",
    5248: "Novo Gama (GO)",
    5249: "Padre Bernardo (GO)",
    5250: "Planaltina de Goiás (GO)",
    5251: "Santo Antônio do Descoberto (GO)",
    5252: "Valparaíso de Goiás (GO)",
}

# Dicionário único com todas as localidades (RAs do DF + municípios de GO).
MAPA_LOCALIDADE = {**RAS_DF, **MUNICIPIOS_GO}

# --- Escolaridade (variável derivada "Nível de instrução mais elevado") ------
# A escala é ORDINAL de 1 a 7. O código 8 ("Sem classificação") NÃO é o topo
# da escala: é um valor residual (não classificado, geralmente crianças) e
# deve ser tratado como dado ausente nas análises de escolaridade.
MAPA_ESCOLARIDADE = {
    1: "Sem instrução",
    2: "Fundamental incompleto",
    3: "Fundamental completo",
    4: "Médio incompleto",
    5: "Médio completo",
    6: "Superior incompleto",
    7: "Superior completo",
    8: "Sem classificação",
}

# Ordem dos níveis válidos usados nos gráficos e estatísticas (1..7).
NIVEIS_ESCOLARIDADE = [1, 2, 3, 4, 5, 6, 7]
ESCOLARIDADE_SEM_CLASSE = 8       # tratado como "não informado"

SUPERIOR_COMPLETO = 7             # código de "Superior completo"
AO_MENOS_MEDIO = (5, 6, 7)        # concluiu ao menos o ensino médio
SEM_INSTRUCAO = 1                 # nenhuma instrução formal

# Anos de estudo APROXIMADOS por nível (para calcular uma média comparável).
# São valores aproximados, apenas para dar uma noção resumida em um número.
ANOS_ESTUDO = {1: 0, 2: 4, 3: 9, 4: 10, 5: 12, 6: 14, 7: 16}

# --- Sexo (variável E03) -----------------------------------------------------
# Usamos E03 (sexo) para a comparação por gênero por estar disponível para
# TODA a amostra (sem sentinelas). A variável id_genero (identidade de gênero,
# citada no enunciado) só foi coletada para maiores de 18 anos e é fortemente
# concentrada em "Cisgênero", sendo menos informativa para este recorte.
MAPA_SEXO = {1: "Masculino", 2: "Feminino"}


def nome_localidade(codigo):
    """Devolve o nome legível de uma localidade a partir do código numérico."""
    return MAPA_LOCALIDADE.get(codigo, f"Localidade {codigo}")


def eh_ra_df(codigo):
    """Informa se o código de localidade é uma Região Administrativa do DF."""
    return codigo in RAS_DF
