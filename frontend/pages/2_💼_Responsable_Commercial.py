"""
Dashboard Responsable Commercial - Performance Commerciale
💼 Suivi des ventes, clients et segments de marché
📊 Analyse de la performance commerciale et fidélisation
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas as pd
from datetime import datetime
import os

# Configuration
st.set_page_config(page_title="Commercial", page_icon="💼", layout="wide")

# Styles
st.markdown("""
<style>
    .commercial-header {
        background: linear-gradient(90deg, #3498db, #2980b9);
        color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
    }
    .metric-commercial { border-left: 4px solid #3498db; }
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
<div class="commercial-header">
    <h1>💼 Dashboard Responsable Commercial</h1>
    <p>Performance commerciale, analyse clientèle et suivi des ventes</p>
</div>
""", unsafe_allow_html=True)

# Sidebar filtres
st.sidebar.header("💼 Filtres Commercial")
valeurs_filtres = appeler_api("/filters/valeurs")

date_min = datetime.strptime(valeurs_filtres['plage_dates']['min'], '%Y-%m-%d')
date_max = datetime.strptime(valeurs_filtres['plage_dates']['max'], '%Y-%m-%d')

col1, col2 = st.sidebar.columns(2)
with col1:
    date_debut = st.date_input("Du", value=date_min, min_value=date_min, max_value=date_max)
with col2:
    date_fin = st.date_input("Au", value=date_max, min_value=date_min, max_value=date_max)

segment = st.sidebar.selectbox("Segment Client", ["Tous"] + valeurs_filtres['segments'])
region = st.sidebar.selectbox("Région", ["Toutes"] + valeurs_filtres['regions'])

params_filtres = {
    'date_debut': date_debut.strftime('%Y-%m-%d'),
    'date_fin': date_fin.strftime('%Y-%m-%d')
}
if segment != "Tous": 
    params_filtres['segment'] = segment
if region != "Toutes": 
    params_filtres['region'] = region

# KPIs Commerciaux
st.header("📊 KPIs Commerciaux")

kpi_data = appeler_api("/kpi/globaux", params=params_filtres)
comparaison_data = appeler_api("/kpi/comparaison", params=params_filtres)

col1, col2, col3, col4 = st.columns(4)

with col1:
    delta_cmd = f"{comparaison_data['evolution_commandes_pct']:+.1f}%" if comparaison_data['evolution_commandes_pct'] != 0 else None
    st.metric("🧾 Commandes", formater_nombre(kpi_data['nb_commandes']), delta_cmd)

with col2:
    st.metric("🛒 Panier Moyen", formater_euro(kpi_data['panier_moyen']))

with col3:
    st.metric("👥 Clients Actifs", formater_nombre(kpi_data['nb_clients']))

with col4:
    articles_par_commande = kpi_data['quantite_vendue'] / kpi_data['nb_commandes'] if kpi_data['nb_commandes'] > 0 else 0
    st.metric("📊 Articles/Commande", f"{articles_par_commande:.2f}")

st.divider()

# Analyses détaillées
tab1, tab2, tab3 = st.tabs(["👥 Analyse Clients", "🎯 Segments de Marché", "📈 Évolution Commerciale"])

with tab1:
    st.subheader("🏆 Top Clients & Fidélisation")
    
    clients_data = appeler_api("/kpi/clients", params={'limite': 15})
    
    col_client1, col_client2 = st.columns([2, 1])
    
    with col_client1:
        df_top_clients = pd.DataFrame(clients_data['top_clients'])
        
        # Sélecteur pour limiter l'affichage
        nb_clients = st.slider("Nombre de clients à afficher", 5, 15, 10)
        df_display = df_top_clients.head(nb_clients)
        
        fig_clients = px.bar(
            df_display,
            x='ca_total',
            y='nom',
            orientation='h',
            title=f"Top {nb_clients} Clients par CA",
            color='nb_commandes',
            color_continuous_scale='Blues',
            labels={'ca_total': 'CA Total (€)', 'nom': 'Client', 'nb_commandes': 'Nb Commandes'},
            height=400
        )
        fig_clients.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_clients, use_container_width=True)
    
    with col_client2:
        st.markdown("### 📊 Statistiques Fidélisation")
        rec = clients_data['recurrence']
        
        st.metric("Total Clients", formater_nombre(rec['total_clients']))
        st.metric("Clients Récurrents", formater_nombre(rec['clients_recurrents']))
        st.metric("Clients 1 Achat", formater_nombre(rec['clients_1_achat']))
        st.metric("Commandes/Client", f"{rec['nb_commandes_moyen']:.2f}")
        
        # Taux de fidélisation
        taux_fidelisation = (rec['clients_recurrents'] / rec['total_clients'] * 100) if rec['total_clients'] > 0 else 0
        st.metric("Taux de Fidélisation", f"{taux_fidelisation:.1f}%")
    
    # Graphique de fidélisation
    st.markdown("### 🔄 Répartition Client : Nouveaux vs Récurrents")
    
    fidelisation_data = [
        {'Type': 'Clients Récurrents', 'Nombre': rec['clients_recurrents']},
        {'Type': 'Clients 1 Achat', 'Nombre': rec['clients_1_achat']}
    ]
    df_fidelisation = pd.DataFrame(fidelisation_data)
    
    fig_fidelisation = px.pie(
        df_fidelisation,
        values='Nombre',
        names='Type',
        title="Répartition des Clients par Fidélité",
        color_discrete_sequence=['#3498db', '#85c1e1'],
        height=350
    )
    st.plotly_chart(fig_fidelisation, use_container_width=True)

with tab2:
    st.subheader("🏢 Performance par Segment Client")
    
    df_segments = pd.DataFrame(clients_data['segments'])
    
    col_seg1, col_seg2 = st.columns(2)
    
    with col_seg1:
        # CA et Profit par segment
        fig_segments = go.Figure()
        fig_segments.add_trace(go.Bar(
            name='CA',
            x=df_segments['segment'],
            y=df_segments['ca'],
            marker_color='#3498db',
            text=df_segments['ca'].apply(lambda x: f"{x:,.0f}€"),
            textposition='outside'
        ))
        fig_segments.add_trace(go.Bar(
            name='Profit',
            x=df_segments['segment'],
            y=df_segments['profit'],
            marker_color='#2980b9',
            text=df_segments['profit'].apply(lambda x: f"{x:,.0f}€"),
            textposition='outside'
        ))
        fig_segments.update_layout(
            title="CA et Profit par Segment",
            barmode='group',
            height=350,
            xaxis_title="Segment",
            yaxis_title="Montant (€)"
        )
        st.plotly_chart(fig_segments, use_container_width=True)
    
    with col_seg2:
        # Répartition clients par segment
        fig_segments_pie = px.pie(
            df_segments,
            values='nb_clients',
            names='segment',
            title="Répartition des Clients",
            color_discrete_sequence=px.colors.sequential.Blues_r,
            height=350
        )
        st.plotly_chart(fig_segments_pie, use_container_width=True)
    
    # Analyse détaillée des segments
    st.markdown("### 📋 Analyse détaillée par segment")
    
    # Calcul du panier moyen par segment
    df_segments['panier_moyen_calc'] = df_segments['ca'] / df_segments['nb_commandes']
    
    st.dataframe(
        df_segments[['segment', 'ca', 'profit', 'nb_clients', 'nb_commandes', 'panier_moyen']].rename(columns={
            'segment': 'Segment',
            'ca': 'CA (€)',
            'profit': 'Profit (€)',
            'nb_clients': 'Clients',
            'nb_commandes': 'Commandes',
            'panier_moyen': 'Panier Moyen (€)'
        }),
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.subheader("📈 Évolution Performance Commerciale")
    
    granularite = st.radio("Période d'analyse", ['jour', 'mois'], horizontal=True)
    
    temporal = appeler_api("/kpi/temporel", params={'periode': granularite})
    df_temporal = pd.DataFrame(temporal)
    
    # Graphique évolution commandes et panier moyen
    fig_commercial = go.Figure()
    
    # Ajouter les commandes sur l'axe Y principal
    fig_commercial.add_trace(
        go.Bar(
            name='Commandes',
            x=df_temporal['periode'],
            y=df_temporal['nb_commandes'],
            marker_color='#3498db',
            yaxis='y'
        )
    )
    
    # Calculer et ajouter le panier moyen sur l'axe Y secondaire
    df_temporal['panier_moyen_temp'] = df_temporal['ca'] / df_temporal['nb_commandes']
    
    fig_commercial.add_trace(
        go.Scatter(
            name='Panier Moyen',
            x=df_temporal['periode'],
            y=df_temporal['panier_moyen_temp'],
            mode='lines+markers',
            line=dict(color='#e74c3c', width=3),
            yaxis='y2'
        )
    )
    
    # Configuration des axes
    fig_commercial.update_layout(
        title="Évolution Commandes et Panier Moyen",
        xaxis_title="Période",
        yaxis=dict(title="Nombre de Commandes", side="left"),
        yaxis2=dict(title="Panier Moyen (€)", side="right", overlaying="y"),
        height=400,
        showlegend=True
    )
    
    st.plotly_chart(fig_commercial, use_container_width=True)
    
    # Statistiques de période
    col_perf1, col_perf2, col_perf3, col_perf4 = st.columns(4)
    
    with col_perf1:
        st.metric("📊 Commandes moy/période", f"{int(df_temporal['nb_commandes'].mean()):,}")
    with col_perf2:
        st.metric("🛒 Panier moyen global", f"{df_temporal['panier_moyen_temp'].mean():.0f} €")
    with col_perf3:
        best_period = df_temporal.loc[df_temporal['nb_commandes'].idxmax()]
        st.metric("🏆 Meilleure période", best_period['periode'])
    with col_perf4:
        st.metric("📈 Croissance commandes", f"{((df_temporal['nb_commandes'].iloc[-1] / df_temporal['nb_commandes'].iloc[0] - 1) * 100):+.1f}%")

# Footer
st.divider()
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>💼 <b>Dashboard Responsable Commercial</b> | Performance commerciale et fidélisation</p>
</div>
""", unsafe_allow_html=True)