# ============================================================
# Ficheiro: dags/saudemoz_etl_dag.py
# Projecto: SaúdeMoz Analytics
# Descrição: DAG que automatiza o pipeline ETL mensal
#            de indicadores de saúde de Moçambique
# ============================================================

import os
import sys
import logging
from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator

# ============================================================
# CONFIGURAÇÃO DO LOGGER
# O logger regista mensagens no sistema de logs do Airflow
# Permite ver o que aconteceu em cada execução
# ============================================================

log = logging.getLogger(__name__)

# ============================================================
# CONFIGURAÇÕES PADRÃO DO DAG
# Estas configurações aplicam-se a todas as tasks
# ============================================================

default_args = {
    "owner": "francisco",           # dono do DAG
    "depends_on_past": False,       # não depende de execuções anteriores
    "email_on_failure": False,      # não envia email em caso de falha
    "email_on_retry": False,        # não envia email em caso de retry
    "retries": 3,                   # tenta 3 vezes em caso de falha
    "retry_delay": timedelta(minutes=5),  # espera 5 minutos entre tentativas
}

# ============================================================
# DEFINIÇÃO DO DAG
# ============================================================

dag = DAG(
    dag_id="saudemoz_etl_mensal",
    description="Pipeline ETL mensal de indicadores de saúde de Moçambique",
    default_args=default_args,
    schedule_interval="0 6 1 * *",  # dia 1 de cada mês às 6h da manhã
    start_date=datetime(2024, 1, 1),
    catchup=False,                  # não corre execuções passadas em falta
    tags=["saudemoz", "etl", "saude", "mocambique"],
)

# ============================================================
# TASK 1 — EXTRACT
# Vai buscar os dados à API do World Bank
# ============================================================

