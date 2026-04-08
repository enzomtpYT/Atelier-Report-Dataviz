"""
Superstore BI Dashboard - Page d'accueil avec KPIs
🏠 Dashboard principal avec aperçu global et navigation
📊 KPIs globaux + accès aux dashboards spécialisés
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas as pd
from datetime import datetime
import os

# === CONFIGURATION PAGE ===
st.set_page_config(
    page_title="Superstore BI - Dashboard Général",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# === STYLES CSS PERSONNALISÉS ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    .stApp,
    [data-testid="stAppViewContainer"],
    .main {
        background: linear-gradient(180deg, #0f172a 0%, #111827 100%) !important;
        color: #e2e8f0;
    }

    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    /* Modern Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(0, 0, 0, 0.88) !important;
        backdrop-filter: blur(10px) !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        padding: 24px !important;
        border-radius: 20px !important;
        box-shadow: 0 10px 28px rgba(0, 0, 0, 0.35) !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 16px 36px rgba(0, 0, 0, 0.42) !important;
        background: rgba(6, 6, 6, 0.95) !important;
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricValue"] {
        color: #f8fafc !important;
    }

    /* Style titles */
    h1 { 
        color: #f8fafc; 
        font-weight: 800; 
        letter-spacing: -0.02em; 
    }
    
    h2 { 
        color: #f8fafc; 
        font-weight: 700; 
        border: none;
        margin-top: 40px;
        font-size: 1.75rem;
    }

    h3 {
        color: #e2e8f0;
    }

    /* Navigation Card Refinement */
    .navigation-card {
        background: rgba(0, 0, 0, 0.86);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        padding: 40px 30px;
        border-radius: 24px;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        margin-bottom: 25px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .navigation-card:hover {
        background: rgba(8, 8, 8, 0.95);
        transform: scale(1.02);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.45);
    }

    .navigation-card .icon-container {
        width: 80px;
        height: 80px;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-bottom: 20px;
        font-size: 2.5rem;
        transition: all 0.3s;
    }

    .ceo-card .icon-container { background: #fef2f2; }
    .commercial-card .icon-container { background: #eff6ff; }
    .produit-card .icon-container { background: #ecfdf5; }

    .navigation-card h3 { 
        margin: 10px 0; 
        font-weight: 700; 
        color: #f8fafc;
        font-size: 1.4rem;
    }
    
    .navigation-card p { 
        color: #cbd5e1; 
        font-size: 1rem;
        line-height: 1.5;
    }
    
    /* Button refinement */
    .stButton>button {
        border-radius: 12px !important;
        padding: 12px 24px !important;
        font-weight: 600 !important;
        border: none !important;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.2s !important;
    }

    .stButton>button:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1) !important;
        transform: translateY(-1px);
    }
</style>
""", unsafe_allow_html=True)

# === CONFIGURATION API ===
API_URL = os.getenv("API_URL", "http://localhost:8000")

# === FONCTIONS HELPER ===
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

def formater_pourcentage(valeur: float) -> str:
    return f"{valeur:.1f}%"

# === HEADER PRINCIPAL ===
st.markdown("""
<div style='background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 60px 40px; border-radius: 32px; color: white; text-align: center; margin-bottom: 50px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25); position: relative; overflow: hidden;'>
    <div style='position: relative; z-index: 1;'>
        <h1 style='color: white; margin: 0; font-size: 3.5rem; font-weight: 800; letter-spacing: -0.04em;'>Superstore <span style='color: #3b82f6;'>Intelligence</span></h1>
        <p style='font-size: 1.25rem; opacity: 0.8; margin-top: 15px; font-weight: 500; max-width: 600px; margin-left: auto; margin-right: auto;'>Pilotez votre activité avec une vision data-driven en temps réel.</p>
    </div>
    <div style='position: absolute; top: -50px; right: -50px; width: 200px; height: 200px; background: rgba(59, 130, 246, 0.1); border-radius: 100px; blur: 50px;'></div>
</div>
""", unsafe_allow_html=True)

