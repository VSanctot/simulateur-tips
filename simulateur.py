import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from fpdf import FPDF
import io

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
# GENERATION PDF
# ======================
def generer_pdf(prenom_nom, societe, capital, rendement, duree, df, valeur_ct, valeur_cc, gain_absolu, gain_relatif, fig):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    # Logo
    try:
        pdf.image("logo_tips.png", 10, 8, 33)
    except:
        pass

    # Titre
    pdf.cell(200, 10, "TIPS : le simulateur qui valorise votre patrimoine", ln=True, align="C")
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)

    # Paramètres
    pdf.cell(200, 10, f"Simulation pour {prenom_nom} - {societe}", ln=True)
    pdf.cell(200, 10, f"Capital investi : {capital:,.0f} €", ln=True)
    pdf.cell(200, 10, f"Rendement brut attendu : {rendement:.2f} %", ln=True)
    pdf.cell(200, 10, f"Durée : {duree} ans", ln=True)
    pdf.ln(5)

    # Conclusion
    pdf.multi_cell(0, 10, 
        f"Après {duree} ans, le Contrat de Capitalisation atteint {valeur_cc:,.0f} €, "
        f"contre {valeur_ct:,.0f} € pour le Compte Titres.\n\n"
        f"➡ Gain net constaté : {gain_absolu:,.0f} € "
        f"({gain_relatif:.0f}% en faveur du Contrat de Capitalisation)."
    )
    pdf.ln(5)

    # Tableau simplifié
    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Année", 1)
    pdf.cell(70, 10, "Compte Titres", 1)
    pdf.cell(70, 10, "Contrat Capitalisation", 1)
    pdf.ln()
    pdf.set_font("Arial", "", 10)
    for i in range(len(df)):
        pdf.cell(40, 10, str(df['Années'][i]), 1)
        pdf.cell(70, 10, f"{df['Compte Titres (fiscalité 25%)'][i]:,.0f}", 1)
        pdf.cell(70, 10, f"{df['Contrat Capitalisation (fiscalité 105% x 3,41%)'][i]:,.0f}", 1)
        pdf.ln()

    # Graphique
    pdf.ln(10)
    img_bytes = io.BytesIO()
    fig.savefig(img_bytes, format="png")
    img_bytes.seek(0)
    pdf.image(img_bytes, x=10, w=180)

    # Retourne le PDF en mémoire
    return pdf.output(dest="S").encode("latin1")


# ======================
# PAGE D’ACCUEIL
# ======================
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    # Header accueil
    col1, col2 = st.columns([1,4])
    with col1:
        st.image("logo_tips.png", width=150)
    with col2:
        st.markdown("## TIPS : le simulateur qui valorise votre patrimoine")
        st.markdown("### *Un outil clair et factuel pour comparer vos solutions d’investissement*")

    st.markdown("---")

    st.markdown(
        """
        ### Pourquoi utiliser ce simulateur ?  
        🔹 Comparez de façon claire et factuelle un **Compte Titres** et un **Contrat de Capitalisation**  
        🔹 Évaluez vos gains nets après fiscalité, en fonction de votre **capital, rendement et durée**  
        🔹 Obtenez un **résumé clair et professionnel** de vos résultats  
        """
    )

    if st.button("🚀 Démarrer la simulation"):
        st.session_state.started = True
        st.rerun()

else:
    # ======================
    # INTERFACE SIMULATEUR
    # ======================
    col1, col2 = st.columns([1,4])
    with col1:
        st.image("logo_tips.png", width=120)
    with col2:
        st.markdown("## TIPS : le simulateur qui valorise votre patrimoine")
        st.markdown("*Un outil clair et factuel pour comparer vos solutions d’investissement*")

    # ✅ Bouton retour en haut
    if st.button("⬅ Retour à l’accueil"):
        st.session_state.started = False
        st.rerun()

    st.markdown("---")

    # Étape 1 : saisie utilisateur
    st.markdown("### 🔹 Étape 1 : Paramètres de simulation")

    prenom_nom = st.text_input("👤 Prénom / Nom")
    societe = st.text_input("🏢 Société")
    email_pro = st.text_input("📧 Email professionnel")
    capital_initial = st.number_input("💰 Capital investi (€)", min_value=1000, step=1000, value=100000)  # base 100 000 €
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

        # Étape 3 : Conclusion premium
        valeur_finale_ct = valeurs_ct[-1]
        valeur_finale_cc = valeurs_cc[-1]

        gain_absolu = valeur_finale_cc - valeur_finale_ct
        gain_relatif = (valeur_finale_cc / valeur_finale_ct - 1) * 100 if valeur_finale_ct > 0 else float("inf")

        st.markdown("### 🔹 Conclusion comparative")

        with st.container():
            st.markdown(
                f"""
                <div style="background-color:#e6f4ea; padding:20px; border-radius:10px; border-left:8px solid #34a853;">
                    <h4 style="margin-top:0;">📌 Résumé de la simulation</h4>
                    <p style="font-size:16px;">
                        Après <strong>{duree} ans</strong>, le <strong>Contrat de Capitalisation</strong> atteint 
                        <strong>{valeur_finale_cc:,.0f} €</strong>, contre <strong>{valeur_finale_ct:,.0f} €</strong> pour le 
                        <strong>Compte Titres</strong>.
                    </p>
                    <p style="font-size:16px;">
                        ✅ <strong>Gain net constaté :</strong> {gain_absolu:,.0f} €  
                        <br>📈 <strong>Écart de performance :</strong> {gain_relatif:.0f}% en faveur du Contrat de Capitalisation.
                    </p>
                </div>
                """,
                unsafe_allow_html=True
            )

        # ✅ Bouton retour sous la conclusion
        if st.button("⬅ Refaire une simulation"):
            st.session_state.started = False
            st.rerun()

        # ✅ Bouton export PDF
        pdf_bytes = generer_pdf(prenom_nom, societe, capital_initial, taux_rendement, duree,
                                df, valeur_finale_ct, valeur_finale_cc, gain_absolu, gain_relatif, fig)

        st.download_button(
            label="📄 Télécharger le rapport PDF",
            data=pdf_bytes,
            file_name="simulation_TIPS.pdf",
            mime="application/pdf"
        )

        # Enregistrement invisible (Google Sheets)
        envoi_google_sheets(prenom_nom, societe, email_pro, capital_initial, taux_rendement, duree, valeur_finale_ct, valeur_finale_cc)