def task_extract(**context):
    log.info("=" * 50)
    log.info("TASK 1 — EXTRACÇÃO DE DADOS")
    log.info("Fonte: World Bank API")
    log.info("País: Moçambique (MZ)")
    log.info("=" * 50)

    import requests
    import pandas as pd
    import time

    INDICADORES = {
        "SP.DYN.LE00.IN":    "Expectativa de Vida ao Nascer (anos)",
        "SP.DYN.IMRT.IN":    "Taxa de Mortalidade Infantil (por 1000)",
        "SH.STA.MMRT":       "Taxa de Mortalidade Materna (por 100k)",
        "SH.H2O.BASW.ZS":    "Acesso a Agua Potavel (% populacao)",
        "SH.STA.BASS.ZS":    "Acesso a Saneamento Basico (% populacao)",
        "SH.IMM.IDPT":       "Cobertura Vacinal DTP (% criancas)",
        "SH.DYN.AIDS.ZS":    "Prevalencia de HIV (% adultos)",
        "SH.MED.PHYS.ZS":    "Medicos por 1000 habitantes",
        "SH.XPD.CHEX.GD.ZS": "Despesa em Saude (% PIB)",
        "SP.POP.TOTL":       "Populacao Total"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    all_data = []

    for code, name in INDICADORES.items():
        url = (
            f"http://api.worldbank.org/v2/country/MZ"
            f"/indicator/{code}"
            f"?format=json&per_page=100&date=2000:2023"
        )

        try:
            response = requests.get(url, timeout=30, headers=headers)

            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 1 and data[1]:
                    for item in data[1]:
                        all_data.append({
                            "country_code":   "MZ",
                            "country_name":   "Mozambique",
                            "indicator_code": code,
                            "indicator_name": name,
                            "year":           int(item["date"]),
                            "value":          item["value"]
                        })
                    log.info(f"OK: {name} — {len(data[1])} registos")
                else:
                    log.warning(f"Sem dados: {name}")
            else:
                log.error(f"Erro {response.status_code}: {name}")

        except Exception as e:
            log.error(f"Erro ao extrair {name}: {e}")

        time.sleep(0.5)

    if not all_data:
        raise ValueError("Nenhum dado extraído — pipeline interrompido")

    df = pd.DataFrame(all_data)
    log.info(f"Total extraído: {len(df)} registos")

    # Guarda os dados no XCom para passar à próxima task
    # XCom é o mecanismo do Airflow para partilhar dados entre tasks
    context["ti"].xcom_push(key="raw_data", value=df.to_json())
    log.info("Dados guardados no XCom")


# ============================================================
# TASK 2 — TRANSFORM
# Limpa e valida os dados extraídos
# ============================================================

def task_transform(**context):
    log.info("=" * 50)
    log.info("TASK 2 — TRANSFORMAÇÃO DE DADOS")
    log.info("=" * 50)

    import pandas as pd

    # Recebe os dados da task anterior via XCom
    raw_json = context["ti"].xcom_pull(key="raw_data", task_ids="extract")

    if not raw_json:
        raise ValueError("Sem dados do XCom — extract falhou?")

    df = pd.read_json(raw_json)
    registos_iniciais = len(df)
    log.info(f"Registos recebidos: {registos_iniciais}")

    # Remove nulos
    df = df.dropna(subset=["value"])
    log.info(f"Após remover nulos: {len(df)} registos")

    # Converte tipos
    df["year"]  = df["year"].astype(int)
    df["value"] = df["value"].astype(float).round(3)

    # Adiciona timestamp
    df["processed_at"] = pd.Timestamp.now().isoformat()

    log.info(f"Registos após transformação: {len(df)}")

    # Passa os dados para a próxima task
    context["ti"].xcom_push(key="clean_data", value=df.to_json())
    log.info("Dados limpos guardados no XCom")


# ============================================================
# TASK 3 — LOAD
# Carrega os dados na base de dados PostgreSQL
# ============================================================

def task_load(**context):
    log.info("=" * 50)
    log.info("TASK 3 — CARREGAMENTO NA BASE DE DADOS")
    log.info("=" * 50)

    import pandas as pd
    from sqlalchemy import create_engine, text

    # Recebe os dados da task anterior via XCom
    clean_json = context["ti"].xcom_pull(key="clean_data", task_ids="transform")

    if not clean_json:
        raise ValueError("Sem dados do XCom — transform falhou?")

    df = pd.read_json(clean_json)

    # Ligação à base de dados
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL não definida")

    engine = create_engine(database_url)

    # Cria tabela se não existir
    create_sql = """
    CREATE TABLE IF NOT EXISTS health_indicators (
        id              SERIAL PRIMARY KEY,
        country_code    VARCHAR(10)  NOT NULL,
        country_name    VARCHAR(100) NOT NULL,
        indicator_code  VARCHAR(50)  NOT NULL,
        indicator_name  VARCHAR(200) NOT NULL,
        year            SMALLINT     NOT NULL,
        value           NUMERIC(12,3),
        processed_at    TIMESTAMPTZ,
        CONSTRAINT uq_health_indicator
            UNIQUE (country_code, indicator_code, year)
    );
    """

    upsert_sql = """
    INSERT INTO health_indicators
        (country_code, country_name, indicator_code,
         indicator_name, year, value, processed_at)
    VALUES
        (:country_code, :country_name, :indicator_code,
         :indicator_name, :year, :value, :processed_at)
    ON CONFLICT (country_code, indicator_code, year)
    DO UPDATE SET
        value        = EXCLUDED.value,
        processed_at = EXCLUDED.processed_at
    """

    inseridos = 0
    erros = 0

    with engine.connect() as conn:
        conn.execute(text(create_sql))
        conn.commit()

        for _, row in df.iterrows():
            try:
                conn.execute(text(upsert_sql), {
                    "country_code":   row["country_code"],
                    "country_name":   row["country_name"],
                    "indicator_code": row["indicator_code"],
                    "indicator_name": row["indicator_name"],
                    "year":           int(row["year"]),
                    "value":          float(row["value"]),
                    "processed_at":   row["processed_at"]
                })
                inseridos += 1
            except Exception as e:
                erros += 1
                log.error(f"Erro: {e}")

        conn.commit()

    log.info(f"Registos carregados: {inseridos}")
    log.info(f"Erros: {erros}")
    log.info("PIPELINE CONCLUÍDO COM SUCESSO")


# ============================================================
# DEFINIÇÃO DAS TASKS E DEPENDÊNCIAS
# ============================================================

t1_extract = PythonOperator(
    task_id="extract",
    python_callable=task_extract,
    dag=dag,
)

t2_transform = PythonOperator(
    task_id="transform",
    python_callable=task_transform,
    dag=dag,
)

t3_load = PythonOperator(
    task_id="load",
    python_callable=task_load,
    dag=dag,
)

# Define a ordem: extract → transform → load
t1_extract >> t2_transform >> t3_load