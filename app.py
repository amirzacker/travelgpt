import os
import streamlit as st
from openai import OpenAI
import requests
import json
from datetime import datetime
import folium
from streamlit_folium import folium_static

# Chargement des clés API
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")

# Initialisation des clients API
nvidia_client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)

# Configuration de l'application Streamlit
st.set_page_config(
    page_title="TravelGPT Pro 🌍",
    page_icon="✈️",
    layout="wide"
)

# Style CSS avancé
st.markdown("""
    <style>
    .main {background: #f8f9fa;color: #333;}
    .stChatInput input {border-radius: 15px !important;}
    .chat-message {padding: 1.5rem; border-radius: 15px; margin: 1rem 0;}
    .user-message {background: #e3f2fd; border: 1px solid #bbdefb; color: #0d47a1;}
    .ai-message {background: #fff3e0; border: 1px solid #ffe0b2;color: #333;}
    .weather-card {padding: 1rem; background: white; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); color: #333; text-align: center; transition: transform 0.3s ease;}
    .weather-card:hover {transform: scale(1.05);}
    h1, h2, h3, h4 {color: #1a73e8;}
    .stMarkdown, .stTextArea, .stTextInput {
        color: #333;
    }
    .css-1aumxhk {
        background-color: #f8f9fa;
    }
    </style>
""", unsafe_allow_html=True)


# Fonctions principales
def get_geolocation(city):
    """Obtenir les coordonnées GPS d'une ville"""
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={OPENWEATHER_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data[0] if data else None


def get_weather_forecast(lat, lon):
    """Obtenir les prévisions météo sur 5 jours"""
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=fr"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else None


def create_interactive_map(locations):
    """Créer une carte interactive avec Folium"""
    map_center = [locations[0]['lat'], locations[0]['lon']]
    m = folium.Map(location=map_center, zoom_start=12)

    for idx, loc in enumerate(locations, 1):
        folium.Marker(
            location=[loc['lat'], loc['lon']],
            popup=f"Jour {idx}: {loc['name']}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)

    return m


# Interface utilisateur
st.title("🌍 TravelGPT Pro - Assistant de Voyage")
st.markdown("---")
st.markdown("### Comment utiliser TravelGPT?")
st.markdown("""
1. 📅 Choisissez votre date de départ
2. ⏳ Sélectionnez la durée du séjour
3. 💰 Définissez votre budget
4. 🎯 Choisissez vos centres d'intérêt
5. 🌍 Entrez votre destination de rêve
6. 🚀 Parlez à votre assistant de voyage...
""")

# Initialisation de l'historique de chat
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Bonjour ! Où souhaitez-vous voyager aujourd'hui ? 🌎"}
    ]

# Panneau latéral pour les paramètres
with st.sidebar:
    st.header("⚙️ Paramètres du voyage")
    start_date = st.date_input("Date de départ 📅", datetime.now())
    days = st.slider("Nombre de jours ⏳", 1, 14, 7)
    budget = st.selectbox("Budget 💰", ["Économique", "Moyen", "Luxe"])
    interests = st.multiselect("Centres d'intérêt 🎯",
                               ["Histoire", "Nature", "Gastronomie", "Art", "Aventure", "Shopping"])

# Affichage de l'historique de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Gestion de l'entrée utilisateur
if prompt := st.chat_input("Destination de rêve 🌍 Paris, Tokyo..."):
    # Ajout du message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Génération de la réponse
    with st.spinner("Recherche des meilleures options..."):
        try:
            # Appel à l'API NVIDIA pour Llama3-70B
            response = nvidia_client.chat.completions.create(
                model="meta/llama3-70b-instruct",
                messages=[
                    {"role": "system", "content": f"""
                    Vous êtes un expert en voyages. Créez un itinéraire détaillé avec:
                    - Des lieux en accord avec: {', '.join(interests)}
                    - Budget: {budget}
                    - Durée: {days} jours
                    - Date de départ: {start_date}
                    """},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=1500
            )

            ai_response = response.choices[0].message.content

            # Extraction des lieux pour la carte
            locations = []
            geo_data = get_geolocation(prompt.split()[-1])
            if geo_data:
                locations.append({
                    'name': geo_data['name'],
                    'lat': geo_data['lat'],
                    'lon': geo_data['lon']
                })

            # Ajout des éléments à la réponse
            full_response = f"{ai_response}\n\n🌤️ Météo prévue: 25°C, Ensoleillé\n📌 Carte interactive ci-dessous:"

        except Exception as e:
            full_response = f"Erreur: {str(e)}"

    # Affichage de la réponse de l'IA
    with st.chat_message("assistant"):
        st.markdown(full_response)

        if geo_data:
            # Affichage météo
            weather = get_weather_forecast(geo_data['lat'], geo_data['lon'])
            if weather:
                st.markdown("### Prévisions météo")
                cols = st.columns(5)
                for i in range(5):
                    with cols[i]:
                        day = weather['list'][i * 8]
                        st.markdown(f"""
                        <div class="weather-card">
                            <b>{datetime.fromtimestamp(day['dt']).strftime('%a')}</b><br>
                            <img src="http://openweathermap.org/img/wn/{day['weather'][0]['icon']}.png" width=40>
                            <br>{day['main']['temp']}°C
                        </div>
                        """, unsafe_allow_html=True)

        # Affichage de la carte
        if locations:
            st.markdown("### Carte interactive")
            m = create_interactive_map(locations)
            folium_static(m, width=700)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Section d'export
st.sidebar.markdown("---")
st.sidebar.download_button(
    label="💾 Exporter l'itinéraire",
    data=json.dumps(st.session_state.messages, indent=2, ensure_ascii=False),
    file_name="travelgpt_itinerary.json",
    mime="application/json")