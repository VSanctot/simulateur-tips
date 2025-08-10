"""
TIPS – Simulateur CT vs Contrat de Capitalisation (optimisé)
"""
from __future__ import annotations
import re
from dataclasses import dataclass
from typing import Tuple
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

LOGO_PATH = "logo_tips.png"
SHEET_NAME = "TIPS_Simulateur"
TAX_CT = 0.25
ADVANCE_FACTOR = 1.05
CC_RATE_BASE = 0.0341
TAX_FACTOR_CC = 0.25
TAX_CC = ADVANCE_FACTOR * CC_RATE_BASE * TAX_FACTOR_CC
CURRENCY = "€"

@dataclass(frozen=True)
class SimulationParams:
    capital_initial: float
    taux_rendement: float
    duree: int
    def is_valid(self) -> Tuple[bool, str]:
        if self.capital_initial < 1000: return False, "Capital ≥ 1 000 €"
        if not (0 < self.taux_rendement <= 50): return False, "Rendement dans (0;50]%"
        if not (1 <= self.duree <= 50): return False, "Durée entre 1 et 50 ans"
        return True, ""

@st.cache_data
def simulate(params: SimulationParams):
    net_ct = params.taux_rendement * (1 - TAX_CT) / 100
    net_cc = params.taux_rendement * (1 - TAX_CC) / 100
    annees = np.arange(0, params.duree + 1)
    growth_ct = params.capital_initial * np.power(1 + net_ct, annees)
    growth_cc = params.capital_initial * np.power(1 + net_cc, annees)
    df = pd.DataFrame({"Années": annees, "Compte Titres": growth_ct, "Contrat Capitalisation": growth_cc})
    v_ct, v_cc = float(growth_ct[-1]), float(growth_cc[-1])
    return df, v_ct, v_cc, v_cc - v_ct, (v_cc / v_ct - 1) * 100 if v_ct else 0

def money(x: float) -> str: return f"{x:,.0f} {CURRENCY}".replace(",", " ")
def valid_email(email: str) -> bool: return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email)) if email else False
@st.cache_resource
def _logo_exists(path: str) -> bool:
    import os; return os.path.exists(path)

def plot(df: pd.DataFrame) -> None:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["Années"], y=df["Compte Titres"], mode="lines+markers", name="Compte Titres"))
    fig.add_trace(go.Scatter(x=df["Années"], y=df["Contrat Capitalisation"], mode="lines+markers", name="Contrat Capitalisation"))
    fig.update_layout(title="Évolution comparée des placements", xaxis_title="Années", yaxis_title=f"Montant ({CURRENCY})", template="plotly_white", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

def display_table(df: pd.DataFrame) -> None:
    df_aff = df.copy()
    df_aff["Compte Titres"] = df_aff["Compte Titres"].map(money)
    df_aff["Contrat Capitalisation"] = df_aff["Contrat Capitalisation"].map(money)
    st.markdown(df_aff.to_html(index=False), unsafe_allow_html=True)

def push_to_sheets(prenom_nom: str, societe: str, email: str, params: SimulationParams, v_ct: float, v_cc: float) -> None:
    try:
        from oauth2client.service_account import ServiceAccountCredentials
        import gspread
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        secrets = st.secrets.get("GOOGLE_SHEETS_CREDS", None)
        if not secrets: st.warning("Pas de clé Google Sheets"); return
        creds = ServiceAccountCredentials.from_json_keyfile_dict(secrets, scope)
        client = gspread.authorize(creds)
        client.open(SHEET_NAME).sheet1.append_row([prenom_nom, societe, email, params.capital_initial, params.taux_rendement, params.duree, v_ct, v_cc])
        st.toast("Données envoyées ✅")
    except Exception as e:
        st.info(f"Envoi Google Sheets non réalisé : {e}")

def main() -> None:
    st.set_page_config(page_title="TIPS – Simulateur", page_icon="📈", layout="wide")
    col1, col2 = st.columns([1, 4])
    with col1: st.image(LOGO_PATH, width=120) if _logo_exists(LOGO_PATH) else None
    with col2: st.markdown("## TIPS : le simulateur qui valorise votre patrimoine")
    if "started" not in st.session_state: st.session_state.started = False
    if not st.session_state.started:
        if st.button("🚀 Démarrer la simulation"): st.session_state.started = True; st.rerun(); return
    else:
        if st.button("⬅ Retour à l’accueil"): st.session_state.started = False; st.rerun()
        with st.form("params_form"):
            prenom_nom = st.text_input("👤 Prénom / Nom"); societe = st.text_input("🏢 Société"); email_pro = st.text_input("📧 Email professionnel")
            capital_initial = st.number_input("💰 Capital investi (€)", min_value=1000, step=1000, value=100000)
            taux_rendement = st.number_input("📈 Rendement brut attendu (%)", min_value=1.0, step=0.1, value=5.0)
            duree = st.slider("⏳ Durée de placement (années)", 1, 30, 10)
            lancer = st.form_submit_button("🚀 Lancer la simulation")
        if not lancer: return
        params = SimulationParams(capital_initial=float(capital_initial), taux_rendement=float(taux_rendement), duree=int(duree))
        ok, msg = params.is_valid();
        if not ok: st.error(msg); return
        df, v_ct, v_cc, gain_abs, gain_rel = simulate(params)
        display_table(df); plot(df)
        st.markdown(f"Après {params.duree} ans: CC = {money(v_cc)}, CT = {money(v_ct)}, gain {money(gain_abs)} (+{gain_rel:.1f}%)")
        if st.button("Enregistrer dans Google Sheets"):
            if valid_email(email_pro): push_to_sheets(prenom_nom, societe, email_pro, params, v_ct, v_cc)
            else: st.error("Email invalide")

if __name__ == "__main__":
    main()
