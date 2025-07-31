import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ======================
# CONFIGURATION GOOGLE SHEETS
# ======================
def envoi_google_sheets(prenom_nom, societe, email_pro, capital, rendement, duree):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GOOGLE_SHEETS_CREDS"], scope)
        client = gspread.authorize(creds)

        sh = client.open("TIPS_Simulateur")
        sheet = sh.sheet1
        sheet.append_row([prenom_nom, societe, email_pro, capital, rendement, duree])
        
        # Message neutre pour les clients
        st.success("✅ Simulation enregistrée avec succès")
    except Exception as e:
        # Message discret côté client
        st.warning("⚠️ Impossible d’enregistrer la simulation pour le moment.")
        # Log détaillé uniquement en console (pour toi)
        print(f"[DEBUG] Erreur Google Sheets : {e}")

# ======================
# INTERFACE
# ======================
col1, col2 = st.columns([1,5])
with col1:
    st.image("logo_tips.png", width=120)  # <-- Mets ton logo dans le dossier
with col2:
    st.title("Comparateur Compte Titres vs Contrat de Capitalisation")

st.markdown("### Remplissez vos informations :")

prenom_nom = st.text_input("Prénom / Nom")
societe = st.text_input("Société")
email_pro = st.text_input("Email professionnel")
capital_initial = st.number_input("Capital investi (€)", min_value=1000, step=1000, value=10000)
taux_rendement = st.number_input("Rendement annuel (%)", min_value=1.0, step=0.1, value=4.0)
duree = st.slider("Durée de placement (années)", 1, 30, 10)

if st.button("Lancer la simulation"):
    annees = list(range(1, duree + 1))
    rendement_net = taux_rendement * (1 - 0.30)  # Exemple : fiscalité fixe de 30% sur les rendements

    valeurs_ct = [capital_initial * ((1 + (taux_rendement / 100)) ** annee) for annee in annees]
    valeurs_capitalisation = [capital_initial * ((1 + (rendement_net / 100)) ** annee) for annee in annees]

    # Forcer même point de départ (année 0 = capital initial)
    valeurs_ct.insert(0, capital_initial)
    valeurs_capitalisation.insert(0, capital_initial)
    annees = [0] + annees

    df = pd.DataFrame({
        "Années": annees,
        "Compte Titres": valeurs_ct,
        "Contrat Capitalisation": valeurs_capitalisation
    })

    # Affichage tableau
    st.subheader("📊 Résultats chiffrés")
    st.dataframe(df)

    # Courbes comparatives
    st.subheader("📈 Évolution des placements")
    fig, ax = plt.subplots()
    ax.plot(df["Années"], df["Compte Titres"], label="Compte Titres", linewidth=2)
    ax.plot(df["Années"], df["Contrat Capitalisation"], label="Contrat de Capitalisation", linewidth=2)
    ax.set_xlabel("Années")
    ax.set_ylabel("Valeur (€)")
    ax.legend()
    st.pyplot(fig)

    # Envoi des données (stockage invisible pour le client)
    envoi_google_sheets(prenom_nom, societe, email_pro, capital_initial, taux_rendement, duree)
