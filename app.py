import os
import streamlit as st
from openai import OpenAI
import requests
import json
from datetime import datetime
import folium
from streamlit_folium import folium_static
import pandas as pd
from fpdf import FPDF
import base64
import re

# Chargement des clés API
from dotenv import load_dotenv

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")

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
    .image-grid {display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;}
    .stDownloadButton button {
    width: 100%;
    margin: 5px 0;
    border-radius: 10px !important;
    background: #1a73e8 !important;
    color: white !important;
    transition: all 0.3s ease;
    }

    .stDownloadButton button:hover {
        background: #1557b0 !important;
        transform: scale(1.05);
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


def generate_destination_image(prompt: str) -> str:
    """Génère une image à partir d'un texte descriptif"""
    invoke_url = "https://ai.api.nvidia.com/v1/genai/stabilityai/sdxl-turbo"
    headers = {"Authorization": f"Bearer {NVIDIA_API_KEY}", "Accept": "application/json"}
    payload = {"text_prompts": [{"text": prompt}], "seed": 42, "steps": 4}

    response = requests.post(invoke_url, headers=headers, json=payload)
    response.raise_for_status()

    image_data = base64.b64decode(response.json()["artifacts"][0]["base64"])
    filename = f"generated_images/{datetime.now().timestamp()}.png"

    os.makedirs("generated_images", exist_ok=True)
    with open(filename, "wb") as f:
        f.write(image_data)

    return filename


def save_itinerary(itinerary: dict):
    """Sauvegarde l'itinéraire dans la session"""
    if "saved_itineraries" not in st.session_state:
        st.session_state.saved_itineraries = []

    st.session_state.saved_itineraries.append({
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "data": itinerary
    })


import io  # Ajouter en haut du fichier


def create_pdf(itinerary: dict):
    pdf = FPDF()

    # Ajout des polices Unicode (à adapter selon votre chemin)
    pdf.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
    pdf.add_font('DejaVu', 'B', 'fonts/DejaVuSans-Bold.ttf', uni=True)

    pdf.add_page()
    pdf.set_font("DejaVu", size=12)

    # Titre
    pdf.set_font_size(16)
    pdf.cell(0, 10, f"Itinéraire pour {itinerary['destination']}", 0, 1, 'C')
    pdf.ln(10)

    # Contenu des jours
    pdf.set_font_size(12)
    for day in itinerary['days']:
        pdf.set_font('DejaVu', 'B')  # Style gras avec police Unicode
        pdf.cell(0, 10, f"Jour {day['number']}: {day['title']}", 0, 1)
        pdf.set_font('DejaVu', '')  # Retour au style normal
        pdf.multi_cell(0, 8, day['description'].replace('\n', ' '))
        pdf.ln(5)

    buffer = io.BytesIO()
    pdf.output(buffer)
    return buffer.getvalue()

def get_real_time_prices(origin: str, destination: str):
    """Récupère les prix en temps réel via l'API Amadeus"""
    headers = {"Authorization": f"Bearer {AMADEUS_API_KEY}"}
    url = f"https://api.amadeus.com/v2/shopping/flight-offers?originLocationCode={origin}&destinationLocationCode={destination}&departureDate=2024-08-01&adults=1"

    response = requests.get(url, headers=headers)
    return response.json() if response.status_code == 200 else None


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

    # Section des itinéraires sauvegardés
    st.subheader("📁 Itinéraires Sauvegardés")
    if "saved_itineraries" in st.session_state:
        for idx, itinerary in enumerate(st.session_state.saved_itineraries):
            if st.button(f"{itinerary['date']} - {itinerary['data'].get('destination', '')}"):
                st.session_state.current_itinerary = itinerary['data']

# Affichage de l'historique de chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Gestion de l'entrée utilisateur
if prompt := st.chat_input("Destination de rêve 🌍 Paris, Tokyo..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Génération de la réponse
    with st.spinner("Recherche des meilleures options..."):
        try:
            # Appel à l'API NVIDIA
            response = nvidia_client.chat.completions.create(
                model="meta/llama3-70b-instruct",
                messages=[
                    {"role": "system", "content": f"""
                    Générez un itinéraire détaillé STRUCTURÉ en francais avec ce format EXACT pour {days} jours :

                    Jour 1: [Titre du jour]
                    - [Activité matin]
                    - [Activité après-midi]
                    - [Activité soir]

                    Jour 2: [Titre du jour]
                    ...

                    Budget: {budget}
                    Thèmes: {', '.join(interests)}
                    Date: {start_date}
                    """},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=2000
            )

            ai_response = response.choices[0].message.content
            geo_data = get_geolocation(prompt.split()[-1])
            locations = []
            images = []

            # Génération des données supplémentaires
            if geo_data:
                locations.append({
                    'name': geo_data['name'],
                    'lat': geo_data['lat'],
                    'lon': geo_data['lon']
                })

                # Génération d'image
                try:
                    image_path = generate_destination_image(f"Vue touristique de {prompt}")
                    images.append(image_path)
                except Exception as e:
                    st.error(f"Erreur de génération d'image: {str(e)}")

            # Construction de l'itinéraire
            # Remplacer la section de parsing par :
            try:
                days_data = []
                current_day = None
                day_pattern = re.compile(r"Jour (\d+)[:.]?\s*(.*)", re.IGNORECASE)

                for line in ai_response.split('\n'):
                    line = line.strip()
                    day_match = day_pattern.match(line)

                    if day_match:
                        if current_day:
                            days_data.append(current_day)
                        day_num = int(day_match.group(1))
                        current_day = {
                            "number": day_num,
                            "title": day_match.group(2) or f"Jour {day_num}",
                            "description": ""
                        }
                    elif current_day and line:
                        if line.startswith(("- ", "* ")):
                            current_day["description"] += line[2:] + "\n"
                        else:
                            current_day["description"] += line + "\n"

                if current_day:
                    days_data.append(current_day)

                # Alignement avec le nombre de jours demandé
                if len(days_data) > days:
                    days_data = days_data[:days]
                elif len(days_data) < days:
                    for i in range(len(days_data), days):
                        days_data.append({
                            "number": i + 1,
                            "title": f"Jour {i + 1}",
                            "description": "Détails à compléter"
                        })

                itinerary_data = {
                    "destination": prompt,
                    "days": days_data,
                    "weather": get_weather_forecast(geo_data['lat'], geo_data['lon']) if geo_data else {},
                    "prices": get_real_time_prices("PAR", prompt.split()[-1].upper()),
                    "images": images
                }

            except Exception as e:
                st.error(f"Erreur de parsing de l'itinéraire : {str(e)}")
                itinerary_data = {
                    "destination": prompt,
                    "days": [{"number": i + 1, "title": f"Jour {i + 1}", "description": ""} for i in range(days)],
                    "weather": {},
                    "prices": {},
                    "images": []
                }

            # Sauvegarde de l'itinéraire
            save_itinerary(itinerary_data)
            st.session_state.current_itinerary = itinerary_data
            full_response = f"{ai_response}\n\n🌤️ Météo prévue | 📌 Carte interactive | 🖼️ Photos disponibles"

        except Exception as e:
            full_response = f"Erreur: {str(e)}"

    # Affichage de la réponse
    with st.chat_message("assistant"):
        st.markdown(full_response)

        if geo_data:
            # Affichage météo
            if weather := get_weather_forecast(geo_data['lat'], geo_data['lon']):
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

            # Affichage des images
            if images:
                st.markdown("### 🖼️ Galerie des destinations")
                cols = st.columns(3)
                for idx, img_path in enumerate(images):
                    with cols[idx % 3]:
                        st.image(img_path, use_column_width=True)

    st.session_state.messages.append({"role": "assistant", "content": full_response})

# Section d'export
st.sidebar.markdown("---")
st.sidebar.subheader("📤 Exporter l'itinéraire")

# Vérifie s'il y a un itinéraire courant OU le dernier généré
current_itinerary = st.session_state.get('current_itinerary') or \
                    (st.session_state.saved_itineraries[-1]['data'] if st.session_state.get(
                        'saved_itineraries') else None)

if current_itinerary:
    # Export JSON
    json_data = json.dumps(current_itinerary, indent=2, ensure_ascii=False)
    st.sidebar.download_button(
        label="💾 JSON",
        data=json_data,
        file_name="itinerary.json",
        mime="application/json"
    )

    # Export CSV
    # Modifier l'export CSV :
    csv_data = pd.DataFrame(current_itinerary['days']).to_csv(
        index=False,
        encoding='utf-8-sig',
        sep=';'
    ).encode('utf-8-sig')
    st.sidebar.download_button(
        label="📊 CSV",
        data=csv_data,
        file_name="itinerary.csv",
        mime="text/csv"
    )

    # Export PDF
    pdf_bytes = create_pdf(current_itinerary)
    st.sidebar.download_button(
        label="🖨️ PDF",
        data=pdf_bytes,
        file_name="itinerary.pdf",
        mime="application/pdf"
    )
else:
    st.sidebar.info("Générez un itinéraire pour activer l'export")