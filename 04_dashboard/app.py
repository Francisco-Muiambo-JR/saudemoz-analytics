# ============================================================
# Ficheiro: 04_dashboard/app.py
# Projecto: SaúdeMoz Analytics
# ============================================================

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv()

# ============================================================
# CONFIGURAÇÃO DA PÁGINA
# ============================================================

st.set_page_config(
    page_title="SaúdeMoz Analytics",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS PERSONALIZADO
# ============================================================

st.markdown("""
<style>
    /* Cabeçalho principal */
    .main-header {
        background: linear-gradient(135deg, #006633 0%, #009933 50%, #00CC44 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,102,51,0.3);
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.3);
    }
    .main-header p {
        color: rgba(255,255,255,0.9);
        font-size: 1.1rem;
        margin: 0.5rem 0 0 0;
    }

    /* Cards de KPI */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
        border-left: 4px solid #009933;
        margin-bottom: 1rem;
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: 700;
        color: #006633;
        margin: 0;
    }
    .kpi-label {
        font-size: 0.85rem;
        color: #666;
        margin: 0.3rem 0 0 0;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-delta {
        font-size: 0.9rem;
        color: #009933;
        font-weight: 500;
        margin: 0.3rem 0 0 0;
    }

    /* Secções */
    .section-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #006633;
        border-bottom: 2px solid #009933;
        padding-bottom: 0.5rem;
        margin: 1.5rem 0 1rem 0;
    }

    /* Sidebar */
    .sidebar-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #006633;
        margin-bottom: 1rem;
    }

    /* Fonte de dados */
    .data-source {
        background: #f0f8f0;
        border: 1px solid #cceecc;
        border-radius: 8px;
        padding: 0.8rem;
        font-size: 0.85rem;
        color: #555;
        margin-top: 1rem;
    }

    /* Ocultar menu padrão streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ============================================================
# LIGAÇÃO À BASE DE DADOS
# ============================================================

@st.cache_resource(ttl=0)
def get_engine():
    url = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL")
    return create_engine(url)

@st.cache_data
def load_data(_engine):
    query = "SELECT * FROM health_indicators ORDER BY indicator_code, year"
    return pd.read_sql(query, _engine)

engine = get_engine()
df = load_data(engine)

# ============================================================
# CABEÇALHO
# ============================================================

st.markdown("""
<div class="main-header">
    <h1>🏥 SaúdeMoz Analytics</h1>
    <p>Plataforma de Análise de Indicadores de Saúde Pública de Moçambique · 2000–2023</p>
    <p style="font-size:0.9rem; opacity:0.8;">Fonte: World Bank Open Data · Dados actualizados automaticamente via pipeline ETL</p>
</div>
""", unsafe_allow_html=True)

# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown('<p class="sidebar-title">🔍 Painel de Controlo</p>', unsafe_allow_html=True)
    
    st.markdown("**Período de Análise**")
    ano_min = int(df["year"].min())
    ano_max = int(df["year"].max())
    ano_range = st.slider(
        "",
        min_value=ano_min,
        max_value=ano_max,
        value=(ano_min, ano_max),
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("**Indicador Principal**")
    indicadores = sorted(df["indicator_name"].unique().tolist())
    indicador_sel = st.selectbox(
        "",
        indicadores,
        index=indicadores.index("Expectativa de Vida ao Nascer (anos)")
        if "Expectativa de Vida ao Nascer (anos)" in indicadores else 0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    st.markdown("""
    <div class="data-source">
        📊 <strong>Sobre os dados</strong><br>
        Dados reais extraídos via API do World Bank. 
        Pipeline ETL automatizado em Python.
        Base de dados PostgreSQL na cloud.
    </div>
    """, unsafe_allow_html=True)

# Filtrar dados
df_filtrado = df[
    (df["year"] >= ano_range[0]) &
    (df["year"] <= ano_range[1])
]
df_indicador = df_filtrado[df_filtrado["indicator_name"] == indicador_sel]

# ============================================================
# KPIs
# ============================================================

valor_atual  = df_indicador[df_indicador["year"] == df_indicador["year"].max()]["value"].values[0]
valor_inicio = df_indicador[df_indicador["year"] == df_indicador["year"].min()]["value"].values[0]
variacao     = valor_atual - valor_inicio
variacao_pct = (variacao / valor_inicio) * 100

vida_atual = df[(df["indicator_code"] == "SP.DYN.LE00.IN") & (df["year"] == df["year"].max())]["value"].values[0]
mort_atual = df[(df["indicator_code"] == "SP.DYN.IMRT.IN") & (df["year"] == df["year"].max())]["value"].values[0]
hiv_atual  = df[(df["indicator_code"] == "SH.DYN.AIDS.ZS") & (df["year"] == df["year"].max())]["value"].values[0]
vac_atual  = df[(df["indicator_code"] == "SH.IMM.IDPT") & (df["year"] == df["year"].max())]["value"].values[0]

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(f"""
    <div class="kpi-card">
        <p class="kpi-value">{vida_atual:.1f}</p>
        <p class="kpi-label">Expectativa de Vida</p>
        <p class="kpi-delta">anos · {df["year"].max()}</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #cc3300;">
        <p class="kpi-value" style="color:#cc3300;">{mort_atual:.1f}</p>
        <p class="kpi-label">Mortalidade Infantil</p>
        <p class="kpi-delta" style="color:#cc3300;">por 1.000 nascimentos</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #cc6600;">
        <p class="kpi-value" style="color:#cc6600;">{hiv_atual:.1f}%</p>
        <p class="kpi-label">Prevalência HIV</p>
        <p class="kpi-delta" style="color:#cc6600;">% adultos infectados</p>
    </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown(f"""
    <div class="kpi-card" style="border-left-color: #0066cc;">
        <p class="kpi-value" style="color:#0066cc;">{vac_atual:.1f}%</p>
        <p class="kpi-label">Cobertura Vacinal DTP</p>
        <p class="kpi-delta" style="color:#0066cc;">% crianças vacinadas</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# GRÁFICO 1 — EVOLUÇÃO DO INDICADOR SELECCIONADO
# ============================================================

st.markdown(f'<p class="section-header">📈 Evolução — {indicador_sel}</p>', unsafe_allow_html=True)

fig1 = px.area(
    df_indicador,
    x="year",
    y="value",
    title=f"{indicador_sel} · Moçambique {ano_range[0]}–{ano_range[1]}",
    labels={"year": "Ano", "value": "Valor"},
    color_discrete_sequence=["#009933"]
)
fig1.update_traces(fill="tozeroy", fillcolor="rgba(0,153,51,0.15)", line=dict(width=2.5))
fig1.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    xaxis=dict(showgrid=True, gridcolor="#f0f0f0", tickmode="linear", dtick=2),
    yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    font=dict(family="Arial", size=12),
    title=dict(font=dict(size=14))
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ============================================================
# GRÁFICO 2 e 3 — LADO A LADO
# ============================================================

col_a, col_b = st.columns(2)

with col_a:
    st.markdown('<p class="section-header">💀 Mortalidade ao Longo do Tempo</p>', unsafe_allow_html=True)
    
    df_vida = df_filtrado[df_filtrado["indicator_code"] == "SP.DYN.LE00.IN"][["year","value"]].rename(columns={"value": "Expectativa de Vida"})
    df_mort = df_filtrado[df_filtrado["indicator_code"] == "SP.DYN.IMRT.IN"][["year","value"]].rename(columns={"value": "Mortalidade Infantil"})
    df_corr = df_vida.merge(df_mort, on="year")

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df_corr["year"], y=df_corr["Expectativa de Vida"],
        name="Expectativa de Vida", yaxis="y1",
        line=dict(color="#009933", width=2.5), mode="lines+markers",
        marker=dict(size=5)
    ))
    fig2.add_trace(go.Scatter(
        x=df_corr["year"], y=df_corr["Mortalidade Infantil"],
        name="Mortalidade Infantil", yaxis="y2",
        line=dict(color="#cc3300", width=2.5), mode="lines+markers",
        marker=dict(size=5)
    ))
    fig2.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        yaxis=dict(title="Expectativa de Vida (anos)", color="#009933", showgrid=False),
        yaxis2=dict(title="Mortalidade Infantil (por 1000)", color="#cc3300", overlaying="y", side="right"),
        legend=dict(orientation="h", y=-0.2),
        font=dict(family="Arial", size=11),
        height=380
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_b:
    st.markdown('<p class="section-header">💧 Infraestruturas Básicas</p>', unsafe_allow_html=True)
    
    df_agua = df_filtrado[df_filtrado["indicator_code"] == "SH.H2O.BASW.ZS"][["year","value"]].rename(columns={"value": "agua"})
    df_san  = df_filtrado[df_filtrado["indicator_code"] == "SH.STA.BASS.ZS"][["year","value"]].rename(columns={"value": "saneamento"})
    df_infra = df_agua.merge(df_san, on="year")
    df_melt  = df_infra.melt(id_vars="year", var_name="tipo", value_name="pct")
    df_melt["tipo"] = df_melt["tipo"].map({"agua": "Água Potável", "saneamento": "Saneamento Básico"})

    fig3 = px.area(
        df_melt, x="year", y="pct", color="tipo",
        labels={"year": "Ano", "pct": "% População", "tipo": ""},
        color_discrete_map={"Água Potável": "#0066cc", "Saneamento Básico": "#2ca02c"}
    )
    fig3.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", range=[0, 100]),
        legend=dict(orientation="h", y=-0.2),
        font=dict(family="Arial", size=11),
        height=380
    )
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ============================================================
# GRÁFICO 4 — HIV e VACINAÇÃO
# ============================================================

col_c, col_d = st.columns(2)

with col_c:
    st.markdown('<p class="section-header">🦠 Evolução do HIV</p>', unsafe_allow_html=True)
    
    df_hiv = df_filtrado[df_filtrado["indicator_code"] == "SH.DYN.AIDS.ZS"]
    fig4 = px.bar(
        df_hiv, x="year", y="value",
        labels={"year": "Ano", "value": "% Adultos"},
        color="value",
        color_continuous_scale="Reds"
    )
    fig4.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        coloraxis_showscale=False,
        font=dict(family="Arial", size=11),
        height=350
    )
    st.plotly_chart(fig4, use_container_width=True)

with col_d:
    st.markdown('<p class="section-header">💉 Cobertura Vacinal DTP</p>', unsafe_allow_html=True)
    
    df_vac = df_filtrado[df_filtrado["indicator_code"] == "SH.IMM.IDPT"]
    fig5 = px.bar(
        df_vac, x="year", y="value",
        labels={"year": "Ano", "value": "% Crianças"},
        color="value",
        color_continuous_scale="Greens"
    )
    fig5.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0", range=[0, 100]),
        coloraxis_showscale=False,
        font=dict(family="Arial", size=11),
        height=350
    )
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# ============================================================
# TABELA DE DADOS
# ============================================================

st.markdown('<p class="section-header">📋 Dados Completos</p>', unsafe_allow_html=True)

df_tabela = df_filtrado[["year", "indicator_name", "value"]].copy()
df_tabela.columns = ["Ano", "Indicador", "Valor"]
df_tabela = df_tabela.sort_values(["Indicador", "Ano"])
st.dataframe(df_tabela, use_container_width=True, height=300)