# 🛒 Superstore BI - API FastAPI + Dashboard Streamlit

Système complet d'analyse Business Intelligence du dataset **Sample Superstore** avec API REST et dashboard interactif.

---

## 👥 Récits Utilisateur

### User Story #1 - Directeur Général (CEO)
**En tant que** Directeur Général de Superstore,
**Je veux** avoir une vue stratégique globale sur les performances de l'entreprise avec les évolutions en temps réel,
**J'ai besoin de :**
- ✅ Analyser la rentabilité avec le profit total et sa progression
- ✅ Voir le CA total avec son évolution en % par rapport à la période précédente
- ✅ Suivre l'activité commerciale via le nombre de commandes et son évolution
- ✅ Voir si je vends des produits qui ne sont pas rentables

### User Story #2 - Responsable Commercial
**En tant que** Responsable Commercial de Superstore,
**Je veux** analyser les performances de vente par segment client et région,
**Afin de** optimiser ma stratégie commerciale et atteindre mes objectifs de vente.
**J'ai besoin de :**
- ✅ Analyser les performances par région pour optimiser mes actions terrain
- ✅ Identifier les top clients et leur contribution au CA
- ✅ Suivre l'évolution du panier moyen
- ✅ Voir mon taux de fidélisation pour pouvoir lancer des campagnes de fidélisations

## 🎯 Résumé Exécutif

### ✅ Points forts
- Base clients solide : 793 clients actifs sur 5 009 commandes
- Panier moyen élevé : 458,61 € (excellent pour du B2B/retail)
- Volume significatif : 37 873 articles vendus
- Performance Technology : catégorie leader avec 17,4 % de marge

### ⚠️ Points d'attention
- Marge globale faible : 12,47 % seulement (critique pour la rentabilité)
- Ratio client/commandes : 6,3 commandes par client (potentiel de fidélisation)
- Géographie concentrée : dépendance forte sur la région West

## 📊 Analyse Détaillée

### 💰 Performance financière
- Chiffre d'affaires : 2,297 M€ (volume respectable)
- Profit : 286 K€ avec seulement 12,47 % de marge
- Diagnostic : revenu fort mais rentabilité à améliorer

### 👥 Analyse client
- Fréquence d'achat : 6,3 commandes/client
- Potentiel : opportunité de fidélisation et de cross-selling
- Recommandation : programme de fidélité et marketing relationnel

### 🌍 Performance géographique
- West : 725 K€ (31,6 % du CA), région leader
- East : 679 K€ (29,6 % du CA), performance solide
- Répartition globalement équilibrée entre les 4 régions

### 📦 Analyse produit
- Technology : star performer (836 K€, 17,4 % de marge)
- Furniture : volume élevé, marge probablement plus faible
- Office Supplies : complète le mix produit

## 🚨 Alertes & Recommandations

### 🚨 Urgences
1. Marge trop faible (12,47 %) : revoir pricing et mix produit
2. Technology porte l'entreprise : diversifier pour réduire le risque
3. Taux de réachat client : améliorer la rétention

### 💡 Actions immédiates
1. Optimiser les marges : focus sur les produits Technology (17,4 %)
2. Mettre en place un programme fidélité : passer de 6,3 à 10+ commandes/client
3. Renforcer l'expansion géographique : réduire la dépendance régionale
4. Analyser les pertes : identifier les catégories déficitaires

### 🎯 Objectifs suggérés
- Marge cible : passer de 12,47 % à 15 %+
- Fidélisation : +50 % de récurrence client
- Croissance : +20 % de CA en conservant la marge

---

## 🎯 Objectifs pédagogiques

Ce projet permet d'apprendre :
- ✅ Développement d'une **API REST** avec FastAPI
- ✅ Création de **dashboards interactifs** avec Streamlit/Plotly
- ✅ Analyse de données avec **Pandas**
- ✅ Calcul de **KPI e-commerce**
- ✅ Tests unitaires avec **pytest**

---

## 📊 KPI implémentés

### 🔹 KPI Globaux
- 💰 Chiffre d'affaires total
- 🧾 Nombre de commandes
- 👤 Nombre de clients uniques
- 🛒 Panier moyen
- 📦 Quantité vendue
- 💵 Profit total
- 📈 Marge moyenne

### 🔹 KPI Produits
- 🏆 Top 10 produits par CA/Profit/Quantité
- 📦 CA par catégorie
- 💹 Marge par produit
- ⚠️ Produits les moins rentables

### 🔹 KPI Clients
- 💎 Top clients par CA
- 🔄 Clients récurrents vs nouveaux
- 📊 Fréquence d'achat
- 💼 Performance par segment

### 🔹 KPI Temporels
- 📅 Évolution du CA par jour/mois/année
- 📈 Comparaison des périodes
- 🌡️ Saisonnalité

### 🔹 KPI Géographiques
- 🌍 CA par région
- 📍 Nombre de clients par zone

---

## 📁 Structure du projet

```
superstore-bi/
│
├── backend/
│   └── main.py              # API FastAPI (endpoints KPI)
│
├── frontend/
│   └── dashboard.py         # Dashboard Streamlit
│
├── tests/
│   └── test_api.py          # Tests unitaires
│
├── requirements.txt         # Dépendances Python
└── README.md                # Ce fichier
```

