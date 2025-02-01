import streamlit as st

################################ CONF PAGE ################################

st.set_page_config(
    layout="centered" # Mode wide uniquement pour cette page
)

###########################################################################

st.title("🔢 Sources de données")

# API
st.header("🔄️ APIs")
st.markdown("📍 [Aviation Edge](https://aviation-edge.com/) pour les données de suivi en temps réel et l'historique des données de vol")
st.markdown("> **À quelle fréquence les données sont-elles mises à jour pour les données en temps réel ?** \n\n > Pour le suivi de la localisation des vols en direct les données sont mises à jour toutes les 5 minutes environ.\n Pour les données de calendrier elles sont mises à jour toutes les 15 minutes environ.")
st.markdown("> **Quelle est l'historique des données disponibles sur l'API ?** \n\n > Nous avons accès aux données des 12 derniers mois, selon nos conditions d'abonnement.")
st.divider()
st.markdown("💲[Google Flights API](https://serpapi.com/google-flights-api) pour les prix des vols")

# Sites et data
st.header("🛜 Les sites")
st.markdown("📈 [Eurocontrol](https://www.eurocontrol.int/) pour les statistiques de vols")
st.divider()