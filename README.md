# 🏥 SaúdeMoz Analytics

Plataforma de análise de indicadores de saúde pública de Moçambique, com pipeline ETL automatizado e dashboard interactivo.

## 🚀 Dashboard

👉 **[Ver Dashboard](https://francisco-muiambo-jr.github.io/saudemoz-analytics/04_dashboard/dashboard.html)**

## 📋 Sobre o Projecto

Pipeline end-to-end que extrai dados reais do World Bank via API, transforma e carrega numa base de dados PostgreSQL na cloud, e gera um dashboard HTML profissional com Plotly.

## 🏗️ Arquitectura
World Bank API → Extract → Transform → Load → PostgreSQL → Dashboard HTML

## 📊 Indicadores Analisados

| Indicador | Código |
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
| Dashboard | Plotly, HTML, CSS |
| Versionamento | Git, GitHub |

## 📁 Estrutura do Projecto
saudemoz-analytics/
├── 01_pipeline/
│   ├── extract.py      # Extracção via API do World Bank
│   ├── transform.py    # Limpeza e validação dos dados
│   └── load.py         # Carregamento com UPSERT no PostgreSQL
├── 02_database/        # Scripts SQL
├── 03_queries/         # Queries analíticas
├── 04_dashboard/
│   ├── app.py                  # Dashboard Streamlit
│   └── generate_dashboard.py   # Gerador HTML com Plotly
├── pipeline.py         # Orquestrador ETL
└── requirements.txt

## 🔍 Conceitos de Data Engineering Aplicados

- **Pipeline ETL** — Extract, Transform, Load automatizado
- **UPSERT** — inserção sem duplicação de dados
- **Data Quality** — validação de valores por indicador
- **API Integration** — ingestão de dados em tempo real
- **Cloud Database** — PostgreSQL serverless no Neon

## 👤 Autor

**Francisco Salomão Muiambo Júnior**  
Analista de Dados  
📍 Maputo, Moçambique

[![GitHub](https://img.shields.io/badge/GitHub-Francisco--Muiambo--JR-black?logo=github)](https://github.com/Francisco-Muiambo-JR)