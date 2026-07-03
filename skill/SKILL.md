# Skill: Análise de Indicadores Educacionais (World Bank EdStats)

## Objetivo
Esta skill ensina um agente de IA a gerar análises padronizadas sobre indicadores 
educacionais do World Bank (dataset EdStats), reutilizando o pipeline de dados 
já processado neste projeto.

## Quando usar esta skill
Use esta skill sempre que precisar de:
- Um ranking de países por crescimento em um indicador educacional específico
- Uma comparação entre países específicos em um ou mais indicadores
- Uma análise interpretativa (não apenas descritiva) sobre tendências educacionais

## Pré-requisitos
- O arquivo `data/processed/crescimento_por_pais_indicador.csv` deve existir 
  (gerado pelo notebook `notebooks/02_analises_rankings.ipynb`)
- As funções reutilizáveis estão em `scripts/analises.py`

## Indicadores disponíveis
| Código | Descrição |
|---|---|
| SE.PRM.CMPT.ZS | Taxa de conclusão do ensino primário |
| SE.PRM.ENRR | Taxa de matrícula no ensino primário |
| SE.SEC.ENRR | Taxa de matrícula no ensino secundário |
| SE.PRM.TCHR | Número de professores no ensino primário |
| SE.XPD.PRIM.ZS | Gasto em educação primária (% do gasto total) |
| SE.XPD.TOTL.GD.ZS | Investimento público em educação (% do PIB) |

## Como usar: Gerar um ranking

```python
import pandas as pd
from scripts.analises import gerar_ranking

df_crescimento = pd.read_csv("data/processed/crescimento_por_pais_indicador.csv")
resultado = gerar_ranking(df_crescimento, "SE.SEC.ENRR", top_n=10)
```

## Como usar: Comparar países

```python
from scripts.analises import comparar_paises

resultado = comparar_paises(df_crescimento, ["Brazil", "Argentina", "Chile"], "SE.PRM.ENRR")
```

## Boas práticas aprendidas neste projeto (importante seguir)

1. **Sempre filtrar países de verdade**: o dataset original inclui agrupamentos 
   regionais (ex: "Arab World", "European Union") junto com países reais. 
   Use a coluna `Income Group` do arquivo `EdStatsCountry.csv` para filtrar 
   (agrupamentos têm esse campo vazio).

2. **Cuidado com outliers de escala**: já identificamos um erro de dado real 
   no indicador `SE.XPD.TOTL.GD.ZS` para Tuvalu (valor de milhões de % do PIB, 
   fisicamente impossível). Sempre aplique um filtro de sanidade 
   (ex: % do PIB não pode ultrapassar 100%) antes de gerar rankings.

3. **Tratamento de valores ausentes**: use preenchimento por país 
   (forward-fill + backward-fill), nunca infira valores entre países diferentes.

4. **Ao gerar análises com IA**: sempre peça interpretação (possíveis causas, 
   recomendações), não apenas descrição de números. Um bom prompt pede 
   explicitamente: quais evoluíram mais, quais estagnaram, possíveis explicações, 
   recomendações.

## Limitações conhecidas
- Dados anuais confiáveis vão de 1990 a 2017 (após isso, o World Bank só 
  disponibiliza projeções esparsas, de 5 em 5 anos)
- O indicador de alfabetização de adultos (SE.ADT.LITR.ZS) foi removido da 
  análise principal por ter 89,6% de dados ausentes