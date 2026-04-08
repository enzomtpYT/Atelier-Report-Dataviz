"""
API FastAPI pour l'analyse du dataset Superstore
🎯 Niveau débutant - Code simple et bien commenté
📊 Tous les KPI e-commerce implémentés
"""

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from datetime import datetime
import pandas as pd
import numpy as np
from pydantic import BaseModel
import logging

# Configuration du logger pour faciliter le débogage
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'application FastAPI
app = FastAPI(
    title="Superstore BI API",
    description="API d'analyse Business Intelligence pour le dataset Superstore",
    version="1.0.0",
    docs_url="/docs",  # Documentation Swagger accessible via /docs
    redoc_url="/redoc"  # Documentation ReDoc accessible via /redoc
)

# Configuration CORS pour permettre les appels depuis Streamlit
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En production, spécifier l'URL exacte de Streamlit
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === CHARGEMENT DES DONNÉES ===

# URL et chemin local du dataset Superstore
DATASET_URL = "https://raw.githubusercontent.com/leonism/sample-superstore/master/data/superstore.csv"
DATASET_LOCAL_PATH = "data/superstore.csv"

def load_data() -> pd.DataFrame:
    """
    Charge le dataset Superstore depuis un fichier local ou GitHub
    Nettoie et prépare les données pour l'analyse
    
    Returns:
        pd.DataFrame: Dataset nettoyé et prêt à l'emploi
    """
    import os
    try:
        # Tentative de chargement local d'abord (plus rapide et évite les erreurs DNS)
        if os.path.exists(DATASET_LOCAL_PATH):
            logger.info(f"Chargement du dataset local depuis {DATASET_LOCAL_PATH}")
            df = pd.read_csv(DATASET_LOCAL_PATH, encoding='latin-1')
        else:
            logger.info(f"Fichier local non trouvé. Chargement depuis {DATASET_URL}")
            df = pd.read_csv(DATASET_URL, encoding='latin-1')
        
        # Nettoyage des noms de colonnes (suppression espaces)
        df.columns = df.columns.str.strip()
        
        # Conversion des dates au format datetime
        df['Order Date'] = pd.to_datetime(df['Order Date'])
        df['Ship Date'] = pd.to_datetime(df['Ship Date'])
        
        # Suppression des lignes avec valeurs manquantes critiques
        df = df.dropna(subset=['Order ID', 'Customer ID', 'Sales'])
        
        logger.info(f"✅ Dataset chargé : {len(df)} commandes")
        return df
        
    except Exception as e:
        logger.error(f"❌ Erreur lors du chargement des données : {e}")
        raise HTTPException(status_code=500, detail=f"Erreur de chargement : {str(e)}")

# Chargement des données au démarrage de l'application
df = load_data()

# === MODÈLES PYDANTIC (pour la validation des réponses) ===

class KPIGlobaux(BaseModel):
    """Modèle pour les KPI globaux"""
    ca_total: float
    nb_commandes: int
    nb_clients: int
    panier_moyen: float
    quantite_vendue: int
    profit_total: float
    marge_moyenne: float

class ProduitTop(BaseModel):
    """Modèle pour les produits top performers"""
    produit: str
    categorie: str
    ca: float
    quantite: int
    profit: float

class CategoriePerf(BaseModel):
    """Modèle pour la performance par catégorie"""
    categorie: str
    ca: float
    profit: float
    nb_commandes: int
    marge_pct: float

class ComparaisonPeriode(BaseModel):
    """Modèle pour la comparaison de périodes"""
    ca_actuel: float
    ca_precedent: float
    evolution_ca_pct: float
    profit_actuel: float
    profit_precedent: float
    evolution_profit_pct: float
    commandes_actuel: int
    commandes_precedent: int
    evolution_commandes_pct: float
    tendance: str  # "hausse", "baisse", "stable"

class Rentabilite(BaseModel):
    """Modèle pour les indicateurs de rentabilité"""
    ca_par_client: float
    profit_par_commande: float
    nb_produits_negatifs: int
    pct_produits_negatifs: float
    ratio_profit_ca: float
    top_rentables: List[Dict[str, Any]]
    flop_rentables: List[Dict[str, Any]]

class Saisonnalite(BaseModel):
    """Modèle pour l'analyse de saisonnalité"""
    performance_jour_semaine: List[Dict[str, Any]]
    performance_mois: List[Dict[str, Any]]
    meilleur_jour: str
    meilleur_mois: str
    pic_ventes: Dict[str, Any]

