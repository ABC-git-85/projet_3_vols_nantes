import streamlit as st
import folium
from geopy.distance import geodesic
from streamlit_folium import st_folium
import requests
import pandas as pd

# Coordonnées de l'aéroport de Nantes Atlantique
airport_coords = (47.1532, -1.6107)  # Latitude, Longitude
radius_km = 50  # Rayon en kilomètres

# URL de l'API OpenSky pour récupérer les données des avions
url = "https://opensky-network.org/api/states/all"

# Récupérer les données des avions suivis
response = requests.get(url)
flights_data = []

if response.status_code == 200:
    data = response.json()
    states = data.get('states', [])
    
    # Créer une carte avec Folium
    m = folium.Map(location=airport_coords, zoom_start=8)
    
    # Ajouter un cercle pour le périmètre
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
        popup="Aéroport de Nantes Atlantique",
        icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)
    
    # Filtrer et afficher les avions dans le rayon de 50 km
    for state in states:
        callsign = state[1]  # Indicatif du vol
        latitude = state[6]  # Latitude
        longitude = state[5]  # Longitude
        altitude = state[13]  # Altitude barométrique
        on_ground = state[8]  # Statut au sol ou en vol
        
        # Vérifier si les coordonnées sont disponibles
        if latitude is not None and longitude is not None:
            plane_coords = (latitude, longitude)
            
            # Calculer la distance entre l'avion et l'aéroport
            distance = geodesic(airport_coords, plane_coords).km
            
            if distance <= radius_km:
                status = "au sol" if on_ground else "en vol"
                
                # Ajouter les données du vol à la liste
                flights_data.append({
                    "Indicatif": callsign.strip() or "Inconnu",
                    "Latitude": round(latitude, 5),
                    "Longitude": round(longitude, 5),
                    "Altitude (m)": altitude or "Inconnue",
                    "Distance (km)": round(distance, 2),
                    "Statut": status
                })
                
                # Ajouter un marqueur pour l'avion sur la carte
                popup_info = (f"Vol : {callsign.strip() or 'Inconnu'}<br>"
                              f"Distance : {round(distance, 2)} km<br>"
                              f"Altitude : {altitude or 'Inconnue'} m<br>"
                              f"Statut : {status}")
                
                folium.Marker(
                    location=[latitude, longitude],
                    popup=popup_info,
                    icon=folium.Icon(color="blue", icon="plane", prefix="fa")
                ).add_to(m)
else:
    st.error("Erreur lors de la récupération des données : Vérifiez la connexion ou l'API.")

# Afficher la carte et la liste des vols dans Streamlit
st.title("Carte des avions autour de l'aéroport de Nantes Atlantique")
st.write(f"Visualisation des avions dans un rayon de {radius_km} km.")

# Carte Folium intégrée
st_data = st_folium(m, width=700, height=500)

# Afficher la liste des vols repérés
if flights_data:
    st.write("### Liste des vols repérés")
    flights_df = pd.DataFrame(flights_data)
    st.dataframe(flights_df)  # Affichage interactif avec Streamlit
else:
    st.write("Aucun vol trouvé dans la zone.")
