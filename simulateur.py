import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ======================
# CONFIGURATION GOOGLE SHEETS
# ======================
def envoi_google_sheets(nom, email, capital, rendement, duree):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GOOGLE_SHEETS_CREDS"], scope)
        client = gspread.authorize(creds)

        sheet = client.open("TIPS_Simulateur").sheet1
        sheet.append_row([nom, email, capital, rendement, duree])
        st.success("✅ Données envoyées dans la base TIPS (Google Sheets)")
    except Exception as e:
        st.error(f"⚠️ Erreur Google Sheets : {e}")

# ======================
# INTERFACE
# ======================
st.title("Comparateur Compte Titres vs Contrat de Capitalisation")

st.markdown("### Remplissez vos informations :")

nom = st.text_input("Nom")
email = st.text_input("Email")
capital_initial = st.number_input("Capital investi (€)", min_value=1000, step=1000, value=10000)
taux_rendement = st.number_input("Rendement annuel (%)", min_value=1.0, step=0.1, value=4.0)
duree = st.slider("Durée de placement (années)", 1, 30, 10)

if st.button("Lancer la simulation"):
    annees = list(range(1, duree + 1))
    rendement_net = taux_rendement * (1 - 0.30)  # Exemple fiscalité = 30% sur les rendements

    valeurs_ct = [capital_initial * ((1 + (taux_rendement / 100)) ** annee) for annee in annees]
    valeurs_capitalisation = [capital_initial * ((1 + (rendement_net / 100)) ** annee) for annee in annees]

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

    # Envoi des données
    envoi_google_sheets(nom, email, capital_initial, taux_rendement, duree)
