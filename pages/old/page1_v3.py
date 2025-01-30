import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import requests
import pandas as pd
import time
from datetime import datetime

################################### CSV ###################################

# Charger le fichier CSV
def load_airports():
    return pd.read_csv("data/airports.csv")
airports_df = load_airports()

################################### API ###################################

api_key = 'ea7fa4-b8076f'

# Récupération des données de l'API Aviation Edge avec mise en cache
@st.cache_data(ttl=60)  # Cache pendant 60 secondes
def fetch_flight_data():    
    url_flights = f"https://aviation-edge.com/v2/public/flights?key={api_key}&status=en-route"
    response = requests.get(url_flights)
    if response.status_code == 200:
        flights = response.json()
        return flights
    else:
        st.error("Erreur lors de la récupération des données.")
    return None

# Fonction pour ajuster le zoom en fonction du rayon
def get_zoom_level(radius_km):
    if radius_km > 50:
        return 8  # Vue large pour des rayons > 100 km
    else:
        return 9  # Vue modérée pour des rayons entre 50 et 100 km

# Création de la carte Folium
def create_map(flight_data, airport_coords, radius_km):
    # Calcul du niveau de zoom en fonction du rayon sélectionné
    zoom_level = get_zoom_level(radius_km)
    # Ajouter un cercle représentant le périmètre
    m = folium.Map(location=airport_coords, zoom_start=zoom_level)
    folium.Circle(
        location=airport_coords,
        radius=radius_km * 1000,  # Convertir en mètres
        color="blue",
        fill=True,
        fill_color="blue",
        fill_opacity=0.2,
        popup=f"Périmètre de {radius_km} km autour de l'aéroport"
    ).add_to(m)
    # Ajouter un marqueur pour l'aéroport
    folium.Marker(
        location=airport_coords,
        popup=f"Aéroport de {chosen_airport_row['nom_aeroport']}",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    nearby_flights = []
    for flight in flight_data or []: # Éviter une erreur si flight_data est None
    # Vérification des coordonnées
        try:
            latitude = flight['geography']['latitude']
            longitude = flight['geography']['longitude']
            altitude = flight['geography']['altitude']
            plane_coords = (latitude, longitude)
            distance = geodesic(airport_coords, plane_coords).km

            if distance <= radius_km and flight['flight']['iataNumber'] != "XXD":  # Exclusion des vols XXD
                nearby_flights.append({
                    "Latitude": latitude,
                    "Longitude": longitude,
                    "Altitude (m)": altitude,
                    "Distance (km)": round(distance, 2),
                    "Code Vol": flight['flight']['iataNumber'] or "Inconnu"
                })
        except KeyError:
            # Passer les vols qui ne possèdent pas les données nécessaires
            continue
    # Ajouter les avions sur la carte
    for flight in nearby_flights:
        folium.Marker(
            location=[flight['Latitude'], flight['Longitude']],
            popup=f"Vol : {flight['Code Vol']}",
            icon=folium.Icon(color="blue", icon="plane", prefix="fa")
        ).add_to(m)
    return m, nearby_flights

# Ajouter les informations commerciales
@st.cache_data(ttl=60)  # Cache pendant 60 secondes
def flights_info(nearby_flights):
    enriched_flights = []
    for flight in nearby_flights:
        flight_code = flight.get('Code Vol')  # Corrected access to flight code
        if flight_code and flight_code != "Inconnu":
            url_timetable = f"https://aviation-edge.com/v2/public/timetable?key={api_key}&flight_iata={flight_code}"
            response_timetable = requests.get(url_timetable)

            if response_timetable.status_code == 200:
                try:
                    timetable_data = response_timetable.json()
                    # Vérifier que timetable_data est une liste valide
                    if isinstance(timetable_data, list) and timetable_data:
                        for info in timetable_data:
                            flight.update({
                                "Départ prévu": format_time(info['departure'].get('scheduledTime')),
                                "Départ réel": format_time(info['departure'].get('estimatedTime')),
                                "Arrivée prévue": format_time(info['arrival'].get('scheduledTime')),
                                "Arrivée estimée": f"🟢 {format_time(info['arrival'].get('estimatedTime'))}",
                                "Aéroport départ": info['departure'].get('iataCode', "Inconnu"),
                                "Aéroport arrivée": info['arrival'].get('iataCode', "Inconnu"),
                                "Compagnie": info['airline'].get('name', "Inconnue")
                            })
                    else:
                        print(f"Aucune donnée horaire valide pour le vol {flight_code}")
                except ValueError:
                    print(f"Erreur JSON pour le vol {flight_code} : {response_timetable.text}")
            else:
                print(f"Erreur {response_timetable.status_code} pour l'API Timetable du vol {flight_code}")
        enriched_flights.append(flight)
    return enriched_flights

# Fonction pour calculer le temps de retard moyen des arrivés et des départs sur un aéroport donné
@st.cache_data(ttl=60)  # Cache pendant 60 secondes
def calcul_delays_moyen(aeroport):
    delays_arrival = []
    delays_departure = []
    url_flights_commercial = f'https://aviation-edge.com/v2/public/timetable?key={api_key}&iataCode={aeroport}'
    response = requests.get(url_flights_commercial)
    if response.status_code != 200:
        st.error("Erreur lors de la récupération des données.")
        return None, None  # En cas d'erreur

    flights = response.json()
    for flight in flights:
        arrival_delay = flight['arrival']['delay']
        departure_delay = flight['departure']['delay']
        if arrival_delay is not None:
            delays_arrival.append(int(arrival_delay))
        if departure_delay is not None:
            delays_departure.append(int(departure_delay))

    moyenne_delays_arrival = sum(delays_arrival) / len(delays_arrival)
    moyenne_delays_departure = sum(delays_departure) / len(delays_departure)
    return(moyenne_delays_arrival, moyenne_delays_departure)

# Fonction pour formater les heures
def format_time(time_str):
    if time_str and isinstance(time_str, str):
        try:
            return datetime.fromisoformat(time_str).strftime("%H:%M")
        except ValueError:
            return "Invalide"
    return "Inconnu"

################################### PAGE ###################################

st.subheader("✈️ Aéroport")

# Création de la liste pour la selectbox avec format "Nom Aéroport (Trigramme)"
airport_options = [f"{row['nom_aeroport']} ({row['trigramme']})" for _, row in airports_df.iterrows()]

# Liste déroulante des aéroports
airport_choice = st.selectbox('Choisir un aéroport', airport_options)

# Extraire le trigramme de l'aéroport choisi pour retrouver les coordonnées
chosen_airport_row = airports_df[airports_df.apply(lambda row: f"{row['nom_aeroport']} ({row['trigramme']})" == airport_choice, axis=1)].iloc[0]

st.subheader("🕔 Retards moyens")

# Affichage des KPI
if chosen_airport_row['trigramme']:
    moyenne_arrival, moyenne_departure = calcul_delays_moyen(chosen_airport_row['trigramme'])

    col1, col2 = st.columns(2)    
    col1.metric("🛫 Au départ", f"{int(moyenne_arrival)} min", "-2%" if moyenne_arrival else "-")
    col2.metric("🛬 À l'arrivée", f"{int(moyenne_departure)} min", "4%" if moyenne_departure else "-")
else:
    st.error("Aéroport non valide ou introuvable.")

st.subheader("🌍 Carte des avions autour de l'aéroport")

# Coordonnées de l'aéroport choisi
airport_coords = (chosen_airport_row['latitude'], chosen_airport_row['longitude'])

# Curseur pour définir le rayon du périmètre
radius_km = st.slider("Rayon d'observation (en km) :", 10, 100, 50)

# Bouton pour mettre à jour les données
#if st.button("Mettre à jour les données"):
#    st.session_state.flight_data = fetch_flight_data()

# Récupération des données depuis le cache ou l'état
if "flight_data" not in st.session_state:
    st.session_state.flight_data = fetch_flight_data()
flight_data = st.session_state.flight_data

# Création de la carte avec le rayon sélectionné
with st.spinner('Veuillez patienter...'):
    time.sleep(5)
map_object, nearby_flights = create_map(flight_data, airport_coords, radius_km)

# Enrichir les vols avec les données commerciales
if nearby_flights:
    nearby_flights = flights_info(nearby_flights)

# Affichage de la carte
st_data = st_folium(map_object, width=700, height=500)

st.divider()

# Affichage de la liste des vols dans un tableau
# Affichage du tableau unique avec ordre des colonnes modifié
columns_order = [
    "Code Vol", "Compagnie", "Aéroport départ", "Aéroport arrivée",
    "Départ prévu", "Départ réel", "Arrivée prévue", "Arrivée estimée",
    "Distance (km)", "Altitude (m)", "Latitude", "Longitude"
]
if nearby_flights:
    st.write("### Liste des vols repérés")
    flights_df = pd.DataFrame(nearby_flights)
    flights_df = flights_df.reindex(columns=columns_order, fill_value="Inconnu")
    st.dataframe(flights_df, use_container_width=True)
else:
    st.write("Aucun vol trouvé dans la zone.")