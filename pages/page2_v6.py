import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_plotly_events import plotly_events

################################ CONF PAGE ################################

st.set_page_config(
    layout="wide" # Mode wide uniquement pour cette page
)

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

# Retards et comptage des vols par compagnie aérienne à Nantes
def load_delays_companies_NTE():
    return pd.read_csv("data/flights_stats_by_company_year_month_NTE_2024.csv")
flights_by_companies_2024 = load_delays_companies_NTE()

# Comptage des vols mois et par heure à Nantes
def load_flights_by_month_per_hour_NTE():
    return pd.read_csv("data/flights_by_hour_month_NTE_2024.csv")
flights_by_hour_2024 = load_flights_by_month_per_hour_NTE()

# Charger les détails des compagnies aériennes (couleurs)
def load_companies():
    return pd.read_csv("data/companies.csv")
companies = load_companies()
companies_colors = dict(zip(companies["Compagnie"], companies["Couleur"])) # Conversion en dictionnaire {Compagnie: Couleur}

##########################################################################################

################################### AÉROPORTS FRANCAIS ###################################

st.header("Quelques chiffres...")

st.subheader("🔵⚪🔴 ... sur les aéroports français")

# KPI - 3 colonnes
kpi1, spacer, kpi2 = st.columns([1, 0.2, 1])
    
kpi1.metric("En France...", "🐓 63 aéroports", "")
kpi2.metric("En 2024...", "✈️ 1 707 533 vols réalisés", "+1,46%")

# 2 colonnes
col1, spacer, col2 = st.columns([2, 0.2, 3])

with col1:
    # Présentation des 5 aéroports français ayant le plus gros trafic (2016-2024)
    # 2 colonnes
    annee, spacer, type_graph = st.columns([1, 0.1, 1])
    with annee:
        years = sorted(top_airports_per_year["YEAR"].unique(), reverse=True)
        selected_year = st.selectbox("Choisissez une année :", years) # Sélection de l'année dans une liste déroulante
        top_airports_per_year_choice = top_airports_per_year[top_airports_per_year["YEAR"] == selected_year]
    with type_graph:
        graph_type = st.radio("Choisissez le type de graphique :", ("Barres", "Donut")) # Boutons radio

    color_palette = px.colors.qualitative.G10
    # Source
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.23,
                                xanchor='center', yanchor='top',
                                text='Source : © 2024 EUROCONTROL',
                                font=dict(size=10, color='rgb(150,150,150)'),
                                showarrow=False))

    if graph_type == "Barres":
        fig = px.bar(top_airports_per_year_choice, x="FLT_TOT_1", y="APT_NAME", color='APT_NAME', labels=dict(FLT_TOT_1="Vols", APT_NAME="Aéroport", YEAR="Année"), text_auto='.2s', orientation='h', title=f"👍 Top 5 des aéroports français en {selected_year}", color_discrete_sequence=color_palette)
        fig.update_traces(textfont_size=14, texttemplate="%{x:,.0f} vols")
        fig.update_layout(showlegend=False, title={'font': {'size': 20}}, xaxis_title='', yaxis_title='', annotations=annotations)
        #st.plotly_chart(fig)
    elif graph_type == "Donut":
        fig = px.pie(top_airports_per_year_choice, values='FLT_TOT_1', names='APT_NAME', color='APT_NAME', labels={"FLT_TOT_1": "Nombre de vols", "APT_NAME": "Aéroport", "YEAR": "Année"}, title=f"🍩 Répartition des vols par aéroport en {selected_year}", color_discrete_sequence=color_palette, hole=0.5)
        fig.update_traces(textfont_size=14, textinfo='percent+label', texttemplate='%{percent:.1%}')
        fig.update_layout(showlegend=True, title={'font': {'size': 20}}, annotations=annotations)        
    st.plotly_chart(fig)

with col2:
    st.header(" ")
    st.write(" ")
    fig = px.line(top_airports_per_year, x="YEAR", y="FLT_TOT_1", color='APT_NAME', markers=True, labels=dict(FLT_TOT_1="Vols", APT_NAME="Aéroports", YEAR="Année"), title="📈 Évolution du trafic aérien des plus gros aéroports français", color_discrete_sequence=px.colors.qualitative.G10)
    # Source
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.23,
                                xanchor='center', yanchor='top',
                                text='Source : © 2024 EUROCONTROL',
                                font=dict(size=10, color='rgb(150,150,150)'),
                                showarrow=False))
    fig.update_layout(title={'font': {'size': 20}}, xaxis_title='', annotations=annotations)
    st.plotly_chart(fig)

