import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ======================
# CONFIGURATION GOOGLE SHEETS
# ======================
def envoi_google_sheets(prenom_nom, societe, email_pro, capital, rendement, duree, valeur_ct, valeur_cc):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GOOGLE_SHEETS_CREDS"], scope)
        client = gspread.authorize(creds)

        sh = client.open("TIPS_Simulateur")
        sheet = sh.sheet1
        sheet.append_row([prenom_nom, societe, email_pro, capital, rendement, duree, valeur_ct, valeur_cc])
    except Exception as e:
        print(f"[DEBUG] Erreur Google Sheets : {e}")  # Log invisible pour les clients

# ======================
# INTERFACE
# ======================
# Header avec logo + titre
col1, col2 = st.columns([1,4])
with col1:
    st.image("logo_tips.png", width=120)  # Logo TIPS
with col2:
    st.markdown("## Comparateur Patrimonial TIPS")
    st.markdown("*Comparez vos placements en toute transparence*")

st.markdown("---")

# Étape 1 : saisie utilisateur
st.markdown("### 🔹 Étape 1 : Paramètres de simulation")

prenom_nom = st.text_input("👤 Prénom / Nom")
societe = st.text_input("🏢 Société")
email_pro = st.text_input("📧 Email professionnel")
capital_initial = st.number_input("💰 Capital investi (€)", min_value=1000, step=1000, value=10000)
taux_rendement = st.number_input("📈 Rendement brut attendu (%)", min_value=1.0, step=0.1, value=5.0)
duree = st.slider("⏳ Durée de placement (années)", 1, 30, 10)

lancer = st.button("🚀 Lancer la simulation")

if lancer:
    annees = list(range(1, duree + 1))

    # Hypothèses fiscales
    taux_fiscal_ct = 0.25             # 25%
    taux_fiscal_cc = 1.05 * 0.0341    # 105% x 3,41% ≈ 3,5805%

    # Rendements nets
    rendement_ct = taux_rendement * (1 - taux_fiscal_ct)
    rendement_cc = taux_rendement * (1 - taux_fiscal_cc)

    # Évolution des valeurs
    valeurs_ct = [capital_initial * ((1 + (rendement_ct / 100)) ** annee) for annee in annees]
    valeurs_cc = [capital_initial * ((1 + (rendement_cc / 100)) ** annee) for annee in annees]

    # Point de départ identique
    valeurs_ct.insert(0, capital_initial)
    valeurs_cc.insert(0, capital_initial)
    annees = [0] + annees

    # DataFrame résultats
    df = pd.DataFrame({
        "Années": annees,
        "Compte Titres (fiscalité 25%)": valeurs_ct,
        "Contrat Capitalisation (fiscalité 105% x 3,41%)": valeurs_cc
    })

    # Étape 2 : Résultats chiffrés
    st.markdown("### 🔹 Étape 2 : Résultats chiffrés")
    st.dataframe(df)

    # Graphique comparatif
    st.markdown("### 🔹 Évolution des placements")
    fig, ax = plt.subplots()
    ax.plot(df["Années"], df["Compte Titres (fiscalité 25%)"], label="Compte Titres (25%)", linewidth=2)
    ax.plot(df["Années"], df["Contrat Capitalisation (fiscalité 105% x 3,41%)"], label="Contrat Capitalisation", linewidth=2)
    ax.set_xlabel("Années")
    ax.set_ylabel("Valeur (€)")
    ax.legend()
    st.pyplot(fig)

    # Étape 3 : Conclusion factuelle
    valeur_finale_ct = valeurs_ct[-1]
    valeur_finale_cc = valeurs_cc[-1]
    ecart_absolu = valeur_finale_ct - valeur_finale_cc
    ecart_relatif = (valeur_finale_ct / valeur_finale_cc - 1) * 100 if valeur_finale_cc > 0 else float("inf")

    st.markdown("### 🔹 Conclusion")
    st.success(
        f"Après **{duree} ans**, le **Compte Titres** atteint **{valeur_finale_ct:,.0f} €**, "
        f"contre **{valeur_finale_cc:,.0f} €** pour le **Contrat de Capitalisation**.  \n\n"
        f"➡️ L’écart est de **{ecart_absolu:,.0f} €**, soit **{ecart_relatif:.0f}%** en faveur du Compte Titres."
    )

    # Enregistrement invisible (Google Sheets)
    envoi_google_sheets(prenom_nom, societe, email_pro, capital_initial, taux_rendement, duree, valeur_finale_ct, valeur_finale_cc)