class Insight(BaseModel):
    """Modèle pour un insight de storytelling"""
    type: str  # "principal", "attention", "tendance", "recommandation"
    titre: str
    message: str
    icone: str

class StorytellingResponse(BaseModel):
    """Modèle pour la réponse storytelling complète"""
    resume_principal: str
    insights: List[Insight]
    alertes: List[Insight]
    recommandations: List[str]


class KPIExecutif(BaseModel):
    """Modèle pour les KPI exécutifs et financiers (avec proxys)."""
    croissance_mensuelle_moyenne_pct: float
    croissance_annuelle_pct: float
    roi_global_pct: float
    projection_ca_prochain_mois: float
    taux_clients_recurrents_pct: float
    ltv_moyen_proxy: float
    taux_lignes_perte_pct: float
    taux_commandes_perte_pct: float

# === FONCTIONS UTILITAIRES ===

def filtrer_dataframe(
    df: pd.DataFrame,
    date_debut: Optional[str] = None,
    date_fin: Optional[str] = None,
    categorie: Optional[str] = None,
    region: Optional[str] = None,
    segment: Optional[str] = None
) -> pd.DataFrame:
    """
    Applique les filtres sur le dataframe
    
    Args:
        df: DataFrame source
        date_debut: Date de début (YYYY-MM-DD)
        date_fin: Date de fin (YYYY-MM-DD)
        categorie: Catégorie de produit
        region: Région géographique
        segment: Segment client
        
    Returns:
        pd.DataFrame: DataFrame filtré
    """
    df_filtered = df.copy()
    
    # Filtre par date
    if date_debut:
        df_filtered = df_filtered[df_filtered['Order Date'] >= date_debut]
    if date_fin:
        df_filtered = df_filtered[df_filtered['Order Date'] <= date_fin]
    
    # Filtre par catégorie
    if categorie and categorie != "Toutes":
        df_filtered = df_filtered[df_filtered['Category'] == categorie]
    
    # Filtre par région
    if region and region != "Toutes":
        df_filtered = df_filtered[df_filtered['Region'] == region]
    
    # Filtre par segment
    if segment and segment != "Tous":
        df_filtered = df_filtered[df_filtered['Segment'] == segment]
    
    return df_filtered


