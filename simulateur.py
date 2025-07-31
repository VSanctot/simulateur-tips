import streamlit as st
import gspread
import json
import pandas as pd
import matplotlib.pyplot as plt
from google.oauth2.service_account import Credentials

# --- Design de la page ---
st.set_page_config(page_title="TIPS - Comparateur Fiscalité", page_icon="💼", layout="centered")

# --- Titre ---
st.markdown("<h1 style='color:#003366;'>💼 Comparateur Compte Titres vs Contrat de Capitalisation</h1>", unsafe_allow_html=True)
st.write("Un outil TIPS pour comparer l'impact fiscal sur vos placements.")

# --- Formulaire utilisateur ---
capital = st.number_input("💰 Capital initial (€)", min_value=1000, value=100000, step=1000)
rendement = st.number_input("📈 Rendement annuel (%)", min_value=1.0, value=3.5, step=0.1)
duree = st.number_input("⏳ Durée (années)", min_value=1, value=10, step=1)

# --- Fonction connexion Google Sheets ---
def connect_google_sheets():
    try:
        creds_dict = dict(st.secrets["GOOGLE_SHEETS_CREDS"])
        creds_json = json.loads(json.dumps(creds_dict))
        credentials = Credentials.from_service_account_info(creds_json)
        gc = gspread.authorize(credentials)
        sh = gc.open("TIPS_SIMULATEUR")  # ⚠️ Nom exact de ta feuille Google Sheets
        return sh.sheet1
    except Exception as e:
        st.error(f"⚠️ Erreur connexion Google Sheets : {e}")
        return None

# --- Fonction sauvegarde Google Sheets ---
def save_to_google_sheets(capital, rendement, duree, compte_titres, contrat_capitalisation):
    worksheet = connect_google_sheets()
    if worksheet:
        try:
            worksheet.append_row([
                capital, rendement, duree,
                round(compte_titres, 2), round(contrat_capitalisation, 2)
            ])
            st.success("✅ Données envoyées dans Google Sheets")
        except Exception as e:
            st.error(f"⚠️ Erreur envoi Google Sheets : {e}")

# --- Simulation ---
if st.button("🚀 Lancer la simulation"):
    taux_net = rendement / 100 * (1 - 0.105)  # Fiscalité sur rendements uniquement

    # Calcul année par année
    annees = list(range(1, duree + 1))
    valeurs_ct = [capital * ((1 + taux_net) ** an) for an in annees]
    valeurs_cc = [capital * ((1 + rendement/100) ** an) for an in annees]

    compte_titres_final = valeurs_ct[-1]
    contrat_capitalisation_final = valeurs_cc[-1]

    # Résultats
    st.markdown("<h2 style='color:#003366;'>📌 Résultats de la simulation</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#444;'>💼 Valeur finale Compte Titres : <b style='color:#CC0000;'>{compte_titres_final:,.0f} €</b></p>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#444;'>🏦 Valeur finale Contrat Capitalisation : <b style='color:#009933;'>{contrat_capitalisation_final:,.0f} €</b></p>", unsafe_allow_html=True)

    # --- Graphique comparatif ---
    df = pd.DataFrame({
        "Années": annees,
        "Compte Titres": valeurs_ct,
        "Contrat de Capitalisation": valeurs_cc
    })

    fig, ax = plt.subplots(figsize=(8,5))
    ax.plot(df["Années"], df["Compte Titres"], label="Compte Titres", linewidth=2.5, color="#CC0000")
    ax.plot(df["Années"], df["Contrat de Capitalisation"], label="Contrat de Capitalisation", linewidth=2.5, color="#009933")
    ax.set_xlabel("Années", fontsize=12, color="#003366")
    ax.set_ylabel("Valeur (€)", fontsize=12, color="#003366")
    ax.set_title("📈 Évolution comparée des placements", fontsize=14, color="#003366")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    st.pyplot(fig)

    # Enregistrement Google Sheets
    if st.button("💾 Enregistrer dans la base TIPS"):
        save_to_google_sheets(capital, rendement, duree, compte_titres_final, contrat_capitalisation_final)
