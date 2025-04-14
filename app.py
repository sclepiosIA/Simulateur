# Simulateur Streamlit de valorisation des urgences avec interface interactive et animations

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Simulateur Urgences - Sclépios I.A.", layout="wide")

# Logo Sclépios I.A.
st.image("https://www.sclepios-ia.com/wp-content/uploads/2024/03/logo_SclepiosIA_complet.png", width=250)

st.title("📊 Simulateur de Valorisation des Urgences")
st.markdown("""
Bienvenue sur le simulateur **Sclépios I.A.** permettant d’estimer les **gains financiers potentiels** issus d’une meilleure valorisation des passages aux urgences.

Ce simulateur intègre les leviers suivants :
- Avis spécialisés
- Cotation CCMU 2+ et 3+
- Valorisation des séjours UHCD
""")

# Interface utilisateur
col1, col2 = st.columns(2)
with col1:
    nb_passages = st.slider("Nombre total de passages aux urgences", 10000, 100000, 40000, step=1000)
with col2:
    taux_uhcd_global = st.slider("Taux global d’orientation vers l’UHCD (%)", 0, 30, 8)

cs_ext = int(nb_passages * 0.8)

# Tarifs unitaires
TARIF_AVIS_SPE = 24.56
TARIF_CCMU2 = 14.53
TARIF_CCMU3 = 19.38
TARIF_UHCD = 400

# Volumes estimés
nb_avis_spe = 0.07 * cs_ext
nb_ccmu2 = 0.03 * cs_ext
nb_ccmu3 = 0.03 * cs_ext
nb_uhcd = (taux_uhcd_global / 100) * nb_passages

# Valorisation globale
gain_avis_spe = nb_avis_spe * TARIF_AVIS_SPE
gain_ccmu2 = nb_ccmu2 * TARIF_CCMU2
gain_ccmu3 = nb_ccmu3 * TARIF_CCMU3
gain_uhcd = nb_uhcd * TARIF_UHCD
total_gain = gain_avis_spe + gain_ccmu2 + gain_ccmu3 + gain_uhcd

# DataFrame pour affichage
data = pd.DataFrame({
    "Levier": ["Avis spécialisés", "CCMU 2+", "CCMU 3+", "UHCD"],
    "Volume": [int(nb_avis_spe), int(nb_ccmu2), int(nb_ccmu3), int(nb_uhcd)],
    "Gain estimé (€)": [gain_avis_spe, gain_ccmu2, gain_ccmu3, gain_uhcd]
})
data["Gain estimé (€)"] = data["Gain estimé (€)"].round(2)

# Résumé affiché
st.subheader("📋 Résumé des estimations")
st.dataframe(data.set_index("Levier"), use_container_width=True)

# Graphique interactif avec animation
fig = px.bar(
    data,
    x="Gain estimé (€)",
    y="Levier",
    orientation="h",
    text="Gain estimé (€)",
    color="Levier",
    color_discrete_sequence=px.colors.qualitative.Safe,
    title="💶 Impact financier global par levier"
)
fig.update_traces(texttemplate='%{text:,.0f} €', textposition='outside')
fig.update_layout(
    xaxis_title="Montant en euros",
    yaxis_title="",
    plot_bgcolor="#f9f9f9",
    paper_bgcolor="#f9f9f9",
    font=dict(size=14),
    transition_duration=500
)

st.plotly_chart(fig, use_container_width=True)

# Affichage du total
total = total_gain.round(2)
st.markdown(f"### 💰 **Valorisation totale estimée : {total:,.2f} €**")

st.markdown("""
---
Développé avec ❤️ par **Sclépios I.A.** pour révéler la valeur cachée des données médicales.
""")