def calculer_projection_ca_prochain_mois(df_source: pd.DataFrame, nb_mois: int = 12) -> float:
    """
    Calcule une projection simple du CA du mois suivant via régression linéaire.
    """
    mensuel = df_source.groupby(df_source['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
    mensuel.columns = ['periode', 'ca']
    mensuel = mensuel.sort_values('periode').tail(nb_mois).reset_index(drop=True)

    if mensuel.empty:
        return 0.0
    if len(mensuel) == 1:
        return float(mensuel.loc[0, 'ca'])

    x = pd.Series(range(len(mensuel)), dtype='float64')
    y = mensuel['ca'].astype('float64')

    # Polyfit renvoie pente/interception pour une tendance linéaire simple
    pente, interception = np.polyfit(x, y, 1)
    projection = pente * len(mensuel) + interception
    return float(max(projection, 0.0))

# === ENDPOINTS API ===

@app.get("/", tags=["Info"])
def root():
    """
    Endpoint racine - Informations sur l'API
    """
    return {
        "message": "🛒 API Superstore BI",
        "version": "1.0.0",
        "dataset": "Sample Superstore",
        "nb_lignes": len(df),
        "periode": {
            "debut": df['Order Date'].min().strftime('%Y-%m-%d'),
            "fin": df['Order Date'].max().strftime('%Y-%m-%d')
        },
        "endpoints": {
            "documentation": "/docs",
            "kpi_globaux": "/kpi/globaux",
            "top_produits": "/kpi/produits/top",
            "categories": "/kpi/categories",
            "evolution_temporelle": "/kpi/temporel",
            "performance_geo": "/kpi/geographique",
            "analyse_clients": "/kpi/clients"
        }
    }

@app.get("/kpi/globaux", response_model=KPIGlobaux, tags=["KPI"])
def get_kpi_globaux(
    date_debut: Optional[str] = Query(None, description="Date début (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin (YYYY-MM-DD)"),
    categorie: Optional[str] = Query(None, description="Catégorie produit"),
    region: Optional[str] = Query(None, description="Région"),
    segment: Optional[str] = Query(None, description="Segment client")
):
    """
    📊 KPI GLOBAUX
    
    Calcule les indicateurs clés globaux :
    - Chiffre d'affaires total
    - Nombre de commandes
    - Nombre de clients uniques
    - Panier moyen
    - Quantité totale vendue
    - Profit total
    - Marge moyenne (%)
    """
    # Application des filtres
    df_filtered = filtrer_dataframe(df, date_debut, date_fin, categorie, region, segment)
    
    # Calcul des KPI
    ca_total = df_filtered['Sales'].sum()
    nb_commandes = df_filtered['Order ID'].nunique()
    nb_clients = df_filtered['Customer ID'].nunique()
    panier_moyen = ca_total / nb_commandes if nb_commandes > 0 else 0
    quantite_vendue = int(df_filtered['Quantity'].sum())
    profit_total = df_filtered['Profit'].sum()
    marge_moyenne = (profit_total / ca_total * 100) if ca_total > 0 else 0
    
    return KPIGlobaux(
        ca_total=round(ca_total, 2),
        nb_commandes=nb_commandes,
        nb_clients=nb_clients,
        panier_moyen=round(panier_moyen, 2),
        quantite_vendue=quantite_vendue,
        profit_total=round(profit_total, 2),
        marge_moyenne=round(marge_moyenne, 2)
    )

@app.get("/kpi/produits/top", tags=["KPI"])
def get_top_produits(
    limite: int = Query(10, ge=1, le=50, description="Nombre de produits à retourner"),
    tri_par: str = Query("ca", regex="^(ca|profit|quantite)$", description="Critère de tri")
):
    """
    🏆 TOP PRODUITS
    
    Retourne les meilleurs produits selon le critère choisi :
    - ca : Chiffre d'affaires
    - profit : Profit
    - quantite : Quantité vendue
    """
    # Agrégation par produit
    produits = df.groupby(['Product Name', 'Category']).agg({
        'Sales': 'sum',
        'Quantity': 'sum',
        'Profit': 'sum'
    }).reset_index()
    
    # Tri selon le critère
    if tri_par == "ca":
        produits = produits.sort_values('Sales', ascending=False)
    elif tri_par == "profit":
        produits = produits.sort_values('Profit', ascending=False)
    else:  # quantite
        produits = produits.sort_values('Quantity', ascending=False)
    
    # Sélection du top
    top = produits.head(limite)
    
    # Formatage de la réponse
    result = []
    for _, row in top.iterrows():
        result.append({
            "produit": row['Product Name'],
            "categorie": row['Category'],
            "ca": round(row['Sales'], 2),
            "quantite": int(row['Quantity']),
            "profit": round(row['Profit'], 2)
        })
    
    return result

@app.get("/kpi/categories", tags=["KPI"])
def get_performance_categories():
    """
    📦 PERFORMANCE PAR CATÉGORIE
    
    Analyse la performance de chaque catégorie :
    - CA total
    - Profit
    - Nombre de commandes
    - Marge (%)
    """
    # Agrégation par catégorie
    categories = df.groupby('Category').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()

    # Proxy de risque retour : lignes à profit négatif et commandes en perte
    retours_proxy = df.assign(ligne_perte=df['Profit'] < 0).groupby('Category').agg({
        'ligne_perte': 'mean'
    }).reset_index()
    retours_proxy.columns = ['Category', 'taux_lignes_perte_pct']
    retours_proxy['taux_lignes_perte_pct'] = (retours_proxy['taux_lignes_perte_pct'] * 100).round(2)
    
    # Calcul de la marge
    categories['marge_pct'] = (categories['Profit'] / categories['Sales'] * 100).round(2)

    categories = categories.merge(retours_proxy, on='Category', how='left')
    
    # Renommage des colonnes
    categories.columns = ['categorie', 'ca', 'profit', 'nb_commandes', 'quantite', 'marge_pct', 'taux_lignes_perte_pct']
    
    # Tri par CA décroissant
    categories = categories.sort_values('ca', ascending=False)
    
    return categories.to_dict('records')


@app.get("/kpi/executif", response_model=KPIExecutif, tags=["KPI Avancés"])
def get_kpi_executif():
    """
    🎯 KPI EXÉCUTIFS (incluant des proxys quand la donnée métier n'existe pas)

    - Croissance mensuelle moyenne
    - Croissance annuelle (dernière année vs précédente)
    - ROI global proxy (Profit / Sales)
    - Projection CA mois prochain (tendance linéaire)
    - Taux de clients récurrents
    - LTV moyen proxy (CA / clients)
    - Taux de lignes et commandes en perte (proxy retours/remboursements)
    """
    # Croissance mensuelle
    df_mensuel = df.groupby(df['Order Date'].dt.to_period('M'))['Sales'].sum().reset_index()
    df_mensuel.columns = ['periode', 'ca']
    df_mensuel = df_mensuel.sort_values('periode')
    df_mensuel['croissance_pct'] = df_mensuel['ca'].pct_change() * 100
    croissance_mensuelle_moyenne_pct = df_mensuel['croissance_pct'].dropna().mean()

    # Croissance annuelle
    df_annuel = df.groupby(df['Order Date'].dt.year)['Sales'].sum().reset_index()
    df_annuel.columns = ['annee', 'ca']
    df_annuel = df_annuel.sort_values('annee')
    if len(df_annuel) >= 2 and df_annuel.iloc[-2]['ca'] > 0:
        croissance_annuelle_pct = ((df_annuel.iloc[-1]['ca'] - df_annuel.iloc[-2]['ca']) / df_annuel.iloc[-2]['ca']) * 100
    else:
        croissance_annuelle_pct = 0.0

    # ROI global proxy
    ca_total = df['Sales'].sum()
    profit_total = df['Profit'].sum()
    roi_global_pct = (profit_total / ca_total * 100) if ca_total > 0 else 0.0

    # Projection simple du mois suivant
    projection_ca_prochain_mois = calculer_projection_ca_prochain_mois(df)

    # Fidélisation et LTV proxy
    clients = df.groupby('Customer ID').agg({
        'Order ID': 'nunique',
        'Sales': 'sum'
    }).reset_index()
    total_clients = len(clients)
    clients_recurrents = len(clients[clients['Order ID'] > 1])
    taux_clients_recurrents_pct = (clients_recurrents / total_clients * 100) if total_clients > 0 else 0.0
    ltv_moyen_proxy = (clients['Sales'].sum() / total_clients) if total_clients > 0 else 0.0

    # Proxys retours/remboursements: pertes
    taux_lignes_perte_pct = ((df['Profit'] < 0).mean() * 100) if len(df) > 0 else 0.0
    commandes_profit = df.groupby('Order ID')['Profit'].sum().reset_index()
    taux_commandes_perte_pct = ((commandes_profit['Profit'] < 0).mean() * 100) if len(commandes_profit) > 0 else 0.0

    return KPIExecutif(
        croissance_mensuelle_moyenne_pct=round(float(croissance_mensuelle_moyenne_pct) if pd.notna(croissance_mensuelle_moyenne_pct) else 0.0, 2),
        croissance_annuelle_pct=round(float(croissance_annuelle_pct), 2),
        roi_global_pct=round(float(roi_global_pct), 2),
        projection_ca_prochain_mois=round(float(projection_ca_prochain_mois), 2),
        taux_clients_recurrents_pct=round(float(taux_clients_recurrents_pct), 2),
        ltv_moyen_proxy=round(float(ltv_moyen_proxy), 2),
        taux_lignes_perte_pct=round(float(taux_lignes_perte_pct), 2),
        taux_commandes_perte_pct=round(float(taux_commandes_perte_pct), 2)
    )

@app.get("/kpi/temporel", tags=["KPI"])
def get_evolution_temporelle(
    periode: str = Query('mois', regex='^(jour|mois|annee)$', description="Granularité temporelle")
):
    """
    📈 ÉVOLUTION TEMPORELLE
    
    Analyse l'évolution du CA, profit et commandes dans le temps
    Granularités disponibles : jour, mois, annee
    """
    df_temp = df.copy()
    
    # Création de la colonne période selon la granularité
    if periode == 'jour':
        df_temp['periode'] = df_temp['Order Date'].dt.strftime('%Y-%m-%d')
    elif periode == 'mois':
        df_temp['periode'] = df_temp['Order Date'].dt.strftime('%Y-%m')
    else:  # annee
        df_temp['periode'] = df_temp['Order Date'].dt.strftime('%Y')
    
    # Agrégation
    temporal = df_temp.groupby('periode').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    
    temporal.columns = ['periode', 'ca', 'profit', 'nb_commandes', 'quantite']
    
    # Tri chronologique
    temporal = temporal.sort_values('periode')
    
    return temporal.to_dict('records')

@app.get("/kpi/geographique", tags=["KPI"])
def get_performance_geographique():
    """
    🌍 PERFORMANCE GÉOGRAPHIQUE
    
    Analyse la performance par région :
    - CA par région
    - Profit par région
    - Nombre de clients
    - Nombre de commandes
    """
    geo = df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Customer ID': 'nunique',
        'Order ID': 'nunique'
    }).reset_index()
    
    geo.columns = ['region', 'ca', 'profit', 'nb_clients', 'nb_commandes']
    geo = geo.sort_values('ca', ascending=False)
    
    return geo.to_dict('records')

