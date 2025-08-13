import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
        print(f"[DEBUG] Erreur Google Sheets : {e}")

# ======================
# PAGE D’ACCUEIL
# ======================
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo_tips.png", width=150)
    with col2:
        st.markdown("## Le simulateur qui transforme vos décisions en valeur")
        st.markdown("### *Un outil d’aide à la décision pour optimiser les choix d’investissement*")

    st.markdown("---")

    st.markdown("""
    ### Pourquoi utiliser ce simulateur ?  

    🔹 Comprendre l'impact de la fiscalité sur la performance d'un **Compte Titres** et d'un **Contrat de Capitalisation**, indépendamment de l'allocation choisie  
    🔹 Évaluer vos gains nets, en fonction de vos objectifs  
    🔹 Renforcer votre compréhension de chaque dispositif
    """)

    if st.button("🚀 Démarrer la simulation"):
        st.session_state.started = True
        st.rerun()

else:
    col1, col2 = st.columns([1, 4])
    with col1:
        st.image("logo_tips.png", width=120)
    with col2:
        st.markdown("## Le simulateur qui transforme vos décisions en valeur")
        st.markdown("*Un outil clair et factuel pour comparer vos solutions d’investissement*")

    if st.button("⬅ Retour à l’accueil"):
        st.session_state.started = False
        st.rerun()

    st.markdown("---")
    st.markdown("### 🔹 Étape 1 : Paramètres de simulation")

    prenom_nom = st.text_input("👤 Prénom / Nom")
    societe = st.text_input("🏢 Société")
    email_pro = st.text_input("📧 Email professionnel")
    capital_initial = st.number_input("💰 Capital investi (€)", min_value=1000, step=1000, value=1000000)
    taux_rendement = st.number_input("📈 Rendement brut attendu (%)", min_value=1.0, step=0.1, value=5.0)
    duree = st.slider("⏳ Durée de placement (années)", 1, 30, 10)

    lancer = st.button("🚀 Lancer la simulation")

    if lancer:
        annees = list(range(1, duree + 1))
        taux_fiscal_ct = 0.25
        taux_fiscal_cc = 1.05 * 0.0341 * 0.25

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
            "Plus-value CT (€)": [v - capital_initial for v in valeurs_ct],
            "Plus-value CT (%)": [(v / capital_initial - 1) * 100 for v in valeurs_ct],
            "Contrat Capitalisation": valeurs_cc,
            "Plus-value CC (€)": [v - capital_initial for v in valeurs_cc],
            "Plus-value CC (%)": [(v / capital_initial - 1) * 100 for v in valeurs_cc]
        })

        # Stylisation
        styled_df = df.copy()
        styled_df["Compte Titres"] = styled_df["Compte Titres"].map("{:,.0f} €".format)
        styled_df["Plus-value CT (€)"] = df["Plus-value CT (€)"].map("{:,.0f} €".format)
        styled_df["Plus-value CT (%)"] = df["Plus-value CT (%)"].map("{:,.1f} %".format)
        styled_df["Contrat Capitalisation"] = styled_df["Contrat Capitalisation"].map("{:,.0f} €".format)
        styled_df["Plus-value CC (€)"] = df["Plus-value CC (€)"].map("{:,.0f} €".format)
        styled_df["Plus-value CC (%)"] = df["Plus-value CC (%)"].map("{:,.1f} %".format)

        def color_rows(row_idx):
            return ['background-color: #eef3fb'] * len(df.columns) if row_idx % 2 == 0 else ['background-color: #ffffff'] * len(df.columns)

        st.markdown("### 🔹 Résultats chiffrés")
        st.dataframe(
            styled_df.style
            .set_properties(**{"text-align": "center"})
            .set_table_styles([{
                'selector': 'th',
                'props': [('background-color', '#00274D'), ('color', 'white'), ('font-weight', 'bold')]
            }])
            .apply(lambda _: color_rows(_.name), axis=1)
        )

        # Résumé visuel des plus-values
        st.markdown("### 🔹 Résumé des plus-values")
        st.markdown(
            f"""
            <div style="background-color:#f0f2f6; padding:20px; border-radius:10px; border-left:6px solid #005bbb;">
                <p style="font-size:16px; margin-bottom:10px;"><strong>Compte Titres</strong> : {df['Plus-value CT (€)'].iloc[-1]:,.0f} € soit {df['Plus-value CT (%)'].iloc[-1]:.1f} %</p>
                <p style="font-size:16px; margin-bottom:0;"><strong>Contrat de Capitalisation</strong> : {df['Plus-value CC (€)'].iloc[-1]:,.0f} € soit {df['Plus-value CC (%)'].iloc[-1]:.1f} %</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("### 🔹 Évolution des placements")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=annees, y=valeurs_ct, mode='lines', name="Compte Titres"))
        fig.add_trace(go.Scatter(x=annees, y=valeurs_cc, mode='lines', name="Contrat Capitalisation"))
        fig.update_layout(xaxis_title='Années', yaxis_title='Valeur (€)', height=400)
        st.plotly_chart(fig, use_container_width=True)

        # Explication fiscalité
        with st.container():
            st.markdown("### 📘 Comprendre la fiscalité appliquée dans la simulation")
            st.markdown("""
            #### 🔷 Contrat de Capitalisation  
            Une **avance fiscale annuelle** est appliquée selon la formule suivante :  
            **105 % × TME × Rendement annuel brut**

            > Hypothèse utilisée dans cette simulation :  
            TME (Juillet 2025) = **3,41 %**  
            [Source : Banque de France – TME](https://webstat.banque-france.fr/fr/catalogue/fm/FM.M.FR.EUR.FR2.MM.TME.HSTA)

            Cette avance est ajoutée chaque année au résultat imposable de l’entreprise.

            #### 🔷 Compte Titres  
            La **plus-value annuelle** est directement intégrée au résultat imposable de l’entreprise et **soumise à l’Impôt sur les Sociétés (IS) au taux de 25 %**.

            ---  
            Le traitement fiscal plus avantageux du contrat de capitalisation permet une économie d’impôt annuelle.  
            Cette économie est **réinvestie**, générant des gains supplémentaires grâce à **l’effet des intérêts composés**.
            """)

        if st.button("⬅ Refaire une simulation"):
            st.session_state.started = False
            st.rerun()

        st.markdown("---")
        st.markdown("### 📅 Prochaine étape : réservez directement un rendez-vous")
        st.components.v1.iframe("https://calendly.com/vincent-sanctot-tips-placements", width=700, height=700, scrolling=True)

        envoi_google_sheets(prenom_nom, societe, email_pro, capital_initial, taux_rendement, duree, valeurs_ct[-1], valeurs_cc[-1])
