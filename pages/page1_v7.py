import streamlit as st
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium
from geopy.distance import geodesic
import requests
import pandas as pd
import time
from datetime import datetime
import re

################################ CONF PAGE ################################

st.set_page_config(
    layout="centered"  # Mode par défaut
)

################################### CSS ###################################

# Charger ton fichier CSS
css_file = 'css/style.css'  # Spécifie le chemin vers ton fichier CSS

# Ajouter un fichier CSS à la carte (ou inclure dans la page HTML)
with open(css_file, 'r') as file:
    css = file.read()

# Ajouter le CSS au fichier HTML généré
folium.Map().get_root().html.add_child(folium.Element(f'<style>{css}</style>'))

# Injecter le CSS dans l'application
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

################################### CSV ###################################

# Charger le fichier CSV
def load_airports():
    return pd.read_csv("data/airports.csv")
airports_df = load_airports()

################################### API ###################################

# AVIATION EDGE
api_key = 'ea7fa4-b8076f'

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

# WEATHER
api_key_meteo = "7cba9d33598e41d78e8135111252201"
url_meteo = "http://api.weatherapi.com/v1/current.json"

# Fonction pour appeler la météo
def get_weather(city_name):
    params = {
        "key": api_key_meteo,
        "q": city_name,
        "lang": "fr",
    }
    response = requests.get(url_meteo, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return None

###########################################################################

# CARTE - Création de la carte Folium
def create_map(flight_data, airport_coords, radius_km):
    # Calcul du niveau de zoom en fonction du rayon sélectionné
    zoom_level = get_zoom_level(radius_km)
    # Ajouter un cercle représentant le périmètre
    m = folium.Map(location=airport_coords, zoom_start=zoom_level, tiles="cartodb positron")
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
        popup=chosen_airport_row['nom_aeroport'],
        icon=folium.Icon(color="blue", icon="info-sign")
    ).add_to(m)
    # Collecter les vols proches
    nearby_flights = []
    for flight in flight_data or []: # Éviter une erreur si flight_data est None
    # Vérification des coordonnées
        try:
            latitude = flight['geography']['latitude']
            longitude = flight['geography']['longitude']
            altitude = flight['geography']['altitude']
            plane_coords = (latitude, longitude)
            distance = geodesic(airport_coords, plane_coords).km
            
            # Vérification des vols dans le rayon
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

    # Appeler `flights_info` pour enrichir les vols avec des informations horaires
    enriched_flights = flights_info(nearby_flights)

    # Ajouter les avions sur la carte
    for flight in enriched_flights:
        icon_color = flight.get("Icon Color", "lightgray")
        temps_restants = flight.get('Temps restant', 'Inconnu')
        
        if temps_restants == 'Inconnu':
            temps_restants = "Pas d'heure d'arrivée communiquée"
        elif temps_restants == 'Arrivé':
            temps_restants = "Arrivé"
        else:
        # Regex pour extraire heures et minutes
            match = re.match(r'(\d+)(h|)(\d*)(min|)', temps_restants.strip())
            if match:
                hours = int(match.group(1))  # Récupérer les heures
                minutes = int(match.group(3)) if match.group(3) else 0 # Récupérer les minutes (par défaut 0 si non spécifié)            
                minutes_formatted = str(minutes).zfill(2) # Formater les minutes pour qu'elles soient toujours à 2 chiffres

                # Si le temps est inférieur à 1h, convertir en minutes
                if hours < 1:
                    # Si le temps restant est inférieur à 1 heure, afficher uniquement les minutes
                    minutes += hours * 60  # Convertir les heures en minutes
                    temps_restants = f"Arrivée dans <b>{minutes} min</b>"
                else:
                    # Si le temps est supérieur ou égal à 1 heure, afficher les heures et minutes formatées
                    temps_restants = f"Arrivée dans <b>{hours}h{minutes_formatted}</b>"
            else:
                temps_restants = f"Arrivée dans <b>{flight['Temps restant']}</b>"

        popup_text = f"""
        <div class="popup-content">
            <div class="popup-header">{flight['Code Vol']}</div>
            <div class="popup-body">{temps_restants}</div>
        </div>
        """
        folium.Marker(
            location=[flight['Latitude'], flight['Longitude']],
            popup=folium.Popup(popup_text, max_width=300, min_width=100),
            icon=folium.Icon(color=icon_color, icon="plane", prefix="fa")
        ).add_to(m)
    return m, enriched_flights

# ZOOM - Fonction pour ajuster le zoom de la carte en fonction du rayon sélectionné
def get_zoom_level(radius_km):
    if radius_km > 50:
        return 8  # Vue large pour des rayons > 100 km
    else:
        return 9  # Vue modérée pour des rayons entre 50 et 100 km

