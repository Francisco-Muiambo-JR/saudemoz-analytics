# ============================================================
# Ficheiro: 01_pipeline/extract.py
# Objectivo: Extrair dados de saúde de Moçambique
#            directamente da API do World Bank
# ============================================================

from wsgiref import headers

import requests
import pandas as pd
import time

# ============================================================
# INDICADORES A EXTRAIR
# ============================================================

INDICADORES = {
    "SP.DYN.LE00.IN": "Expectativa de Vida ao Nascer (anos)",
    "SP.DYN.IMRT.IN": "Taxa de Mortalidade Infantil (por 1000)",
    "SH.STA.MMRT":    "Taxa de Mortalidade Materna (por 100k)",
    "SH.H2O.BASW.ZS": "Acesso a Agua Potavel (% populacao)",
    "SH.STA.BASS.ZS": "Acesso a Saneamento Basico (% populacao)",
    "SH.IMM.IDPT":    "Cobertura Vacinal DTP (% criancas)",
    "SH.DYN.AIDS.ZS": "Prevalencia de HIV (% adultos)",
    "SH.MED.PHYS.ZS": "Medicos por 1000 habitantes",
    "SH.XPD.CHEX.GD.ZS": "Despesa em Saude (% PIB)",
    "SP.POP.TOTL":    "Populacao Total"
}

# ============================================================
# FUNÇÃO: fetch_indicator
# Objectivo: ir buscar um indicador específico à API
# Parâmetros:
#   - indicator_code: código do indicador (ex: SP.DYN.LE00.IN)
#   - indicator_name: nome legível do indicador
#   - country: código do país (MZ = Moçambique)
#   - start_year: ano inicial dos dados
#   - end_year: ano final dos dados
# ============================================================

def fetch_indicator(indicator_code, indicator_name, country="MZ", start_year=2000, end_year=2023):
    
    url = (
        f"http://api.worldbank.org/v2/country/{country}"
        f"/indicator/{indicator_code}"
        f"?format=json&per_page=100"
        f"&date={start_year}:{end_year}"
    )
    
    print(f"  A extrair: {indicator_name}...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    try:
        response = requests.get(url, timeout=30, headers=headers)
        
        # Verifica se o pedido foi bem sucedido
        if response.status_code != 200:
            print(f"  ERRO: Status code {response.status_code}")
            return pd.DataFrame()
        
        data = response.json()
        
        # Verifica se há dados na resposta
        if not data or len(data) < 2 or not data[1]:
            print(f"  AVISO: Sem dados para {indicator_name}")
            return pd.DataFrame()
        
        # Converte os dados para uma lista de dicionários
        records = []
        for item in data[1]:
            records.append({
                "country_code": country,
                "country_name": item["country"]["value"],
                "indicator_code": indicator_code,
                "indicator_name": indicator_name,
                "year": int(item["date"]),
                "value": item["value"]  # pode ser None
            })
        
        df = pd.DataFrame(records)
        print(f"  OK: {len(df)} registos extraídos")
        return df
        
    except requests.exceptions.Timeout:
        print(f"  ERRO: Timeout ao aceder à API")
        return pd.DataFrame()
    
    except Exception as e:
        print(f"  ERRO: {e}")
        return pd.DataFrame()


# ============================================================
# FUNÇÃO PRINCIPAL: extract_all
# Objectivo: extrair todos os indicadores e juntar num
#            único DataFrame
# ============================================================

def extract_all():
    
    print("=" * 50)
    print("FASE 1 — EXTRACÇÃO DE DADOS")
    print("Fonte: World Bank API")
    print("País: Moçambique (MZ)")
    print("Período: 2000 a 2023")
    print("=" * 50)
    
    all_data = []
    
    for code, name in INDICADORES.items():
        df = fetch_indicator(code, name)
        
        if not df.empty:
            all_data.append(df)
        
        # Pausa de 0.5 segundos entre pedidos
        time.sleep(0.5)
    
    if not all_data:
        print("ERRO: Nenhum dado extraído")
        return pd.DataFrame()
    
    # Junta todos os DataFrames num só
    final_df = pd.concat(all_data, ignore_index=True)
    
    print("=" * 50)
    print(f"EXTRACÇÃO CONCLUÍDA")
    print(f"Total de registos: {len(final_df)}")
    print(f"Indicadores extraídos: {final_df['indicator_name'].nunique()}")
    print(f"Anos cobertos: {final_df['year'].min()} a {final_df['year'].max()}")
    print("=" * 50)
    
    return final_df


# ============================================================
# TESTE: corre apenas quando executamos este ficheiro
#        directamente (não quando importamos noutro ficheiro)
# ============================================================

if __name__ == "__main__":
    df = extract_all()
    print("\nPrimeiras 5 linhas:")
    print(df.head())
    print(f"\nColunas: {list(df.columns)}")