# Évolution du trafic aérien en France par jour (2016-2024)
trafic_aerien_fr['FLT_DATE'] = pd.to_datetime(trafic_aerien_fr['FLT_DATE'], format='%d/%m/%Y')
fig = px.line(trafic_aerien_fr, x='FLT_DATE', y='FLT_TOT_1', labels=dict(FLT_TOT_1="Vols", FLT_DATE="Dates"), title="🔵⚪🔴 Évolution du trafic global en France", color_discrete_sequence=px.colors.qualitative.G10, hover_data={'FLT_DATE': '|%d/%m/%Y', 'FLT_TOT_1': True})
fig.update_xaxes(
    tickformat='%m/%Y',
    rangeslider=dict(visible=True),  # Curseur pour zoomer
)
fig.update_layout(title={'font': {'size': 20}}, xaxis_title='', annotations=annotations)
st.plotly_chart(fig)

# Affichage du bouton pour basculer l'affichage du graphique
col1, col2, col3 = st.columns([2,1,2])
with col2:
    if "show_graph" not in st.session_state:
        st.session_state.show_graph = False

    if st.button("Découvrir la saisonnalité des vols 🌼"):
        # Bascule l'état de show_graph
        st.session_state.show_graph = not st.session_state.show_graph

# Si l'état du graphique est "True", affiche-le
if st.session_state.show_graph:
    # Saisonnalité du trafic aérien en France par mois (2016-2024)
    months = {'1':'Janvier', '2':'Février', '3':'Mars', '4':'Avril', '5':'Mai', '6':'Juin', '7':'Juillet', '8':'Août', '9':'Septembre', '10':'Octobre', '11':'Novembre', '12':'Décembre'}

    trafic_aerien_fr_month = trafic_aerien_fr[['MONTH_NUM', 'YEAR', 'FLT_TOT_1']]
    trafic_aerien_fr_month = trafic_aerien_fr_month[trafic_aerien_fr_month['YEAR'] > 2018]
    trafic_aerien_fr_month = trafic_aerien_fr_month.groupby(["YEAR", "MONTH_NUM"]).sum()
    trafic_aerien_fr_month = trafic_aerien_fr_month.reset_index()
    trafic_aerien_fr_month['MONTH_NAME'] = trafic_aerien_fr_month['MONTH_NUM'].astype(str).map(months)
    trafic_aerien_fr_month = trafic_aerien_fr_month.sort_values(by=["YEAR", "MONTH_NUM"], ascending=True)
    trafic_aerien_fr_month['YEAR'] = trafic_aerien_fr_month['YEAR'].astype(str)

    graph_type = st.radio("", ("En barres", "En lignes"))
    color_palette = px.colors.qualitative.Plotly
    # Source
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.23,
                                xanchor='center', yanchor='top',
                                text='Source : © 2024 EUROCONTROL',
                                font=dict(size=10, color='rgb(150,150,150)'),
                                showarrow=False))
    
    if graph_type == "En barres":
        fig = px.bar(trafic_aerien_fr_month, x='MONTH_NAME', y='FLT_TOT_1', color='YEAR', barmode='group', text_auto=True, labels={'FLT_TOT_1': "Vols", 'MONTH_NAME': "Mois", 'YEAR':'Année'}, title="☀️ Saisonnalité du trafic en France", color_discrete_sequence=color_palette)
        fig.update_traces(texttemplate="%{y:,.0f}")
        fig.update_layout(title={'font': {'size': 20}}, xaxis_title='', annotations=annotations)
    elif graph_type == "En lignes":
        fig = px.line(trafic_aerien_fr_month, x='MONTH_NAME', y='FLT_TOT_1', color='YEAR', markers=True, labels=dict(FLT_TOT_1="Vols", MONTH_NAME="Mois", YEAR="Année"), title="☀️ Saisonnalité du trafic en France", color_discrete_sequence=color_palette)
        fig.update_layout(title={'font': {'size': 20}}, xaxis_title='', annotations=annotations)
    st.plotly_chart(fig)    

################################### AÉROPORT DE NANTES ###################################