# === CHARGEMENT DES DONNÉES ===
with st.spinner("📊 Chargement des données..."):
    try:
        kpi_data = appeler_api("/kpi/globaux")
        comparaison_data = appeler_api("/kpi/comparaison")
        kpi_executif = appeler_api("/kpi/executif")
        
        # KPIs principaux
        st.header("📊 KPIs Globaux")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            delta_ca = f"{comparaison_data['evolution_ca_pct']:+.1f}%" if comparaison_data['evolution_ca_pct'] != 0 else None
            st.metric("💰 Chiffre d'Affaires", formater_euro(kpi_data['ca_total']), delta_ca)
        
        with col2:
            delta_profit = f"{comparaison_data['evolution_profit_pct']:+.1f}%" if comparaison_data['evolution_profit_pct'] != 0 else None
            st.metric("💵 Profit Total", formater_euro(kpi_data['profit_total']), delta_profit)
        
        with col3:
            delta_cmd = f"{comparaison_data['evolution_commandes_pct']:+.1f}%" if comparaison_data['evolution_commandes_pct'] != 0 else None
            st.metric("🧾 Commandes", formater_nombre(kpi_data['nb_commandes']), delta_cmd)
        
        with col4:
            st.metric("👥 Clients", formater_nombre(kpi_data['nb_clients']))
        
        st.divider()
        
        # KPIs secondaires
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            st.metric("🛒 Panier Moyen", formater_euro(kpi_data['panier_moyen']))
        
        with col6:
            st.metric("📈 Marge Moyenne", formater_pourcentage(kpi_data['marge_moyenne']))
        
        with col7:
            st.metric("📦 Articles Vendus", formater_nombre(kpi_data['quantite_vendue']))
        
        with col8:
            articles_par_cmd = kpi_data['quantite_vendue'] / kpi_data['nb_commandes'] if kpi_data['nb_commandes'] > 0 else 0
            st.metric("📊 Articles/Commande", f"{articles_par_cmd:.1f}")

        col9, col10, col11, col12 = st.columns(4)
        with col9:
            st.metric("📅 Croissance mensuelle moy.", f"{kpi_executif['croissance_mensuelle_moyenne_pct']:+.1f}%")
        with col10:
            st.metric("🗓️ Croissance annuelle", f"{kpi_executif['croissance_annuelle_pct']:+.1f}%")
        with col11:
            st.metric("🎯 ROI global (proxy)", f"{kpi_executif['roi_global_pct']:.1f}%")
        with col12:
            st.metric("🔮 Projection CA mois+1", formater_euro(kpi_executif['projection_ca_prochain_mois']))
        
        st.divider()
        
        # Graphiques d'analyse
        st.header("📈 Analyses Visuelles")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            # Top catégories
            categories = appeler_api("/kpi/categories")
            df_categories = pd.DataFrame(categories)
            
            fig_categories = px.bar(
                df_categories, 
                x='categorie', 
                y='ca', 
                title="📦 Chiffre d'Affaires par Catégorie",
                color='ca',
                color_continuous_scale='Viridis',
                labels={'ca': 'CA (€)', 'categorie': 'Catégorie'}
            )
            fig_categories.update_layout(
                height=450,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=60, b=20),
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
            )
            st.plotly_chart(fig_categories, use_container_width=True)
        
        with col_right:
            # Performance géographique
            geo_data = appeler_api("/kpi/geographique")
            df_geo = pd.DataFrame(geo_data)
            
            fig_region = px.pie(
                df_geo, 
                values='ca', 
                names='region', 
                title="🌍 Répartition par Région",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_region.update_layout(
                height=450,
                margin=dict(l=20, r=20, t=60, b=20),
                legend=dict(orientation="h", yanchor="bottom", y=-0.1, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig_region, use_container_width=True)
        
        # Evolution temporelle
        st.subheader("📅 Evolution Temporelle")
        temporal_data = appeler_api("/kpi/temporel", params={'periode': 'mois'})
        df_temporal = pd.DataFrame(temporal_data)
        
        fig_temporal = go.Figure()
        fig_temporal.add_trace(go.Scatter(
            x=df_temporal['periode'], 
            y=df_temporal['ca'],
            mode='lines+markers',
            name='CA (€)',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8),
            fill='tozeroy',
            fillcolor='rgba(59, 130, 246, 0.1)'
        ))
        fig_temporal.add_trace(go.Scatter(
            x=df_temporal['periode'], 
            y=df_temporal['profit'],
            mode='lines+markers',
            name='Profit (€)',
            line=dict(color='#10b981', width=3),
            marker=dict(size=8)
        ))
        fig_temporal.update_layout(
            title="Performance mensuelle (CA vs Profit)",
            xaxis_title="Période",
            yaxis_title="Montant (€)",
            height=500,
            hovermode="x unified",
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
        )
        st.plotly_chart(fig_temporal, use_container_width=True)
        
    except Exception as e:
        st.error(f"❌ Erreur lors du chargement des données: {e}")
        st.info("💡 Vérifiez que l'API backend est démarrée")

st.divider()

# === NAVIGATION VERS LES DASHBOARDS SPÉCIALISÉS ===
st.header("🎯 Dashboards Spécialisés")
st.markdown("### Choisissez votre tableau de bord selon votre rôle :")

col_nav1, col_nav2, col_nav3 = st.columns(3)

with col_nav1:
    st.markdown("""
    <div class="navigation-card ceo-card">
        <div class="icon-container">🎯</div>
        <h3>Direction CEO</h3>
        <p>Vision stratégique & KPIs globaux pour la prise de décision agile</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Accéder à la Stratégie", use_container_width=True, key="btn_ceo"):
        st.switch_page("pages/1_🎯_Direction_CEO.py")

with col_nav2:
    st.markdown("""
    <div class="navigation-card commercial-card">
        <div class="icon-container">💼</div>
        <h3>Commercial</h3>
        <p>Analyse des ventes, segments clients et performance terrain</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Voir la Performance", use_container_width=True, key="btn_comm"):
        st.switch_page("pages/2_💼_Responsable_Commercial.py")

with col_nav3:
    st.markdown("""
    <div class="navigation-card produit-card">
        <div class="icon-container">📦</div>
        <h3>Produit</h3>
        <p>Gestion du catalogue, rotation des stocks et analyses marketing</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Gérer le Catalogue", use_container_width=True, key="btn_prod"):
        st.switch_page("pages/3_📦_Responsable_Produit.py")

# === FOOTER ===
st.divider()
st.markdown("""
<div style='text-align: center; color: #7f8c8d; margin-top: 2rem;'>
    <p>📊 <b>Superstore BI Dashboard</b> | Propulsé par FastAPI + Streamlit + Plotly</p>
    <p>💡 Dashboard principal avec KPIs globaux et navigation vers dashboards spécialisés</p>
</div>
""", unsafe_allow_html=True)