# Agente de Inteligência Global em Educação

Pipeline completo de coleta, tratamento, análise e geração de relatórios inteligentes sobre indicadores educacionais globais, utilizando o dataset **World Bank Education Statistics (EdStats)**.

Projeto desenvolvido para o desafio **Acelera AI** (Proteus Academy), integrando Python, n8n, OpenAI e agentes de programação (Codex).

---

## 📋 Sumário

- [Visão geral](#visão-geral)
- [Arquitetura do projeto](#arquitetura-do-projeto)
- [Estrutura de pastas](#estrutura-de-pastas)
- [Como executar](#como-executar)
- [Pipeline de dados (Python)](#pipeline-de-dados-python)
- [Workflow de orquestração (n8n)](#workflow-de-orquestração-n8n)
- [Camada de inteligência artificial](#camada-de-inteligência-artificial)
- [Skill reutilizável](#skill-reutilizável)
- [Como o Codex foi utilizado](#como-o-codex-foi-utilizado)
- [Decisões técnicas e tratamento de dados](#decisões-técnicas-e-tratamento-de-dados)
- [Limitações conhecidas](#limitações-conhecidas)
- [Vídeo de demonstração](#vídeo-de-demonstração)

---

## Visão geral

Este projeto constrói um **Agente Inteligente de Monitoramento Educacional**, capaz de:

- ✅ Consultar e processar dados do World Bank EdStats (dataset Kaggle)
- ✅ Tratar e enriquecer os dados com Python (limpeza, valores ausentes, agregações, rankings, cálculo de crescimento)
- ✅ Selecionar países e indicadores, comparar países e gerar rankings
- ✅ Utilizar IA (OpenAI) para produzir **análises executivas interpretativas** — não apenas descrição de números
- ✅ Orquestrar todo o fluxo com **n8n** (gatilho → script → IA → armazenamento)
- ✅ Disponibilizar uma **Skill reutilizável** que documenta boas práticas e pode ser usada por qualquer agente de IA
- ✅ Ser desenvolvido com apoio do **Codex** (OpenAI) como agente de programação

### Indicadores analisados

| Código | Indicador |
|---|---|
| `SE.PRM.CMPT.ZS` | Taxa de conclusão do ensino primário (%) |
| `SE.PRM.ENRR` | Taxa de matrícula bruta no ensino primário (%) |
| `SE.SEC.ENRR` | Taxa de matrícula bruta no ensino secundário (%) |
| `SE.PRM.TCHR` | Número de professores no ensino primário |
| `SE.XPD.PRIM.ZS` | Gasto em educação primária (% do gasto total em educação) |
| `SE.XPD.TOTL.GD.ZS` | Investimento público em educação (% do PIB) |

> O indicador de alfabetização de adultos (`SE.ADT.LITR.ZS`) foi avaliado e **descartado** por apresentar 89,6% de dados ausentes — decisão documentada na seção [Decisões técnicas](#decisões-técnicas-e-tratamento-de-dados).

---

## Arquitetura do projeto

```
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│  World Bank      │     │   Pipeline        │     │   Análises         │
│  EdStats (Kaggle) │ →  │   Python (ETL)    │ →  │   Rankings /        │
│  CSV bruto        │     │   pandas/numpy    │     │   Crescimento       │
└─────────────────┘     └──────────────────┘     └───────────────────┘
                                                              │
                                                              ▼
┌─────────────────┐     ┌──────────────────┐     ┌───────────────────┐
│   Relatório       │  ←  │   OpenAI          │  ←  │   Workflow n8n      │
│   final (.txt)     │     │   (GPT-5-mini)    │     │   (orquestração)    │
└─────────────────┘     └──────────────────┘     └───────────────────┘
```

---

## Estrutura de pastas

```
acelera-ai-educacao/
├── data/
│   ├── raw/                 # Dados originais do World Bank (EdStats), não versionados
│   └── processed/           # CSVs tratados e relatórios gerados
├── notebooks/
│   ├── 01_exploracao_inicial.ipynb
│   └── 02_analises_rankings.ipynb
├── scripts/
│   ├── analises.py          # Funções reutilizáveis (crescimento, ranking, comparação)
│   ├── test_analises.py     # Testes unitários (pytest)
│   └── gerar_insights.py    # Geração de análise executiva via OpenAI
├── n8n/
│   └── workflow.json        # Workflow exportado do n8n
├── skill/
│   ├── SKILL.md              # Skill reutilizável de análise educacional
│   └── README.md
├── docs/
├── .env                      # Chaves de API (não versionado)
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Como executar

### 1. Pré-requisitos

- Python 3.12+
- Node.js (para n8n e Codex CLI)
- Docker Desktop (para rodar o n8n)
- Conta na OpenAI Platform com créditos (para a API)

### 2. Configurar o ambiente Python

```bash
python -m venv venv
venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 3. Configurar variáveis de ambiente

Crie um arquivo `.env` na raiz do projeto:

```
OPENAI_API_KEY=sua_chave_aqui
```

### 4. Baixar o dataset

O dataset **World Bank EdStats** deve ser baixado do Kaggle e extraído em `data/raw/`:

```
https://www.kaggle.com/datasets/theworldbank/education-statistics
```

### 5. Rodar o pipeline de análise

Execute, em ordem, os notebooks em `notebooks/`:
1. `01_exploracao_inicial.ipynb` — exploração e primeira limpeza
2. `02_analises_rankings.ipynb` — cálculo de crescimento, rankings e comparações

### 6. Gerar a análise executiva com IA

```bash
python scripts/gerar_insights.py
```

O relatório é salvo em `data/processed/relatorio_ia.txt`.

### 7. Rodar o workflow n8n

```bash
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n -v /c/caminho/para/acelera-ai-educacao:/home/node/.n8n-files docker.n8n.io/n8nio/n8n
```

Acesse `http://localhost:5678`, importe o arquivo `n8n/workflow.json` e execute o workflow manualmente pelo botão "Execute workflow".

### 8. Rodar os testes

```bash
python -m pytest scripts/test_analises.py -v
```

---

## Pipeline de dados (Python)

O pipeline cobre as seguintes atividades obrigatórias em Python:

1. **Limpeza de dados**: remoção de colunas irrelevantes, tratamento do formato "largo" do CSV original (transformação para formato longo via `pandas.melt`)
2. **Tratamento de valores ausentes**: preenchimento por país usando `forward-fill` + `backward-fill` (reduzindo a ausência de dados de **55,1% para 11,4%**), sem inferir valores entre países diferentes
3. **Seleção de indicadores**: escolha criteriosa de 6 indicadores com boa cobertura de dados, descartando indicadores com cobertura insuficiente
4. **Agregações e cálculo de crescimento**: cálculo de crescimento absoluto e percentual por país e indicador, entre o primeiro e o último ano com dado válido
5. **Rankings**: função reutilizável `gerar_ranking()` para ordenar países por crescimento em qualquer indicador
6. **Comparação entre países**: função reutilizável `comparar_paises()` para comparar indicadores entre uma lista de países específicos
7. **Geração de CSV final**: dados tratados e analisados salvos em `data/processed/`

### Funções principais (`scripts/analises.py`)

```python
calcular_crescimento(df)              # Calcula crescimento absoluto/percentual por país+indicador
gerar_ranking(df, indicator_code)     # Gera ranking de países por crescimento
comparar_paises(df, lista_paises, indicator_code)  # Compara indicador entre países
```

---

## Workflow de orquestração (n8n)

O workflow (`n8n/workflow.json`) implementa o fluxo mínimo exigido pelo edital:

```
Gatilho Manual
  → Ler CSV do disco (Read/Write Files from Disk)
    → Extrair dados do CSV (Extract from File)
      → Processar e montar resumo por indicador (Code – JavaScript)
        → Chamar API da OpenAI (HTTP Request)
          → Extrair texto da análise (Code – JavaScript)
            → Converter para arquivo (Convert to File)
              → Salvar relatório em disco (Read/Write Files from Disk)
```

**Nota técnica:** a lógica de processamento dentro do n8n foi implementada em JavaScript (nó `Code`), já que a versão utilizada do n8n não possuía um runtime Python configurado internamente. Isso não compromete o requisito de uso de Python do edital, que já está integralmente cumprido no pipeline de dados (`scripts/` e `notebooks/`), fora do n8n.

---

## Camada de inteligência artificial

A análise gerada pela OpenAI (modelo `gpt-5-mini`) **não se limita a resumir números** — o prompt foi desenhado para produzir interpretação analítica real, cobrindo:

- Quais países mais evoluíram em cada indicador
- Quais estagnaram ou regrediram
- Quais apresentam maior investimento em educação
- Possíveis explicações para as tendências observadas (contexto histórico, políticas públicas, fatores demográficos)
- Recomendações práticas e acionáveis

Exemplo de trecho da análise gerada (dataset real, 1990–2017):

> *"Países como Afeganistão, Etiópia, Níger, Burkina e Mali mostram saltos substanciais em matrícula primária/secundária, taxa de conclusão e número de professores. Isso indica esforços coordenados (...) Risco/limitação: a expansão rápida frequentemente gera deficiências na formação docente, infraestrutura e insumos pedagógicos."*

O relatório completo gerado está disponível em `data/processed/relatorio_ia.txt` (via script Python) e `data/processed/relatorio_n8n.txt` (via workflow n8n).

---

## Skill reutilizável

A Skill deste projeto (`skill/SKILL.md`) documenta, de forma reutilizável por qualquer agente de IA, como gerar análises padronizadas sobre os dados educacionais — incluindo os indicadores disponíveis, as funções prontas para uso e, principalmente, **as boas práticas e armadilhas descobertas durante o desenvolvimento** (filtro de países reais, tratamento de outliers, etc.).

A Skill foi testada na prática: o Codex a utilizou para gerar um ranking de investimento em educação (`data/processed/ranking_investimento.csv`), seguindo corretamente todas as regras documentadas, sem necessidade de reexplicação manual.

---

## Como o Codex foi utilizado

O **Codex** (agente de programação da OpenAI, via CLI) foi utilizado ao longo de todo o desenvolvimento para acelerar tarefas técnicas:

| Tarefa | Descrição |
|---|---|
| **Docstrings** | Revisão e padronização das docstrings das funções de análise, seguindo o padrão Google Style |
| **Refatoração** | Extração das funções de análise do notebook para um módulo reutilizável (`scripts/analises.py`), permitindo reuso tanto nos notebooks quanto no workflow n8n |
| **Criação de testes** | Geração de 7 testes unitários (`scripts/test_analises.py`) cobrindo as funções de cálculo de crescimento, ranking e comparação |
| **Criação de script** | Desenvolvimento do script `scripts/gerar_insights.py`, que monta o resumo dos dados e chama a API da OpenAI para gerar a análise executiva |
| **Uso da Skill** | Execução de uma tarefa real (geração de ranking) seguindo as instruções documentadas na Skill do projeto, validando sua reutilização |

Em todas as tarefas, o Codex validou o próprio trabalho antes de reportar conclusão — rodando os testes automatizados (`pytest`) e verificando a integridade dos arquivos alterados (ex: validação de JSON do notebook após edição).

---

## Decisões técnicas e tratamento de dados

Durante o desenvolvimento, foram tomadas decisões técnicas importantes, documentadas aqui para transparência:

### 1. Filtro de países "de verdade"
O dataset original inclui, na mesma coluna de países, tanto países reais quanto **agrupamentos regionais** (ex: "Arab World", "European Union", "World"). A distinção foi feita usando a coluna `Income Group` do arquivo `EdStatsCountry.csv`: agrupamentos não possuem esse campo preenchido, enquanto países reais sempre têm. Essa regra reduziu 241 registros para 214 países válidos (com uma exceção conhecida: Gibraltar, um território real classificado incorretamente como agrupamento por essa regra).

### 2. Tratamento de valores ausentes
Aplicado `forward-fill` + `backward-fill` **por país e indicador**, nunca inferindo valores entre países diferentes. Essa técnica reduziu a ausência de dados de 55,1% para 11,4%.

### 3. Correção de outlier de escala (Tuvalu)
Identificado um erro de dado no indicador de investimento público em educação (`SE.XPD.TOTL.GD.ZS`) para Tuvalu: valores de **3.730.834% do PIB** entre 1997–2017 — fisicamente impossível. A causa raiz foi um provável erro de escala na fonte original, amplificado pelo preenchimento `ffill`. Foi aplicado um filtro de sanidade (valores de % do PIB não podem ultrapassar 100%), preservando casos extremos, porém plausíveis, como o Zimbábue durante o período de hiperinflação (valores de até 44% do PIB).

### 4. Remoção do indicador de alfabetização
O indicador `SE.ADT.LITR.ZS` (alfabetização de adultos) foi avaliado e removido da análise principal por apresentar 89,6% de dados ausentes — cobertura insuficiente para gerar rankings confiáveis.

### 5. Período de análise
Definido o intervalo de 1990 a 2017 para as análises de crescimento, já que o dataset não possui dados anuais completos fora desse intervalo (após 2017, o World Bank disponibiliza apenas projeções esparsas, de 5 em 5 anos).

---

## Limitações conhecidas

- Dados anuais confiáveis cobrem o período de 1990 a 2017
- Indicadores baseados em pesquisas domiciliares específicas (DHS, MICS, PIAAC) foram descartados por baixa cobertura de países
- Não foram incluídos indicadores de proficiência em leitura/PISA por ausência de série padronizada e comparável entre países no dataset utilizado
- O runtime Python não estava disponível dentro do container n8n utilizado; o processamento dentro do workflow foi implementado em JavaScript

---

## Vídeo de demonstração

🔗 [Link do vídeo no YouTube] — *(adicionar aqui após a gravação)*

---

## Autoria

Projeto desenvolvido por **Jéssica Line Mendes Gomes** para o desafio Acelera AI (Proteus Academy), com apoio de ferramentas de IA (OpenAI Codex e ChatGPT/Claude) ao longo do desenvolvimento.