st.subheader("🐘 ... à l'aéroport de Nantes")

months = {'2':'Février', '3':'Mars', '4':'Avril', '5':'Mai', '6':'Juin', '7':'Juillet', '8':'Août', '9':'Septembre', '10':'Octobre', '11':'Novembre', '12':'Décembre'}

# KPI - 3 colonnes
kpi1, spacer, kpi2,  = st.columns([1, 0.2, 1])
    
kpi1.metric("À Nantes en 2024...", "🧳 131 compagnies aériennes recensées", "")
kpi2.metric("En 2024...", "✈️ 52 549 vols réalisés", "+3,59%")

### LES COMPAGNIES AÉRIENNES ###

# Présentation de l'évolution du nombre de vols à Nantes en 2024
df_flight_nantes = trafic_aerien_fr[['APT_NAME', 'MONTH_NUM', 'YEAR', 'FLT_TOT_1']]
df_flight_nantes = df_flight_nantes[(df_flight_nantes['YEAR'] > 2021) & (df_flight_nantes['APT_NAME'] == 'Nantes-Atlantique')]
df_flight_nantes = df_flight_nantes.groupby(["APT_NAME", "YEAR", "MONTH_NUM"]).sum()
df_flight_nantes = df_flight_nantes.reset_index()
df_flight_nantes['MONTH_NAME'] = df_flight_nantes['MONTH_NUM'].astype(str).map(months)
df_flight_nantes = df_flight_nantes.sort_values(by=["MONTH_NUM", "YEAR"], ascending=True)
df_flight_nantes['YEAR'] = df_flight_nantes['YEAR'].astype(str)

fig = px.bar(df_flight_nantes, x='MONTH_NAME', y='FLT_TOT_1', color='YEAR', barmode='group', text_auto=True, labels={'FLT_TOT_1': "Vols", 'MONTH_NAME': "Mois", 'YEAR':'Année'}, title="🐘 Évolution du trafic aérien à Nantes", color_discrete_sequence=px.colors.qualitative.Plotly)
# Source
annotations = []
annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.23,
                            xanchor='center', yanchor='top',
                            text='Source : © 2024 EUROCONTROL',
                            font=dict(size=10, color='rgb(150,150,150)'),
                            showarrow=False))
fig.update_layout(title={'font': {'size': 20}}, xaxis_title='', bargap=0.15, bargroupgap=0.1, annotations=annotations)
st.plotly_chart(fig)

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

    fig = px.bar(flop5_flights_delays_companies, x="Moyenne_Retard", y="Compagnie", color='Compagnie', labels=dict(Moyenne_Retard="Retard moyen (en minutes)", Compagnie="Compagnie"), text_auto='.2s', orientation='h', title="🕓 En délai de retard moyen...", color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_traces(textfont_size=14, texttemplate="%{x:,.1f} minutes")
    # Source
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.23,
                                xanchor='center', yanchor='top',
                                text='Source : Aviation Edge (02/2024 - 12/2024) - Compagnies réalisant plus de 500 vols par an',
                                font=dict(size=10, color='rgb(150,150,150)'),
                                showarrow=False))
    fig.update_layout(showlegend=False, title={'font': {'size': 18}}, yaxis_title='', annotations=annotations)
    st.plotly_chart(fig)
    
with col2:
    # Présentation des 5 compagnies aériennes ayant le plus mauvais ratio de retards de vols    
    flights_sup_500_by_companies_2024_year_delays['Ratio_Retards'] = round(flights_sup_500_by_companies_2024_year_delays['Nombre_Vols_En_Retard'] / flights_sup_500_by_companies_2024_year_delays['Nombre_Total_Vols'] * 100, 2)
    flop5_flights_delays_ratio_companies = flights_sup_500_by_companies_2024_year_delays.sort_values('Ratio_Retards', ascending=False).head(5)

    fig = px.bar(flop5_flights_delays_ratio_companies, x="Ratio_Retards", y="Compagnie", color='Compagnie', labels=dict(Ratio_Retards="Part des vols en retard (en % des vols totals de la compagnie)", Compagnie="Compagnie"), text_auto='.2s', orientation='h', title="✈️ En part des vols en retard...", color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_traces(textfont_size=14, texttemplate="%{x:,.1f} %")
    # Source
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.23,
                                xanchor='center', yanchor='top',
                                text='Source : Aviation Edge (02/2024 - 12/2024) - Compagnies réalisant plus de 500 vols par an',
                                font=dict(size=10, color='rgb(150,150,150)'),
                                showarrow=False))
    fig.update_layout(showlegend=False, title={'font': {'size': 18}}, yaxis_title='', annotations=annotations)
    st.plotly_chart(fig)

