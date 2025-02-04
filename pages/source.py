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
st.markdown("💲[Google Flights API](https://rapidapi.com/DataCrawler/api/google-flights2/) pour les prix des vols")
st.markdown("[Documentation](https://rapidapi.com/DataCrawler/api/google-flights2 pour la documentation")
st.markdown(">**Combien de endpoints sont utilisés ?** \n\n > Nous utilisons 3 endpoints, une pour la recherche des vols et 2 autres pour obtenir le lien de réservation.")
            
# Sites et data
st.header("🛜 Les sites")
st.markdown("📈 [Eurocontrol](https://www.eurocontrol.int/) pour les statistiques de vols")
st.markdown("🗺️ [Ourairports](https://ourairports.com/data/) pour avoir une liste de destinations")
st.divider()
