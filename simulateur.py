import streamlit as st
import gspread
import json
from google.oauth2.service_account import Credentials

# --- Titre ---
st.title("📊 Comparateur Compte Titres vs Contrat de Capitalisation")

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
if st.button("Lancer la simulation"):
    taux_net = rendement / 100 * (1 - 0.105)  # Fiscalité sur rendements uniquement
    compte_titres = capital * ((1 + taux_net) ** duree)
    contrat_capitalisation = capital * ((1 + rendement/100) ** duree)

    st.subheader("📌 Résultats de la simulation")
    st.write(f"💼 Valeur finale Compte Titres : **{compte_titres:,.0f} €**")
    st.write(f"🏦 Valeur finale Contrat Capitalisation : **{contrat_capitalisation:,.0f} €**")

    # Enregistrement Google Sheets
    if st.button("💾 Enregistrer dans la base TIPS"):
        save_to_google_sheets(capital, rendement, duree, compte_titres, contrat_capitalisation)
