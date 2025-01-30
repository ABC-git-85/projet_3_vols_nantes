import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.distance import geodesic
import requests
import pandas as pd
import time

################################### CSV ###################################

# Charger le fichier CSV
def load_airports():
    return pd.read_csv("data/airports.csv")

airports_df = load_airports()

################################### API ###################################

# Récupération des données de l'API OpenSky avec mise en cache
@st.cache_data(ttl=60)  # Cache pendant 60 secondes
def fetch_flight_data_OS():
    url_OS = "https://opensky-network.org/api/states/all"
    response_OS = requests.get(url_OS)
    if response_OS.status_code == 200:
        return response_OS.json()
    return None

# Fonction pour calculer le temps de retard moyen des arrivés et des départs sur un aéroport donné
@st.cache_data(ttl=60)  # Cache les données pendant 60 secondes
def calcul_delays_moyen(aeroport):
    delays_arrival = []
    delays_departure = []
    API_KEY = 'ea7fa4-b8076f'
    url_vol_aeroport = f'https://aviation-edge.com/v2/public/timetable?key={API_KEY}&iataCode={aeroport}'
    response_AE = requests.get(url_vol_aeroport)

    if response_AE.status_code != 200:
        st.error("Erreur lors de la récupération des données.")
        return None, None  # En cas d'erreur

    flights = response_AE.json()
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

# Fonction pour ajuster le zoom en fonction du rayon
def get_zoom_level(radius_km):
    if radius_km > 50:
        return 8  # Vue large pour des rayons > 100 km
    else:
        return 9  # Vue modérée pour des rayons entre 50 et 100 km

# Création de la carte Folium
def create_map(data, airport_coords, radius_km):
    # Calcul du niveau de zoom en fonction du rayon sélectionné
    zoom_level = get_zoom_level(radius_km)
    
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

    folium.Marker(
        location=airport_coords,
        popup=f"Aéroport de {chosen_airport_row['nom_aeroport']}",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    flights_data = []
    if data:
        states = data.get('states', [])
        for state in states:
            callsign = state[1]
            latitude = state[6]
            longitude = state[5]
            altitude = state[13]
            on_ground = state[8]

            if latitude and longitude:
                plane_coords = (latitude, longitude)
                distance = geodesic(airport_coords, plane_coords).km

                if distance <= radius_km:
                    status = "au sol" if on_ground else "en vol"
                    flights_data.append({
                        "Indicatif": callsign.strip() or "Inconnu",
                        "Statut": status,
                        "Latitude": round(latitude, 5),
                        "Longitude": round(longitude, 5),
                        "Altitude (m)": altitude or "Inconnue",
                        "Distance (km)": round(distance, 2)                        
                    })
                    folium.Marker(
                        location=[latitude, longitude],
                        popup=f"Vol : {callsign.strip() or 'Inconnu'}<br>"
                              f"Distance : {round(distance, 2)} km",
                        icon=folium.Icon(color="blue", icon="plane", prefix="fa")
                        ).add_to(m)
    return m, flights_data

################################### PAGE ###################################

st.subheader("✈️ Aéroport")

# Création de la liste pour la selectbox avec format "Nom Aéroport (Trigramme)"
airport_options = [f"{row['nom_aeroport']} ({row['trigramme']})" for _, row in airports_df.iterrows()]

# Liste déroulante des aéroports
airport_choice = st.selectbox('Choisir un aéroport', airport_options)

# Extraire le trigramme de l'aéroport choisi pour retrouver les coordonnées
chosen_airport_row = airports_df[airports_df.apply(lambda row: f"{row['nom_aeroport']} ({row['trigramme']})" == airport_choice, axis=1)].iloc[0]
#chosen_airport = next((city for city, info in airports_df.items() if f"{info['nom_aeroport']} ({info['trigramme']})" == airport_choice), None)
#chosen_airport_code = next((info['trigramme'] for city, info in airports_df.items() if f"{info['nom_aeroport']} ({info['trigramme']})" == airport_choice), None)

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
#    st.session_state.flight_data = fetch_flight_data_OS()

# Récupération des données depuis le cache ou l'état
if "flight_data" not in st.session_state:
    st.session_state.flight_data = fetch_flight_data_OS()
flight_data = st.session_state.flight_data

# Création de la carte avec le rayon sélectionné
with st.spinner('Veuillez patienter...'):
    time.sleep(5)
map_object, flights_data = create_map(flight_data, airport_coords, radius_km)

# Affichage de la carte
st_data = st_folium(map_object, width=700, height=500)

st.divider()

# Affichage de la liste des vols dans un tableau
if flights_data:
    st.write("### Liste des vols repérés")
    flights_df = pd.DataFrame(flights_data)        
    flights_df['Altitude (m)'] = pd.to_numeric(flights_df['Altitude (m)'], errors='coerce')  # Convertir les altitudes en numérique (en gérant les erreurs)
    #flights_df = flights_df.sort_values(by='Altitude (m)', ascending=True, na_position='last')  # Trier les données par altitude (NaN seront mis en dernier)
    st.dataframe(flights_df, use_container_width=True)
else:
    st.write("Aucun vol trouvé dans la zone.")