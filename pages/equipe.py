import streamlit as st
import base64

################################ CONF PAGE ################################

st.set_page_config(
    layout="wide" # Mode wide uniquement pour cette page
)

################################### CSS ###################################

# Charger ton fichier CSS
css_file = 'css/style.css'  # Spécifie le chemin vers ton fichier CSS

# Ajouter un fichier CSS à la carte (ou inclure dans la page HTML)
with open(css_file, 'r', encoding='utf-8') as file:
    css = file.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

################################### Fx ###################################

# Fonction pour afficher le profil
def afficher_profil(col, image_path, name, linkedin, github, citation, cv_path):
    # Charger l'image et la convertir en base64
    with open(image_path, "rb") as img_file:
        img_data = base64.b64encode(img_file.read()).decode()

    # Afficher le contenu de chaque profil
    with col:
        # Insérer l'image encodée en base64 dans le HTML
        st.write(f"""
            <div class="container">
                <div class="box">
                    <div class="spin-container">
                        <div class="shape">
                            <div class="bd">
                                <img src="data:image/png;base64,{img_data}" alt="{name}">
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 20px;">
            <h3>{name}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div style="display: flex; gap: 15px; margin-bottom: 20px; justify-content: center; align-items: center; text-align: center;">
            <a href="{linkedin}" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="25">
            </a>
            <a href="{github}" target="_blank">
                <svg class="github-icon" width="25" height="25" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                    <path fill-rule="evenodd" clip-rule="evenodd" d="M12 0.297C5.372 0.297 0 5.669 0 12.297c0 5.304 3.438 9.801 8.207 11.387.6.111.793-.261.793-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.609-4.042-1.609-.546-1.386-1.333-1.755-1.333-1.755-1.09-.745.083-.729.083-.729 1.204.085 1.838 1.238 1.838 1.238 1.07 1.835 2.805 1.305 3.49.998.107-.774.42-1.305.763-1.605-2.665-.302-5.466-1.332-5.466-5.93 0-1.31.469-2.38 1.236-3.22-.124-.303-.535-1.521.117-3.169 0 0 1.008-.322 3.3 1.23a11.505 11.505 0 013.003-.403c1.02.004 2.046.137 3.003.403 2.292-1.552 3.3-1.23 3.3-1.23.652 1.648.241 2.866.117 3.169.769.84 1.236 1.91 1.236 3.22 0 4.609-2.807 5.625-5.479 5.921.431.372.815 1.103.815 2.222 0 1.605-.015 2.898-.015 3.293 0 .319.192.694.798.576C20.565 22.095 24 17.6 24 12.297c0-6.628-5.372-12-12-12z"/>
                </svg>
            </a>
        </div>
        """, unsafe_allow_html=True)

        # Ajouter le texte de la citation
        st.markdown(f"""
        <div class="quote-box">
            {citation}
        </div>
        """, unsafe_allow_html=True)
        
        # Ajouter le bouton de téléchargement du CV
        spacer, cv, spacer = st.columns([0.5,1,0.5])
        with cv:
            with open(cv_path, "rb") as f:
                st.download_button(label="Télécharger le CV", data=f, file_name=f"{name}_cv.pdf", mime="application/pdf")

################################## PAGE ##################################

st.title("💖 L'équipe")
#st.header("👉 À propos de nous")

# Informations des membres
members = [
{
    "image": "images/amandine.png",
    "name": "Amandine 👋",
    "linkedin": "https://www.linkedin.com/in/amandine-bessé-2153b1143",
    "github": "https://github.com/ABC-git-85",
    "citation": "Je suis passionnée par l'aviation, le traitement de données et le développement informatique depuis longtemps, et ce site m'a offert l'opportunité de combiner mes intérêts personnels et les compétences acquises lors de ma formation de data analyst. Je suis fière de vous présenter cette application !",
    "cv": "docs/cv_abesse.pdf"
},
{
    "image": "images/laura.png",
    "name": "Laura 👍",
    "linkedin": "https://www.linkedin.com/in/laura-sébille-4908ba2b",
    "github": "https://github.com/Laura4422",
    "citation": "Forte de mon expérience en gestion de projet, j’ai adopté une approche Agile pour assurer un développement fluide et efficace de cette application. En concevant la page de recherche de vols avec affichage des prix, j’ai affiné mon expertise en requêtage d’API et en web scraping, permettant d’offrir aux utilisateurs des informations tarifaires précises et en temps réel.",
    "cv": "docs/cv_lsebille.pdf"
},
{
    "image": "images/sophie.png",
    "name": "Sophie 🫶",
    "linkedin": "https://www.linkedin.com/in/sophiellch",
    "github": "https://github.com/Sophiellch",
    "citation": "Passionnée par l'IA et la data, je développe des solutions innovantes pour analyser et prédire les tendances. Cette application explore les données aériennes avec des modèles de Machine Learning pour offrir des insights pertinents.",
    "cv": "docs/cv_sle_loch.pdf"
}
]

# 3 colonnes
col1, spacer, col2, spacer, col3 = st.columns([1, 0.1, 1, 0.1, 1])

# Boucle pour afficher les profils dans chaque colonne
for i, col in enumerate([col1, col2, col3]):
    afficher_profil(col, members[i]["image"], members[i]["name"], members[i]["linkedin"], members[i]["github"], members[i]["citation"], members[i]["cv"])
