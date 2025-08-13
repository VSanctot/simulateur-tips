# streamlit_app.py
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go

# ----------------- Réglages généraux -----------------
st.set_page_config(page_title="Simulateur Placements", page_icon="📊", layout="wide")

# CSS minimal pour lisibilité (fond clair, texte foncé, tableau contrasté)
st.markdown("""
<style>
/* Fond clair et texte foncé même si l'utilisateur force un thème sombre */
html, body, [data-testid="stAppViewContainer"] {
  background: #ffffff !important; color: #111 !important;
}
h1, h2, h3, h4, h5 { color:#1f2937 !important; }

/* Tableau : texte foncé + zebra */
[data-testid="stTable"], [data-testid="stDataFrame"] table {
  color: #111 !important;
}
[data-testid="stDataFrame"] tbody tr:nth-child(odd) td {
  background: #fafafa !important;
}
[data-testid="stDataFrame"] tbody tr:nth-child(even) td {
  background: #f3f4f6 !important;
}

/* Marges resserrées sur mobile */
@media (max-width: 640px) {
  .block-container { padding-top: 0.5rem; }
}
</style>
""", unsafe_allow_html=True)

# ----------------- État de l'app -----------------
if "locked" not in st.session_state:
    st.session_state.locked = False
if "result" not in st.session_state:
    st.session_state.result = None
if "table" not in st.session_state:
    st.session_state.table = None

# ----------------- Modèle de calcul -----------------
def simulate(capital_initial: float, n_years: int, r_ct: float, r_cc: float):
    """
    Calcule les trajectoires de valeur pour :
    - Compte Titres (CT)
    - Contrat de Capitalisation (CC)
    r_ct et r_cc en décimal (ex: 0.0375 pour 3,75%).
    """
    years = np.arange(0, n_years + 1)
    ct = capital_initial * (1 + r_ct) ** years
    cc = capital_initial * (1 + r_cc) ** years
    return {"years": years, "ct": ct, "cc": cc}

def build_table(data: dict) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Construit le tableau récapitulatif avec écart € et % (brut + affichage formaté FR)."""
    years = data["years"]
    ct = data["ct"]
    cc = data["cc"]
    diff = cc - ct
    pct = np.where(ct != 0, diff / ct, 0.0)

    raw_df = pd.DataFrame({
        "Années": years.astype(int),
        "Compte Titres (€)": ct,
        "Contrat Capitalisation (€)": cc,
        "Écart (€)": diff,
        "Écart (%)": pct
    })

    # Formatage FR pour l'affichage (espaces, virgules)
    disp_df = pd.DataFrame({
        "Années": raw_df["Années"],
        "Compte Titres (€)": raw_df["Compte Titres (€)"].map(lambda x: f"{x:,.0f}".replace(",", " ").replace(".", ",")),
        "Contrat Capitalisation (€)": raw_df["Contrat Capitalisation (€)"].map(lambda x: f"{x:,.0f}".replace(",", " ").replace(".", ",")),
        "Écart (€)": raw_df["Écart (€)"].map(lambda x: f"{x:,.0f}".replace(",", " ").replace(".", ",")),
        "Écart (%)": raw_df["Écart (%)"].map(lambda x: f"{x*100:,.2f} %".replace(",", " ").replace(".", ","))
    })
    return raw_df, disp_df

# ----------------- Graphique Plotly -----------------
def build_figure(data: dict) -> go.Figure:
    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data["years"], y=data["ct"], mode="lines+markers",
        name="Compte Titres"
    ))
    fig.add_trace(go.Scatter(
        x=data["years"], y=data["cc"], mode="lines+markers",
        name="Contrat Capitalisation"
    ))

    # Légende horizontale, au-dessus, ancrée à droite -> lisible sur mobile
    fig.update_layout(
        title="Évolution comparée des placements",
        xaxis_title="Années",
        yaxis_title="Montant (€)",
        legend=dict(
            orientation="h",
            yanchor="bottom", y=1.02,
            xanchor="right",  x=1
        ),
        margin=dict(l=10, r=10, t=60, b=10),
        hovermode="x unified"
    )
    fig.update_yaxes(separatethousands=True)
    return fig

# ----------------- UI -----------------
st.title("Simulateur Placements")

with st.form("params"):
    c1, c2, c3 = st.columns(3)
    with c1:
        capital_initial = st.number_input(
            "Capital initial (€)", min_value=10_000, max_value=10_000_000,
            value=100_000, step=1_000, disabled=st.session_state.locked
        )
    with c2:
        r_ct = st.number_input(
            "Rendement CT (%)", min_value=0.0, max_value=50.0,
            value=3.75, step=0.10, disabled=st.session_state.locked
        ) / 100.0
    with c3:
        r_cc = st.number_input(
            "Rendement CC (%)", min_value=0.0, max_value=50.0,
            value=4.95, step=0.10, disabled=st.session_state.locked
        ) / 100.0

    n_years = st.slider(
        "Durée (années)", min_value=1, max_value=40, value=10,
        disabled=st.session_state.locked
    )

    submitted = st.form_submit_button(
        "Lancer la simulation", disabled=st.session_state.locked, use_container_width=True
    )

# Calcul uniquement au clic (évite les reruns à chaque frappe)
if submitted and not st.session_state.locked:
    st.session_state.result = simulate(capital_initial, n_years, r_ct, r_cc)
    st.session_state.table = build_table(st.session_state.result)

# ----------------- Résultats -----------------
if st.session_state.result is not None:
    fig = build_figure(st.session_state.result)

    # Graphique figé si locked=True (pas de pan/zoom, pas de barre d'outils)
    st.plotly_chart(
        fig, use_container_width=True,
        config={"displayModeBar": False, "staticPlot": st.session_state.locked}
    )

    # -- Tableau chiffré + Download --
    st.subheader("Résultats chiffrés")
    raw_df, disp_df = st.session_state.table

    st.dataframe(
        disp_df, use_container_width=True, hide_index=True
    )

    # Export CSV (UTF-8-SIG pour Excel)
    csv = raw_df.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        "📥 Télécharger les résultats (CSV)",
        data=csv,
        file_name="simulation_resultats.csv",
        mime="text/csv",
        use_container_width=True
    )

    # -- Actions de contrôle --
    colL, colR = st.columns(2)
    with colL:
        if not st.session_state.locked:
            if st.button("✅ Figer ce résultat", use_container_width=True):
                st.session_state.locked = True
                st.rerun()
        else:
            st.info("Résultat figé : les entrées sont verrouillées et le graphe est statique.")

    with colR:
        if st.button("🔄 Réinitialiser / Nouvelle simulation", use_container_width=True):
            st.session_state.locked = False
            st.session_state.result = None
            st.session_state.table = None
            st.rerun()
else:
    st.caption("Réglez vos paramètres puis cliquez sur **Lancer la simulation**.")
