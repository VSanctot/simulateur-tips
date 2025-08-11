import streamlit as st

# ---------- Config page ----------
st.set_page_config(page_title="Simulateur TIPS", layout="wide")

# ---------- Import Plotly (sécurisé) ----------
try:
    import plotly.graph_objects as go
except ModuleNotFoundError as e:
    st.error(
        "❌ Plotly n'est pas installé.\n"
        "➡️ Ajoute `plotly` dans `requirements.txt` (ex. `plotly==5.22.0`) puis redéploie."
    )
    st.stop()

import pandas as pd

# ---------- Utilitaires UI ----------
def safe_image(path: str, **kwargs):
    try:
        st.image(path, **kwargs)
    except Exception as e:
        st.warning(f"⚠️ Image introuvable : `{path}`. (Détail : {e})")

def fmt_eur(x): return f"{x:,.0f} €".replace(",", " ")
def fmt_pct(x): return f"{x:.2f} %".replace(".", ",")

# ---------- Google Sheets (imports paresseux + gestion erreurs) ----------
def envoi_google_sheets(prenom_nom, societe, email_pro, capital, rendement, duree, valeur_ct, valeur_cc):
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        # Secrets
        creds_dict = st.secrets["GOOGLE_SHEETS_CREDS"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sh = client.open("TIPS_Simulateur")
        sheet = sh.sheet1
        sheet.append_row([prenom_nom, societe, email_pro, capital, rendement, duree, valeur_ct, valeur_cc])
    except KeyError:
        st.warning("⚠️ Secret manquant : `GOOGLE_SHEETS_CREDS`. Configure-le dans **Settings → Secrets**.")
    except ModuleNotFoundError:
        st.warning("⚠️ Dépendances Google Sheets absentes. Ajoute `gspread` et `oauth2client` dans `requirements.txt`.")
    except Exception as e:
        st.warning(f"⚠️ Échec d’envoi vers Google Sheets : {e}")

# ---------- State ----------
if "started" not in st.session_state:
    st.session_state.started = False

try:
    # ================= Accueil =================
    if not st.session_state.started:
        col1, col2 = st.columns([1, 4])
        with col1:
            safe_image("logo_tips.png", width=150)
        with col2:
            st.markdown("## Le simulateur qui transforme vos décisions en valeur")
            st.markdown("### *Un outil d’aide à la décision pour optimiser vos choix d’investissement*")

        st.markdown("---")
        st.markdown("""
<style>
.features{list-style:none;padding:0;margin:6px 0 0 0;max-width:900px;}
.features li{position:relative;margin:10px 0;padding-left:28px;line-height:1.45;font-size:17px;}
.features li::before{content:"";position:absolute;left:0;top:7px;width:12px;height:12px;background:#1a73e8;transform:rotate(45deg);border-radius:2px;box-shadow:0 0 0 2px rgba(26,115,232,.12);}
@media (min-width:900px){.features{column-count:2;column-gap:48px;}}
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

    # ================= Simulateur =================
    else:
        col1, col2 = st.columns([1, 4])
        with col1:
            safe_image("logo_tips.png", width=120)
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
            - Une **avance fiscale** (montant égal à **105% × 3,41%** du rendement annuel) est **ajoutée au résultat imposable** chaque année.
            - Pour un **Compte Titres** détenu en société, les revenus entrent au **taux d’IS 25%**.
            - L’écart de taxation est **réinvesti** chaque année (effet composé).
            """)

        if st.button("🚀 Lancer la simulation"):
            annees = list(range(1, duree + 1))
            taux_fiscal_ct = 0.25
            taux_fiscal_cc = 1.05 * 0.0341 * 0.25

            rendement_ct = taux_rendement * (1 - taux_fiscal_ct)
            rendement_cc = taux_rendement * (1 - taux_fiscal_cc)

            valeurs_ct = [capital_initial * ((1 + (rendement_ct / 100)) ** a) for a in annees]
            valeurs_cc = [capital_initial * ((1 + (rendement_cc / 100)) ** a) for a in annees]

            valeurs_ct.insert(0, capital_initial)
            valeurs_cc.insert(0, capital_initial)
            annees = [0] + annees

            df = pd.DataFrame({
                "Années": annees,
                "Compte Titres": valeurs_ct,
                "Contrat Capitalisation": valeurs_cc
            })
            df["Écart (€)"] = df["Contrat Capitalisation"] - df["Compte Titres"]
            df["Écart (%)"] = (df["Écart (€)"] / df["Compte Titres"]) * 100

            # ----- Tableau -----
            col_annee = df["Années"].tolist()
            col_ct = df["Compte Titres"].map(fmt_eur).tolist()
            col_cc = df["Contrat Capitalisation"].map(fmt_eur).tolist()
            col_ecart = df["Écart (€)"].map(fmt_eur).tolist()
            col_ecartp = df["Écart (%)"].map(fmt_pct).tolist()

            n = len(col_annee)
            row_colors = [("#f8fbff" if i % 2 == 0 else "#ffffff") for i in range(n)]
            row_colors[-1] = "#e8f1ff"

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

