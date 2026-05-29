# ============================================================
# Ficheiro: 04_dashboard/generate_dashboard.py
# Projecto: SaúdeMoz Analytics
# ============================================================

import os
import sys
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio
from sqlalchemy import create_engine
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv()

# ============================================================
# PALETA DE CORES 
# ============================================================

CORES = {
    "verde_escuro":  "#006400",
    "verde_medio":   "#228B22",
    "verde_claro":   "#32CD32",
    "vermelho":      "#DC143C",
    "laranja":       "#FF8C00",
    "azul":          "#1E90FF",
    "azul_escuro":   "#003087",
    "cinza_claro":   "#F8F9FA",
    "cinza_medio":   "#6C757D",
    "branco":        "#FFFFFF",
    "preto":         "#1A1A2E",
    "fundo":         "#FAFAFA",
}

# ============================================================
# LIGAÇÃO À BASE DE DADOS
# ============================================================

def get_data():
    url = os.getenv("DATABASE_URL")
    engine = create_engine(url)
    df = pd.read_sql("SELECT * FROM health_indicators ORDER BY indicator_code, year", engine)
    return df

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def get_indicator(df, code):
    return df[df["indicator_code"] == code].sort_values("year")

def get_latest_value(df, code):
    d = get_indicator(df, code)
    return d[d["year"] == d["year"].max()]["value"].values[0]

def get_change(df, code):
    d = get_indicator(df, code)
    v_start = d[d["year"] == d["year"].min()]["value"].values[0]
    v_end   = d[d["year"] == d["year"].max()]["value"].values[0]
    return v_end - v_start, ((v_end - v_start) / v_start) * 100

# ============================================================
# GERAR DASHBOARD
# ============================================================

