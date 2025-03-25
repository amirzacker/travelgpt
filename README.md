# TravelGPT - Assistant de Voyage Intelligent
https://travel-pro.streamlit.app/

## Description
TravelGPT est une application web interactive qui utilise l'intelligence artificielle pour aider les utilisateurs à planifier leurs voyages. L'application permet de discuter naturellement avec un assistant virtuel qui peut suggérer des destinations, créer des itinéraires personnalisés, et fournir des informations pratiques sur les lieux à visiter.

## Fonctionnalités

- **Chat interactif** avec un assistant voyage AI
- **Génération d'itinéraires** personnalisés selon vos préférences
- **Visualisation cartographique** des destinations proposées avec marqueurs détaillés
- **Génération d'images** des lieux à visiter
- **Comparaison de prix** vols/hôtels en temps réel
- **Météo intégrée** avec prévisions sur 5 jours
- **Export rapport multi-formats** (PDF professionnel, CSV, JSON)
- **Recommandations d'activités** adaptées à vos centres d'intérêt

## Technologies utilisées

- **Modèle de langage**: NVIDIA Llama2 70B pour le traitement du langage naturel
- **Génération d'images**: Stable Diffusion pour la visualisation des destinations
- **Interface web**: Streamlit pour une application web réactive
- **Cartographie**: Folium pour l'affichage des cartes interactives
- **APIs externes**: OpenWeatherMap pour les données météorologiques, Amadeus API (prix vols)

## Installation

1. Clonez ce dépôt:
```bash
git clone https://github.com/amirzacker/travelgpt
cd travelgpt
```

2. Installez les dépendances:
```bash
pip install -r requirements.txt
```

3. Configurez vos clés API:
Créez un fichier `.env` à la racine du projet:
```
NVIDIA_API_KEY=lé_api_nvidia
OPENWEATHER_API_KEY=clé_api_openweather
AMADEUS_API_KEY=clé_api_amadeus
```

4. Lancez l'application:
```bash
streamlit run app.py
```

## Déploiement

L'application est déployée sur:

- **Streamlit Cloud**: Pour un déploiement rapide et gratuit https://travel-pro.streamlit.app/

## Utilisation

1. Lancez l'application en local ou accédez à l'URL de déploiement
2. Utilisez le panneau latéral pour définir vos préférences de voyage (dates, durée, budget, intérêts)
3. Discutez avec l'assistant en posant des questions ou en décrivant le type de voyage que vous recherchez
4. Consultez l'itinéraire généré, la carte interactive et les images des destinations
5. Affinez vos préférences en continuant la conversation avec l'assistant

## Crédits

- Modèles AI: NVIDIA NGC Catalog (https://catalog.ngc.nvidia.com/)
- Données cartographiques: OpenStreetMap
- Données météo: OpenWeatherMap
- Données de prix: Amadeus API
- Images: Stability AI


© 2024 TravelGPT Pro - Réinventons le voyage ensemble

AMIR MAHAMAT SAlEH
```

