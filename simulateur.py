import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials

# 🎨 Configuration page
st.set_page_config(
    page_title="Comparateur Compte-titres vs Contrat de Capitalisation",
    page_icon="💼",
    layout="centered"
)

# ===============================
# 🔹 Fonction Google Sheets via Secrets
# ===============================
def sauvegarder_donnees(prenom_nom, societe, email, montant, performance, horizon, resultat_cto, resultat_cap):
    try:
        # Autorisations pour Google Sheets
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

        # 🔹 Charger les credentials depuis les Secrets Streamlit
        creds_json = json.loads(st.secrets["GOOGLE_SHEETS_CREDS"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
        client = gspread.authorize(creds)

        # ⚠️ Remplace "Simulations TIPS" par le nom exact de ton Google Sheet
        sheet = client.open("Simulations TIPS").sheet1

        # Ajout d'une ligne
        sheet.append_row([prenom_nom, societe, email, montant, performance, horizon, resultat_cto, resultat_cap])

    except Exception as e:
        raise Exception(f"Erreur Google Sheets : {e}")

# ===============================
# 🔹 Interface utilisateur
# ===============================
st.title("💼 Comparateur Compte-titres vs Contrat de Capitalisation")
st.markdown("### Un outil développé par **TIPS** pour optimiser vos décisions d’investissement")

# Formulaire utilisateur
prenom_nom = st.text_input("Prénom / Nom")
societe = st.text_input("Société")
email = st.text_input("Email professionnel")

montant = st.number_input("💶 Montant d'investissement (€)", min_value=100000.0, max_value=100000000.0, step=1000.0, value=100000.0)
performance = st.number_input("📈 Objectif de performance (%)", min_value=3.0, max_value=15.0, step=0.5, value=5.0)
horizon = st.number_input("⏳ Horizon d'investissement (années)", min_value=3, max_value=40, step=1, value=10)

# ===============================
# 🔹 Calcul et affichage résultats
# ===============================
if st.button("🚀 Lancer la simulation"):
    perf = performance / 100
    annees = list(range(1, horizon + 1))
    valeurs_ct = [montant]
    valeurs_cap = [montant]

    # Taux fiscaux
    fiscalite_ct = 0.30      # CTO = 30% sur les gains
    fiscalite_cap = 1.05 * 0.0341  # Contrat = 105% × 3,41% = 3,5805%

    for an in annees:
        # CTO : impôt chaque année sur les gains
        gain_ct = valeurs_ct[-1] * perf
        net_gain_ct = gain_ct * (1 - fiscalite_ct)
        valeurs_ct.append(valeurs_ct[-1] + net_gain_ct)

        # Contrat : impôt réduit chaque année sur les gains
        gain_cap = valeurs_cap[-1] * perf
        net_gain_cap = gain_cap * (1 - fiscalite_cap)
        valeurs_cap.append(valeurs_cap[-1] + net_gain_cap)

    # Résultats finaux
    gain = valeurs_cap[-1] - valeurs_ct[-1]

    st.subheader("📊 Résultats finaux")
    st.write(f"Montant investi : **{montant:,.0f} €**")
    st.write(f"Horizon : **{horizon} ans**")
    st.write(f"Performance annuelle : **{performance}%**")

    st.success(f"💼 Compte-titres (après fiscalité annuelle) : {valeurs_ct[-1]:,.0f} €")
    st.success(f"📑 Contrat de capitalisation (après fiscalité annuelle) : {valeurs_cap[-1]:,.0f} €")

    if gain > 0:
        st.info(f"✅ Avantage du contrat de capitalisation : **{gain:,.0f} €**")
    else:
        st.warning(f"⚠️ Pas d’avantage (écart : {gain:,.0f} €**)")

    # 🔹 Tableau comparatif
    df = pd.DataFrame({
        "Année": [0] + annees,
        "Compte-titres": valeurs_ct,
        "Contrat de capitalisation": valeurs_cap
    })
    st.subheader("📑 Comparatif année par année")
    st.dataframe(df)

    # 🔹 Graphique comparatif
    fig, ax = plt.subplots()
    ax.plot(df["Année"], df["Compte-titres"], label="Compte-titres (30%)", linewidth=2, color="#003366")
    ax.plot(df["Année"], df["Contrat de capitalisation"], label="Contrat de capitalisation (3,58%)", linewidth=2, color="#009966")
    ax.set_xlabel("Année")
    ax.set_ylabel("Valeur après fiscalité (€)")
    ax.set_title("Évolution comparée - TIPS")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.6)
    st.pyplot(fig)

    # 🔹 Sauvegarde des données avec debug
    try:
        sauvegarder_donnees(
            prenom_nom, 
            societe, 
            email, 
            montant, 
            performance, 
            horizon, 
            valeurs_ct[-1], 
            valeurs_cap[-1]
        )
        st.success("✅ Données envoyées dans Google Sheets")
    except Exception as e:
        st.error(f"⚠️ Erreur lors de l'envoi vers Google Sheets : {e}")
