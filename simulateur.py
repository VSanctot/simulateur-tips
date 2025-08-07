import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Configuration Google Sheets (utilisé en arrière-plan)
def envoi_google_sheets(prenom_nom, societe, email_pro, capital, rendement, duree, valeur_ct, valeur_cc):
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(st.secrets["GOOGLE_SHEETS_CREDS"], scope)
        client = gspread.authorize(creds)
        sh = client.open("TIPS_Simulateur")
        sheet = sh.sheet1
        sheet.append_row([prenom_nom, societe, email_pro, capital, rendement, duree, valeur_ct, valeur_cc])
    except Exception as e:
        print(f"[DEBUG] Erreur Google Sheets : {e}")

# Page d’accueil
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo_tips.png", width=150)
    with col2:
        st.markdown("## Le simulateur qui transforme vos décisions en valeur")
        st.markdown("### *Un levier d’aide à la décision pour optimiser les choix d’investissement*")

    st.markdown("---")

    st.markdown("""
    ### Pourquoi utiliser ce simulateur ?
    🔹 Comparer la fiscalité entre un **Compte Titres** et un **Contrat de Capitalisation**  
    🔹 Évaluer les gains nets après fiscalité  
    🔹 Décider avec des **données claires et factuelles**
    """)

    if st.button("🚀 Démarrer la simulation"):
        st.session_state.started = True
        st.rerun()

else:
    # Interface simulateur
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo_tips.png", width=120)
    with col2:
        st.markdown("## TIPS : le simulateur qui valorise votre patrimoine")
        st.markdown("*Un outil clair et factuel pour comparer vos solutions d’investissement*")

    if st.button("⬅ Retour à l’accueil"):
        st.session_state.started = False
        st.rerun()

    st.markdown("---")

    # Étape 1
    st.markdown("### 🔹 Étape 1 : Paramètres de simulation")

    prenom_nom = st.text_input("👤 Prénom / Nom")
    societe = st.text_input("🏢 Société")
    email_pro = st.text_input("📧 Email professionnel")
    capital_initial = st.number_input("💰 Capital investi (€)", min_value=1000, step=1000, value=100000)
    taux_rendement = st.number_input("📈 Rendement brut attendu (%)", min_value=1.0, step=0.1, value=5.0)
    duree = st.slider("⏳ Durée de placement (années)", 1, 30, 10)

    if st.button("🚀 Lancer la simulation"):

        annees = list(range(0, duree + 1))

        # Hypothèses fiscales
        taux_fiscal_ct = 0.25
        taux_fiscal_cc = 1.05 * 0.0341 * 0.25  # ≈ 0.00896 (0.896%)

        # Rendements nets
        rendement_ct = taux_rendement * (1 - taux_fiscal_ct)
        rendement_cc = taux_rendement * (1 - taux_fiscal_cc)

        # Évolution des placements
        valeurs_ct = [capital_initial * ((1 + (rendement_ct / 100)) ** annee) for annee in annees]
        valeurs_cc = [capital_initial * ((1 + (rendement_cc / 100)) ** annee) for annee in annees]

        df = pd.DataFrame({
            "Années": annees,
            "Compte Titres": valeurs_ct,
            "Contrat Capitalisation": valeurs_cc
        })

        # Résultats chiffrés
        st.markdown("### 📊 Résultats chiffrés (comparatif amélioré)")
        styled_df = df.style\
            .format({"Compte Titres": "€ {:,.0f}", "Contrat Capitalisation": "€ {:,.0f}"})\
            .apply(lambda x: ['background-color: #f0f4ff' if x.name % 2 == 0 else '' for _ in x], axis=1)\
            .apply(lambda x: ['background-color: #e6f9ec' if x.name % 2 == 0 else '' for _ in x], axis=1, subset=["Contrat Capitalisation"])

        st.dataframe(styled_df, use_container_width=True)

        # Résumé année par année
        st.markdown("### 📅 Détail par année")
        for i in range(1, len(df)):
            with st.expander(f"Année {df.iloc[i]['Années']}"):
                st.markdown(
                    f"""
                    - **Compte Titres** : {df.iloc[i]['Compte Titres']:,.0f} €
                    - **Contrat Capitalisation** : {df.iloc[i]['Contrat Capitalisation']:,.0f} €
                    """
                )

        # Graphique interactif Plotly
        st.markdown("### 📈 Évolution des placements")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Années"], y=df["Compte Titres"], mode='lines', name='Compte Titres'))
        fig.add_trace(go.Scatter(x=df["Années"], y=df["Contrat Capitalisation"], mode='lines', name='Contrat Capitalisation'))
        fig.update_layout(xaxis_title="Années", yaxis_title="Valeur (€)", height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Résumé en fin de simulation
        valeur_finale_ct = valeurs_ct[-1]
        valeur_finale_cc = valeurs_cc[-1]
        gain_absolu = valeur_finale_cc - valeur_finale_ct
        gain_relatif = (valeur_finale_cc / valeur_finale_ct - 1) * 100

        st.markdown("### 🔍 Conclusion comparative")
        st.markdown(
            f"""
            <div style="background-color:#f0f9ff; padding:20px; border-radius:10px; border-left:8px solid #1f77b4;">
                <h4 style="margin-top:0;">✅ Synthèse</h4>
                <p>Après <strong>{duree} ans</strong>, vous obtenez :</p>
                <ul>
                    <li><strong>{valeur_finale_cc:,.0f} €</strong> avec le Contrat de Capitalisation</li>
                    <li><strong>{valeur_finale_ct:,.0f} €</strong> avec le Compte Titres</li>
                </ul>
                <p><strong>Différentiel constaté :</strong> {gain_absolu:,.0f} € soit +{gain_relatif:.1f}%</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("---")
        st.markdown("### 📅 Réservez un échange avec un conseiller TIPS")
        st.components.v1.iframe("https://calendly.com/vincent-sanctot-tips-placements", width=700, height=700)

        # Enregistrement Google Sheets en arrière-plan
        envoi_google_sheets(prenom_nom, societe, email_pro, capital_initial, taux_rendement, duree, valeur_finale_ct, valeur_finale_cc)
