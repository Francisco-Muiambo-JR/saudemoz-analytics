# ============================================================
# Ficheiro: pipeline.py
# Objectivo: Orquestrador do pipeline ETL completo
# Projecto: SaúdeMoz Analytics
# Como usar: python pipeline.py
# ============================================================

import sys
import os
from datetime import datetime

sys.path.append(os.path.join(os.path.dirname(__file__), "01_pipeline"))

from extract import extract_all
from transform import transform
from load import load


def run_pipeline():

    inicio = datetime.now()

    print("\n" + "=" * 50)
    print("SAUDEMOZ ANALYTICS — PIPELINE ETL")
    print(f"Inicio: {inicio.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50 + "\n")

    try:
        # FASE 1 — EXTRACT
        df_raw = extract_all()

        if df_raw.empty:
            print("ERRO: Nenhum dado extraído. Pipeline interrompido.")
            sys.exit(1)

        # FASE 2 — TRANSFORM
        df_clean = transform(df_raw)

        if df_clean.empty:
            print("ERRO: Nenhum dado após transformação. Pipeline interrompido.")
            sys.exit(1)

        # FASE 3 — LOAD
        inseridos, erros = load(df_clean)

        # SUMÁRIO FINAL
        fim = datetime.now()
        duracao = (fim - inicio).seconds

        print("\n" + "=" * 50)
        print("PIPELINE CONCLUÍDO COM SUCESSO")
        print(f"Duração: {duracao} segundos")
        print(f"Registos carregados: {inseridos}")
        print(f"Erros: {erros}")
        print("=" * 50 + "\n")

    except Exception as e:
        print(f"\nERRO CRÍTICO NO PIPELINE: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_pipeline()