import streamlit as st
import pandas as pd
import re
import plotly.express as px

st.set_page_config(page_title="SUTOM Family Stats", layout="wide")

# --- FONCTION D'EXTRACTION ---
@st.cache_data
def parse_data(file_path):
    data = []
    # Regex précise pour : Date, Heure, Nom, Numéro Sutom, Score
    pattern = r"(\d{2}/\d{2}/\d{4}), (\d{2}:\d{2}) - (.*?): #SUTOM #(\d+) (\d|X)/6"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(pattern, content)
        for date, heure, pseudo, num_sutom, score_raw in matches:
            score_val = 7 if score_raw == 'X' else int(score_raw)
            data.append({
                "Date": pd.to_datetime(date, dayfirst=True),
                "Heure_Brute": heure,
                "Heure_H": int(heure.split(':')[0]),
                "Joueur": pseudo,
                "Sutom_ID": int(num_sutom),
                "Score": score_val,
                "Succès": 1 if score_raw != 'X' else 0
            })
    return pd.DataFrame(data)

# Chargement
df = parse_data("chat.txt")

# --- FILTRES DYNAMIQUES (SIDEBAR) ---
st.sidebar.header("⚙️ Configuration")

# # Ajout du bouton d'upload pour l'option "Refresh" manuelle
# st.sidebar.subheader("📤 Mettre à jour les données")
# uploaded_file = st.sidebar.file_uploader("Glisser un nouvel export chat.txt", type="txt")

# if uploaded_file is not None:
#     # On pourrait adapter la fonction pour lire directement le contenu uploadé
#     # Pour l'instant on garde le fonctionnement standard
#     st.sidebar.info("Fichier reçu ! (Nécessite intégration lecture directe)")

st.sidebar.subheader("Joueurs à afficher")
joueurs_disponibles = sorted(df['Joueur'].unique())
selection_joueurs = []

for j in joueurs_disponibles:
    is_checked = st.sidebar.checkbox(j, value=True)
    if is_checked:
        selection_joueurs.append(j)

df_filtre = df[df['Joueur'].isin(selection_joueurs)]

# --- TITRE ---
st.title("🏆 SUTOM : Le Dashboard Interactif")

if not selection_joueurs:
    st.warning("Veuillez cocher au moins un joueur dans la barre latérale.")
    st.stop()

# --- SECTION 1 : CLASSEMENT (Pleine largeur) ---
st.header("🥇 Classement par performance")

# Calcul des stats
stats = df_filtre.groupby("Joueur").agg(
    Moyenne_Tentatives=("Score", "mean"),
    Parties_Postées=("Score", "count")
).sort_values("Moyenne_Tentatives")

stats['Moyenne_Tentatives'] = stats['Moyenne_Tentatives'].round(2)

# Affichage sur toute la largeur
st.dataframe(stats, use_container_width=True)

# --- SECTION 2 : ÉVOLUTION DYNAMIQUE ---
st.header("📈 Évolution des scores")
st.write("Moyenne glissante sur 7 jours (pour voir la tendance)")

df_evol = df_filtre.pivot_table(index="Date", columns="Joueur", values="Score")
df_evol_smooth = df_evol.rolling(window=7, min_periods=1).mean()

fig_evol = px.line(
    df_evol_smooth, 
    labels={"value": "Score moyen (lissé)", "Date": "Jour"},
    template="plotly_white"
)
# Inverser l'axe Y pour que le "1" soit en haut
fig_evol.update_yaxes(autorange="reversed")
st.plotly_chart(fig_evol, use_container_width=True)

# --- SECTION 3 : RÉPARTITION DES HEURES ---
st.header("⏰ À quelle heure joue-t-on ?")
fig_heure = px.histogram(
    df_filtre, 
    x="Heure_H", 
    color="Joueur", 
    nbins=24, 
    barmode="group",
    labels={"Heure_H": "Heure (0-23h)"},
    template="plotly_white"
)
st.plotly_chart(fig_heure, use_container_width=True)