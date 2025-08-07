import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ======================
# 🎯 Configuration de la page
# ======================
st.set_page_config(
    page_title="Simulateur Patrimonial TIPS",
    page_icon="💼",
    layout="centered"
)

# ======================
# 🖼️ Logo et Titre
# ======================
st.image("logo_tips.png", width=180)
st.markdown("# Bienvenue sur le Simulateur Patrimonial TIPS")
st.markdown("##### TIPS : Le simulateur qui valorise votre patrimoine")

st.markdown("---")

# ======================
# 📋 Formulaire utilisateur
# ======================
with st.form("formulaire"):
    st.markdown("## 📄 Paramètres de simulation")

    investissement = st.number_input("Montant investi (€)", min_value=1000, value=100000, step=1000)
    duree = st.slider("Durée de placement (en années)", 1, 30, 10)
    taux_cgt = st.slider("Taux fiscalité Compte Titres (%)", 0.0, 50.0, 25.0)
    taux_cc = 1.05 * 3.41 / 100  # 3,58%

    soumis = st.form_submit_button("Lancer la simulation")

# ======================
# 📊 Simulation et graphiques
# ======================
if soumis:
    # Simulation sur la durée choisie
    annees = list(range(duree + 1))
    capital_initial = investissement

    # Hypothèses
    rendement_brut = 0.0341  # 3,41%
    rendement_net_ct = rendement_brut * (1 - taux_cgt / 100)
    rendement_net_cc = taux_cc

    ct = [capital_initial]
    cc = [capital_initial]

    for i in range(1, duree + 1):
        ct.append(ct[-1] * (1 + rendement_net_ct))
        cc.append(cc[-1] * (1 + rendement_net_cc))

    df = pd.DataFrame({
        "Année": annees,
        "Compte Titres": ct,
        "Contrat Capitalisation": cc
    })

    # Courbe
    st.markdown("## 📈 Projection des valeurs futures")
    fig, ax = plt.subplots()
    ax.plot(df["Année"], df["Compte Titres"], label="Compte Titres")
    ax.plot(df["Année"], df["Contrat Capitalisation"], label="Contrat de Capitalisation")
    ax.set_xlabel("Années")
    ax.set_ylabel("Valeur finale (€)")
    ax.legend()
    st.pyplot(fig)

    # Résultats finaux
    st.markdown("## 🧾 Résultats")
    gain_ct = ct[-1]
    gain_cc = cc[-1]
    diff = gain_cc - gain_ct

    st.success(f"📌 Après {duree} ans, votre placement vaudrait :")
    st.markdown(f"- Compte Titres : **{gain_ct:,.0f} €**")
    st.markdown(f"- Contrat de Capitalisation : **{gain_cc:,.0f} €**")
    st.markdown(f"➡️ Écart en faveur du contrat de capitalisation : **{diff:,.0f} €**")

    st.markdown("---")

    # ======================
    # 📅 Call to action Calendly
    # ======================
    st.markdown("### 🤝 Planifier un rendez-vous avec un conseiller TIPS")

    st.markdown(
        """
        Vous souhaitez approfondir cette simulation et obtenir des recommandations personnalisées ?  
        Réservez un entretien confidentiel de 30 minutes avec un conseiller TIPS :
        """
    )

    calendly_url = "https://calendly.com/vincent-sanctot-tips-placements"

    if st.button("📅 Réserver un rendez-vous"):
        st.markdown(
            f'<meta http-equiv="refresh" content="0; url={calendly_url}">',
            unsafe_allow_html=True
        )
