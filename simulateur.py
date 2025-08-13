import re
import time
from datetime import datetime

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ======================
# OPTIONNEL: Google Sheets (gspread)
# ======================
try:
    import gspread
    from oauth2client.service_account import ServiceAccountCredentials
    GSPREAD_AVAILABLE = True
except Exception:
    GSPREAD_AVAILABLE = False

# ======================
# CONFIG GÉNÉRALE
# ======================
st.set_page_config(
    page_title="TIPS — Simulateur d'investissement",
    page_icon="💹",
    layout="wide",
)

# --- Thème léger
st.markdown(
    """
    <style>
    /* Cartes et sections */
    .metric-card {background:#f8fafc;border:1px solid #e5e7eb;padding:16px;border-radius:12px}
    .accent {background:#eef6ff;border-left:6px solid #2563eb;padding:16px;border-radius:10px}
    .warn {background:#fff7ed;border-left:6px solid #f97316;padding:16px;border-radius:10px}
    .ok {background:#ecfdf5;border-left:6px solid #10b981;padding:16px;border-radius:10px}
    .muted {color:#6b7280}
    .cap {text-transform:uppercase; letter-spacing: .08em; font-weight:600; font-size:0.8rem}
    </style>
    """,
    unsafe_allow_html=True,
)

# ======================
# UTILITAIRES
# ======================
CURRENCY = "€"

@st.cache_data(show_spinner=False)
def format_eur(x: float) -> str:
    try:
        return f"{x:,.0f} {CURRENCY}".replace(",", " ")
    except Exception:
        return str(x)

@st.cache_data(show_spinner=False)
def compute_projection(capital: float, taux_brut_pct: float, duree: int, *,
                       taux_fiscal_ct_pct: float,
                       ps_cc_pct: float,
                       frais_cc_pct: float) -> pd.DataFrame:
    """Calcule l'évolution annuelle sous hypothèses simplifiées.
    - CT: rendement net = taux_brut * (1 - taux_fiscal_ct)
    - CC: les prélèvements sociaux et frais sont approchés par une décote du taux brut
    """
    annees = list(range(0, duree + 1))

    # CT
    r_ct_net = taux_brut_pct * (1 - taux_fiscal_ct_pct / 100)
    valeurs_ct = [capital * ((1 + r_ct_net / 100) ** t) for t in annees]

    # CC (approximation: PS et frais mordent le rendement chaque année)
    r_cc_net = taux_brut_pct * (1 - (ps_cc_pct + frais_cc_pct) / 100)
    valeurs_cc = [capital * ((1 + r_cc_net / 100) ** t) for t in annees]

    df = pd.DataFrame({
        "Année": annees,
        "Compte titres": valeurs_ct,
        "Contrat de capitalisation": valeurs_cc,
    })
    return df


def valid_email(email: str) -> bool:
    if not email:
        return False
    return re.match(r"^[\w\.-]+@[\w\.-]+\.[a-zA-Z]{2,}$", email) is not None


def can_send_to_sheets() -> bool:
    if not GSPREAD_AVAILABLE:
        return False
    # Secrets requis: st.secrets["GOOGLE_SHEETS_CREDS"]
    try:
        _ = st.secrets["GOOGLE_SHEETS_CREDS"]
        return True
    except Exception:
        return False


def send_to_google_sheets(row: list) -> tuple[bool, str]:
    if not can_send_to_sheets():
        return False, "Google Sheets non configuré (dépendances ou secrets manquants)."
    try:
        scope = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive",
        ]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(
            st.secrets["GOOGLE_SHEETS_CREDS"], scope
        )
        client = gspread.authorize(creds)
        sh = client.open("TIPS_Simulateur")
        sheet = sh.sheet1
        sheet.append_row(row)
        return True, "Enregistré."
    except Exception as e:
        return False, f"Erreur Google Sheets: {e}"


# ======================
# EN-TÊTE
# ======================
col1, col2 = st.columns([1, 6])
with col1:
    st.image("logo_tips.png", width=120)
with col2:
    st.markdown("# Le simulateur qui transforme vos décisions en valeur")
    st.markdown("*Un outil clair et factuel pour comparer vos solutions d’investissement*")

st.divider()

# ======================
# ACCUEIL / MODE
# ======================
if "started" not in st.session_state:
    st.session_state.started = False

if not st.session_state.started:
    st.markdown(
        """
        ### Pourquoi utiliser ce simulateur ?
        - Comprendre l'impact de la **fiscalité** sur la performance d'un **Compte Titres** et d'un **Contrat de Capitalisation**
        - Évaluer vos gains **nets** en fonction de vos objectifs
        - Consolider votre **décision** avec des chiffres et un visuel
        """
    )

    st.info("Cette version client inclut l’export, la conformité RGPD, et la configuration des hypothèses fiscales.")

    if st.button("🚀 Démarrer la simulation"):
        st.session_state.started = True
        st.rerun()

