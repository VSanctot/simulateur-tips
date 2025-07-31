import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# 🎨 Configuration page
st.set_page_config(
    page_title="Comparateur Compte-titres vs Contrat de Capitalisation",
    page_icon="💼",
    layout="centered"
)

# 🎯 Titre
st.title("💼 Comparateur Compte-titres vs Contrat de Capitalisation")
st.markdown("### Un outil développé par **TIPS** pour optimiser vos décisions d’investissement")

# 📝 Formulaire utilisateur
prenom_nom = st.text_input("Prénom / Nom")
societe = st.text_input("Société")
email = st.text_input("Email professionnel")

montant = st.number_input("💶 Montant d'investissement (€)", min_value=100000.0, max_value=100000000.0, step=1000.0, value=100000.0)
performance = st.number_input("📈 Objectif de performance (%)", min_value=3.0, max_value=15.0, step=0.5, value=5.0)
horizon = st.number_input("⏳ Horizon d'investissement (années)", min_value=3, max_value=40, step=1, value=10)

# 📊 Calculs
if st.button("🚀 Lancer la simulation"):
    perf = performance / 100
    annees = list(range(1, horizon + 1))
    valeurs_ct = [montant]
    valeurs_cap = [montant]

    # Taux fiscaux
    fiscalite_ct = 0.30      # CTO = 30% sur les gains
    fiscalite_cap = 1.05 * 0.0341  # Contrat = 105% × 3,41%

    for an in annees:
        # CTO : impôt chaque année sur les gains
        gain_ct = valeurs_ct[-1] * perf
        net_gain_ct = gain_ct * (1 - fiscalite_ct)
        valeurs_ct.append(valeurs_ct[-1] + net_gain_ct)

        # Contrat : impôt réduit chaque année sur les gains
        gain_cap = valeurs_cap[-1] * perf
        net_gain_cap = gain_cap * (1 - fiscalite_cap)
        valeurs_cap.append(valeurs_cap[-1] + net_gain_cap)

    # Résultats
    gain = valeurs_cap[-1] - valeurs_ct[-1]

    st.subheader("📊 Résultats finaux")
    st.write(f"Montant investi : **{montant:,.0f} €**")
    st.write(f"Horizon : **{horizon} ans**")
    st.write(f"Performance annuelle : **{performance}%**")

    st.success(f"💼 Compte-titres (après fiscalité annuelle) : {valeurs_ct[-1]:,.0f} €")
    st.success(f"📑 Contrat de capitalisation (après fiscalité annuelle) : {valeurs_cap[-1]:,.0f} €")

    if gain > 0:
        st.info(f"✅ Avantage du contrat de capitalisation : **{gain:,.0f} €**")
    else:
        st.warning(f"⚠️ Pas d’avantage (écart : {gain:,.0f} €**)")

    # 🔹 Graphique comparatif
    df = pd.DataFrame({
        "Année": [0] + annees,
        "Compte-titres": valeurs_ct,
        "Contrat de capitalisation": valeurs_cap
})


