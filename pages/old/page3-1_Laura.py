import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime 

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
def display_flights_table(flights_data):
    if "data" in flights_data and "itineraries" in flights_data["data"]:
        itineraries = flights_data["data"]["itineraries"]
        top_flights = itineraries.get("topFlights", [])

        if not top_flights:
            st.warning("⚠️ Aucun vol trouvé.")
            return

        flight_list = []

        for i, flight in enumerate(top_flights):
            flights = flight.get("flights", []) or flight.get("extensions", [])
            
            departure_airport = arrival_airport = airline_logo = departure_time = arrival_time = None
            price = flight.get("price", "Non précisé")
            stops = len(flights) - 1
            stop_details = []
            total_duration = flight.get("duration", {}).get("text", "Non spécifiée").replace("hr", "h").replace("r", "")
            carbon_emissions = flight.get("carbon_emissions", {}).get("CO2e", "Non précisé")

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
                "Vol": i + 1,
                "Départ": departure_airport,
                "Arrivée": arrival_airport,
                "Compagnie": airline_logo,
                "Heure de départ": departure_time,
                "Heure d'arrivée": arrival_time,
                "Durée": total_duration,
                "Prix (EUR)": price,
                "CO₂ (kg)": carbon_emissions,
                "Escales": f"{stops} escale(s)" if stops > 0 else "Direct",
                "Détails des escales": ", ".join(stop_details) if stop_details else "Aucune",
                "Réservation": f'<a href="https://www.google.com/flights?booking_token={flight.get("booking_token")}" target="_blank">Réserver ici</a>'
            })

        df_flights = pd.DataFrame(flight_list)
        st.markdown(df_flights.to_html(escape=False, index=False), unsafe_allow_html=True)
    else:
        st.warning("⚠️ Aucune donnée disponible.")

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

if st.button("🔍 Rechercher les vols"):
    if departure_id and arrival_id:
        flights_data = get_flight_prices(departure_id, arrival_id, outbound_date.strftime('%Y-%m-%d'))
        if flights_data:
            display_flights_table(flights_data)
        else:
            st.warning("❌ Aucun vol trouvé.")
