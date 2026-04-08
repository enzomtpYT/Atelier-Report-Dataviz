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
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 10px;
    }
    
    .stMetric {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
    }
    
    h1 { color: #2c3e50; font-weight: 700; text-align: center; }
    h2 { color: #34495e; font-weight: 600; }
    
    .navigation-card {
        background: linear-gradient(135deg, var(--bg-color), var(--bg-color-light));
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .navigation-card:hover {
        transform: translateY(-2px);
    }
    
    .ceo-card { --bg-color: #e74c3c; --bg-color-light: #c0392b; }
    .commercial-card { --bg-color: #3498db; --bg-color-light: #2980b9; }
    .produit-card { --bg-color: #2ecc71; --bg-color-light: #27ae60; }
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
<div style='background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 15px; color: white; text-align: center; margin-bottom: 30px;'>
    <h1>🛒 Superstore BI - Dashboard Général</h1>
    <p>Vue d'ensemble des performances globales de l'entreprise</p>
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
                title="📦 CA par Catégorie",
                color='ca',
                color_continuous_scale='Blues',
                labels={'ca': 'Chiffre d\'Affaires (€)', 'categorie': 'Catégorie'}
            )
            fig_categories.update_layout(height=400)
            st.plotly_chart(fig_categories, use_container_width=True)
        
        with col_right:
            # Performance géographique
            geo_data = appeler_api("/kpi/geographique")
            df_geo = pd.DataFrame(geo_data)
            
            fig_geo = px.pie(
                df_geo, 
                values='ca', 
                names='region', 
                title="🌍 Répartition du CA par Région",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_geo.update_layout(height=400)
            st.plotly_chart(fig_geo, use_container_width=True)
        
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
            line=dict(color='#667eea')
        ))
        fig_temporal.add_trace(go.Scatter(
            x=df_temporal['periode'], 
            y=df_temporal['profit'],
            mode='lines+markers',
            name='Profit (€)',
            line=dict(color='#764ba2')
        ))
        fig_temporal.update_layout(
            title="Evolution du CA et Profit par Mois",
            xaxis_title="Période",
            yaxis_title="Montant (€)",
            height=400
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
        <h3>🎯 Direction CEO</h3>
        <p>Vision stratégique & KPIs globaux</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📈 Dashboard Direction", use_container_width=True):
        st.switch_page("pages/1_🎯_Direction_CEO.py")

with col_nav2:
    st.markdown("""
    <div class="navigation-card commercial-card">
        <h3>💼 Commercial</h3>
        <p>Performance commerciale & clients</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🛒 Dashboard Commercial", use_container_width=True):
        st.switch_page("pages/2_💼_Responsable_Commercial.py")

with col_nav3:
    st.markdown("""
    <div class="navigation-card produit-card">
        <h3>📦 Produit</h3>
        <p>Gestion des produits & catalogue</p>
    </div>
    """, unsafe_allow_html=True)
    if st.button("📊 Dashboard Produit", use_container_width=True):
        st.switch_page("pages/3_📦_Responsable_Produit.py")

# === FOOTER ===
st.divider()
st.markdown("""
<div style='text-align: center; color: #7f8c8d; margin-top: 2rem;'>
    <p>📊 <b>Superstore BI Dashboard</b> | Propulsé par FastAPI + Streamlit + Plotly</p>
    <p>💡 Dashboard principal avec KPIs globaux et navigation vers dashboards spécialisés</p>
</div>
""", unsafe_allow_html=True)