else:
    if st.button("⬅ Retour à l’accueil"):
        st.session_state.started = False
        st.rerun()

    st.subheader("🔹 Étape 1 : Paramètres de simulation")

    with st.form("parametres"):
        c1, c2, c3 = st.columns([1.2, 1, 1])
        with c1:
            prenom_nom = st.text_input("👤 Prénom / Nom", placeholder="Prénom Nom")
            societe = st.text_input("🏢 Société", placeholder="Votre société (optionnel)")
            email_pro = st.text_input("📧 Email professionnel", placeholder="prenom@entreprise.com")
        with c2:
            capital_initial = st.number_input("💰 Capital investi (€)", min_value=1000, step=1000, value=1_000_000)
            taux_rendement = st.number_input("📈 Rendement brut attendu (%)", min_value=0.1, step=0.1, value=5.0)
            duree = st.slider("⏳ Durée de placement (années)", 1, 40, 10)
        with c3:
            taux_fiscal_ct = st.number_input("📑 PFU Compte Titres (%)", min_value=0.0, max_value=100.0, value=30.0,
                                             help="Hypothèse PFU (IR + PS) — paramétrable.")
            ps_cc = st.number_input("🏷️ Prélèvements sociaux annuels CC (%)", min_value=0.0, max_value=100.0, value=17.2,
                                    help="Approche simplifiée: ponction annuelle des PS sur le rendement.")
            frais_cc = st.number_input("⚙️ Frais de gestion CC (%)", min_value=0.0, max_value=5.0, value=0.0)

        consent = st.checkbox("J’autorise l’enregistrement de mes informations pour recontact (RGPD)", value=False)
        lancer = st.form_submit_button("🚀 Lancer la simulation")

    # ======================
    # VALIDATION
    # ======================
    if lancer:
        errs = []
        if not prenom_nom.strip():
            errs.append("Veuillez saisir un nom.")
        if not valid_email(email_pro):
            errs.append("Email professionnel invalide.")
        if capital_initial <= 0:
            errs.append("Le capital doit être > 0.")
        if duree < 1:
            errs.append("Durée invalide.")

        if errs:
            st.error("\n".join(errs))
        else:
            # ======================
            # CALCULS
            # ======================
            df = compute_projection(
                capital=capital_initial,
                taux_brut_pct=taux_rendement,
                duree=duree,
                taux_fiscal_ct_pct=taux_fiscal_ct,
                ps_cc_pct=ps_cc,
                frais_cc_pct=frais_cc,
            )

            # ======================
            # TABLEAU
            # ======================
            st.subheader("🔹 Résultats chiffrés")
            df_fmt = df.copy()
            for col in ["Compte titres", "Contrat de capitalisation"]:
                df_fmt[col] = df_fmt[col].map(format_eur)
            st.dataframe(df_fmt, use_container_width=True, hide_index=True)

            # ======================
            # COURBES
            # ======================
            st.subheader("🔹 Évolution des placements")
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["Année"], y=df["Compte titres"], mode="lines", name="Compte titres"))
            fig.add_trace(go.Scatter(x=df["Année"], y=df["Contrat de capitalisation"], mode="lines", name="Contrat de capitalisation"))
            fig.update_layout(xaxis_title="Années", yaxis_title=f"Valeur ({CURRENCY})", height=420, legend=dict(orientation="h"))
            st.plotly_chart(fig, use_container_width=True)

            # ======================
            # COMPARATIF FINAL
            # ======================
            v_ct = float(df["Compte titres"].iloc[-1])
            v_cc = float(df["Contrat de capitalisation"].iloc[-1])
            gain_abs = v_cc - v_ct
            gain_rel = (v_cc / v_ct - 1) * 100 if v_ct > 0 else float("inf")

            st.markdown(
                f"""
                <div class="accent">
                    <div class="cap">Comparatif final (à {duree} ans)</div>
                    <p>Contrat de Capitalisation : <strong>{format_eur(v_cc)}</strong></p>
                    <p>Compte Titres : <strong>{format_eur(v_ct)}</strong></p>
                    <p>💡 <strong>Écart de performance :</strong> {format_eur(gain_abs)} ({gain_rel:.1f} %)</p>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # ======================
            # EXPORTS
            # ======================
            st.subheader("🔹 Export")
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Télécharger le CSV", data=csv, file_name=f"simulation_TIPS_{datetime.now().date()}.csv", mime="text/csv")

            # ======================
            # RDV
            # ======================
            st.divider()
            st.subheader("📅 Prochaine étape : réservez directement un rendez-vous")
            st.components.v1.iframe("https://calendly.com/vincent-sanctot-tips-placements", width=900, height=720, scrolling=True)

            # ======================
            # ENREGISTREMENT (opt-in)
            # ======================
            if consent:
                ok, msg = send_to_google_sheets([
                    prenom_nom,
                    societe,
                    email_pro,
                    capital_initial,
                    taux_rendement,
                    duree,
                    v_ct,
                    v_cc,
                    datetime.utcnow().isoformat(),
                ])
                if ok:
                    st.success("Données enregistrées. Merci !")
                else:
                    st.warning(msg)
            else:
                st.markdown(
                    """
                    <div class="warn">Vous n'avez pas autorisé l'enregistrement de vos informations. 
                    La simulation fonctionne sans sauvegarde. Cochez la case RGPD ci-dessus si vous souhaitez être recontacté.</div>
                    """,
                    unsafe_allow_html=True,
                )

            # ======================
            # HYPOTHÈSES & LIMITES
            # ======================
            with st.expander("Hypothèses, fiscalité et limites du modèle"):
                st.markdown(
                    """
                    - **Modèle simplifié.** CT: application d'un PFU global paramétrable sur le rendement.\
                    - **CC:** les prélèvements sociaux et les frais éventuels sont modélisés par une **décote annuelle** du rendement (approximation).\
                    - Les **régimes réels** diffèrent selon le profil, les dates de versement, les arbitrages, et la durée de détention.
                    - Ce simulateur n'est **pas un conseil** en investissement ni fiscal. Merci de valider toute décision avec un professionnel.
                    """
                )
