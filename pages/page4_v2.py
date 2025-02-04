import streamlit as st
from st_files_connection import FilesConnection
import requests
import pandas as pd
import os
from datetime import datetime
import s3fs
import re

##################################### AVIATION EDGE #####################################
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

###############################################################################################################

# Create connection object and retrieve file contents.
# Specify input format is a csv and to cache the result for 600 seconds.
conn = st.connection('s3', type=FilesConnection)
df = conn.read("projet-3-avion/exports_mageAI/delays_20250204_150043.csv", input_format="csv", ttl=600)
st.dataframe(df)


def get_most_recent_file_s3(bucket_name, folder_path, file_prefix):
    fs = s3fs.S3FileSystem() # Connexion à S3 via s3fs    
    files = fs.glob(f"{bucket_name}/{folder_path}/{file_prefix}*.csv") # Lister tous les fichiers du dossier S3
    # Si des fichiers sont trouvés, trier par date et retourner le plus récent
    if not files:
        return None
    # Trier les fichiers par date en extrayant la date dans le nom du fichier
    def extract_date_from_filename(filename):
        # Exemple de format de nom de fichier: delays_20250204_140042.csv
        match = re.search(r"(\d{8})_(\d{6})", filename)
        if match:
            return datetime.strptime(match.group(0), "%Y%m%d_%H%M%S")
        return None
    
    # Trier les fichiers par date extraite
    files_with_dates = [(file, extract_date_from_filename(file)) for file in files]
    files_with_dates = [file for file in files_with_dates if file[1] is not None]
    
    if not files_with_dates:
        return None
    
    # Trier par date en ordre décroissant (le plus récent en premier)
    files_with_dates.sort(key=lambda x: x[1], reverse=True)
    
    # Retourner le fichier le plus récent
    return files_with_dates[0][0]

# Exemple d'appel
bucket_name = 'projet-3-avion'  # Nom du bucket S3
folder_path = 'exports_mageAI'  # Dossier contenant les fichiers CSV
file_prefix = 'delays_'  # Préfixe du nom du fichier
current_time = datetime.now()  # Heure actuelle

files = get_most_recent_file_s3(bucket_name, folder_path, file_prefix)
st.write(files)

def load_and_compare_delays_s3(bucket_name, folder_path, current_time):
    # Initialisation de df pour éviter l'erreur
    df = pd.DataFrame()  # Initialiser un DataFrame vide au début
    file_prefix = 'delays_'  # Préfixe du nom du fichier
    
    # Récupérer le fichier le plus récent
    most_recent_file = get_most_recent_file_s3(bucket_name, folder_path, file_prefix)
    
    if most_recent_file:
        # Charger le fichier CSV depuis S3
        df = pd.read_csv(f"s3://{most_recent_file}")
        
        # Si tu veux aussi récupérer les informations de l'heure précédente
        last_hour = current_time.replace(minute=0, second=0, microsecond=0)
        previous_hour = last_hour - pd.Timedelta(hours=1)
        
        previous_file_name = f"delays_{previous_hour.strftime('%Y%m%d_%H%M%S')}.csv"
        
        # Vérifier si le fichier précédent existe
        previous_file_path = f"s3://{bucket_name}/{folder_path}/{previous_file_name}"
        
        try:
            previous_df = pd.read_csv(previous_file_path)            
        except FileNotFoundError:
            print("Aucun fichier précédent trouvé pour la comparaison.")
    else:
        print("Aucun fichier trouvé pour l'heure actuelle.")
    
    return df

df = load_and_compare_delays_s3(bucket_name, folder_path, current_time)

# Vérifier si df est bien chargé et afficher les informations
if df is not None and not df.empty:
    st.dataframe(df)
else:
    st.write("Aucun fichier de retard n'a été trouvé ou le fichier est vide.")

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
    delta_departure = int(moyenne_delays_departure_t) - int(moyenne_delays_departure_h) if moyenne_delays_departure_h else None
    delta_display_departure = f"{'+' if delta_departure and delta_departure > 0 else ''}{delta_departure} min" if delta_departure is not None and delta_departure != 0 else "-"
    delta_color_mode = "inverse" if delta_departure is not None and delta_departure != 0 else "off"
    col1.metric("Au départ", f"🛫 {int(moyenne_delays_departure_t)} min", delta_display_departure, delta_color=delta_color_mode)
    # Filtre du df (retirer les valeurs 0 du calcul)
    df_delays_departure = df[(df['departure_airport'] == chosen_airport_row['trigramme'])  & (df['delays_departure'] > 0)]
    moyenne_delays_departure_h = sum(df_delays_departure['delays_departure']) / len(df_delays_departure['delays_departure'])
    st.write(int(moyenne_delays_departure_h))

with col2:
    # Afficher les métriques de départ et d'arrivée
    delta_arrival = int(moyenne_delays_arrival_t) - int(moyenne_delays_arrival_h) if moyenne_delays_arrival_h else None
    delta_display_arrival = f"{'+' if delta_arrival and delta_arrival > 0 else ''}{delta_arrival} min" if delta_arrival is not None and delta_arrival != 0 else "-"
    delta_color_mode = "inverse" if delta_arrival is not None and delta_arrival != 0 else "off"
    col2.metric("À l'arrivée", f"🛬 {int(moyenne_delays_arrival_t)} min", delta_display_arrival, delta_color=delta_color_mode)
    # Calcul des moyennes des retards
    # Filtre du df (retirer les valeurs 0 du calcul)
    df_delays_arrival = df[(df['arrival_airport'] == chosen_airport_row['trigramme'])  & (df['delays_arrival'] > 0)]
    moyenne_delays_arrival_h = sum(df_delays_arrival['delays_arrival']) / len(df_delays_arrival['delays_arrival'])
    st.write(int(moyenne_delays_arrival_h))
