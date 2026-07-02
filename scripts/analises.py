"""Funções auxiliares para análises de crescimento e rankings educacionais."""

import pandas as pd


def calcular_crescimento(grupo):
    """Calcula o crescimento de um indicador em um grupo temporal.

    Considera apenas registros com valor válido na coluna ``Valor`` e usa o
    primeiro e o último registro disponível do grupo para calcular as variações.
    O grupo deve estar previamente ordenado por ano para que o resultado reflita
    corretamente o período analisado.

    Args:
        grupo (pandas.DataFrame): Dados de um país e indicador, contendo as
            colunas ``Ano`` e ``Valor``.

    Returns:
        pandas.Series: Série com valor e ano iniciais, valor e ano finais,
        crescimento absoluto e crescimento percentual. Retorna valores ``None``
        quando o grupo não possui valores válidos; o crescimento percentual
        também é ``None`` quando o valor inicial é zero.
    """
    grupo_valido = grupo.dropna(subset=["Valor"])
    if grupo_valido.empty:
        return pd.Series({
            "Valor_Inicial": None,
            "Ano_Inicial": None,
            "Valor_Final": None,
            "Ano_Final": None,
            "Crescimento_Absoluto": None,
            "Crescimento_Percentual": None,
        })

    primeiro = grupo_valido.iloc[0]
    ultimo = grupo_valido.iloc[-1]

    crescimento_absoluto = ultimo["Valor"] - primeiro["Valor"]
    if primeiro["Valor"] != 0:
        crescimento_percentual = (crescimento_absoluto / primeiro["Valor"]) * 100
    else:
        crescimento_percentual = None

    return pd.Series({
        "Valor_Inicial": primeiro["Valor"],
        "Ano_Inicial": primeiro["Ano"],
        "Valor_Final": ultimo["Valor"],
        "Ano_Final": ultimo["Ano"],
        "Crescimento_Absoluto": crescimento_absoluto,
        "Crescimento_Percentual": crescimento_percentual,
    })


def gerar_ranking(df_crescimento, indicator_code, top_n=10, crescente=False):
    """Gera um ranking de países por crescimento percentual de um indicador.

    Filtra ``df_crescimento`` pelo código do indicador, ordena os países pelo
    crescimento percentual e retorna as primeiras linhas do ranking. Também
    imprime o nome do indicador e o sentido da ordenação.

    Args:
        df_crescimento (pandas.DataFrame): Dados de crescimento por país e
            indicador.
        indicator_code (str): Código do indicador a ser ranqueado, como
            ``"SE.SEC.ENRR"``.
        top_n (int, optional): Quantidade de países a retornar. O padrão é 10.
        crescente (bool, optional): Se ``True``, ordena do menor para o maior
            crescimento percentual. Se ``False``, ordena do maior para o menor.
            O padrão é ``False``.

    Returns:
        pandas.DataFrame: Ranking com as colunas ``Country Name``,
        ``Valor_Inicial``, ``Valor_Final`` e ``Crescimento_Percentual``.

    Raises:
        IndexError: Se ``indicator_code`` não existir em ``df_crescimento``.
    """
    dados = df_crescimento[df_crescimento["Indicator Code"] == indicator_code]
    dados = dados.sort_values("Crescimento_Percentual", ascending=crescente)

    nome_indicador = dados["Indicator Name"].iloc[0]
    print(f"Ranking: {nome_indicador}")
    print(f"({'Menores crescimentos' if crescente else 'Maiores crescimentos'})\n")

    return dados[
        ["Country Name", "Valor_Inicial", "Valor_Final", "Crescimento_Percentual"]
    ].head(top_n)


def comparar_paises(df_crescimento, lista_paises, indicator_code):
    """Compara o crescimento percentual de um indicador entre países.

    Filtra ``df_crescimento`` pelos países informados e pelo código do indicador.
    O resultado é ordenado do maior para o menor crescimento percentual e a
    função imprime o nome do indicador comparado.

    Args:
        df_crescimento (pandas.DataFrame): Dados de crescimento por país e
            indicador.
        lista_paises (list[str]): Nomes dos países a comparar, como
            ``["Brazil", "Argentina"]``.
        indicator_code (str): Código do indicador a comparar, como
            ``"SE.PRM.ENRR"``.

    Returns:
        pandas.DataFrame: Dados filtrados com as colunas ``Country Name``,
        ``Valor_Inicial``, ``Valor_Final`` e ``Crescimento_Percentual``,
        ordenados por ``Crescimento_Percentual`` em ordem decrescente. Retorna
        um DataFrame vazio quando nenhum país ou indicador correspondente é
        encontrado.
    """
    dados = df_crescimento[
        (df_crescimento["Country Name"].isin(lista_paises))
        & (df_crescimento["Indicator Code"] == indicator_code)
    ]

    nome_indicador = dados["Indicator Name"].iloc[0] if not dados.empty else "N/A"
    print(f"Comparação: {nome_indicador}\n")

    return dados[
        ["Country Name", "Valor_Inicial", "Valor_Final", "Crescimento_Percentual"]
    ].sort_values("Crescimento_Percentual", ascending=False)
