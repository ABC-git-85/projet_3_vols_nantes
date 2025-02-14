import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime
import google.generativeai as genai

# Assurer que flights_df est bien stocké et ne disparaît pas après un clic sur un autre bouton
if "flights_df" not in st.session_state:
    st.session_state.flights_df = None

if "show_recommendations" not in st.session_state:
    st.session_state.show_recommendations = False

# 📌 Correction du chemin du fichier CSV
csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "airports.csv")
destinations_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "destinations.csv")

# Vérifier si le fichier existe
if not os.path.exists(csv_path):
    st.error(f"❌ Le fichier 'airports.csv' est introuvable. Chemin vérifié : {csv_path}")
    st.stop()

# Charger la liste des aéroports et destinations
@st.cache_data
def load_airports():
    df = pd.read_csv(csv_path, encoding="ISO-8859-1")
    return df

@st.cache_data
def load_destinations():
    df = pd.read_csv(destinations_path, encoding="ISO-8859-1")
    return df

df_airports = load_airports()
df_destinations = load_destinations()

airport_choices = df_airports["ville"].unique().tolist()

# 🔑 Remplacez votre clé API par une variable d'environnement ou un fichier sécurisé
API_KEY = "27b6a4f616mshbf04aa536be573ap1de13cjsn4912d0384fc9"

