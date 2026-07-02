"""Gera um relatório executivo com IA a partir dos dados de crescimento."""

import os
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv


ARQUIVO_ENTRADA = Path("data/processed/crescimento_por_pais_indicador.csv")
ARQUIVO_SAIDA = Path("data/processed/relatorio_ia.txt")
MODELO = "gpt-5-mini"


def carregar_dados(caminho=ARQUIVO_ENTRADA):
    """Carrega os dados processados de crescimento por país e indicador."""
    return pd.read_csv(caminho)


def _formatar_linha_pais(linha):
    return (
        f"- {linha['Country Name']}: "
        f"{linha['Crescimento_Percentual']:.2f}% "
        f"({linha['Valor_Inicial']:.2f} em {linha['Ano_Inicial']:.0f} -> "
        f"{linha['Valor_Final']:.2f} em {linha['Ano_Final']:.0f})"
    )


def montar_resumo_compacto(df_crescimento, top_n=5):
    """Monta um resumo textual compacto com destaques por indicador."""
    partes = [
        "Resumo dos principais destaques por indicador.",
        "Cada linha mostra crescimento percentual e evolução valor inicial -> final.",
    ]

    dados_validos = df_crescimento.dropna(subset=["Crescimento_Percentual"]).copy()

    for (indicator_code, indicator_name), grupo in dados_validos.groupby(
        ["Indicator Code", "Indicator Name"],
        sort=True,
    ):
        grupo_ordenado = grupo.sort_values("Crescimento_Percentual", ascending=False)
        maiores_crescimentos = grupo_ordenado.head(top_n)
        menores_crescimentos = grupo_ordenado.tail(top_n).sort_values(
            "Crescimento_Percentual",
            ascending=True,
        )

        partes.append(f"\nIndicador: {indicator_name} ({indicator_code})")
        partes.append("Top 5 países que mais cresceram:")
        partes.extend(_formatar_linha_pais(linha) for _, linha in maiores_crescimentos.iterrows())
        partes.append("Top 5 países que menos cresceram ou mais caíram:")
        partes.extend(_formatar_linha_pais(linha) for _, linha in menores_crescimentos.iterrows())

    return "\n".join(partes)


def gerar_prompt(resumo):
    """Cria o prompt enviado ao modelo de IA."""
    return f"""
Você é um analista executivo de educação e políticas públicas.

Com base no resumo abaixo, produza uma análise interpretativa em português,
clara e objetiva, cobrindo:

1. Quais países mais evoluíram nos indicadores educacionais.
2. Quais países parecem estagnados ou em queda.
3. Quais países demonstram maior investimento em educação, considerando os
   indicadores de gasto e os valores finais informados.
4. Possíveis explicações para os padrões observados, deixando claro quando
   forem hipóteses e não fatos comprovados pelos dados.
5. Recomendações práticas para formuladores de políticas públicas.

Evite repetir todos os rankings. Priorize síntese executiva, comparações entre
indicadores e recomendações acionáveis.

Resumo dos dados:
{resumo}
""".strip()


def chamar_openai(prompt):
    """Chama a API da OpenAI e retorna o texto gerado."""
    from openai import OpenAI

    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Defina a variável de ambiente OPENAI_API_KEY antes de executar o script.")

    client = OpenAI(api_key=api_key)

    resposta = client.responses.create(
        model=MODELO,
        input=prompt,
        max_output_tokens=3000,
    )

    return resposta.output_text


def salvar_relatorio(texto, caminho=ARQUIVO_SAIDA):
    """Salva o relatório gerado em arquivo de texto."""
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")


def main():
    """Executa o fluxo completo de geração do relatório com IA."""
    df_crescimento = carregar_dados()
    resumo = montar_resumo_compacto(df_crescimento)
    prompt = gerar_prompt(resumo)
    relatorio = chamar_openai(prompt)
    salvar_relatorio(relatorio)
    print(f"Relatório salvo em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
