import streamlit as st

# ================== CONFIG ==================
st.set_page_config(page_title="Simulateur TIPS", layout="wide")

# ------ Palette & thème ------
BRAND = {
    "primary": "#1a73e8",   # bleu TIPS
    "primary_soft": "#e8f1ff",
    "text_dark": "#0f172a",
    "neutral": "#64748b",   # pour série comparative
}
try:
    THEME_BASE = st.get_option("theme.base")  # "light" | "dark"
except Exception:
    THEME_BASE = "light"
PLOTLY_TEMPLATE = "plotly_dark" if THEME_BASE == "dark" else "plotly_white"
TABLE_HEADER = BRAND["primary"]

# ================== CSS (mobile-first) ==================
st.markdown(f"""
<style>
/* Layout & typographie mobile */
@media (max-width: 640px){{
  .block-container{{padding:0.6rem 0.8rem 2rem;}}
  h1{{font-size:1.6rem;}} h2{{font-size:1.3rem;}} h3{{font-size:1.05rem;}}
  .stTextInput input, .stNumberInput input{{font-size:0.95rem;}}
}}
/* Boutons confortables */
.stButton>button{{border-radius:12px; box-shadow:0 2px 6px rgba(0,0,0,.06);}}
@media (max-width: 640px){{ .stButton>button{{width:100%; padding:0.9rem 1rem; font-size:1rem;}} }}
/* Conteneur Plotly centré */
div[data-testid="stPlotlyChart"]{{overflow-x:auto; margin-left:auto; margin-right:auto;}}
/* Liste features */
.features{{list-style:none;padding:0;margin:6px 0 0 0;max-width:900px;}}
.features li{{position:relative;margin:10px 0;padding-left:28px;line-height:1.45;font-size:17px;}}
.features li::before{{content:"";position:absolute;left:0;top:7px;width:12px;height:12px;background:{BRAND["primary"]};transform:rotate(45deg);border-radius:2px;box-shadow:0 0 0 2px rgba(26,115,232,.12);}}

/* ====== KPI badges ====== */
.kpi-grid{{display:grid; grid-template-columns: repeat(3,1fr); gap:12px; margin:10px 0 16px;}}
@media (max-width: 640px){{ .kpi-grid{{grid-template-columns:1fr;}} }}
.kpi{{border-radius:14px; padding:12px 14px; box-shadow:0 4px 12px rgba(0,0,0,.06);}}
.kpi .label{{font-size:.85rem; opacity:.8; margin-bottom:2px;}}
.kpi .value{{font-weight:700; font-size:1.3rem;}}
/* variantes clair/sombre */
:root{{--kpi-bg: {("#0f172a" if THEME_BASE=="dark" else "#ffffff")}; --kpi-sub: {("#94a3b8" if THEME_BASE=="dark" else "#475569")};}}
.kpi{{background: var(--kpi-bg);}}
.kpi.primary{{background: linear-gradient(180deg, {BRAND["primary_soft"]}, #ffffff);}}
.kpi .label{{color: var(--kpi-sub);}}
</style>
""", unsafe_allow_html=True)

# ================== Imports ==================
try:
    import plotly.graph_objects as go
except ModuleNotFoundError:
    st.error("❌ Plotly n'est pas installé. Ajoute `plotly==5.22.0` dans `requirements.txt` puis redéploie.")
    st.stop()

import pandas as pd

# ================== Utils ==================
def safe_image(path: str, **kwargs):
    try:
        st.image(path, **kwargs)
    except Exception as e:
        st.warning(f"⚠️ Image introuvable : `{path}`. (Détail : {e})")

def fmt_eur(x): return f"{x:,.0f} €".replace(",", " ")
def fmt_pct(x): return f"{x:.2f} %".replace(".", ",")

def cagr(initial, final, years):
    if years <= 0 or initial <= 0:
        return 0.0
    return (final / initial) ** (1/years) - 1