---

## 🚀 Installation et démarrage

### 1️⃣ Prérequis

- Python 3.8+ installé
- pip installé

### 2️⃣ Installation des dépendances

```bash
# Cloner ou créer le projet
mkdir superstore-bi
cd superstore-bi

# Installer les dépendances
pip install -r requirements.txt
```

### 3️⃣ Démarrer l'API FastAPI

```bash
# Dans un premier terminal
python backend/main.py
```

✅ L'API sera accessible sur **http://localhost:8000**
📚 Documentation Swagger : **http://localhost:8000/docs**

### 4️⃣ Démarrer le Dashboard Streamlit

```bash
# Dans un second terminal
streamlit run frontend/dashboard.py
```

✅ Le dashboard sera accessible sur **http://localhost:8501**



---

## 📖 Utilisation de l'API

### Exemples de requêtes

#### **1. KPI globaux**
```bash
# Sans filtre
curl http://localhost:8000/kpi/globaux

# Avec filtres
curl "http://localhost:8000/kpi/globaux?date_debut=2015-01-01&categorie=Technology"
```

**Réponse** :
```json
{
  "ca_total": 2297200.86,
  "nb_commandes": 5009,
  "nb_clients": 793,
  "panier_moyen": 458.58,
  "quantite_vendue": 37873,
  "profit_total": 286397.02,
  "marge_moyenne": 12.47
}
```

#### **2. Top produits**
```bash
# Top 10 par CA
curl http://localhost:8000/kpi/produits/top

# Top 5 par profit
curl "http://localhost:8000/kpi/produits/top?limite=5&tri_par=profit"
```

#### **3. Performance catégories**
```bash
curl http://localhost:8000/kpi/categories
```

#### **4. Évolution temporelle**
```bash
# Par mois
curl "http://localhost:8000/kpi/temporel?periode=mois"

# Par année
curl "http://localhost:8000/kpi/temporel?periode=annee"
```

#### **5. Performance géographique**
```bash
curl http://localhost:8000/kpi/geographique
```

#### **6. Analyse clients**
```bash
curl "http://localhost:8000/kpi/clients?limite=10"
```

---

## 🎨 Fonctionnalités du Dashboard

### ✅ Filtres interactifs
- 📅 Plage de dates
- 📦 Catégorie
- 🌍 Région
- 👥 Segment client

### ✅ Visualisations Plotly
- 📊 Graphiques en barres interactifs
- 📈 Courbes d'évolution temporelle
- 🥧 Graphiques circulaires
- 📉 Graphiques combinés

### ✅ KPI Cards
- Affichage en temps réel
- Mise en forme automatique (€, %, nombres)
- Organisation claire

### ✅ Tabs organisés
- 🏆 Produits
- 📦 Catégories
- 📅 Temporel
- 🌍 Géographique

---

## 🗃️ Dataset utilisé

**Source** : [Sample Superstore sur GitHub](https://github.com/leonism/sample-superstore)

**Colonnes principales** :
- `Order ID` : Identifiant de commande
- `Order Date` : Date de commande
- `Customer ID` : Identifiant client
- `Product Name` : Nom du produit
- `Category` / `Sub-Category` : Catégorie
- `Sales` : Chiffre d'affaires
- `Quantity` : Quantité
- `Discount` : Remise
- `Profit` : Profit
- `Region` : Région géographique

**Période** : 2014-2017
**Taille** : ~10 000 lignes


---

## 🔧 Personnalisation

### Ajouter un nouveau KPI

**1. Dans l'API (`backend/main.py`)** :
```python
@app.get("/kpi/mon_nouveau_kpi", tags=["KPI"])
def get_mon_nouveau_kpi():
    # Votre calcul ici
    resultat = df.groupby('colonne').sum()
    return resultat.to_dict('records')
```

**2. Dans le dashboard (`frontend/dashboard.py`)** :
```python
# Appeler l'API
data = appeler_api("/kpi/mon_nouveau_kpi")

# Créer la visualisation
fig = px.bar(data, x='colonne', y='valeur')
st.plotly_chart(fig)
```

---

## 🐛 Résolution de problèmes

### ❌ Erreur "Connection refused"
➡️ Vérifiez que l'API est démarrée : `python backend/main.py`

### ❌ Erreur "Module not found"
➡️ Installez les dépendances : `pip install -r requirements.txt`

### ❌ Dashboard vide
➡️ Vérifiez l'URL de l'API dans `dashboard.py` (ligne 41)

### ❌ Erreur de chargement du dataset
➡️ Vérifiez votre connexion internet (le CSV est téléchargé depuis GitHub)

---

## 📚 Documentation complète

### **FastAPI**
- [Documentation officielle](https://fastapi.tiangolo.com/)
- [Tutoriels](https://fastapi.tiangolo.com/tutorial/)

### **Streamlit**
- [Documentation officielle](https://docs.streamlit.io/)
- [Galerie d'exemples](https://streamlit.io/gallery)

### **Plotly**
- [Documentation Python](https://plotly.com/python/)
- [Galerie de graphiques](https://plotly.com/python/basic-charts/)

### **Pandas**
- [Documentation officielle](https://pandas.pydata.org/docs/)
- [10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html)

---
