import streamlit as st

################################ CONF PAGE ################################

st.set_page_config(
    layout="wide"  # Centrage de l'affichage pour une meilleure lisibilité
)

########################## 📌 GUIDE UTILISATEUR ###########################

st.title("📖 Guide Utilisateur")

st.markdown("""
Bienvenue sur **Projet 3 Vols Nantes**, une application qui vous permet d'explorer les vols en temps réel, d'accéder à des statistiques sur le trafic aérien en France et de rechercher des vols avec leurs prix.

---
            
## 🔢 Sources de données

#### 🔹 APIs
 - 📍 [Aviation Edge](https://aviation-edge.com/) pour les données de suivi en temps réel et l'historique des données de vol"
 - 💲 [Google Flights API](https://serpapi.com/google-flights-api) pour les prix des vols"
 - 🌤️ [Weather API](https://www.weatherapi.com) pour la météo"
            
#### 🔹 Les sites            
 - Pour les statistiques de vols : [Eurocontrol](https://www.eurocontrol.int/)

---

## ✈️ Fonctionnalités principales  

#### 🔹 Suivi des vols en temps réel
- Consultez les vols en cours autour des grands aéroports français.  
- Visualisez les coordonnées et les détails des vols en direct.  
- Actualisation régulière pour obtenir les données les plus récentes.

#### 🔹 Statistiques sur le trafic aérien en France
- Analysez les tendances du trafic aérien.  
- Accédez aux données sur les retards et annulations.  
- Comparez les volumes de vols selon différentes périodes.

#### 🔹 Recherche de vols et comparaison des prix
- Trouvez les meilleures offres de vols au départ des aéroports français.  
- Comparez les prix et les options de voyage.  
- Filtrez les résultats selon vos préférences.

---

## 🛠️ Comment utiliser l'application ?  

1. **Accédez au site** : [Projet 3 Vols Nantes](https://projet3volsnantes-als.streamlit.app/)  
2. **Naviguez entre les sections** grâce au menu latéral :  
   - ✈️ **Vols en temps réel** : Affichage des avions en vol près des aéroports.  
   - 📈 **Statistiques** : Consultez les tendances et analyses du trafic aérien.  
   - 💺 **Recherche de vols** : Trouvez les meilleures offres et comparez les prix.  
3. **Sélectionnez un aéroport ou une plage de dates** pour personnaliser vos résultats.  
4. **Explorez les données et profitez des services offerts par l’application !**  

---

## ❓ FAQ  

#### 🔹 À quelle fréquence les données sont-elles mises à jour ?
- Les données des vols en temps réel sont rafraîchies environ **toutes les 5 minutes**. Les horaires des vols sont mises à jour toutes les **15 minutes** environ.
- Les données des statistiques sont mises à jour régulièrement en fonction des sources disponibles.
            
#### 🔹 Quel est l'historique des données disponibles ?
- Selon la source, nous avons soit accès aux données des 12 derniers mois pour les API notamment, soit aux données jusqu'à 2016 pour les statistiques des vols.

#### 🔹 L’application est-elle gratuite ?
- Oui, l’application est accessible **gratuitement** et ne nécessite pas de compte utilisateur.

#### 🔹 Quels aéroports sont couverts ?
- Tous les principaux **aéroports français** sont inclus dans la base de données.

---

## 🆘 Support & Contact  
Si vous avez des questions ou rencontrez un problème, vous pouvez contacter l’équipe ici : [**À propos de nous**](https://projet3volsnantes-als.streamlit.app/equipe)
""")