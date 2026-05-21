# ============================================================
# Ficheiro: 01_pipeline/transform.py
# Objectivo: Limpar e validar os dados extraídos da API
# Padrão: ETL — fase Transform
# ============================================================

import pandas as pd

# ============================================================
# REGRAS DE VALIDAÇÃO POR INDICADOR
# Define os valores mínimos e máximos aceitáveis
# para cada indicador — valores fora deste intervalo
# são considerados erros de dados
# ============================================================

VALIDATION_RULES = {
    "SP.DYN.LE00.IN":    {"min": 20,  "max": 90},   # Expectativa de vida
    "SP.DYN.IMRT.IN":    {"min": 0,   "max": 300},  # Mortalidade infantil
    "SH.STA.MMRT":       {"min": 0,   "max": 5000}, # Mortalidade materna
    "SH.H2O.BASW.ZS":    {"min": 0,   "max": 100},  # Acesso a água
    "SH.STA.BASS.ZS":    {"min": 0,   "max": 100},  # Saneamento
    "SH.IMM.IDPT":       {"min": 0,   "max": 100},  # Vacinação
    "SH.DYN.AIDS.ZS":    {"min": 0,   "max": 50},   # HIV
    "SH.MED.PHYS.ZS":    {"min": 0,   "max": 10},   # Médicos
    "SH.XPD.CHEX.GD.ZS": {"min": 0,  "max": 30},   # Despesa saúde
    "SP.POP.TOTL":       {"min": 0,   "max": 1e9}   # População
}


def transform(df):
    
    print("=" * 50)
    print("FASE 2 — TRANSFORMAÇÃO DE DADOS")
    print("=" * 50)
    
    registos_iniciais = len(df)
    print(f"Registos recebidos: {registos_iniciais}")
    
    # --------------------------------------------------------
    # PASSO 1: Remover linhas com valor nulo
    # Porquê: não podemos analisar dados que não existem
    # --------------------------------------------------------
    df = df.dropna(subset=["value"])
    removidos_nulos = registos_iniciais - len(df)
    print(f"Valores nulos removidos: {removidos_nulos}")
    
    # --------------------------------------------------------
    # PASSO 2: Validar valores dentro dos limites aceitáveis
    # Porquê: um valor de expectativa de vida de 200 anos
    #         é claramente um erro de dados
    # --------------------------------------------------------
    valid_mask = pd.Series([True] * len(df), index=df.index)
    
    for indicator_code, rules in VALIDATION_RULES.items():
        mask = df["indicator_code"] == indicator_code
        invalid = mask & (
            (df["value"] < rules["min"]) | 
            (df["value"] > rules["max"])
        )
        valid_mask = valid_mask & ~invalid
    
    df = df[valid_mask]
    removidos_invalidos = registos_iniciais - removidos_nulos - len(df)
    print(f"Valores inválidos removidos: {removidos_invalidos}")
    
    # --------------------------------------------------------
    # PASSO 3: Converter tipos de dados
    # Porquê: garantir que year é inteiro e value é decimal
    # --------------------------------------------------------
    df["year"] = df["year"].astype(int)
    df["value"] = df["value"].astype(float)
    
    # --------------------------------------------------------
    # PASSO 4: Arredondar valores
    # Porquê: 63.611234567 não é mais útil que 63.61
    # --------------------------------------------------------
    df["value"] = df["value"].round(3)
    
    # --------------------------------------------------------
    # PASSO 5: Ordenar os dados
    # --------------------------------------------------------
    df = df.sort_values(
        ["indicator_code", "year"]
    ).reset_index(drop=True)
    
    # --------------------------------------------------------
    # PASSO 6: Adicionar coluna de timestamp
    # Porquê: rastrear quando os dados foram processados
    # --------------------------------------------------------
    df["processed_at"] = pd.Timestamp.now()
    
    print(f"Registos após transformação: {len(df)}")
    print(f"Indicadores: {df['indicator_name'].nunique()}")
    print(f"Anos: {df['year'].min()} a {df['year'].max()}")
    print("=" * 50)
    print("TRANSFORMAÇÃO CONCLUÍDA")
    print("=" * 50)
    
    return df


# ============================================================
# TESTE
# ============================================================

if __name__ == "__main__":
    from extract import extract_all
    
    df_raw = extract_all()
    df_clean = transform(df_raw)
    
    print("\nAmostra dos dados limpos:")
    print(df_clean.head(10))
    print(f"\nTipos de dados:\n{df_clean.dtypes}")