import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events
import os

################################### CSV ###################################

# Liste des aéroports
def load_airports():
    return pd.read_csv("data/airports.csv")
airports_df = load_airports()

# Top 5 des aéroports en France (en nombre de vols comptabilisés (arrivées + départs))
def load_nb_flights_airports():
    return pd.read_csv("data/nb_flights_airports_2016-2024.csv")
top_airports_per_year = load_nb_flights_airports()

# Trafic aérien en France
def load_trafic_aerien_FR():
    return pd.read_csv("data/trafic_airports_FRA.csv", sep=";")
trafic_aerien_fr = load_trafic_aerien_FR()

# Retards par compagnie aérienne à Nantes
def load_delays_companies_NTE():
    return pd.read_csv("data/flights_stats_by_company_year_month_NTE_2024.csv")
flights_by_companies_2024 = load_delays_companies_NTE()

###########################################################################

st.header("Quelques chiffres...")

st.subheader("🔵⚪🔴 ... sur les aéroports français")

# 2 colonnes
col1, spacer, col2 = st.columns([2, 0.2, 3])

with col1:
    # Présentation des 5 aéroports français ayant le plus gros trafic (2016-2024)
    years = sorted(top_airports_per_year["YEAR"].unique())
    selected_year = st.selectbox("Choisissez une année :", years) # Sélection de l'année dans une liste déroulante
    top_airports_per_year_choice = top_airports_per_year[top_airports_per_year["YEAR"] == selected_year]
    fig = px.bar(top_airports_per_year_choice, x="FLT_TOT_1", y="APT_NAME", color='APT_NAME', labels=dict(FLT_TOT_1="Nombre de vols", APT_NAME=""), text_auto='.2s', orientation='h', title="👍 Top 5 des aéroports français")
    fig.update_traces(textfont_size=12)
    fig.update_layout(showlegend=False, title={'font': {'size': 20}})
    st.plotly_chart(fig)

with col2:
    st.header(" ")
    st.write(" ")
    fig = px.line(top_airports_per_year, x="YEAR", y="FLT_TOT_1", color='APT_NAME', labels=dict(FLT_TOT_1="Vols", APT_NAME="", YEAR=""), title="📈 Évolution du trafic aérien des 5 plus gros aéroports français")
    fig.update_layout(title={'font': {'size': 20}})
    st.plotly_chart(fig)

# Évolution du trafic aérien en France (2016-2024)
fig = px.line(trafic_aerien_fr, x='FLT_DATE', y='FLT_TOT_1', labels=dict(FLT_TOT_1="Vols", FLT_DATE="Dates"), title="🔵⚪🔴 Évolution du trafic global en France")
fig.update_layout(title={'font': {'size': 20}})
st.plotly_chart(fig)

################################### AEROPORT DE NANTES ###################################

st.subheader("🏙️ ... à l'aéroport de Nantes")

# Création de la liste pour la selectbox avec format "Nom Aéroport (Trigramme)"
#airport_options = [f"{row['nom_aeroport']} ({row['trigramme']})" for _, row in airports_df.iterrows()]

# Liste déroulante des aéroports
#airport_choice = st.selectbox('Choisir un aéroport', airport_options)
# Liste déroulante des mois
months = {'2':'Février', '3':'Mars', '4':'Avril', '5':'Mai', '6':'Juin', '7':'Juillet', '8':'Août', '9':'Septembre', '10':'Octobre', '11':'Novembre', '12':'Décembre'}    
flights_by_companies_2024['Mois_Nom'] = flights_by_companies_2024['Mois'].astype(str).map(months) # Ajouter une colonne 'Mois_Nom' qui contient le nom du mois en français
#selected_month = st.selectbox("Choisissez un mois :", months.values()) # Sélection du mois dans une liste déroulante
#delays_companies_2024_fr_choice = delays_companies_2024_fr[delays_companies_2024_fr["Mois_Nom"] == selected_month]


### LE TRAFIC AÉRIEN ###

# Présentation de l'évolution du nombre de vols à Nantes en 2024 (graph => ligne)
flights_by_companies_2024_global = flights_by_companies_2024.groupby(["Mois"]).sum().reset_index()

fig = px.line(flights_by_companies_2024_global, x="Mois", y="Nombre_Total_Vols", labels=dict(Mois="", Nombre_Total_Vols="Vols"), title="Trafic aérien en 2024")
fig.update_layout(showlegend=False, title={'font': {'size': 20}})
st.plotly_chart(fig)