@app.get("/kpi/clients", tags=["KPI"])
def get_analyse_clients(
    limite: int = Query(10, ge=1, le=100, description="Nombre de top clients")
):
    """
    👥 ANALYSE CLIENTS
    
    Retourne :
    - Top clients par CA
    - Statistiques de récurrence
    - Analyse par segment
    """
    # Top clients
    clients = df.groupby('Customer ID').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Customer Name': 'first'
    }).reset_index()
    
    clients.columns = ['customer_id', 'ca_total', 'profit_total', 'nb_commandes', 'nom']
    clients['valeur_commande_moy'] = (clients['ca_total'] / clients['nb_commandes']).round(2)
    
    top_clients = clients.sort_values('ca_total', ascending=False).head(limite)
    
    # Statistiques de récurrence
    recurrence = {
        "clients_1_achat": len(clients[clients['nb_commandes'] == 1]),
        "clients_recurrents": len(clients[clients['nb_commandes'] > 1]),
        "nb_commandes_moyen": round(clients['nb_commandes'].mean(), 2),
        "total_clients": len(clients)
    }
    
    # Analyse par segment
    segments = df.groupby('Segment').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Customer ID': 'nunique',
        'Order ID': 'nunique'
    }).reset_index()
    segments.columns = ['segment', 'ca', 'profit', 'nb_clients', 'nb_commandes']
    segments['panier_moyen'] = segments.apply(
        lambda row: round(row['ca'] / row['nb_commandes'], 2) if row['nb_commandes'] > 0 else 0,
        axis=1
    )
    
    return {
        "top_clients": top_clients.to_dict('records'),
        "recurrence": recurrence,
        "segments": segments.to_dict('records')
    }