# DONNEES - Ajout des informations commerciales aux données de position des avions
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
                            departure_scheduled = info['departure'].get('scheduledTime')
                            arrival_scheduled = info['arrival'].get('scheduledTime')
                            arrival_estimated = info['arrival'].get('estimatedTime')
                            if arrival_estimated:
                                try:                                    
                                    estimated_arrival_time = datetime.fromisoformat(arrival_estimated) # Conversion en datetime
                                    current_time = datetime.now() # Heure actuelle                                    
                                    time_remaining = estimated_arrival_time - current_time # Calcul du temps restant
                                    # Si l'heure d'arrivée est passée, on met "Arrivé" ou un message d'erreur
                                    if time_remaining.total_seconds() > 0:
                                        remaining_str = f"{time_remaining.seconds // 3600}h{time_remaining.seconds % 3600 // 60}m"
                                    else:
                                        remaining_str = "Arrivé"
                                except ValueError:
                                    remaining_str = "Invalide"
                            else:
                                remaining_str = "Inconnu"                           
                            color_delay = compare_arrival_times(arrival_estimated, arrival_scheduled)
                            # Définir les icônes correspondant aux couleurs
                            icon_mapping = {
                                "green": "🟢",  # Vert
                                "red": "🔴",    # Rouge
                                "lightgray": "⚪"    # Blanc
                            }
                            icon_delay = icon_mapping.get(color_delay, "⚪")
                            flight.update({
                                "Départ prévu": format_time(departure_scheduled),
                                "Départ réel": format_time(info['departure'].get('estimatedTime')),
                                "Arrivée prévue": format_time(arrival_scheduled),
                                "Arrivée estimée": f"{icon_delay} {format_time(arrival_estimated)}",
                                "Temps restant": remaining_str,
                                "Aéroport départ": info['departure'].get('iataCode', "Inconnu"),
                                "Aéroport arrivée": info['arrival'].get('iataCode', "Inconnu"),
                                "Compagnie": info['airline'].get('name', "Inconnue"),
                                "Icon Color": color_delay
                            })
                    else:
                        print(f"Aucune donnée horaire valide pour le vol {flight_code}")
                except ValueError:
                    print(f"Erreur JSON pour le vol {flight_code} : {response_timetable.text}")
            else:
                print(f"Erreur {response_timetable.status_code} pour l'API Timetable du vol {flight_code}")
        enriched_flights.append(flight)
    return enriched_flights


# CALCUL - Calculer la différence entre l'heure d'arrivée estimée et l'heure d'arrivée programmée
def compare_arrival_times(arrival_estimated, arrival_scheduled):
    # Conversion des heures en objets datetime pour la comparaison
    arrival_estimated = datetime.strptime(arrival_estimated, "%Y-%m-%dT%H:%M:%S.%f") if arrival_estimated else None
    arrival_scheduled = datetime.strptime(arrival_scheduled, "%Y-%m-%dT%H:%M:%S.%f") if arrival_scheduled else None
    if arrival_estimated and arrival_scheduled:
        return "green" if arrival_estimated <= arrival_scheduled else "red"
    else:
    # Si l'une des heures est absente, on retourne une icône blanche par défaut
        return "lightgray"

# CALCUL - Calculer le temps de retard moyen des arrivés et des départs sur un aéroport donné
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

# FORMATAGE - Fonction pour formater les heures
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
airport_choice = st.selectbox('Choisir un aéroport :', airport_options)

# Extraire le trigramme de l'aéroport choisi pour retrouver les coordonnées
chosen_airport_row = airports_df[airports_df.apply(lambda row: f"{row['nom_aeroport']} ({row['trigramme']})" == airport_choice, axis=1)].iloc[0]

st.subheader("🕔 Retards moyens")

# Affichage des KPI
if chosen_airport_row['trigramme']:
    moyenne_arrival, moyenne_departure = calcul_delays_moyen(chosen_airport_row['trigramme'])

    # Définir les quatre colonnes
    col1, col2, col3, col4 = st.columns([2, 2, 1, 2])  # Colonne 4 plus large

    # Afficher les métriques de départ et d'arrivée
    col1.metric("Au départ", f"🛫 {int(moyenne_arrival)} min", "-2%" if moyenne_arrival else "-")
    col2.metric("À l'arrivée", f"🛬 {int(moyenne_departure)} min", "4%" if moyenne_departure else "-")
    
    # Obtenir les données météo
    weather_data = get_weather(chosen_airport_row['ville'])

    if weather_data and 'current' in weather_data:
        # Informations météo
        description = weather_data['current']['condition']['text']
        icon_code = weather_data['current']['condition']['icon']
        icon_url = f"http:{icon_code}"
        temperature = weather_data['current']['temp_c']
        wind_speed = weather_data['current']['wind_kph']

        # Colonne 3 : icône météo
        with col3:
            st.markdown(f""" <div class="col3-image"><img src="{icon_url}" alt="{description}" style="max-width: 100px;"></div>""", unsafe_allow_html=True)

        # Colonne 4 : détails météo
        with col4:           
            st.markdown(f'<p class="col4-text">{temperature}°C</p>', unsafe_allow_html=True)
            st.write(f"**Vent :** {wind_speed} km/h")
    else:
        # Gestion des erreurs météo
        with col3:
            st.error("Icône météo indisponible.")
        with col4:
            st.error("Données météo indisponibles.")
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
    st.write("### 📍 Liste des vols repérés")
    flights_df = pd.DataFrame(nearby_flights)
    flights_df = flights_df.reindex(columns=columns_order, fill_value="Inconnu")
    st.dataframe(flights_df, use_container_width=True)
else:
    st.write("Aucun vol trouvé dans la zone.")