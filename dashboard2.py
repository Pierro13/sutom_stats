import streamlit as st
import pandas as pd
import re
import plotly.express as px

st.set_page_config(page_title="SUTOM Family Stats", layout="wide")

# --- FONCTION D'EXTRACTION ---
def parse_data(file_path):
    data = []
    # Regex adaptée au format de ton fichier chat.txt
    pattern = r"(\d{2}/\d{2}/\d{4}).*? - (.*?): #SUTOM #(\d+) (\d|X)/6"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(pattern, content)
        for m in matches:
            date, pseudo, num_sutom, score_raw = m
            # On stocke le score : X devient 7, le reste devient int
            score_val = 7 if score_raw == 'X' else int(score_raw)
            data.append({
                "Date": pd.to_datetime(date, dayfirst=True),
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
joueurs_disponibles = sorted(df['Joueur'].unique())
selection_joueurs = st.sidebar.multiselect(
    "Choisir les joueurs à afficher", 
    joueurs_disponibles, 
    default=joueurs_disponibles
)

# Filtrage du DataFrame
df_filtre = df[df['Joueur'].isin(selection_joueurs)]

# --- TITRE ---
st.title("🏆 SUTOM Dashboard")
st.markdown(f"Analyse de **{len(df_filtre)}** parties partagées.")

# --- SECTION 1 : CLASSEMENT & RÉCAP ---
st.header("🥇 Classement Général")
col1, col2 = st.columns([2, 1])

with col1:
    # Calcul des stats par personne
    stats = df_filtre.groupby("Joueur").agg(
        Moyenne=("Score", "mean"),
        Parties=("Score", "count")
    ).sort_values("Moyenne")
    
    # Formattage pour l'affichage
    stats['Moyenne'] = stats['Moyenne'].round(2)
    
    st.dataframe(stats, use_container_width=True)

with col2:
    st.subheader("💡 Statistiques Fun")
    meilleur = stats.index[0]
    st.success(f"**Le Boss :** {meilleur} ({stats.loc[meilleur, 'Moyenne']})")
    
    plus_assidu = stats['Parties'].idxmax()
    st.info(f"**Le plus accro :** {plus_assidu} ({stats.loc[plus_assidu, 'Parties']} grilles)")

# --- SECTION 2 : ÉVOLUTION DYNAMIQUE ---
st.header("📈 Évolution des performances")

# On crée un pivot pour le graphique d'évolution
# On lisse avec une moyenne mobile pour que ce soit plus lisible
df_evol = df_filtre.pivot_table(index="Date", columns="Joueur", values="Score")
df_evol_smooth = df_evol.rolling(window=7, min_periods=1).mean() # Moyenne mobile sur 7 jours

fig_evol = px.line(
    df_evol_smooth, 
    title="Moyenne glissante du score (7 jours)",
    labels={"value": "Score moyen", "Date": "Temps"},
    template="plotly_dark"
)
st.plotly_chart(fig_evol, use_container_width=True)

# --- SECTION 3 : RÉPARTITION DES SCORES ---
st.header("📊 Distribution des scores")
st.write("Répartition des tentatives (combien de 1/6, 2/6, etc.)")

fig_dist = px.histogram(
    df_filtre, 
    x="Score", 
    color="Joueur", 
    barmode="group",
    nbins=7,
    category_orders={"Score": [1, 2, 3, 4, 5, 6, 7]}
)
st.plotly_chart(fig_dist, use_container_width=True)