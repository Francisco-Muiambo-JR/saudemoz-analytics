# 🏥 SaúdeMoz Analytics

Plataforma de análise de indicadores de saúde pública de Moçambique com pipeline ETL automatizado, orquestração com Apache Airflow e dashboard interactivo.

## 🚀 Dashboard ao Vivo

👉 **[Ver Dashboard](https://francisco-muiambo-jr.github.io/saudemoz-analytics/04_dashboard/dashboard.html)**

## 📋 Sobre o Projecto

Pipeline end-to-end que extrai dados reais do World Bank via API, transforma, valida e carrega automaticamente numa base de dados PostgreSQL na cloud. O pipeline corre mensalmente de forma autónoma orquestrado pelo Apache Airflow.

## 🏗️ Arquitectura
World Bank API → Extract → Transform → Load → PostgreSQL → Dashboard HTML

## 📊 Indicadores Analisados

| Indicador | Código API |
|---|---|
| Expectativa de vida ao nascer | SP.DYN.LE00.IN |
| Taxa de mortalidade infantil | SP.DYN.IMRT.IN |
| Taxa de mortalidade materna | SH.STA.MMRT |
| Acesso a água potável | SH.H2O.BASW.ZS |
| Acesso a saneamento básico | SH.STA.BASS.ZS |
| Cobertura vacinal DTP | SH.IMM.IDPT |
| Prevalência de HIV | SH.DYN.AIDS.ZS |
| Médicos por 1000 habitantes | SH.MED.PHYS.ZS |
| Despesa em saúde % PIB | SH.XPD.CHEX.GD.ZS |
| População total | SP.POP.TOTL |

## 🛠️ Tecnologias

| Camada | Tecnologia |
|---|---|
| Extracção | Python, requests, World Bank API |
| Transformação | pandas, validação de dados |
| Carregamento | SQLAlchemy, PostgreSQL, UPSERT |
| Base de dados cloud | Neon (PostgreSQL serverless) |
| Orquestração | Apache Airflow 2.9, Docker |
| Dashboard | Plotly, HTML, CSS |
| Deploy | GitHub Pages |
| Versionamento | Git, GitHub |

```
## 📁 Estrutura do Projecto
saudemoz-analytics/

├── 01_pipeline/

│   ├── extract.py          # Extracção via API do World Bank

│   ├── transform.py        # Limpeza e validação dos dados

│   └── load.py             # Carregamento com UPSERT no PostgreSQL

├── 02_database/            # Scripts SQL

├── 03_queries/             # Queries analíticas

├── 04_dashboard/

│   ├── generate_dashboard.py   # Gerador do dashboard HTML

│   └── dashboard.html          # Dashboard interactivo

├── dags/

│   └── saudemoz_etl_dag.py     # DAG do Apache Airflow

├── pipeline.py             # Orquestrador ETL manual

└── requirements.txt
```
## ⚙️ Pipeline ETL Automatizado

O pipeline é orquestrado pelo Apache Airflow com Docker e corre automaticamente no dia 1 de cada mês às 6h UTC.

### DAG — saudemoz_etl_mensal
extract → transform → load

| Task | Descrição |
|---|---|
| `extract` | Extrai 10 indicadores da API do World Bank |
| `transform` | Remove nulos, valida limites, converte tipos |
| `load` | UPSERT no PostgreSQL — sem duplicação |

**Configurações do DAG:**
- Schedule: `0 6 1 * *` — dia 1 de cada mês às 6h
- Retries: 3 tentativas com intervalo de 5 minutos
- XCom para partilha de dados entre tasks

## 🔍 Conceitos de Data Engineering Aplicados

- **Pipeline ETL** — Extract, Transform, Load automatizado
- **UPSERT** — inserção sem duplicação de dados
- **Data Quality** — validação de valores por indicador
- **API Integration** — ingestão de dados em tempo real
- **Workflow Orchestration** — Apache Airflow com DAGs
- **Containerização** — Docker e Docker Compose
- **Cloud Database** — PostgreSQL serverless no Neon

## 📈 Insights dos Dados

- Expectativa de vida subiu de 49.5 para 63.6 anos (+14.1 anos desde 2000)
- Mortalidade infantil reduziu de 147 para 44.9 por 1.000 nascimentos
- Acesso a água potável cresceu de 22% para 64.5% da população
- Despesa em saúde cresceu de 2.5% para 8.7% do PIB

## 👤 Autor

**Francisco Salomão Muiambo Júnior**  
Analista de Dados
📍 Maputo, Moçambique

[![GitHub](https://img.shields.io/badge/GitHub-Francisco--Muiambo--JR-black?logo=github)](https://github.com/Francisco-Muiambo-JR)

[![GitHub](https://img.shields.io/badge/GitHub-Francisco--Muiambo--JR-black?logo=github)](https://github.com/Francisco-Muiambo-JR)
