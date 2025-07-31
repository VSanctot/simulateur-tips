import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Config de la page
st.set_page_config(
    page_title="Comparateur Compte-titres vs Contrat de Capitalisation",
    page_icon="💼",
    layout="centered"
)

st.title("💼 Comparateur Compte-titres vs Contrat de Capitalisation")
st.markdown("### Un outil développé par **TIPS** pour optimiser vos décisions d’investissement")

# Formulaire
prenom_nom = st.text_input("👤 Prénom / Nom")
societe = st.text_input("🏢 Société")
email = st.text_input("✉️ Email professionnel")

montant = st.number_input("💶 Montant d'investissement (€)", min_value=100000.0, max_value=100000000.0, step=1000.0, value=500000.0)
performance = st.number_input("📈 Objectif de performance (%)", min_value=3.0, max_value=15.0, step=0.1, value=5.0)
horizon = st.number_input("⏳ Horizon d'investissement (années)", min_value=3, max_value=40, step=1, value=15)

# Lancer la simulation
if st.button("🚀 Lancer la simulation"):
    perf = performance / 100
    annees = list(range(1, horizon + 1))
    valeurs_ct = [montant]
    valeurs_cap = [montant]

    # Fiscalité
    fiscalite_ct = 0.30
    fiscalite_cap = 1.05 * 0.0341  # 105% * 3,41% = 3,5805%

    for _ in annees:
        # Compte-titres
        gain_ct = valeurs_ct[-1] * perf
        valeurs_ct.append(valeurs_ct[-1] + gain_ct * (1 - fiscalite_ct))

        # Contrat de capitalisation
        gain_cap = valeurs_cap[-1] * perf
        valeurs_cap.append(valeurs_cap[-1] + gain_cap * (1 - fiscalite_cap))

    # Résultats
    st.subheader("📊 Résultats de la simulation")
    st.write(f"Montant initial : **{montant:,.0f} €**")
    st.write(f"Horizon : **{horizon} ans**")
    st.write(f"Performance : **{performance:.2f} % / an**")

    st.success(f"📎 Contrat de capitalisation : {valeurs_cap[-1]:,.0f} €")
    st.success(f"📄 Compte-titres : {valeurs_ct[-1]:,.0f} €")

    ecart = valeurs_cap[-1] - valeurs_ct[-1]
    if ecart > 0:
        st.info(f"✅ Avantage du contrat de capitalisation : **{ecart:,.0f} €**")
    else:
        st.warning(f"⚠️ Pas d’avantage fiscal constaté ({ecart:,.0f} €)")

    # Graphique
    df = pd.DataFrame({
        "Année": [0] + annees,
        "Compte-titres": valeurs_ct,
        "Contrat de capitalisation": valeurs_cap
    })

    fig, ax = plt.subplots()
    ax.plot(df["Année"], df["Compte-titres"], label="Compte-titres (30%)", color="red", linewidth=2)
    ax.plot(df["Année"], df["Contrat de capitalisation"], label="Contrat de capitalisation (3.58%)", color="green", linewidth=2)
    ax.set_title("📈 Évolution comparée après fiscalité")
    ax.set_xlabel("Année")
    ax.set_ylabel("Capital net (€)")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()
    st.pyplot(fig)

    # Tableau
    st.subheader("📑 Détail par année")
    st.dataframe(df.style.format("{:,.0f}"))

