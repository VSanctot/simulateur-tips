import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ============================
# CONFIGURATION GOOGLE SHEETS
# ============================
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

# ============================
# PAGE D’ACCUEIL
# ============================
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo_tips.png", width=150)
    with col2:
        st.markdown("## le simulateur qui transforme vos décisions en valeur")
        st.markdown("### *Un levier d’aide à la décision pour optimiser les choix d’investissement*")

    st.markdown("---")
    st.markdown("""
        ### Pourquoi utiliser ce simulateur ?  
        🔹 Visualiser l'impact de la fiscalité sur un **Compte Titres** vs un **Contrat de Capitalisation**  
        🔹 Calculer vos **gains nets** en fonction de vos paramètres personnels  
        🔹 Comparaison claire et chiffrée 
    """)

    if st.button("🚀 Démarrer la simulation"):
        st.session_state.started = True
        st.rerun()

else:
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
    st.markdown("### 🔹 Étape 1 : Paramètres de simulation")

    prenom_nom = st.text_input("👤 Prénom / Nom")
    societe = st.text_input("🏢 Société")
    email_pro = st.text_input("📧 Email professionnel")
    capital_initial = st.number_input("💰 Capital investi (€)", min_value=1000, step=1000, value=100000)
    taux_rendement = st.number_input("📈 Rendement brut attendu (%)", min_value=1.0, step=0.1, value=5.0)
    duree = st.slider("⏳ Durée de placement (années)", 1, 30, 10)

    lancer = st.button("🚀 Lancer la simulation")

    if lancer:
        annees = list(range(1, duree + 1))

        # Hypothèses fiscales
        taux_fiscal_ct = 0.25
        taux_fiscal_cc = 1.05 * 0.0341 * 0.25  # ~0.0089

        rendement_ct = taux_rendement * (1 - taux_fiscal_ct)
        rendement_cc = taux_rendement * (1 - taux_fiscal_cc)

        valeurs_ct = [capital_initial * ((1 + (rendement_ct / 100)) ** annee) for annee in annees]
        valeurs_cc = [capital_initial * ((1 + (rendement_cc / 100)) ** annee) for annee in annees]

        valeurs_ct.insert(0, capital_initial)
        valeurs_cc.insert(0, capital_initial)
        annees = [0] + annees

        df = pd.DataFrame({
            "Années": annees,
            "Compte Titres": valeurs_ct,
            "Contrat Capitalisation": valeurs_cc
        })

        # ============================
        # ÉTAPE 2 : RÉSULTATS CHIFFRÉS
        # ============================
        df_affichage = pd.DataFrame({
            "Années": df["Années"],
            "Compte Titres": df["Compte Titres"].apply(lambda x: f"{x:,.0f} €".replace(",", " ")),
            "Contrat Capitalisation": df["Contrat Capitalisation"].apply(lambda x: f"{x:,.0f} €".replace(",", " "))
        })

        st.markdown("""
        <style>
        .styled-table {
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 16px;
            width: 100%;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
        }
        .styled-table thead tr {
            background-color: #002b5c;
            color: #ffffff;
        }
        .styled-table th, .styled-table td {
            padding: 12px 15px;
        }
        .styled-table tbody tr:nth-child(even) {
            background-color: #f3f3f3;
        }
        .styled-table tbody tr:hover {
            background-color: #e0f0ff;
        }
        .styled-table td:nth-child(2) {
            background-color: #e8f0fe;
        }
        .styled-table td:nth-child(3) {
            background-color: #e6f4ea;
        }
        </style>
        """, unsafe_allow_html=True)

        st.markdown("### 🔹 Résultats chiffrés (comparatif amélioré)")
        st.markdown(df_affichage.to_html(classes="styled-table", index=False), unsafe_allow_html=True)

        # ============================
        # COURBE INTERACTIVE
        # ============================
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Années"], y=df["Compte Titres"], mode='lines+markers', name="Compte Titres"))
        fig.add_trace(go.Scatter(x=df["Années"], y=df["Contrat Capitalisation"], mode='lines+markers', name="Contrat Capitalisation"))
        fig.update_layout(title="Évolution comparée des placements", xaxis_title="Années", yaxis_title="Montant (€)", template="plotly_white")
        st.plotly_chart(fig)

        # ============================
        # CONCLUSION VISUELLE
        # ============================
        valeur_finale_ct = valeurs_ct[-1]
        valeur_finale_cc = valeurs_cc[-1]
        gain_absolu = valeur_finale_cc - valeur_finale_ct
        gain_relatif = (valeur_finale_cc / valeur_finale_ct - 1) * 100

        st.markdown("""
        ### 🔹 Conclusion comparative
        <div style="background-color:#e6f4ea; padding:20px; border-radius:10px; border-left:8px solid #34a853;">
            <h4 style="margin-top:0;">📌 Résultat à {duree} ans</h4>
            <p><strong>Compte Titres :</strong> {valeur_finale_ct:,.0f} €</p>
            <p><strong>Contrat de Capitalisation :</strong> {valeur_finale_cc:,.0f} €</p>
            <p>🌟 <strong>Gain généré :</strong> {gain_absolu:,.0f} €<br>📊 <strong>Performance relative :</strong> {gain_relatif:.1f}%</p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⬅ Refaire une simulation"):
            st.session_state.started = False
            st.rerun()

        # ============================
        # RENDEZ-VOUS CALENDLY
        # ============================
        st.markdown("---")
        st.markdown("### 🗓 Prendre rendez-vous avec un conseiller TIPS")
        st.components.v1.iframe("https://calendly.com/vincent-sanctot-tips-placements", width=700, height=700, scrolling=True)

        envoi_google_sheets(prenom_nom, societe, email_pro, capital_initial, taux_rendement, duree, valeur_finale_ct, valeur_finale_cc)
