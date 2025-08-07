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
        print(f"[DEBUG] Erreur Google Sheets : {e}")  # log invisible côté client

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
        st.markdown("### *Un levier d’aide à la décision pour optimiser les choix d’investissement*")

    st.markdown("---")
    st.markdown("""
        ### Pourquoi utiliser ce simulateur ?  
        🔹 Comprendre l’impact de la fiscalité sur la performance d’un **Compte Titres** et d’un **Contrat de Capitalisation**  
        🔹 Visualiser vos gains nets en fonction de votre **capital, rendement et durée**  
        🔹 Obtenir un **résumé clair** des résultats  
    """)

    if st.button("🚀 Démarrer la simulation"):
        st.session_state.started = True
        st.rerun()

else:
    # ======================
    # INTERFACE SIMULATEUR
    # ======================
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
    capital_initial = st.number_input("💰 Capital investi (€)", min_value=100000, step=100000, value=10000000)
    taux_rendement = st.number_input("📈 Rendement brut attendu (%)", min_value=1.0, step=0.1, value=5.0)
    duree = st.slider("⏳ Durée de placement (années)", 1, 30, 10)

    lancer = st.button("🚀 Lancer la simulation")

    if lancer:
        annees = list(range(1, duree + 1))

        # Hypothèses fiscales
        taux_fiscal_ct = 0.25
        taux_fiscal_cc = 1.05 * 0.0341 * 0.25  # 105% x 3.41% x 25%

        rendement_ct = taux_rendement * (1 - taux_fiscal_ct)
        rendement_cc = taux_rendement * (1 - taux_fiscal_cc)

        valeurs_ct = [capital_initial * ((1 + rendement_ct / 100) ** annee) for annee in annees]
        valeurs_cc = [capital_initial * ((1 + rendement_cc / 100) ** annee) for annee in annees]

        valeurs_ct.insert(0, capital_initial)
        valeurs_cc.insert(0, capital_initial)
        annees = [0] + annees

        df = pd.DataFrame({
            "Années": annees,
            "Compte Titres": valeurs_ct,
            "Contrat Capitalisation": valeurs_cc
        })

        # Étape 2 : Résultats
        st.markdown("### 🔹 Résultats chiffrés (comparatif amélioré)")
        styled_df = df.copy()
        styled_df["Compte Titres"] = styled_df["Compte Titres"].map("{:,.0f} €".format)
        styled_df["Contrat Capitalisation"] = styled_df["Contrat Capitalisation"].map("{:,.0f} €".format)
        st.dataframe(styled_df.style
                     .set_properties(**{"text-align": "center"})
                     .set_table_styles([{
                         'selector': 'th',
                         'props': [('background-color', '#00274D'), ('color', 'white'), ('font-weight', 'bold')]
                     }])
                     .apply(lambda _: ['background-color: #eef3fb']*len(df) if _ % 2 == 0 else ['background-color: #ffffff']*len(df), axis=1)
                     )

        # Graphique interactif
        st.markdown("### 🔹 Évolution des placements")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Années"], y=df["Compte Titres"],
                                 mode="lines", name="Compte Titres", line=dict(width=3)))
        fig.add_trace(go.Scatter(x=df["Années"], y=df["Contrat Capitalisation"],
                                 mode="lines", name="Contrat Capitalisation", line=dict(width=3)))
        fig.update_layout(xaxis_title="Années", yaxis_title="Valeur (€)")
        st.plotly_chart(fig, use_container_width=True)

        # Résumé stylisé
        st.markdown("### 🔹 Conclusion comparative")
        valeur_finale_ct = valeurs_ct[-1]
        valeur_finale_cc = valeurs_cc[-1]
        gain_absolu = valeur_finale_cc - valeur_finale_ct
        gain_relatif = (valeur_finale_cc / valeur_finale_ct - 1) * 100

        st.markdown(f"""
            <div style="background-color:#e6f4ea; padding:20px; border-radius:10px; border-left:8px solid #34a853;">
                <h4 style="margin-top:0;">📌 Résumé de la simulation</h4>
                <p style="font-size:16px;">
                    Après <strong>{duree} ans</strong>, le <strong>Contrat de Capitalisation</strong> atteint 
                    <strong>{valeur_finale_cc:,.0f} €</strong>, contre <strong>{valeur_finale_ct:,.0f} €</strong> pour le 
                    <strong>Compte Titres</strong>.
                </p>
                <p style="font-size:16px;">
                    ✅ <strong>Gain net constaté :</strong> {gain_absolu:,.0f} €  
                    <br>📈 <strong>Écart de performance :</strong> {gain_relatif:.1f}% en faveur du Contrat de Capitalisation.
                </p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("⬅ Refaire une simulation"):
            st.session_state.started = False
            st.rerun()

        # Calendly
        st.markdown("---")
        st.markdown("### 📅 Prochaine étape : réservez directement un rendez-vous")
        st.components.v1.iframe("https://calendly.com/vincent-sanctot-tips-placements", width=700, height=700)

        # Enregistrement
        envoi_google_sheets(prenom_nom, societe, email_pro, capital_initial, taux_rendement, duree, valeur_finale_ct, valeur_finale_cc)
