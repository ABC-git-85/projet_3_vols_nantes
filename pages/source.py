import streamlit as st

########################################
# 📌 CONFIGURATION DE LA PAGE
########################################

st.set_page_config(
    layout="centered"  # Centrage de l'affichage pour une meilleure lisibilité
)

########################################
# 📌 SOURCES DE DONNÉES
########################################

st.title("🔢 Sources de données")

# 📡 APIs
st.header("🔄️ APIs")

st.markdown("📍 [Aviation Edge](https://aviation-edge.com/) pour les données de suivi en temps réel et l'historique des données de vol")

st.markdown("""
> **À quelle fréquence les données sont-elles mises à jour pour les données en temps réel ?**  
> - Le suivi de la localisation des vols en direct est mis à jour toutes les **5 minutes** environ.  
> - Les données de calendrier sont mises à jour toutes les **15 minutes** environ.
""")

st.markdown("""
> **Quel est l'historique des données disponibles sur l'API ?**
> - Nous avons accès aux données des 12 derniers mois, selon nos conditions d'abonnement.            
""")

st.markdown("💲 [Google Flights API](https://serpapi.com/google-flights-api) pour les prix des vols")

st.markdown("🌤️ [Weather API](https://www.weatherapi.com) pour la météo")

st.markdown("---")  # Séparateur visuel

# 🌍 Sites et données
st.header("🛜 Les sites")
st.markdown("📊 **Pour les statistiques de vols :** [Eurocontrol](https://www.eurocontrol.int/)")
st.markdown("---")

########################################
# 📌 GUIDE UTILISATEUR
########################################

st.title("📖 Guide Utilisateur")

st.markdown("""
Bienvenue sur **Projet 3 Vols Nantes**, une application qui vous permet d'explorer les vols en temps réel, d'accéder à des statistiques sur le trafic aérien en France et de rechercher des vols avec leurs prix.

---

## ✈️ Fonctionnalités principales  

### 🔹 Suivi des vols en temps réel
- Consultez les vols en cours autour des aéroports français.  
- Visualisez les trajets et les détails des vols en direct.  
- Actualisation régulière pour obtenir les données les plus récentes.

### 🔹 Statistiques sur le trafic aérien en France
- Analysez les tendances du trafic aérien.  
- Accédez aux données sur les retards et annulations.  
- Comparez les volumes de vols selon différentes périodes.

### 🔹 Recherche de vols et comparaison des prix
- Trouvez les meilleures offres de vols au départ des aéroports français.  
- Comparez les prix et les options de voyage.  
- Filtrez les résultats selon vos préférences.

---

## 🛠️ Comment utiliser l'application ?  

1. **Accédez au site** : [Projet 3 Vols Nantes](https://projet3volsnantes-als.streamlit.app/)  
2. **Naviguez entre les sections** grâce au menu latéral :  
   - 📡 **Vols en temps réel** : Affichage des avions en vol près des aéroports.  
   - 📊 **Statistiques** : Consultez les tendances et analyses du trafic aérien.  
   - 🔎 **Recherche de vols** : Trouvez les meilleures offres et comparez les prix.  
3. **Sélectionnez un aéroport ou une plage de dates** pour personnaliser vos résultats.  
4. **Explorez les données et profitez des services offerts par l’application !**  

---

## ❓ FAQ  

**🔹 À quelle fréquence les données sont-elles mises à jour ?**  
- Les données des vols en temps réel sont rafraîchies environ **toutes les 5 minutes**.  
- Les données des statistiques sont mises à jour régulièrement en fonction des sources disponibles.

**🔹 L’application est-elle gratuite ?**  
- Oui, l’application est accessible **gratuitement** et ne nécessite pas de compte utilisateur.

**🔹 Quels aéroports sont couverts ?**  
- Tous les principaux **aéroports français** sont inclus dans la base de données.

---

## 🆘 Support & Contact  
Si vous avez des questions ou rencontrez un problème, vous pouvez contacter l’équipe via la [**Page Équipe**](https://projet3volsnantes-als.streamlit.app/equipe_v2).
""")
