import streamlit as st

################################ CONF PAGE ################################

st.set_page_config(
    layout="centered" # Mode wide uniquement pour cette page
)

###########################################################################

st.title("🔢 Sources de données")

# API
st.header("🔄️ APIs")
st.markdown("[Aviation Edge](https://aviation-edge.com/)")
st.write("Pour les données de suivi en temps réel et l'historique des données de vol (moins de 1 an)")
st.markdown("> **À quelle fréquence les données sont-elles mises à jour pour les données en temps réel ?** \n\n > Pour le suivi de la localisation des vols en direct les données sont mises à jour toutes les 5 minutes environ.\n Pour les données de calendrier elles sont mises à jour toutes les 15 minutes environ.")
st.divider()
st.markdown("Pour les prix des vols : [Google Flights API](https://serpapi.com/google-flights-api)")

# Sites et data
st.header("🛜 Les sites")
st.markdown("Pour les statistiques de vols : [Eurocontrol](https://www.eurocontrol.int/)")
st.divider()