# Fonction pour récupérer les prix des vols
def get_flight_prices(departure_id, arrival_id, outbound_date):
    url = "https://google-flights2.p.rapidapi.com/api/v1/searchFlights"
    querystring = {
        "departure_id": departure_id,
        "arrival_id": arrival_id,
        "outbound_date": outbound_date,
        "travel_class": "ECONOMY",
        "adults": "1",
        "show_hidden": "1",
        "currency": "EUR",
        "language_code": "en-US",
        "country_code": "FR"
    }
    headers = {
        "x-rapidapi-key": API_KEY,
        "x-rapidapi-host": "google-flights2.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)

    if response.status_code != 200:
        st.error(f"Erreur lors de la récupération des données : {response.status_code}")
        return None

    return response.json()

# Fonction pour afficher les vols sous forme de tableau avec CO₂
def display_optimal_flight(flights_data):
    if "data" in flights_data and "itineraries" in flights_data["data"]:
        itineraries = flights_data["data"]["itineraries"]
        top_flights = itineraries.get("topFlights", [])

        if not top_flights:
            st.warning("⚠️ Aucun vol trouvé.")
            return

        flight_list = []
        for flight in top_flights:
            flights = flight.get("flights", []) or flight.get("extensions", [])
            departure_airport = arrival_airport = airline_logo = departure_time = arrival_time = None
            price = flight.get("price", "Non précisé")
            stops = len(flights) - 1
            stop_details = []
            total_duration = flight.get("duration", {}).get("text", "Non spécifiée").replace("hr", "h").replace("r", "").replace("min", "")
            carbon_emissions = int(flight.get("carbon_emissions", {}).get("CO2e", "Non précisé")/1000)

            for idx, f in enumerate(flights):
                if idx == 0:
                    departure_airport = f"{f.get('departure_airport', {}).get('airport_name', 'Inconnu')} ({f.get('departure_airport', {}).get('airport_code', 'Inconnu')})"
                    departure_time = f.get("departure_airport", {}).get("time", "Inconnu").split(' ')[1] if " " in f.get("departure_airport", {}).get("time", "Inconnu") else f.get("departure_airport", {}).get("time", "Inconnu")
                    airline_logo = f"<img src='{f.get('airline_logo')}' width='50'/>" if f.get('airline_logo') else f.get('airline')
                if idx == len(flights) - 1:
                    arrival_airport = f"{f.get('arrival_airport', {}).get('airport_name', 'Inconnu')} ({f.get('arrival_airport', {}).get('airport_code', 'Inconnu')})"
                    arrival_time = f.get("arrival_airport", {}).get("time", "Inconnu").split(' ')[1] if " " in f.get("arrival_airport", {}).get("time", "Inconnu") else f.get("arrival_airport", {}).get("time", "Inconnu")
                if idx > 0:
                    stop_details.append(f"{f.get('departure_airport', {}).get('airport_name', 'Inconnu')} ({f.get('departure_airport', {}).get('airport_code', 'Inconnu')})")

            flight_list.append({
                "Départ": departure_airport,
                "Arrivée": arrival_airport,
                "Compagnie": airline_logo,
                "Heure de départ": departure_time,
                "Heure d'arrivée": arrival_time,
                "Durée": total_duration,
                "Prix (EUR)": price,
                "CO² (T)": carbon_emissions,
                "Escale(s)": f"{stops} escale(s)" if stops > 0 else "Direct",
                "Détails des escales": ", ".join(stop_details) if stop_details else "Aucune",
                "Réservation": f'<a href="https://www.google.com/flights?booking_token={flight.get("booking_token")}" target="_blank">Réserver ici</a>',
            })

        df_flights = pd.DataFrame(flight_list)
        df_flights = df_flights.sort_values(by=["Escale(s)", "Prix (EUR)", "CO² (T)"], ascending=[False, True, True])

        # Sauvegarder les résultats dans session_state
        st.session_state.flights_df = df_flights

# Initialisation du modèle de Chatbot
model = genai.GenerativeModel('gemini-1.5-flash')
GOOGLE_API_KEY= "AIzaSyABSvSuy6IZeOiAFcXrU5Z4d85XEqMjtQo"
genai.configure(api_key=GOOGLE_API_KEY)

# Création du prompt système
system_prompt = """
Tu es un guide touristique spécialisé dans les recommandations de restaurants et d'attractions.
Tu fournis des suggestions basées sur des avis populaires et des lieux bien notés. Termine toujours les recommandations par une phrase du type : "Bon séjour à [destination] !"
"""

# Initialisation de l'historique avec le prompt système
chat = model.start_chat(history=[{'role': 'user', 'parts': [system_prompt]}])

# Fonction pour obtenir des recommandations via le chatbot
def get_chatbot_recommendations(destination):
    prompt = f"Quelles sont les meilleures attractions et restaurants à {destination}?"
    response = chat.send_message(prompt)
    return response.text

# Fonction pour afficher les recommandations
def display_recommendations(destination):
    recommendations = get_chatbot_recommendations(destination)
    st.subheader(f"Recommandations pour {destination}")
    st.write(recommendations)

# 🎨 Interface utilisateur
st.title("🔎 Recherche de Vols ✈️")

departure_city = st.selectbox("Sélectionnez votre ville de départ", airport_choices)

departure_data = df_airports[df_airports["ville"] == departure_city]
if departure_data.empty:
    st.error("❌ Aucune correspondance trouvée pour cette ville de départ.")
    st.stop()
departure_id = departure_data.iloc[0]["trigramme"]

arrival_choices = df_destinations["ville"].unique().tolist()
arrival_city = st.selectbox("Sélectionnez votre destination", arrival_choices)

def get_arrival_iata(arrival_city):
    arrival_data = df_destinations[df_destinations["ville"].str.contains(arrival_city, case=False, na=False)]
    return arrival_data.iloc[0]["trigramme"] if not arrival_data.empty else None

arrival_id = get_arrival_iata(arrival_city)
outbound_date = st.date_input("Date de départ", datetime.today().date())

# Affichage du tableau UNIQUEMENT si des vols ont été trouvés
if "flights_df" in st.session_state and st.session_state.flights_df is not None:
    st.subheader("🛫 Résultats des vols disponibles")
    st.markdown(st.session_state.flights_df.to_html(escape=False, index=False), unsafe_allow_html=True)

# Rechercher les vols
if st.button("🔍 Rechercher les vols"):
    if departure_id and arrival_id:
        flights_data = get_flight_prices(departure_id, arrival_id, outbound_date.strftime('%Y-%m-%d'))
        if flights_data:
            display_optimal_flight(flights_data)
        else:
            st.warning("❌ Aucun vol trouvé.")

# Bouton pour afficher les recommandations IA après le tableau de vols
if st.button("🌟 Recommandations IA"):
    st.session_state.show_recommendations = True

# Si l'utilisateur a cliqué sur le bouton, afficher les recommandations
if st.session_state.show_recommendations:
    display_recommendations(arrival_city)