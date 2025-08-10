import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import gspread
from oauth2client.service_account import ServiceAccountCredentials

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
<style>
.features {
  list-style: none;
  padding: 0;
  margin: 6px 0 0 0;
  max-width: 900px;
}
.features li {
  position: relative;
  margin: 10px 0;
  padding-left: 28px;
  line-height: 1.45;
  font-size: 17px;
}
.features li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 7px;
  width: 12px;
  height: 12px;
  background: #1a73e8;
  transform: rotate(45deg);
  border-radius: 2px;
  box-shadow: 0 0 0 2px rgba(26,115,232,.12);
}
@media (min-width: 900px) {
  .features { column-count: 2; column-gap: 48px; }
}
</style>

### Pourquoi utiliser ce simulateur ?
<ul class="features">
  <li>Visualiser l’impact de la fiscalité sur un <strong>Compte Titres</strong> vs un <strong>Contrat de Capitalisation</strong></li>
  <li>Calculer vos <strong>gains</strong> en fonction de vos objectifs à court, moyen et long terme</li>
  <li>Renforcer votre connaissance sur le fonctionnement de chaque dispositif</li>
</ul>
""", unsafe_allow_html=True)

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

    with st.expander("ℹ️ Détail de la fiscalité du Contrat de Capitalisation"):
        st.markdown("""
        Le contrat de capitalisation bénéficie d’une fiscalité avantageuse en cours de vie :

        - Une avance fiscale est prélevée chaque année à hauteur de **105% × 3,41% × 25%** appliquée au rendement.
        - Pour un **Compte Titres** détenu en société, les plus-values et revenus financiers entrent dans le résultat imposable à l’**Impôt sur les Sociétés (IS)** au taux de **25%** en France.
        - Cette différence permet un **gain fiscal réinvesti** chaque année, qui agit comme un **levier de performance à effet composé**.
        """)

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

        df = pd.DataFrame({"Années": annees, "Compte Titres": valeurs_ct, "Contrat Capitalisation": valeurs_cc})
        df_affichage = pd.DataFrame({
            "Années": df["Années"],
            "Compte Titres": df["Compte Titres"].apply(lambda x: f"{x:,.0f} €".replace(",", " ")),
            "Contrat Capitalisation": df["Contrat Capitalisation"].apply(lambda x: f"{x:,.0f} €".replace(",", " "))
        })

        st.markdown("### 🔹 Résultats chiffrés (comparatif amélioré)")
        st.markdown(df_affichage.to_html(index=False), unsafe_allow_html=True)

        st.markdown("### 🔹 Évolution des placements")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["Années"], y=df["Compte Titres"], mode='lines+markers', name="Compte Titres"))
        fig.add_trace(go.Scatter(x=df["Années"], y=df["Contrat Capitalisation"], mode='lines+markers', name="Contrat Capitalisation"))
        fig.update_layout(title="Évolution comparée des placements", xaxis_title="Années", yaxis_title="Montant (€)", template="plotly_white")
        st.plotly_chart(fig)

        valeur_finale_ct = valeurs_ct[-1]
        valeur_finale_cc = valeurs_cc[-1]
        gain_absolu = valeur_finale_cc - valeur_finale_ct
        gain_relatif = (valeur_finale_cc / valeur_finale_ct - 1) * 100

        st.markdown("### 🔹 Conclusion comparative")
        st.info("💡 Grâce à une fiscalité annuelle bien plus faible, le contrat de capitalisation génère une économie d'impôt réinvestie chaque année.")

        st.markdown(f"""
        Après **{duree} ans**, le Contrat de Capitalisation atteint **{valeur_finale_cc:,.0f} €**, contre **{valeur_finale_ct:,.0f} €** pour le Compte Titres.
        ✅ Gain net : {gain_absolu:,.0f} €  
        📈 Écart de performance : {gain_relatif:.1f}%
        """)

        if st.button("⬅ Refaire une simulation"):
            st.session_state.started = False
            st.rerun()

        st.markdown("---")
        st.markdown("### 📅 Prochaine étape : réservez directement un rendez-vous")
        st.components.v1.iframe("https://calendly.com/vincent-sanctot-tips-placements", width=700, height=700, scrolling=True)

        envoi_google_sheets(prenom_nom, societe, email_pro, capital_initial, taux_rendement, duree, valeur_finale_ct, valeur_finale_cc)