### LES FRÉQUENCES D'ARRIVÉE ###

st.markdown("#### 🛃 Répartition des vols en 2024")

# Liste déroulante des mois
selected_month = st.selectbox("Choisissez un mois :", months.values()) # Sélection du mois dans une liste déroulante

# 2 colonnes
col1, spacer, col2 = st.columns([1, 0.2, 1])

with col1:
    # Présentation des top 5 des compagnies qui réalisent le plus de vols
    flights_by_companies_2024['Mois_Nom'] = flights_by_companies_2024['Mois'].astype(str).map(months) # Ajouter une colonne 'Mois_Nom' qui contient le nom du mois en français
    flights_by_companies_2024 = flights_by_companies_2024.sort_values(['Mois', 'Nombre_Total_Vols'], ascending=False)    
    flights_by_companies_2024_choice = flights_by_companies_2024[flights_by_companies_2024["Mois_Nom"] == selected_month]
    top5_flights_companies = flights_by_companies_2024_choice.head(5)  
    
    fig = px.bar(top5_flights_companies, x="Nombre_Total_Vols", y="Compagnie", color='Compagnie', labels=dict(Nombre_Total_Vols="Vols", Compagnie="Compagnie"), text_auto='.2s', orientation='h', title=f"👍 Top 5 des compagnies aériennes en {selected_month.lower()}", color_discrete_map=companies_colors)
    fig.update_traces(textfont_size=14, texttemplate="%{x:,.0f} vols")
    # Source
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.23,
                                xanchor='center', yanchor='top',
                                text='Source : Aviation Edge (02/2024 - 12/2024)',
                                font=dict(size=10, color='rgb(150,150,150)'),
                                showarrow=False))
    fig.update_layout(showlegend=False, title={'font': {'size': 18}}, xaxis_title='', yaxis_title='', annotations=annotations)
    st.plotly_chart(fig)

with col2:
    flights_by_hour_2024['Mois_Nom'] = flights_by_hour_2024['Mois'].astype(str).map(months) # Ajouter une colonne 'Mois_Nom' qui contient le nom du mois en français
    flights_by_hour_2024_choice = flights_by_hour_2024[flights_by_hour_2024["Mois_Nom"] == selected_month] 
    flights_by_hour_2024_choice['degrees'] = flights_by_hour_2024_choice['Heure'].apply(lambda x: x * 15) # Convertir les heures en degrés (chaque heure = 15° => 360° / 24h)
    flights_by_hour_2024_choice = flights_by_hour_2024_choice.sort_values(by=['Type', 'Mois', 'Heure'])
    fig = px.bar_polar(flights_by_hour_2024_choice, r="Nombre_De_Vols", theta="degrees", color='Type', template="plotly_dark", labels=dict(Nombre_De_Vols="Vols", degrees="Heure", Type="Type de vol"), color_discrete_sequence=px.colors.qualitative.Dark2, title=f"🕟 Vols par tranche horaire en {selected_month.lower()}")
    # Source
    annotations = []
    annotations.append(dict(xref='paper', yref='paper', x=0.5, y=-0.23,
                                xanchor='center', yanchor='top',
                                text='Source : Aviation Edge (02/2024 - 12/2024)',
                                font=dict(size=10, color='rgb(150,150,150)'),
                                showarrow=False))
    fig.update_layout(
        polar=dict(
            angularaxis=dict(
                tickmode='array',
                tickvals=flights_by_hour_2024_choice['degrees'],  # Utiliser les degrés pour la position des ticks
                ticktext=[f"{h}:00" for h in flights_by_hour_2024_choice['Heure']],  # Afficher les heures sous forme de texte
                rotation=90,  # Optionnel : Faire démarrer l'horloge à minuit en haut
                direction="clockwise"  # Les heures augmentent dans le sens des aiguilles d'une montre
            )
        ),
        title={'font': {'size': 18}},
        legend_title=dict(text=""),
        annotations=annotations
    )   
    st.plotly_chart(fig)