### LES COMPAGNIES AÉRIENNES ###

st.markdown("#### 👎 Flop 5 des compagnies aériennes en 2024")

# 2 colonnes : 
col1, spacer, col2 = st.columns([1, 0.2, 1])

with col1:
    # Présentation des 5 plus mauvaises compagnies aériennes en terme de retard
    flights_by_companies_2024_year = flights_by_companies_2024.groupby(['Compagnie', 'Année']).agg(
    {'Moyenne_Retard': 'mean',  # Calculate the mean of 'Moyenne_Retard'
     'Nombre_Vols_En_Retard': 'sum', # Sum the number of delayed flights
     'Nombre_Total_Vols': 'sum'} # Sum the total number of flights
    ).reset_index()
    flights_sup_500_by_companies_2024_year_delays = flights_by_companies_2024_year[flights_by_companies_2024_year['Nombre_Total_Vols'] >= 500].sort_values('Moyenne_Retard', ascending=False)
    flights_sup_500_by_companies_2024_year_delays = flights_sup_500_by_companies_2024_year_delays.reset_index(drop=True)
    flop5_flights_delays_companies = flights_sup_500_by_companies_2024_year_delays.head(5)

    fig = px.bar(flop5_flights_delays_companies, x="Moyenne_Retard", y="Compagnie", color='Compagnie', labels=dict(Moyenne_Retard="Retard moyen (en minutes)", Compagnie=""), text_auto='.2s', orientation='h', title="🕓 En délais de retard moyen...")
    fig.update_traces(textfont_size=12)
    fig.update_layout(showlegend=False, title={'font': {'size': 18}})
    st.plotly_chart(fig)
    
with col2:
    # Présentation des 5 compagnies aériennes ayant le plus mauvais ratio de retards de vols    
    flights_sup_500_by_companies_2024_year_delays['Ratio_Retards'] = round(flights_sup_500_by_companies_2024_year_delays['Nombre_Vols_En_Retard'] / flights_sup_500_by_companies_2024_year_delays['Nombre_Total_Vols'] * 100, 2)
    flop5_flights_delays_ratio_companies = flights_sup_500_by_companies_2024_year_delays.sort_values('Ratio_Retards', ascending=False)
    flop5_flights_delays_ratio_companies = flop5_flights_delays_ratio_companies.head(5)

    fig = px.bar(flop5_flights_delays_ratio_companies, x="Ratio_Retards", y="Compagnie", color='Compagnie', labels=dict(Ratio_Retards="Part des vols retardés (en % des vols totals de la compagnie)", Compagnie=""), text_auto='.2s', orientation='h', title="✈️ En part des vols retardés...")
    fig.update_traces(textfont_size=12)
    fig.update_layout(showlegend=False, title={'font': {'size': 18}})
    st.plotly_chart(fig)

### LES FRÉQUENCES D'ARRIVÉE ###

# 2 colonnes
col1, spacer, col2 = st.columns([1, 0.2, 1])

with col1:
    # Présentation du nombre de vols 
    st.write("En attente")

with col2:
    import numpy as np
    # Simuler les données
    hours = list(range(24))  # 24 heures (0 à 23)
    values = np.random.randint(1, 100, size=24)  # Valeurs simulées aléatoires
    # Convertir les heures en degrés (chaque heure = 15°)
    degrees = [hour * 15 for hour in hours]  # 360° répartis sur 24 heures
    # Créer un DataFrame
    df = pd.DataFrame({
        "hour": hours,
        "value": values,
        "degree": degrees
    })
    # Créer le graphique
    fig = px.bar_polar(df, r="value", theta="degree",
                    template="plotly_dark",
                    color_discrete_sequence=px.colors.sequential.Rainbow,
                    title="Vols par tranche horaire"
                    )
    # Personnaliser les axes
    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                tickmode='array',
                tickvals=degrees,  # Utiliser les degrés pour la position des ticks
                ticktext=[f"{h}:00" for h in hours],  # Afficher les heures sous forme de texte
                rotation=90,  # Optionnel : Faire démarrer l'horloge à minuit en haut
                direction="clockwise"  # Les heures augmentent dans le sens des aiguilles d'une montre
            )
        ),
        title={'font': {'size': 20}}
    )
    # Afficher le graphique
    st.plotly_chart(fig)
