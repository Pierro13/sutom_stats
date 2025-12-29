import streamlit as st
import pandas as pd
import re

# Configuration de la page
st.set_page_config(page_title="SUTOM Stats Dashboard", layout="wide")

def parse_data(file_path):
    data = []
    # Regex pour extraire : Date, Pseudo, Numéro Sutom, Score
    pattern = r"(\d{2}/\d{2}/\d{4}).*? - (.*?): #SUTOM #(\d+) (\d|X)/6"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(pattern, content)
        for m in matches:
            date, pseudo, num_sutom, score = m
            score_val = 7 if score == 'X' else int(score) # On note 7 si échec
            data.append({
                "Date": pd.to_datetime(date, dayfirst=True),
                "Joueur": pseudo,
                "Sutom_ID": int(num_sutom),
                "Score": score_val
            })
    return pd.DataFrame(data)

# Chargement des données
df = parse_data("chat.txt")

# --- DASHBOARD STREAMLIT ---
st.title("📊 SUTOM : Le Dashboard de la Mif")

# 1. KPIs de base
col1, col2, col3 = st.columns(3)
col1.metric("Total de parties", len(df))
col2.metric("Meilleure moyenne", f"{df.groupby('Joueur')['Score'].mean().min():.2f}")
col3.metric("Nombre de joueurs", df['Joueur'].nunique())

# 2. Graphique : Moyenne par joueur
st.subheader("Moyenne de tentatives par joueur (Plus bas = meilleur)")
avg_scores = df.groupby("Joueur")["Score"].mean().sort_values()
st.bar_chart(avg_scores)

# 3. Évolution temporelle
st.subheader("Historique des scores")
df_pivot = df.pivot_table(index="Date", columns="Joueur", values="Score")
st.line_chart(df_pivot.interpolate())

# 4. Tableau détaillé
if st.checkbox("Voir les données brutes"):
    st.write(df)