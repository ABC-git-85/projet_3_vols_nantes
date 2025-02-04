import streamlit as st
from st_files_connection import FilesConnection
import requests
import pandas as pd
import os
from datetime import datetime
import glob

# Create connection object and retrieve file contents.
# Specify input format is a csv and to cache the result for 600 seconds.
conn = st.connection('s3', type=FilesConnection)
df = conn.read("projet-3-avion/exports_mageAI/delays_20250204_114414.csv", input_format="csv", ttl=600)

st.dataframe(df)

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

def get_most_recent_file(folder_path, file_prefix):
    # Récupérer tous les fichiers dans le dossier correspondant
    files = glob.glob(os.path.join(folder_path, f"{file_prefix}*.csv"))
    # Trier les fichiers par date (le plus récent en premier)
    files.sort(reverse=True)
    return files[0] if files else None

def load_and_compare_delays(folder_path, current_time):
    # Calculer le fichier le plus récent
    file_prefix = 'delays_NTE_'  # Préfixe du nom du fichier
    most_recent_file = get_most_recent_file(folder_path, file_prefix)
    
    if most_recent_file:
        # Charger le fichier CSV
        df = pd.read_csv(most_recent_file)
        
        # Calculer les retards moyens à l'arrivée et au départ actuellement
        avg_arrival_delay, avg_departure_delay = calcul_delays_moyen('NTE')
        
        print(f"Moyenne des retards d'arrivée: {avg_arrival_delay:.2f} minutes")
        print(f"Moyenne des retards de départ: {avg_departure_delay:.2f} minutes")
        
        # Si tu veux aussi récupérer les informations de l'heure précédente
        # On peut charger les données pour le fichier précédent (en fonction de l'heure)
        last_hour = current_time.replace(minute=0, second=0, microsecond=0)
        previous_hour = last_hour - pd.Timedelta(hours=1)
        
        previous_file_name = f"delays_NTE_{previous_hour.strftime('%Y%m%d_%H%M%S')}.csv"
        previous_file_path = os.path.join(folder_path, previous_file_name)
        
        if os.path.exists(previous_file_path):
            previous_df = pd.read_csv(previous_file_path)
            avg_arrival_delay_prev, avg_departure_delay_prev = calcul_delays_moyen(previous_df)
            
            print(f"Moyenne des retards d'arrivée à {previous_hour.strftime('%H:%M')}: {avg_arrival_delay_prev:.2f} minutes")
            print(f"Moyenne des retards de départ à {previous_hour.strftime('%H:%M')}: {avg_departure_delay_prev:.2f} minutes")
            
            # Comparer avec les moyennes actuelles
            print(f"Comparaison des retards d'arrivée: {avg_arrival_delay - avg_arrival_delay_prev:.2f} minutes")
            print(f"Comparaison des retards de départ: {avg_departure_delay - avg_departure_delay_prev:.2f} minutes")
        else:
            print("Aucun fichier précédent trouvé pour la comparaison.")
    else:
        print("Aucun fichier trouvé pour l'heure actuelle.")

# Exemple d'appel de la fonction
folder_path = "projet-3-avion/exports_mageAI"  # Le dossier contenant les fichiers CSV
current_time = datetime.now()  # Heure actuelle

load_and_compare_delays(folder_path, current_time)


# Charger le fichier CSV
def load_airports():
    return pd.read_csv("data/airports.csv")
airports_df = load_airports()

### CALCUL de la moyenne à l'instant T
# Création de la liste pour la selectbox avec format "Nom Aéroport (Trigramme)"
airport_options = [f"{row['nom_aeroport']} ({row['trigramme']})" for _, row in airports_df.iterrows()]
# Liste déroulante des aéroports
airport_choice = st.selectbox('Choisir un aéroport :', airport_options)
# Extraire le trigramme de l'aéroport choisi pour retrouver les coordonnées
chosen_airport_row = airports_df[airports_df.apply(lambda row: f"{row['nom_aeroport']} ({row['trigramme']})" == airport_choice, axis=1)].iloc[0]

# Affichage des KPI
if chosen_airport_row['trigramme']:
    moyenne_delays_arrival_t, moyenne_delays_departure_t = calcul_delays_moyen(chosen_airport_row['trigramme'])

### CALCUL de la moyenne l'heure précédente
# Calcul des moyennes des retards
# Filtre du df (retirer les valeurs 0 du calcul)
df_delays_arrival = df[(df['arrival_airport'] == chosen_airport_row['trigramme'])  & (df['delays_arrival'] > 0)]
moyenne_delays_arrival_h = sum(df_delays_arrival['delays_arrival']) / len(df_delays_arrival['delays_arrival'])
# Filtre du df (retirer les valeurs 0 du calcul)
df_delays_departure = df[(df['departure_airport'] == chosen_airport_row['trigramme'])  & (df['delays_departure'] > 0)]
moyenne_delays_departure_h = sum(df_delays_departure['delays_departure']) / len(df_delays_departure['delays_departure'])

# Affichage des KPI
if chosen_airport_row['trigramme']:
    moyenne_delays_arrival_t, moyenne_delays_departure_t = calcul_delays_moyen(chosen_airport_row['trigramme'])

# Définir les quatre colonnes
col1, col2 = st.columns([1, 1])  # Colonne 4 plus large

with col1:
    # Afficher les métriques de départ et d'arrivée
    delta_arrival = int(moyenne_delays_arrival_t) - int(moyenne_delays_arrival_h) if moyenne_delays_arrival_h else None
    delta_display_arrival = f"{'+' if delta_arrival and delta_arrival > 0 else ''}{delta_arrival} min" if delta_arrival is not None and delta_arrival != 0 else "-"
    delta_color_mode = "inverse" if delta_arrival is not None and delta_arrival != 0 else "off"
    col1.metric("Au départ", f"🛫 {int(moyenne_delays_arrival_t)} min", delta_display_arrival, delta_color=delta_color_mode)
    # Calcul des moyennes des retards
    # Filtre du df (retirer les valeurs 0 du calcul)
    df_delays_arrival = df[(df['arrival_airport'] == chosen_airport_row['trigramme'])  & (df['delays_arrival'] > 0)]
    moyenne_delays_arrival_h = sum(df_delays_arrival['delays_arrival']) / len(df_delays_arrival['delays_arrival'])
    st.write(int(moyenne_delays_arrival_h))

with col2:
    # Afficher les métriques de départ et d'arrivée
    delta_departure = int(moyenne_delays_departure_t) - int(moyenne_delays_departure_h) if moyenne_delays_departure_h else None
    delta_display_departure = f"{'+' if delta_departure and delta_departure > 0 else ''}{delta_departure} min" if delta_departure is not None and delta_departure != 0 else "-"
    delta_color_mode = "inverse" if delta_departure is not None and delta_departure != 0 else "off"
    col2.metric("À l'arrivée", f"🛬 {int(moyenne_delays_departure_t)} min", delta_display_departure, delta_color=delta_color_mode)
    # Filtre du df (retirer les valeurs 0 du calcul)
    df_delays_departure = df[(df['departure_airport'] == chosen_airport_row['trigramme'])  & (df['delays_departure'] > 0)]
    moyenne_delays_departure_h = sum(df_delays_departure['delays_departure']) / len(df_delays_departure['delays_departure'])
    st.write(int(moyenne_delays_departure_h))