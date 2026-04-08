"""
Dashboard Direction/CEO - Vision Stratégique
🎯 KPIs stratégiques et analyse globale de performance
🌍 Vue d'ensemble géographique et temporelle
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import pandas as pd
from datetime import datetime
import os

# Configuration
st.set_page_config(page_title="Direction/CEO", page_icon="🎯", layout="wide")

# Styles
st.markdown("""
<style>
    .ceo-header {
        background: linear-gradient(90deg, #e74c3c, #c0392b);
        color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
    }
    .metric-ceo { border-left: 4px solid #e74c3c; }
</style>
""", unsafe_allow_html=True)

# API
API_URL = os.getenv("API_URL", "http://localhost:8000")

@st.cache_data(ttl=300)
def appeler_api(endpoint: str, params: dict = None):
    try:
        url = f"{API_URL}{endpoint}"
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except:
        st.error("❌ Erreur de connexion API")
        st.stop()

def formater_euro(valeur: float) -> str:
    return f"{valeur:,.0f} €".replace(",", " ")

def formater_nombre(valeur: int) -> str:
    return f"{valeur:,}".replace(",", " ")

# Header
st.markdown("""
<div class="ceo-header">
    <h1>🎯 Dashboard Direction/CEO</h1>
    <p>Vision stratégique et performance globale de l'entreprise</p>
</div>
""", unsafe_allow_html=True)

# Sidebar filtres
st.sidebar.header("🎯 Filtres Direction")
valeurs_filtres = appeler_api("/filters/valeurs")

date_min = datetime.strptime(valeurs_filtres['plage_dates']['min'], '%Y-%m-%d')
date_max = datetime.strptime(valeurs_filtres['plage_dates']['max'], '%Y-%m-%d')

col1, col2 = st.sidebar.columns(2)
with col1:
    date_debut = st.date_input("Du", value=date_min, min_value=date_min, max_value=date_max)
with col2:
    date_fin = st.date_input("Au", value=date_max, min_value=date_min, max_value=date_max)

region = st.sidebar.selectbox("Région", ["Toutes"] + valeurs_filtres['regions'])

params_filtres = {
    'date_debut': date_debut.strftime('%Y-%m-%d'),
    'date_fin': date_fin.strftime('%Y-%m-%d')
}
if region != "Toutes": 
    params_filtres['region'] = region

# KPIs Stratégiques
st.header("📊 KPIs Stratégiques")

kpi_data = appeler_api("/kpi/globaux", params=params_filtres)
comparaison_data = appeler_api("/kpi/comparaison", params=params_filtres)

col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_ca = f"{comparaison_data['evolution_ca_pct']:+.1f}%" if comparaison_data['evolution_ca_pct'] != 0 else None
    st.metric("💰 Chiffre d'Affaires", formater_euro(kpi_data['ca_total']), delta_ca)

with col2:
    delta_profit = f"{comparaison_data['evolution_profit_pct']:+.1f}%" if comparaison_data['evolution_profit_pct'] != 0 else None
    st.metric("💵 Profit Total", formater_euro(kpi_data['profit_total']), delta_profit)

with col3:
    st.metric("📈 Marge Moyenne", f"{kpi_data['marge_moyenne']:.2f}%")

with col4:
    st.metric("👥 Clients Uniques", formater_nombre(kpi_data['nb_clients']))

# Tendance globale
tendance_emoji = {"hausse": "📈", "baisse": "📉", "stable": "➡️"}
st.caption(f"{tendance_emoji.get(comparaison_data['tendance'], '📊')} Tendance : **{comparaison_data['tendance'].upper()}** vs période précédente")

st.divider()

# Synthèse stratégique
st.header("📖 Synthèse Stratégique")

insights_data = appeler_api("/kpi/insights")
st.info(f"**📊 Vue d'ensemble** : {insights_data['resume_principal']}")

col_insights, col_alertes, col_reco = st.columns(3)

with col_insights:
    st.markdown("### 📈 Tendances Clés")
    for insight in insights_data['insights']:
        st.markdown(f"{insight['icone']} **{insight['titre']}**")
        st.caption(insight['message'])

with col_alertes:
    st.markdown("### ⚠️ Points d'Attention")
    if insights_data['alertes']:
        for alerte in insights_data['alertes']:
            st.warning(f"{alerte['icone']} **{alerte['titre']}** : {alerte['message']}")
    else:
        st.success("✅ Aucune alerte détectée")

with col_reco:
    st.markdown("### 💡 Recommandations")
    for i, reco in enumerate(insights_data['recommandations'], 1):
        st.markdown(f"{i}. {reco}")

st.divider()

# Analyses
tab1, tab2 = st.tabs(["📅 Évolution Temporelle", "🌍 Performance Géographique"])

with tab1:
    st.subheader("📈 Évolution du Business")
    
    granularite = st.radio("Période", ['mois', 'jour'], horizontal=True)
    
    temporal = appeler_api("/kpi/temporel", params={'periode': granularite})
    df_temporal = pd.DataFrame(temporal)
    
    fig_temporal = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Évolution CA et Profit", "Évolution Commandes"),
        vertical_spacing=0.1
    )
    
    fig_temporal.add_trace(
        go.Scatter(x=df_temporal['periode'], y=df_temporal['ca'], 
                  mode='lines+markers', name='CA', line=dict(color='#e74c3c', width=3)),
        row=1, col=1
    )
    
    fig_temporal.add_trace(
        go.Scatter(x=df_temporal['periode'], y=df_temporal['profit'], 
                  mode='lines+markers', name='Profit', line=dict(color='#c0392b', width=3)),
        row=1, col=1
    )
    
    fig_temporal.add_trace(
        go.Bar(x=df_temporal['periode'], y=df_temporal['nb_commandes'], 
               name='Commandes', marker_color='#e67e22'),
        row=2, col=1
    )
    
    fig_temporal.update_xaxes(title_text="Période", row=2, col=1)
    fig_temporal.update_yaxes(title_text="Montant (€)", row=1, col=1)
    fig_temporal.update_yaxes(title_text="Nombre", row=2, col=1)
    fig_temporal.update_layout(height=600, showlegend=True)
    
    st.plotly_chart(fig_temporal, use_container_width=True)
    
    # Stats temporelles
    col_stats1, col_stats2, col_stats3 = st.columns(3)
    with col_stats1:
        st.metric("📈 CA moyen/période", formater_euro(df_temporal['ca'].mean()))
    with col_stats2:
        st.metric("📊 Commandes moy/période", f"{int(df_temporal['nb_commandes'].mean()):,}")
    with col_stats3:
        meilleure_periode = df_temporal.loc[df_temporal['ca'].idxmax()]
        st.metric("🏆 Meilleure période", meilleure_periode['periode'])

with tab2:
    st.subheader("🗺️ Répartition Géographique")
    
    geo = appeler_api("/kpi/geographique")
    df_geo = pd.DataFrame(geo)
    
    col_geo1, col_geo2 = st.columns(2)
    
    with col_geo1:
        fig_geo_ca = px.bar(
            df_geo, x='region', y='ca',
            title="Chiffre d'Affaires par Région",
            color='ca', color_continuous_scale='Reds',
            text='ca', height=400
        )
        fig_geo_ca.update_traces(texttemplate='%{text:,.0f}€', textposition='outside')
        st.plotly_chart(fig_geo_ca, use_container_width=True)
    
    with col_geo2:
        fig_geo_profit = px.pie(
            df_geo, values='profit', names='region',
            title="Répartition du Profit par Région",
            color_discrete_sequence=px.colors.sequential.Reds_r,
            height=400
        )
        st.plotly_chart(fig_geo_profit, use_container_width=True)
    
    # Tableau géographique
    st.markdown("### 📊 Performance détaillée par région")
    st.dataframe(
        df_geo[['region', 'ca', 'profit', 'nb_clients', 'nb_commandes']].rename(columns={
            'region': 'Région',
            'ca': 'CA (€)',
            'profit': 'Profit (€)',
            'nb_clients': 'Clients',
            'nb_commandes': 'Commandes'
        }),
        use_container_width=True,
        hide_index=True
    )

# Footer
st.divider()
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>🎯 <b>Dashboard Direction/CEO</b> | Vue stratégique globale</p>
</div>
""", unsafe_allow_html=True)