def generate_dashboard():

    print("A carregar dados...")
    df = get_data()

    vida_val  = get_latest_value(df, "SP.DYN.LE00.IN")
    mort_val  = get_latest_value(df, "SP.DYN.IMRT.IN")
    hiv_val   = get_latest_value(df, "SH.DYN.AIDS.ZS")
    vac_val   = get_latest_value(df, "SH.IMM.IDPT")
    agua_val  = get_latest_value(df, "SH.H2O.BASW.ZS")
    san_val   = get_latest_value(df, "SH.STA.BASS.ZS")

    vida_delta, vida_pct = get_change(df, "SP.DYN.LE00.IN")
    mort_delta, mort_pct = get_change(df, "SP.DYN.IMRT.IN")

    df_vida = get_indicator(df, "SP.DYN.LE00.IN")
    df_mort = get_indicator(df, "SP.DYN.IMRT.IN")
    df_hiv  = get_indicator(df, "SH.DYN.AIDS.ZS")
    df_vac  = get_indicator(df, "SH.IMM.IDPT")
    df_agua = get_indicator(df, "SH.H2O.BASW.ZS")
    df_san  = get_indicator(df, "SH.STA.BASS.ZS")
    df_med  = get_indicator(df, "SH.MED.PHYS.ZS")
    df_desp = get_indicator(df, "SH.XPD.CHEX.GD.ZS")

    ano_max = int(df["year"].max())
    ano_min = int(df["year"].min())

    # --------------------------------------------------------
    # HTML COMPLETO
    # --------------------------------------------------------

    html = f"""<!DOCTYPE html>
<html lang="pt">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SaúdeMoz Analytics</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{
            font-family: 'Inter', sans-serif;
            background: #F0F2F5;
            color: #1A1A2E;
        }}

        /* HEADER */
        .header {{
            background: linear-gradient(135deg, #003087 0%, #006400 100%);
            color: white;
            padding: 2.5rem 3rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .header-left h1 {{
            font-size: 2rem;
            font-weight: 800;
            letter-spacing: -0.5px;
        }}
        .header-left p {{
            font-size: 0.95rem;
            opacity: 0.85;
            margin-top: 0.4rem;
        }}
        .header-badge {{
            background: rgba(255,255,255,0.15);
            border: 1px solid rgba(255,255,255,0.3);
            border-radius: 8px;
            padding: 0.6rem 1.2rem;
            font-size: 0.85rem;
            text-align: center;
        }}
        .header-badge strong {{
            display: block;
            font-size: 1.4rem;
            font-weight: 700;
        }}

        /* CONTAINER */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 2rem 2rem;
        }}

        /* SECTION TITLE */
        .section-title {{
            font-size: 1rem;
            font-weight: 600;
            color: #003087;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin: 2rem 0 1rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #006400;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        /* KPI GRID */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 1rem;
            margin-bottom: 0.5rem;
        }}
        .kpi-card {{
            background: white;
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 1px 8px rgba(0,0,0,0.06);
            border-top: 3px solid;
            transition: transform 0.2s;
        }}
        .kpi-card:hover {{ transform: translateY(-2px); }}
        .kpi-icon {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}
        .kpi-value {{
            font-size: 1.8rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 0.3rem;
        }}
        .kpi-label {{
            font-size: 0.75rem;
            color: #666;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 0.3rem;
        }}
        .kpi-delta {{
            font-size: 0.78rem;
            font-weight: 500;
        }}
        .delta-up   {{ color: #006400; }}
        .delta-down {{ color: #DC143C; }}

        /* CHART GRID */
        .chart-grid-2 {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.2rem;
            margin-bottom: 1.2rem;
        }}
        .chart-grid-3 {{
            display: grid;
            grid-template-columns: 1fr 1fr 1fr;
            gap: 1.2rem;
            margin-bottom: 1.2rem;
        }}
        .chart-full {{
            margin-bottom: 1.2rem;
        }}
        .chart-card {{
            background: white;
            border-radius: 12px;
            padding: 1.2rem;
            box-shadow: 0 1px 8px rgba(0,0,0,0.06);
        }}
        .chart-title {{
            font-size: 0.85rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 0.8rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid #f0f0f0;
        }}

        /* FOOTER */
        .footer {{
            background: #1A1A2E;
            color: rgba(255,255,255,0.6);
            padding: 1.5rem 3rem;
            text-align: center;
            font-size: 0.82rem;
            margin-top: 2rem;
        }}
        .footer a {{ color: #32CD32; text-decoration: none; }}
    </style>
</head>
<body>

<!-- HEADER -->
<div class="header">
    <div class="header-left">
        <h1>🏥 SaúdeMoz Analytics</h1>
        <p>Plataforma de Análise de Indicadores de Saúde Pública de Moçambique · {ano_min}–{ano_max}</p>
        <p style="font-size:0.8rem; opacity:0.7; margin-top:0.3rem;">
            Pipeline ETL automatizado · World Bank Open Data · PostgreSQL Cloud
        </p>
    </div>
    <div class="header-badge">
        <strong>{ano_max}</strong>
        Dados mais recentes
    </div>
</div>

<div class="container">

    <!-- KPIs -->
    <div class="section-title">📊 Indicadores Principais — {ano_max}</div>
    <div class="kpi-grid">
        <div class="kpi-card" style="border-top-color: #006400;">
            <div class="kpi-icon">❤️</div>
            <div class="kpi-value" style="color:#006400;">{vida_val:.1f}</div>
            <div class="kpi-label">Expectativa de Vida</div>
            <div class="kpi-delta delta-up">▲ +{vida_delta:.1f} anos desde 2000</div>
        </div>
        <div class="kpi-card" style="border-top-color: #DC143C;">
            <div class="kpi-icon">👶</div>
            <div class="kpi-value" style="color:#DC143C;">{mort_val:.1f}</div>
            <div class="kpi-label">Mortalidade Infantil</div>
            <div class="kpi-delta delta-down">por 1.000 nascimentos</div>
        </div>
        <div class="kpi-card" style="border-top-color: #FF8C00;">
            <div class="kpi-icon">🦠</div>
            <div class="kpi-value" style="color:#FF8C00;">{hiv_val:.1f}%</div>
            <div class="kpi-label">Prevalência HIV</div>
            <div class="kpi-delta delta-down">% adultos infectados</div>
        </div>
        <div class="kpi-card" style="border-top-color: #1E90FF;">
            <div class="kpi-icon">💉</div>
            <div class="kpi-value" style="color:#1E90FF;">{vac_val:.0f}%</div>
            <div class="kpi-label">Cobertura Vacinal</div>
            <div class="kpi-delta delta-up">% crianças vacinadas DTP</div>
        </div>
        <div class="kpi-card" style="border-top-color: #17BECF;">
            <div class="kpi-icon">💧</div>
            <div class="kpi-value" style="color:#17BECF;">{agua_val:.1f}%</div>
            <div class="kpi-label">Acesso a Água</div>
            <div class="kpi-delta delta-up">% população com acesso</div>
        </div>
        <div class="kpi-card" style="border-top-color: #2CA02C;">
            <div class="kpi-icon">🚿</div>
            <div class="kpi-value" style="color:#2CA02C;">{san_val:.1f}%</div>
            <div class="kpi-label">Saneamento Básico</div>
            <div class="kpi-delta delta-up">% população com acesso</div>
        </div>
    </div>

    <!-- GRÁFICO 1 — EXPECTATIVA DE VIDA -->
    <div class="section-title">📈 Evolução dos Indicadores</div>
    <div class="chart-full">
        <div class="chart-card">
            <div class="chart-title">Expectativa de Vida ao Nascer em Moçambique ({ano_min}–{ano_max})</div>
            <div id="chart_vida"></div>
        </div>
    </div>

    <!-- GRÁFICOS 2x2 -->
    <div class="chart-grid-2">
        <div class="chart-card">
            <div class="chart-title">Mortalidade Infantil vs Expectativa de Vida</div>
            <div id="chart_corr"></div>
        </div>
        <div class="chart-card">
            <div class="chart-title">Acesso a Infraestruturas Básicas (% população)</div>
            <div id="chart_infra"></div>
        </div>
    </div>

    <div class="chart-grid-3">
        <div class="chart-card">
            <div class="chart-title">Prevalência do HIV (% adultos)</div>
            <div id="chart_hiv"></div>
        </div>
        <div class="chart-card">
            <div class="chart-title">Cobertura Vacinal DTP (% crianças)</div>
            <div id="chart_vac"></div>
        </div>
        <div class="chart-card">
            <div class="chart-title">Despesa em Saúde (% PIB)</div>
            <div id="chart_desp"></div>
        </div>
    </div>

</div>

<!-- FOOTER -->
<div class="footer">
    <p>
        <strong style="color:white;">SaúdeMoz Analytics</strong> · 
        Dados: <a href="https://data.worldbank.org/country/mozambique" target="_blank">World Bank Open Data</a> · 
        Pipeline ETL em Python · PostgreSQL · Plotly
    </p>
    <p style="margin-top:0.4rem;">
        Desenvolvido por <strong style="color:white;">Francisco Salomão Muiambo Jr</strong> · 
        <a href="https://github.com/Francisco-Muiambo-JR/saudemoz-analytics" target="_blank">GitHub</a>
    </p>
</div>

<script>
const layout = {{
    margin: {{t:20, r:20, b:40, l:50}},
    paper_bgcolor: 'white',
    plot_bgcolor: 'white',
    font: {{family: 'Inter, sans-serif', size: 11, color: '#333'}},
    xaxis: {{showgrid: true, gridcolor: '#F0F0F0', linecolor: '#E0E0E0'}},
    yaxis: {{showgrid: true, gridcolor: '#F0F0F0', linecolor: '#E0E0E0'}},
    height: 300
}};

// CHART 1 — Expectativa de Vida
Plotly.newPlot('chart_vida', [{{
    x: {list(df_vida['year'])},
    y: {list(df_vida['value'].round(2))},
    type: 'scatter', mode: 'lines+markers',
    fill: 'tozeroy',
    fillcolor: 'rgba(0,100,0,0.08)',
    line: {{color: '#006400', width: 2.5}},
    marker: {{color: '#006400', size: 5}},
    name: 'Expectativa de Vida'
}}], {{...layout, height: 280,
    yaxis: {{...layout.yaxis, title: 'Anos'}},
    xaxis: {{...layout.xaxis, title: 'Ano', dtick: 2}}
}}, {{responsive: true, displayModeBar: false}});

// CHART 2 — Correlação
Plotly.newPlot('chart_corr', [
    {{
        x: {list(df_vida['year'])},
        y: {list(df_vida['value'].round(2))},
        type: 'scatter', mode: 'lines+markers',
        line: {{color: '#006400', width: 2}},
        marker: {{size: 4}},
        name: 'Expectativa de Vida',
        yaxis: 'y'
    }},
    {{
        x: {list(df_mort['year'])},
        y: {list(df_mort['value'].round(2))},
        type: 'scatter', mode: 'lines+markers',
        line: {{color: '#DC143C', width: 2}},
        marker: {{size: 4}},
        name: 'Mortalidade Infantil',
        yaxis: 'y2'
    }}
], {{
    ...layout,
    margin: {{t:20, r:70, b:60, l:60}},
    yaxis: {{title: 'Expectativa (anos)', color: '#006400', showgrid: true, gridcolor: '#F0F0F0', domain: [0, 1]}},
    yaxis2: {{title: 'Mortalidade (por 1000)', color: '#DC143C', overlaying: 'y', side: 'right', showgrid: false, domain: [0, 1], anchor: 'x'}},
    legend: {{orientation: 'h', y: -0.3, x: 0}},
    xaxis: {{...layout.xaxis, dtick: 4}}
}}, {{responsive: true, displayModeBar: false}});

// CHART 3 — Infraestruturas
Plotly.newPlot('chart_infra', [
    {{
        x: {list(df_agua['year'])},
        y: {list(df_agua['value'].round(2))},
        type: 'scatter', mode: 'lines',
        fill: 'tozeroy', fillcolor: 'rgba(23,190,207,0.15)',
        line: {{color: '#17BECF', width: 2}},
        name: 'Água Potável'
    }},
    {{
        x: {list(df_san['year'])},
        y: {list(df_san['value'].round(2))},
        type: 'scatter', mode: 'lines',
        fill: 'tozeroy', fillcolor: 'rgba(44,160,44,0.15)',
        line: {{color: '#2CA02C', width: 2}},
        name: 'Saneamento Básico'
    }}
], {{
    ...layout,
    yaxis: {{...layout.yaxis, title: '% População', range: [0, 100]}},
    xaxis: {{...layout.xaxis, dtick: 4}},
    legend: {{orientation: 'h', y: -0.25}}
}}, {{responsive: true, displayModeBar: false}});

// CHART 4 — HIV
Plotly.newPlot('chart_hiv', [{{
    x: {list(df_hiv['year'])},
    y: {list(df_hiv['value'].round(2))},
    type: 'bar',
    marker: {{
        color: {list(df_hiv['value'].round(2))},
        colorscale: [[0,'#FFE0E0'],[1,'#DC143C']],
        showscale: false
    }},
    name: 'HIV'
}}], {{
    ...layout,
    yaxis: {{...layout.yaxis, title: '% Adultos'}},
    xaxis: {{...layout.xaxis, dtick: 4}}
}}, {{responsive: true, displayModeBar: false}});

// CHART 5 — Vacinação
Plotly.newPlot('chart_vac', [{{
    x: {list(df_vac['year'])},
    y: {list(df_vac['value'].round(2))},
    type: 'bar',
    marker: {{
        color: {list(df_vac['value'].round(2))},
        colorscale: [[0,'#E0F0E0'],[1,'#006400']],
        showscale: false
    }},
    name: 'Vacinação'
}}], {{
    ...layout,
    yaxis: {{...layout.yaxis, title: '% Crianças', range: [0, 100]}},
    xaxis: {{...layout.xaxis, dtick: 4}}
}}, {{responsive: true, displayModeBar: false}});

// CHART 6 — Despesa em Saúde
Plotly.newPlot('chart_desp', [{{
    x: {list(df_desp['year'])},
    y: {list(df_desp['value'].round(2))},
    type: 'scatter', mode: 'lines+markers',
    fill: 'tozeroy', fillcolor: 'rgba(30,144,255,0.1)',
    line: {{color: '#1E90FF', width: 2}},
    marker: {{color: '#1E90FF', size: 4}},
    name: 'Despesa'
}}], {{
    ...layout,
    yaxis: {{...layout.yaxis, title: '% PIB'}},
    xaxis: {{...layout.xaxis, dtick: 4}}
}}, {{responsive: true, displayModeBar: false}});

</script>
</body>
</html>"""

    output_path = os.path.join(os.path.dirname(__file__), "dashboard.html")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard gerado: {output_path}")
    return output_path


if __name__ == "__main__":
    generate_dashboard()
    print("Abre o ficheiro 04_dashboard/dashboard.html no browser.")