@app.get("/filters/valeurs", tags=["Filtres"])
def get_valeurs_filtres():
    """
    🎯 VALEURS POUR LES FILTRES
    
    Retourne toutes les valeurs uniques disponibles pour les filtres
    """
    return {
        "categories": sorted(df['Category'].unique().tolist()),
        "regions": sorted(df['Region'].unique().tolist()),
        "segments": sorted(df['Segment'].unique().tolist()),
        "etats": sorted(df['State'].unique().tolist()),
        "plage_dates": {
            "min": df['Order Date'].min().strftime('%Y-%m-%d'),
            "max": df['Order Date'].max().strftime('%Y-%m-%d')
        }
    }

@app.get("/data/commandes", tags=["Données brutes"])
def get_commandes(
    limite: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    📋 DONNÉES BRUTES
    
    Retourne les commandes brutes avec pagination
    """
    total = len(df)
    commandes = df.iloc[offset:offset+limite]
    
    # Conversion des dates en string pour JSON
    commandes_dict = commandes.copy()
    commandes_dict['Order Date'] = commandes_dict['Order Date'].dt.strftime('%Y-%m-%d')
    commandes_dict['Ship Date'] = commandes_dict['Ship Date'].dt.strftime('%Y-%m-%d')
    
    return {
        "total": total,
        "limite": limite,
        "offset": offset,
        "data": commandes_dict.to_dict('records')
    }

# === NOUVEAUX ENDPOINTS POUR LE REPORTING ENRICHI ===

@app.get("/kpi/comparaison", response_model=ComparaisonPeriode, tags=["KPI Avancés"])
def get_comparaison_periodes(
    date_debut: Optional[str] = Query(None, description="Date début période actuelle (YYYY-MM-DD)"),
    date_fin: Optional[str] = Query(None, description="Date fin période actuelle (YYYY-MM-DD)")
):
    """
    📊 COMPARAISON DE PÉRIODES
    
    Compare les performances de la période sélectionnée avec la période précédente de même durée.
    Exemple : si on sélectionne janvier 2017, compare avec décembre 2016.
    """
    # Définir les dates par défaut (dernier mois vs mois précédent)
    if not date_fin:
        date_fin_dt = df['Order Date'].max()
    else:
        date_fin_dt = pd.to_datetime(date_fin)
    
    if not date_debut:
        date_debut_dt = date_fin_dt - pd.Timedelta(days=30)
    else:
        date_debut_dt = pd.to_datetime(date_debut)
    
    # Calculer la durée de la période
    duree = (date_fin_dt - date_debut_dt).days
    
    # Période précédente
    date_fin_prec = date_debut_dt - pd.Timedelta(days=1)
    date_debut_prec = date_fin_prec - pd.Timedelta(days=duree)
    
    # Filtrer les données pour chaque période
    df_actuel = df[(df['Order Date'] >= date_debut_dt) & (df['Order Date'] <= date_fin_dt)]
    df_precedent = df[(df['Order Date'] >= date_debut_prec) & (df['Order Date'] <= date_fin_prec)]
    
    # Calculs période actuelle
    ca_actuel = df_actuel['Sales'].sum()
    profit_actuel = df_actuel['Profit'].sum()
    commandes_actuel = df_actuel['Order ID'].nunique()
    
    # Calculs période précédente
    ca_precedent = df_precedent['Sales'].sum()
    profit_precedent = df_precedent['Profit'].sum()
    commandes_precedent = df_precedent['Order ID'].nunique()
    
    # Calcul des évolutions
    evolution_ca = ((ca_actuel - ca_precedent) / ca_precedent * 100) if ca_precedent > 0 else 0
    evolution_profit = ((profit_actuel - profit_precedent) / profit_precedent * 100) if profit_precedent > 0 else 0
    evolution_commandes = ((commandes_actuel - commandes_precedent) / commandes_precedent * 100) if commandes_precedent > 0 else 0
    
    # Déterminer la tendance
    if evolution_ca > 5:
        tendance = "hausse"
    elif evolution_ca < -5:
        tendance = "baisse"
    else:
        tendance = "stable"
    
    return ComparaisonPeriode(
        ca_actuel=round(ca_actuel, 2),
        ca_precedent=round(ca_precedent, 2),
        evolution_ca_pct=round(evolution_ca, 2),
        profit_actuel=round(profit_actuel, 2),
        profit_precedent=round(profit_precedent, 2),
        evolution_profit_pct=round(evolution_profit, 2),
        commandes_actuel=commandes_actuel,
        commandes_precedent=commandes_precedent,
        evolution_commandes_pct=round(evolution_commandes, 2),
        tendance=tendance
    )

@app.get("/kpi/rentabilite", response_model=Rentabilite, tags=["KPI Avancés"])
def get_rentabilite():
    """
    💰 INDICATEURS DE RENTABILITÉ
    
    Analyse approfondie de la rentabilité :
    - CA par client
    - Profit par commande
    - Produits à marge négative
    - Top/Flop produits par rentabilité
    """
    # Indicateurs globaux
    ca_total = df['Sales'].sum()
    profit_total = df['Profit'].sum()
    nb_clients = df['Customer ID'].nunique()
    nb_commandes = df['Order ID'].nunique()
    
    ca_par_client = ca_total / nb_clients if nb_clients > 0 else 0
    profit_par_commande = profit_total / nb_commandes if nb_commandes > 0 else 0
    ratio_profit_ca = (profit_total / ca_total * 100) if ca_total > 0 else 0
    
    # Analyse des produits
    produits = df.groupby('Product Name').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum'
    }).reset_index()
    
    produits['marge_pct'] = (produits['Profit'] / produits['Sales'] * 100).round(2)
    
    # Produits à marge négative
    produits_negatifs = produits[produits['Profit'] < 0]
    nb_produits_negatifs = len(produits_negatifs)
    pct_produits_negatifs = (nb_produits_negatifs / len(produits) * 100) if len(produits) > 0 else 0
    
    # Top 5 les plus rentables
    top_rentables = produits.nlargest(5, 'marge_pct')[['Product Name', 'Sales', 'Profit', 'marge_pct']]
    top_rentables = top_rentables.rename(columns={
        'Product Name': 'produit', 'Sales': 'ca', 'Profit': 'profit'
    }).to_dict('records')
    
    # Flop 5 les moins rentables
    flop_rentables = produits.nsmallest(5, 'marge_pct')[['Product Name', 'Sales', 'Profit', 'marge_pct']]
    flop_rentables = flop_rentables.rename(columns={
        'Product Name': 'produit', 'Sales': 'ca', 'Profit': 'profit'
    }).to_dict('records')
    
    return Rentabilite(
        ca_par_client=round(ca_par_client, 2),
        profit_par_commande=round(profit_par_commande, 2),
        nb_produits_negatifs=nb_produits_negatifs,
        pct_produits_negatifs=round(pct_produits_negatifs, 2),
        ratio_profit_ca=round(ratio_profit_ca, 2),
        top_rentables=top_rentables,
        flop_rentables=flop_rentables
    )

@app.get("/kpi/saisonnalite", response_model=Saisonnalite, tags=["KPI Avancés"])
def get_saisonnalite():
    """
    📅 ANALYSE DE SAISONNALITÉ
    
    Identifie les patterns temporels :
    - Performance par jour de la semaine
    - Performance par mois de l'année
    - Meilleur jour et meilleur mois
    - Pic de ventes
    """
    df_temp = df.copy()
    
    # Ajout des colonnes temporelles
    df_temp['jour_semaine'] = df_temp['Order Date'].dt.day_name()
    df_temp['mois'] = df_temp['Order Date'].dt.month_name()
    df_temp['mois_num'] = df_temp['Order Date'].dt.month
    
    # Performance par jour de la semaine
    jours_ordre = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    jours_fr = ['Lundi', 'Mardi', 'Mercredi', 'Jeudi', 'Vendredi', 'Samedi', 'Dimanche']
    
    perf_jour = df_temp.groupby('jour_semaine').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique'
    }).reindex(jours_ordre).reset_index()
    perf_jour['jour_fr'] = jours_fr
    perf_jour.columns = ['jour_en', 'ca', 'profit', 'nb_commandes', 'jour']
    perf_jour = perf_jour[['jour', 'ca', 'profit', 'nb_commandes']].to_dict('records')
    
    # Performance par mois
    perf_mois = df_temp.groupby(['mois_num', 'mois']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique'
    }).reset_index().sort_values('mois_num')
    perf_mois.columns = ['mois_num', 'mois', 'ca', 'profit', 'nb_commandes']
    perf_mois = perf_mois[['mois', 'ca', 'profit', 'nb_commandes']].to_dict('records')
    
    # Meilleur jour
    df_jour = df_temp.groupby('jour_semaine')['Sales'].sum()
    meilleur_jour_en = df_jour.idxmax()
    meilleur_jour = jours_fr[jours_ordre.index(meilleur_jour_en)]
    
    # Meilleur mois
    df_mois = df_temp.groupby('mois')['Sales'].sum()
    meilleur_mois = df_mois.idxmax()
    
    # Pic de ventes (meilleur jour absolu)
    df_temp['date'] = df_temp['Order Date'].dt.date
    ventes_par_jour = df_temp.groupby('date').agg({
        'Sales': 'sum',
        'Order ID': 'nunique'
    }).reset_index()
    
    pic = ventes_par_jour.loc[ventes_par_jour['Sales'].idxmax()]
    pic_ventes = {
        "date": str(pic['date']),
        "ca": round(pic['Sales'], 2),
        "nb_commandes": int(pic['Order ID'])
    }
    
    return Saisonnalite(
        performance_jour_semaine=perf_jour,
        performance_mois=perf_mois,
        meilleur_jour=meilleur_jour,
        meilleur_mois=meilleur_mois,
        pic_ventes=pic_ventes
    )

@app.get("/kpi/insights", response_model=StorytellingResponse, tags=["KPI Avancés"])
def get_insights():
    """
    📖 DATA STORYTELLING
    
    Génère automatiquement des insights narratifs :
    - Résumé de la performance
    - Points d'attention (alertes)
    - Tendances identifiées
    - Recommandations d'action
    """
    # Calculs de base
    ca_total = df['Sales'].sum()
    profit_total = df['Profit'].sum()
    marge_globale = (profit_total / ca_total * 100) if ca_total > 0 else 0
    nb_commandes = df['Order ID'].nunique()
    nb_clients = df['Customer ID'].nunique()
    
    insights = []
    alertes = []
    recommandations = []
    
    # === INSIGHT PRINCIPAL ===
    resume = f"Le chiffre d'affaires total s'élève à {ca_total:,.0f} € avec un profit de {profit_total:,.0f} € (marge de {marge_globale:.1f}%). "
    resume += f"{nb_clients:,} clients ont passé {nb_commandes:,} commandes."
    
    # === ANALYSE PAR CATÉGORIE ===
    categories = df.groupby('Category').agg({
        'Sales': 'sum',
        'Profit': 'sum'
    }).reset_index()
    categories['marge'] = (categories['Profit'] / categories['Sales'] * 100).round(2)
    
    # Meilleure catégorie
    best_cat = categories.loc[categories['Sales'].idxmax()]
    insights.append(Insight(
        type="tendance",
        titre="Catégorie phare",
        message=f"{best_cat['Category']} génère le plus gros CA ({best_cat['Sales']:,.0f} €) avec une marge de {best_cat['marge']:.1f}%.",
        icone="🏆"
    ))
    
    # Catégorie à problème (marge la plus faible)
    worst_margin_cat = categories.loc[categories['marge'].idxmin()]
    if worst_margin_cat['marge'] < 10:
        alertes.append(Insight(
            type="attention",
            titre="Marge faible",
            message=f"La catégorie {worst_margin_cat['Category']} a une marge de seulement {worst_margin_cat['marge']:.1f}%.",
            icone="⚠️"
        ))
        recommandations.append(f"Analyser les coûts et prix de la catégorie {worst_margin_cat['Category']}.")
    
    # === ANALYSE PAR RÉGION ===
    regions = df.groupby('Region').agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Customer ID': 'nunique'
    }).reset_index()
    regions['marge'] = (regions['Profit'] / regions['Sales'] * 100).round(2)
    
    # Région sous-performante
    worst_region = regions.loc[regions['marge'].idxmin()]
    if worst_region['marge'] < marge_globale - 3:
        alertes.append(Insight(
            type="attention",
            titre="Région sous-performante",
            message=f"La région {worst_region['Region']} affiche une marge de {worst_region['marge']:.1f}%, en dessous de la moyenne ({marge_globale:.1f}%).",
            icone="📍"
        ))
        recommandations.append(f"Optimiser les coûts logistiques vers la région {worst_region['Region']}.")
    
    # Meilleure région
    best_region = regions.loc[regions['Sales'].idxmax()]
    insights.append(Insight(
        type="tendance",
        titre="Région leader",
        message=f"La région {best_region['Region']} est en tête avec {best_region['Sales']:,.0f} € de CA.",
        icone="🌟"
    ))
    
    # === ANALYSE PRODUITS ===
    produits = df.groupby('Product Name')['Profit'].sum()
    produits_negatifs = (produits < 0).sum()
    pct_negatifs = (produits_negatifs / len(produits) * 100)
    
    if pct_negatifs > 10:
        alertes.append(Insight(
            type="attention",
            titre="Produits déficitaires",
            message=f"{produits_negatifs} produits ({pct_negatifs:.1f}%) génèrent des pertes.",
            icone="❌"
        ))
        recommandations.append("Revoir le portefeuille produits : arrêter ou repositionner les références déficitaires.")
    
    # === ANALYSE SEGMENTS ===
    segments = df.groupby('Segment').agg({
        'Sales': 'sum',
        'Customer ID': 'nunique'
    }).reset_index()
    segments['ca_par_client'] = segments['Sales'] / segments['Customer ID']
    
    best_segment = segments.loc[segments['ca_par_client'].idxmax()]
    insights.append(Insight(
        type="principal",
        titre="Segment le plus rentable",
        message=f"Les clients {best_segment['Segment']} dépensent en moyenne {best_segment['ca_par_client']:,.0f} € par client.",
        icone="💎"
    ))
    
    # === RECOMMANDATIONS GÉNÉRALES ===
    if marge_globale < 12:
        recommandations.append("Améliorer la marge globale en négociant les coûts fournisseurs ou en ajustant les prix.")
    
    if len(recommandations) == 0:
        recommandations.append("Maintenir la stratégie actuelle qui montre de bons résultats.")
    
    return StorytellingResponse(
        resume_principal=resume,
        insights=insights,
        alertes=alertes,
        recommandations=recommandations
    )

@app.get("/kpi/sous-categories", tags=["KPI Avancés"])
def get_sous_categories():
    """
    📦 PERFORMANCE PAR SOUS-CATÉGORIE
    
    Drill-down détaillé par sous-catégorie :
    - CA et profit par sous-catégorie
    - Marge par sous-catégorie
    - Classement par performance
    """
    sous_cat = df.groupby(['Category', 'Sub-Category']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Order ID': 'nunique',
        'Quantity': 'sum'
    }).reset_index()
    
    sous_cat['marge_pct'] = (sous_cat['Profit'] / sous_cat['Sales'] * 100).round(2)
    sous_cat.columns = ['categorie', 'sous_categorie', 'ca', 'profit', 'nb_commandes', 'quantite', 'marge_pct']
    sous_cat = sous_cat.sort_values('ca', ascending=False)
    
    # Arrondir les valeurs
    sous_cat['ca'] = sous_cat['ca'].round(2)
    sous_cat['profit'] = sous_cat['profit'].round(2)
    
    return sous_cat.to_dict('records')

# === DÉMARRAGE DU SERVEUR ===

if __name__ == "__main__":
    import uvicorn
    print("🚀 Démarrage de l'API Superstore BI sur http://localhost:8000")
    print("📚 Documentation disponible sur http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)