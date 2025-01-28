import streamlit as st
import pandas as pd
from datetime import datetime
import requests

################################### CSV ###################################

# Charger le fichier CSV
#def load_airports():
#    return pd.read_csv("data/airports.csv")
#airports_df = load_airports()

###########################################################################

# Fonction pour obtenir un token d'authentification
def get_auth_token():
    client_id = "BB776010akf5tc5WkFP4z4jBwdjo08EQ"
    client_secret = "pTLTntFBemzkMKAf"

    url = "https://test.api.amadeus.com/v1/security/oauth2/token"

    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        error_details = response.json()
        st.error(f"Erreur lors de la récupération du token: {response.status_code}")
        st.write("Détails de la réponse:", error_details)
        return None

# Fonction pour récupérer les offres de vols
def get_flights_from_api(origin, destination, departure_date, return_date, adults, token):
    API_URL = "https://test.api.amadeus.com/v2/shopping/flight-offers"

    headers = {
        "Authorization": f"Bearer {token}",
    }

    params = {
        "originLocationCode": origin,
        "destinationLocationCode": destination,
        "departureDate": departure_date,
        "returnDate": return_date if return_date else None,
        "adults": adults,
        "max": 10  # Nombre de résultats à récupérer
    }

    # Suppression du paramètre returnDate s'il n'est pas défini
    params = {k: v for k, v in params.items() if v is not None}

    response = requests.get(API_URL, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        error_details = response.json()
        st.error(f"Erreur lors de la récupération des vols: {response.status_code}")
        st.write("Détails de la réponse:", error_details)
        return None

# Fonction pour traiter les informations d'escales et ajouter les détails supplémentaires
def extract_flight_details(flight):
    results = []

    for itinerary in flight["itineraries"]:
        segments = itinerary["segments"]
        total_segments = len(segments)

        # Informations sur les escales
        stopovers = []
        for i in range(total_segments - 1):
            departure_airport = segments[i]["arrival"]["iataCode"]
            next_departure_time = datetime.strptime(segments[i + 1]["departure"]["at"], "%Y-%m-%dT%H:%M:%S")
            arrival_time = datetime.strptime(segments[i]["arrival"]["at"], "%Y-%m-%dT%H:%M:%S")

            # Calcul de la durée de l'escale (sans secondes)
            stopover_duration = next_departure_time - arrival_time
            formatted_duration = f"{stopover_duration.days * 24 + stopover_duration.seconds // 3600}h {stopover_duration.seconds % 3600 // 60}m"
            stopovers.append(f"Aéroport: {departure_airport}, Durée escale: {formatted_duration}")

        # Détails pour chaque vol
        flight_info = {
            "Prix Total": f"{flight['price']['total']} {flight['price']['currency']}",
            "Départ": segments[0]["departure"]["iataCode"],
            "Arrivée": segments[-1]["arrival"]["iataCode"],
            "Heure Départ": segments[0]["departure"]["at"][:-3].replace("T", " "),
            "Heure Arrivée": segments[-1]["arrival"]["at"][:-3].replace("T", " "),
            "Nombre Escales": total_segments - 1,
            "Escale(s)": " | ".join(stopovers) if stopovers else "Aucun",
            "Nom Compagnie": segments[0].get("operatingCarrier", "Inconnu"),
            "Lien de réservation": flight.get('deepLink', 'Lien non disponible')
        }
        results.append(flight_info)

    return results

def main():
    # Charger les aéroports depuis le fichier CSV "aéroports.csv"
    try:
        airports_df = pd.read_csv('data/airports.csv')
        airports_df["label"] = airports_df["ville"] + " (" + airports_df["trigramme"] + ")"
        airports = airports_df["label"].tolist()
    except FileNotFoundError:
        st.error("Le fichier 'airports.csv' est introuvable.")
        return

    # Pré-sélectionner Nantes comme aéroport de départ
    default_origin = "Nantes (NTE)"
    origin_label = st.selectbox("Sélectionnez votre aéroport de départ :", airports, index=airports.index(default_origin) if default_origin in airports else 0)
    origin = airports_df.loc[airports_df["label"] == origin_label, "trigramme"].iloc[0]

    # Charger les destinations depuis le fichier CSV "destinations.csv"
    try:
        destinations_df = pd.read_csv("destinations.csv")
        destinations_df["label"] = destinations_df["ville"] + " (" + destinations_df["trigramme"] + ")"
        destination_options = destinations_df["label"].tolist()
    except FileNotFoundError:
        st.error("Le fichier 'destinations.csv' est introuvable.")
        return

    # Sélection d'une destination parmi toutes celles du CSV
    destination_label = st.selectbox("Sélectionnez une destination :", destination_options)
    destination = destinations_df.loc[destinations_df["label"] == destination_label, "trigramme"].iloc[0]

    # Afficher une image pour la destination
    destination_images = {
        "Paris (CDG)": "paris.jpg",
        "New York (JFK)": "newyork.jpg",
        # Ajouter des images pour chaque destination
    }
    if destination_label in destination_images:
        st.image(destination_images[destination_label], caption=f"Bienvenue à {destination_label.split(' ')[0]}!", use_container_width=True)

    # Autres paramètres
    departure_date = st.date_input("Date de départ", value=pd.Timestamp(datetime.now()))
    return_date = st.date_input("Date de retour (facultative)", value=None, help="Sélectionnez une date de retour si nécessaire.")
    adults = st.number_input("Nombre de passagers", min_value=1, max_value=10, value=1)

    # Récupérer le token
    token = get_auth_token()

    if token and origin and destination:
        if st.button("Rechercher les vols"):
            with st.spinner("Chargement des vols... ✈️"):
                flights_data = get_flights_from_api(origin, destination, departure_date, return_date, adults, token)

            if flights_data and "data" in flights_data:
                flight_results = []
                for flight in flights_data["data"]:
                    flight_results.extend(extract_flight_details(flight))

                df_flights = pd.DataFrame(flight_results)
                if not df_flights.empty:
                    df_flights = df_flights.sort_values("Prix Total", ascending=True)
                    st.success(f"{len(df_flights)} vols trouvés.")
                    st.dataframe(df_flights, use_container_width=True)

                    for idx, row in df_flights.iterrows():
                        if row['Lien de réservation'] != 'Lien non disponible':
                            st.markdown(f"[Réserver ce vol]({row['Lien de réservation']})", unsafe_allow_html=True)
                else:
                    st.warning("Aucun vol trouvé pour les critères donnés.")
            else:
                st.warning("Aucun vol trouvé pour les critères donnés.")

    # Ajouter un GIF inspirant en bas de page
    st.markdown("---")
    st.image("https://media1.giphy.com/media/v1.Y2lkPTc5MGI3NjExcDAybjE2eXVvajRhaGh6OGxva2xsdm80ZmhuN245YmxwOHdhcXEwbSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/3o6ZsVuc0gxSeAV3hu/giphy.gif", use_container_width=True)
    st.text("Prêt pour votre prochaine aventure ? 🌟")
if __name__ == "__main__":
    main()
    
# Code principal pour récupérer et afficher les vols
    st.image("header.jpg", use_container_width=True)

    st.title("Où voulez-vous vous évader ? ✈️")