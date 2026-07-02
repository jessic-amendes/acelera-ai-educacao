import pandas as pd
import pytest

from scripts.analises import calcular_crescimento, comparar_paises, gerar_ranking


def _df_crescimento():
    return pd.DataFrame({
        "Country Name": ["Brazil", "Argentina", "Chile", "Peru"],
        "Indicator Name": ["Indicador A", "Indicador A", "Indicador A", "Indicador B"],
        "Indicator Code": ["IND_A", "IND_A", "IND_A", "IND_B"],
        "Valor_Inicial": [10.0, 5.0, 20.0, 2.0],
        "Valor_Final": [15.0, 15.0, 10.0, 6.0],
        "Crescimento_Percentual": [50.0, 200.0, -50.0, 200.0],
    })


def test_calcular_crescimento_usa_primeiro_e_ultimo_valor_valido():
    grupo = pd.DataFrame({
        "Ano": [2000, 2001, 2002, 2003],
        "Valor": [10.0, None, 15.0, 20.0],
    })

    resultado = calcular_crescimento(grupo)

    assert resultado["Valor_Inicial"] == 10.0
    assert resultado["Ano_Inicial"] == 2000
    assert resultado["Valor_Final"] == 20.0
    assert resultado["Ano_Final"] == 2003
    assert resultado["Crescimento_Absoluto"] == 10.0
    assert resultado["Crescimento_Percentual"] == 100.0


def test_calcular_crescimento_retorna_none_sem_valores_validos():
    grupo = pd.DataFrame({"Ano": [2000, 2001], "Valor": [None, None]})

    resultado = calcular_crescimento(grupo)

    assert resultado.isna().all()


def test_gerar_ranking_ordena_por_maior_crescimento(capsys):
    resultado = gerar_ranking(_df_crescimento(), "IND_A", top_n=2)

    assert resultado["Country Name"].tolist() == ["Argentina", "Brazil"]
    assert resultado["Crescimento_Percentual"].tolist() == [200.0, 50.0]
    assert "Ranking: Indicador A" in capsys.readouterr().out


def test_gerar_ranking_ordena_por_menor_crescimento():
    resultado = gerar_ranking(_df_crescimento(), "IND_A", top_n=2, crescente=True)

    assert resultado["Country Name"].tolist() == ["Chile", "Brazil"]


def test_gerar_ranking_falha_para_indicador_inexistente():
    with pytest.raises(IndexError):
        gerar_ranking(_df_crescimento(), "IND_INEXISTENTE")


def test_comparar_paises_filtra_e_ordena_por_crescimento(capsys):
    resultado = comparar_paises(_df_crescimento(), ["Brazil", "Chile"], "IND_A")

    assert resultado["Country Name"].tolist() == ["Brazil", "Chile"]
    assert resultado["Crescimento_Percentual"].tolist() == [50.0, -50.0]
    assert "Comparação: Indicador A" in capsys.readouterr().out


def test_comparar_paises_retorna_dataframe_vazio_sem_correspondencias():
    resultado = comparar_paises(_df_crescimento(), ["Uruguay"], "IND_A")

    assert resultado.empty
    assert resultado.columns.tolist() == [
        "Country Name",
        "Valor_Inicial",
        "Valor_Final",
        "Crescimento_Percentual",
    ]
