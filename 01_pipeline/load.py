# ============================================================
# Ficheiro: 01_pipeline/load.py
# Objectivo: Carregar os dados limpos na base de dados
# Padrão: ETL — fase Load
# Técnica: UPSERT — evita duplicação de dados
# ============================================================

import os
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# ============================================================
# FUNÇÃO: get_engine
# Objectivo: criar a ligação à base de dados
# ============================================================

def get_engine():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL não definida no ficheiro .env")
    return create_engine(url)


# ============================================================
# FUNÇÃO: create_table
# Objectivo: criar a tabela na base de dados se não existir
# Nota: IF NOT EXISTS garante que não dá erro se já existir
# ============================================================

def create_table(engine):
    
    sql = """
    CREATE TABLE IF NOT EXISTS health_indicators (
        id              SERIAL PRIMARY KEY,
        country_code    VARCHAR(10)  NOT NULL,
        country_name    VARCHAR(100) NOT NULL,
        indicator_code  VARCHAR(50)  NOT NULL,
        indicator_name  VARCHAR(200) NOT NULL,
        year            SMALLINT     NOT NULL,
        value           NUMERIC(12,3),
        processed_at    TIMESTAMPTZ,
        
        -- Constraint: combinação única de país, indicador e ano
        -- Isto é o que permite o UPSERT funcionar correctamente
        CONSTRAINT uq_health_indicator 
            UNIQUE (country_code, indicator_code, year)
    );
    """
    
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    
    print("Tabela health_indicators verificada/criada.")


# ============================================================
# FUNÇÃO: upsert_data
# Objectivo: inserir dados novos e actualizar os existentes
# Técnica: INSERT ... ON CONFLICT DO UPDATE (UPSERT)
# ============================================================

def upsert_data(engine, df):
    
    inseridos = 0
    actualizados = 0
    erros = 0
    
    sql = """
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
    
    with engine.connect() as conn:
        for _, row in df.iterrows():
            try:
                conn.execute(text(sql), {
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
                print(f"  ERRO na linha {_}: {e}")
        
        conn.commit()
    
    return inseridos, actualizados, erros


# ============================================================
# FUNÇÃO PRINCIPAL: load
# ============================================================

def load(df):
    
    print("=" * 50)
    print("FASE 3 — CARREGAMENTO NA BASE DE DADOS")
    print("=" * 50)
    
    engine = get_engine()
    
    # Passo 1: criar tabela
    create_table(engine)
    
    # Passo 2: carregar dados
    print(f"A carregar {len(df)} registos...")
    inseridos, actualizados, erros = upsert_data(engine, df)
    
    print(f"Registos processados: {inseridos}")
    print(f"Erros: {erros}")
    print("=" * 50)
    print("CARREGAMENTO CONCLUÍDO")
    print("=" * 50)
    
    return inseridos, erros


# ============================================================
# TESTE
# ============================================================

if __name__ == "__main__":
    from extract import extract_all
    from transform import transform
    
    df_raw   = extract_all()
    df_clean = transform(df_raw)
    load(df_clean)