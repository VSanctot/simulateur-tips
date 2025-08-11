import streamlit as st

# Vérification et import sécurisé de Plotly
try:
    import plotly.graph_objects as go
except ModuleNotFoundError:
    st.error(
        "❌ Plotly n'est pas installé.\n"
        "➡️ Ajoute `plotly` dans `requirements.txt` (ex. `plotly>=5.20`) puis redéploie l'application."
    )
    st.stop()

import pandas as pd
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
        st.markdown("### *Un outil d’aide à la décision pour optimiser vos choix d’investissement*")

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
    capital_initial = st.number_input("💰 Capital investi (€)", min_value=1000, step=1000, value=100000)
    taux_rendement = st.number_input("📈 Rendement brut attendu (%)", min_value=1.0, step=0.1, value=5.0)
    duree = st.slider("⏳ Durée de placement (années)", 1, 30, 10)

    with st.expander("ℹ️ Détail de la fiscalité du Contrat de Capitalisation"):
        st.markdown("""
        - Une **avance fiscale** (montant égal à **105% × 3,41%** du rendement annuel) est **ajoutée au résultat imposable** chaque année. Ici, **3,41%** correspond au *Taux Moyen d’Emprunt d’État* (TME) pour le mois de **juillet 2025**, publié par la Banque de France. 
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

        df = pd.DataFrame({
            "Années": annees,
            "Compte Titres": valeurs_ct,
            "Contrat Capitalisation": valeurs_cc
        })

        # ---- Calcul de l'écart ----
        df["Écart (€)"] = df["Contrat Capitalisation"] - df["Compte Titres"]
        df["Écart (%)"] = (df["Écart (€)"] / df["Compte Titres"]) * 100

        # ---- Formatage ----
        def fmt_eur(x): return f"{x:,.0f} €".replace(",", " ")
        def fmt_pct(x): return f"{x:.2f} %".replace(".", ",")

        col_annee = df["Années"].tolist()
        col_ct    = df["Compte Titres"].map(fmt_eur).tolist()
        col_cc    = df["Contrat Capitalisation"].map(fmt_eur).tolist()
        col_ecart = df["Écart (€)"].map(fmt_eur).tolist()
        col_ecartp= df["Écart (%)"].map(fmt_pct).tolist()

        # ---- Styles par ligne ----
        n = len(col_annee)
        fill_even = "#f8fbff"
        fill_odd  = "#ffffff"
        row_colors = [fill_even if i % 2 == 0 else fill_odd for i in range(n)]
        row_colors[-1] = "#e8f1ff"  # dernière ligne

        # ---- Affichage tableau Plotly ----
        st.markdown("### 🔹 Résultats chiffrés (comparatif amélioré)")
        fig_table = go.Figure(data=[
            go.Table(
                columnwidth=[60, 140, 200, 110, 100],
                header=dict(
                    values=["Années", "Compte Titres", "Contrat Capitalisation", "Écart (€)", "Écart (%)"],
                    fill_color="#1a73e8",
                    font=dict(color="white", size=12),
                    align="center",
                    height=34
                ),
                cells=dict(
                    values=[col_annee, col_ct, col_cc, col_ecart, col_ecartp],
                    align="center",
                    fill_color=[row_colors],
                    height=30
                )
            )
        ])
        fig_table.update_layout(margin=dict(l=0, r=0, t=6, b=0))
        st.plotly_chart(fig_table, use_container_width=True)

        # ---- Graphique évolution ----
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

        # ---- Conclusion ----
        st.markdown("### 🔹 Conclusion comparative")
        st.info("💡 Un levier fiscal qui se transforme en moteur de croissance : chaque euro économisé est réinvesti, et chaque réinvestissement démultiplie la puissance des intérêts composés.")

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