# ================== Google Sheets (optionnel) ==================
def envoi_google_sheets(prenom_nom, societe, email_pro, capital, rendement, duree, valeur_ct, valeur_cc):
    try:
        import gspread
        from oauth2client.service_account import ServiceAccountCredentials
        scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
        creds_dict = st.secrets["GOOGLE_SHEETS_CREDS"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sh = client.open("TIPS_Simulateur")
        sh.sheet1.append_row([prenom_nom, societe, email_pro, capital, rendement, duree, valeur_ct, valeur_cc])
    except KeyError:
        st.warning("⚠️ Secret manquant : `GOOGLE_SHEETS_CREDS`. Configure-le dans **Settings → Secrets**.")
    except ModuleNotFoundError:
        st.warning("⚠️ Ajoute `gspread` et `oauth2client` dans `requirements.txt` pour activer l’envoi Google Sheets.")
    except Exception as e:
        st.warning(f"⚠️ Échec d’envoi vers Google Sheets : {e}")

# ================== State ==================
if "started" not in st.session_state:
    st.session_state.started = False

# ================== APP ==================
try:
    # -------- Accueil --------
    if not st.session_state.started:
        col1, col2 = st.columns([1, 4])
        with col1:
            safe_image("logo_tips.png", width=150)
        with col2:
            st.markdown("## Le simulateur qui transforme vos décisions en valeur")
            st.markdown("### *Un outil d’aide à la décision pour optimiser vos choix d’investissement*")

        st.markdown("---")
        st.markdown("""
### Pourquoi utiliser ce simulateur ?
<ul class="features">
  <li>Visualiser l’impact de la fiscalité sur un <strong>Compte Titres</strong> vs un <strong>Contrat de Capitalisation</strong></li>
  <li>Calculer vos <strong>gains</strong> selon vos objectifs</li>
  <li>Renforcer votre compréhension de chaque dispositif</li>
</ul>
""", unsafe_allow_html=True)

        st.button("🚀 Démarrer la simulation",
                  on_click=lambda: (st.session_state.__setitem__("started", True), st.rerun()))

    # -------- Simulateur --------
    else:
        col1, col2 = st.columns([1, 4])
        with col1:
            safe_image("logo_tips.png", width=120)
        with col2:
            st.markdown("## Le simulateur qui transforme vos décisions en valeur")
            st.markdown("*Un outil clair et factuel pour comparer vos solutions d’investissement*")

        st.button("⬅ Retour à l’accueil",
                  on_click=lambda: (st.session_state.__setitem__("started", False), st.rerun()))

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
            - Une **avance fiscale** de **105% × 3,41%** du rendement annuel est **ajoutée au résultat imposable**.
            - Pour un **Compte Titres** en société : **IS 25%**.
            - L’écart de taxation est **réinvesti** chaque année (effet composé).
            """)

        if st.button("🚀 Lancer la simulation"):
            # --- Modèle ---
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

            # --- KPI cards ---
            valeur_finale_ct = valeurs_ct[-1]
            valeur_finale_cc = valeurs_cc[-1]
            gain_absolu = valeur_finale_cc - valeur_finale_ct
            gain_relatif = (valeur_finale_cc / valeur_finale_ct - 1) * 100
            cagr_ct = cagr(capital_initial, valeur_finale_ct, duree) * 100
            cagr_cc = cagr(capital_initial, valeur_finale_cc, duree) * 100

            st.markdown('<div class="kpi-grid">', unsafe_allow_html=True)
            st.markdown(f'''
                <div class="kpi primary">
                  <div class="label">Valeur finale – Contrat de Capitalisation</div>
                  <div class="value" style="color:{BRAND["primary"]}">{fmt_eur(valeur_finale_cc)}</div>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown(f'''
                <div class="kpi">
                  <div class="label">Gain net vs Compte Titres</div>
                  <div class="value">{fmt_eur(gain_absolu)}  •  {gain_relatif:.1f}%</div>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown(f'''
                <div class="kpi">
                  <div class="label">Taux annualisé (CAGR)</div>
                  <div class="value">{cagr_cc:.2f}%  vs  <span style="color:{BRAND["neutral"]}">{cagr_ct:.2f}%</span></div>
                </div>
            ''', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # --- Tableau unique (Plotly) ---
            st.markdown("### 🔹 Résultats chiffrés")
            col_annee = df["Années"].tolist()
            col_ct    = df["Compte Titres"].map(fmt_eur).tolist()
            col_cc    = df["Contrat Capitalisation"].map(fmt_eur).tolist()
            col_ecart = df["Écart (€)"].map(fmt_eur).tolist()
            col_ecartp= df["Écart (%)"].map(fmt_pct).tolist()
            n = len(col_annee)
            row_colors = [("#f8fbff" if i % 2 == 0 else "#ffffff") for i in range(n)]
            if n: row_colors[-1] = BRAND["primary_soft"]

            fig_table = go.Figure(data=[
                go.Table(
                    columnwidth=[60, 140, 200, 110, 100],
                    header=dict(
                        values=["Années", "Compte Titres", "Contrat Capitalisation", "Écart (€)", "Écart (%)"],
                        fill_color=TABLE_HEADER,
                        font=dict(color="white", size=12),
                        align="center", height=34
                    ),
                    cells=dict(
                        values=[col_annee, col_ct, col_cc, col_ecart, col_ecartp],
                        align="center", fill_color=[row_colors], height=30
                    )
                )
            ])
            fig_table.update_layout(margin=dict(l=0, r=0, t=6, b=0), template=PLOTLY_TEMPLATE)
            st.plotly_chart(fig_table, use_container_width=True)

            # --- Courbes (centrées, couleurs marque) ---
            st.markdown("### 🔹 Évolution des placements")
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["Années"], y=df["Compte Titres"],
                mode='lines+markers', name="Compte Titres",
                line=dict(width=3, color=BRAND["neutral"])
            ))
            fig.add_trace(go.Scatter(
                x=df["Années"], y=df["Contrat Capitalisation"],
                mode='lines+markers', name="Contrat Capitalisation",
                line=dict(width=3, color=BRAND["primary"])
            ))
            fig.update_layout(
                title="Évolution comparée des placements",
                xaxis_title="Années", yaxis_title="Montant (€)",
                template=PLOTLY_TEMPLATE,
                margin=dict(l=16, r=16, t=60, b=8),
                height=380,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5)
            )
            st.plotly_chart(fig, use_container_width=True)

            # --- Conclusion & CTA ---
            st.markdown("### 🔹 Conclusion comparative")
            st.info("💡 Le différentiel fiscal réinvesti agit comme un accélérateur d’intérêts composés.")
            st.markdown(f"""
            Après **{duree} ans**, le Contrat de Capitalisation atteint **{fmt_eur(valeur_finale_cc)}**, 
            contre **{fmt_eur(valeur_finale_ct)}** pour le Compte Titres.  
            ✅ Gain net : {fmt_eur(gain_absolu)}  •  📈 Écart : {gain_relatif:.1f}%  
            """)

            st.button("⬅ Refaire une simulation",
                      on_click=lambda: (st.session_state.__setitem__("started", False), st.rerun()))

            st.markdown("---")
            st.markdown("### 📅 Prochaine étape : réservez directement un rendez-vous")
            st.components.v1.iframe(
                "https://calendly.com/vincent-sanctot-tips-placements",
                width=700, height=700, scrolling=True
            )

            # Envoi Google Sheets (non bloquant)
            envoi_google_sheets(
                prenom_nom, societe, email_pro,
                capital_initial, taux_rendement, duree,
                valeur_finale_ct, valeur_finale_cc
            )

# --------- Catch toutes erreurs UI ---------
except Exception as e:
    st.error("❌ Une erreur s'est produite dans l'application.")
    st.exception(e)
