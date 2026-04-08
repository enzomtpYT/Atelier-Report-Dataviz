"""
Dashboard Responsable Produit - Gestion Produit et Marketing
📦 Analyse des produits, catégories et tendances saisonnières
📊 Performance marketing et optimisation du catalogue
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import requests
import pandas as pd
from datetime import datetime
import os

# Configuration
st.set_page_config(page_title="Produit", page_icon="📦", layout="wide")

# Styles
st.markdown("""
<style>
    .produit-header {
        background: linear-gradient(90deg, #2ecc71, #27ae60);
        color: white; padding: 20px; border-radius: 10px; margin-bottom: 20px;
    }
    .metric-produit { border-left: 4px solid #2ecc71; }
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
<div class="produit-header">
    <h1>📦 Dashboard Responsable Produit</h1>
    <p>Gestion catalogue, performance produits et analyse marketing</p>
</div>
""", unsafe_allow_html=True)

# Sidebar filtres
st.sidebar.header("📦 Filtres Produit")
valeurs_filtres = appeler_api("/filters/valeurs")

date_min = datetime.strptime(valeurs_filtres['plage_dates']['min'], '%Y-%m-%d')
date_max = datetime.strptime(valeurs_filtres['plage_dates']['max'], '%Y-%m-%d')

col1, col2 = st.sidebar.columns(2)
with col1:
    date_debut = st.date_input("Du", value=date_min, min_value=date_min, max_value=date_max)
with col2:
    date_fin = st.date_input("Au", value=date_max, min_value=date_min, max_value=date_max)

categorie = st.sidebar.selectbox("Catégorie", ["Toutes"] + valeurs_filtres['categories'])

params_filtres = {
    'date_debut': date_debut.strftime('%Y-%m-%d'),
    'date_fin': date_fin.strftime('%Y-%m-%d')
}
if categorie != "Toutes": 
    params_filtres['categorie'] = categorie

# KPIs Produit
st.header("📊 KPIs Produit & Marketing")

kpi_data = appeler_api("/kpi/globaux", params=params_filtres)
kpi_executif = appeler_api("/kpi/executif")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("📦 Quantité Vendue", formater_nombre(kpi_data['quantite_vendue']))

with col2:
    st.metric("💰 CA Total", formater_euro(kpi_data['ca_total']))

with col3:
    st.metric("💵 Profit Produits", formater_euro(kpi_data['profit_total']))

with col4:
    articles_par_commande = kpi_data['quantite_vendue'] / kpi_data['nb_commandes'] if kpi_data['nb_commandes'] > 0 else 0
    st.metric("📊 Articles/Commande", f"{articles_par_commande:.2f}")

col5, col6 = st.columns(2)
with col5:
    st.metric("↩️ Lignes en perte (proxy retours)", f"{kpi_executif['taux_lignes_perte_pct']:.1f}%")
with col6:
    st.metric("⚠️ Commandes en perte", f"{kpi_executif['taux_commandes_perte_pct']:.1f}%")

st.divider()

# Analyses détaillées
tab1, tab2, tab3 = st.tabs(["🏆 Top Produits", "📦 Catégories", "📊 Saisonnalité"])

with tab1:
    st.subheader("🏅 Performance des Produits")
    
    col_tri, col_limite = st.columns([3, 1])
    with col_tri:
        critere_tri = st.radio(
            "Trier par",
            options=['ca', 'profit', 'quantite'],
            format_func=lambda x: {'ca': '💰 CA', 'profit': '💵 Profit', 'quantite': '📦 Quantité'}[x],
            horizontal=True
        )
    with col_limite:
        nb_produits = st.number_input("Afficher", min_value=5, max_value=20, value=15, step=5)
    
    top_produits = appeler_api("/kpi/produits/top", params={'limite': nb_produits, 'tri_par': critere_tri})
    df_produits = pd.DataFrame(top_produits)
    
    # Graphique principal
    labels_criteres = {'ca': 'CA', 'profit': 'Profit', 'quantite': 'Quantité'}
    
    fig_produits = px.bar(
        df_produits,
        x=critere_tri,
        y='produit',
        color='categorie',
        orientation='h',
        title=f"Top {nb_produits} Produits par {labels_criteres[critere_tri]}",
        labels={
            'ca': 'Chiffre d\'affaires (€)',
            'profit': 'Profit (€)',
            'quantite': 'Quantité vendue',
            'produit': 'Produit',
            'categorie': 'Catégorie'
        },
        color_discrete_sequence=px.colors.qualitative.Set2,
        height=600
    )
    fig_produits.update_layout(
        showlegend=True,
        yaxis={'categoryorder':'total ascending'}
    )
    st.plotly_chart(fig_produits, use_container_width=True)
    
    # Tableau détaillé
    st.markdown("### 📋 Tableau détaillé")

    # Calcul de la marge par produit
    df_produits['marge_pct'] = (df_produits['profit'] / df_produits['ca'] * 100).round(2)

    st.dataframe(
        df_produits[['produit', 'categorie', 'ca', 'profit', 'quantite', 'marge_pct']].rename(columns={
            'produit': 'Produit',
            'categorie': 'Catégorie',
            'ca': 'CA (€)',
            'profit': 'Profit (€)',
            'quantite': 'Quantité',
            'marge_pct': 'Marge (%)'
        }),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.subheader("📦 Performance par Catégorie")
    
    categories = appeler_api("/kpi/categories")
    df_cat = pd.DataFrame(categories)
    
    col_cat1, col_cat2 = st.columns(2)
    
    with col_cat1:
        # CA vs Profit par catégorie
        fig_cat = go.Figure()
        fig_cat.add_trace(go.Bar(
            name='CA',
            x=df_cat['categorie'],
            y=df_cat['ca'],
            marker_color='#2ecc71',
            text=df_cat['ca'].apply(lambda x: f"{x:,.0f}€"),
            textposition='outside'
        ))
        fig_cat.add_trace(go.Bar(
            name='Profit',
            x=df_cat['categorie'],
            y=df_cat['profit'],
            marker_color='#27ae60',
            text=df_cat['profit'].apply(lambda x: f"{x:,.0f}€"),
            textposition='outside'
        ))
        fig_cat.update_layout(
            title="CA et Profit par Catégorie",
            barmode='group',
            xaxis_title="Catégorie",
            yaxis_title="Montant (€)",
            height=400
        )
        st.plotly_chart(fig_cat, use_container_width=True)
    
    with col_cat2:
        # Marge par catégorie
        fig_marge = px.bar(
            df_cat,
            x='categorie',
            y='marge_pct',
            title="Marge par Catégorie (%)",
            labels={'categorie': 'Catégorie', 'marge_pct': 'Marge (%)'},
            color='marge_pct',
            color_continuous_scale='Greens',
            text='marge_pct',
            height=400
        )
        fig_marge.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_marge, use_container_width=True)

    if 'taux_lignes_perte_pct' in df_cat.columns:
        st.markdown("### ↩️ Risque de retour/perte par catégorie (proxy)")
        fig_retours = px.bar(
            df_cat,
            x='categorie',
            y='taux_lignes_perte_pct',
            title="Taux de lignes en perte par catégorie (%)",
            labels={'categorie': 'Catégorie', 'taux_lignes_perte_pct': 'Taux lignes en perte (%)'},
            color='taux_lignes_perte_pct',
            color_continuous_scale='OrRd',
            text='taux_lignes_perte_pct',
            height=350
        )
        fig_retours.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig_retours, use_container_width=True)
    
    # Analyse sous-catégories
    st.markdown("### 🔍 Zoom sur les Sous-catégories")
    
    sous_categories = appeler_api("/kpi/sous-categories")
    df_sous_cat = pd.DataFrame(sous_categories)
    
    # Treemap des sous-catégories
    fig_treemap = px.treemap(
        df_sous_cat,
        path=['categorie', 'sous_categorie'],
        values='ca',
        color='marge_pct',
        color_continuous_scale='RdYlGn',
        color_continuous_midpoint=10,
        title="Répartition CA par Sous-catégorie (couleur = marge %)",
        labels={'ca': 'CA', 'marge_pct': 'Marge (%)'},
        height=500
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

with tab3:
    st.subheader("📊 Analyse de Saisonnalité")
    
    saisonnalite = appeler_api("/kpi/saisonnalite")
    
    # KPIs saisonnalité
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.metric("📅 Meilleur Jour", saisonnalite['meilleur_jour'])
    with col_s2:
        st.metric("📆 Meilleur Mois", saisonnalite['meilleur_mois'])
    with col_s3:
        pic = saisonnalite['pic_ventes']
        st.metric("🔥 Pic de Ventes", pic['date'])
    
    # Graphiques saisonnalité
    col_jour, col_mois = st.columns(2)
    
    with col_jour:
        st.markdown("### 📅 Performance par Jour de la Semaine")
        df_jour = pd.DataFrame(saisonnalite['performance_jour_semaine'])
        
        fig_jour = px.bar(
            df_jour,
            x='jour',
            y='ca',
            color='nb_commandes',
            color_continuous_scale='Greens',
            labels={'jour': 'Jour', 'ca': 'CA (€)', 'nb_commandes': 'Nb commandes'},
            title="CA par Jour de la Semaine",
            height=350,
            text='ca'
        )
        fig_jour.update_traces(texttemplate='%{text:,.0f}€', textposition='outside')
        st.plotly_chart(fig_jour, use_container_width=True)
    
    with col_mois:
        st.markdown("### 📆 Performance par Mois")
        df_mois = pd.DataFrame(saisonnalite['performance_mois'])
        
        fig_mois = px.bar(
            df_mois,
            x='mois',
            y='ca',
            color='nb_commandes',
            color_continuous_scale='Greens',
            labels={'mois': 'Mois', 'ca': 'CA (€)', 'nb_commandes': 'Nb commandes'},
            title="CA par Mois",
            height=350,
            text='ca'
        )
        fig_mois.update_traces(texttemplate='%{text:,.0f}€', textposition='outside')
        st.plotly_chart(fig_mois, use_container_width=True)
    
    # Insights saisonniers
    st.markdown("### 🎯 Insights Marketing Saisonniers")
    
    col_insight1, col_insight2 = st.columns(2)
    
    with col_insight1:
        # Performance hebdomadaire
        meilleur_jour = df_jour.loc[df_jour['ca'].idxmax()]
        pire_jour = df_jour.loc[df_jour['ca'].idxmin()]
        
        st.info(f"📈 **Jour le plus performant** : {meilleur_jour['jour']} ({meilleur_jour['ca']:,.0f} €)")
        st.warning(f"📉 **Jour le moins performant** : {pire_jour['jour']} ({pire_jour['ca']:,.0f} €)")
    
    with col_insight2:
        # Performance mensuelle
        meilleur_mois = df_mois.loc[df_mois['ca'].idxmax()]
        pire_mois = df_mois.loc[df_mois['ca'].idxmin()]
        
        st.info(f"📈 **Mois le plus performant** : {meilleur_mois['mois']} ({meilleur_mois['ca']:,.0f} €)")
        st.warning(f"📉 **Mois le moins performant** : {pire_mois['mois']} ({pire_mois['ca']:,.0f} €)")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #7f8c8d;'>
    <p>📦 <b>Dashboard Responsable Produit</b> | Optimisation catalogue et marketing</p>
</div>
""", unsafe_allow_html=True)