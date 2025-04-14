# Simulateur web Streamlit de valorisation des urgences

import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Simulateur Urgences - Sclépios I.A.", layout="wide")

# Logo
st.image("logo_complet.png", width=250)

st.title("📊 Simulateur de Valorisation des Urgences")
st.markdown("""
Ce simulateur permet d’estimer les **gains financiers potentiels** issus d’une meilleure valorisation des passages aux urgences optimisés par Sclépios I.A.

- Avis spécialisés
- CCMU 2+ et 3+
- UHCD mono-RUM valorisables
""")

# Interface Streamlit
col1, col2, col3 = st.columns(3)
with col1:
    nb_passages = st.slider("Nombre total de passages aux urgences", 10000, 100000, 40000, step=1000)
with col2:
    taux_uhcd_actuel = st.slider("Taux actuel d’UHCD (%)", 0, 30, 5)
with col3:
    taux_uhcd_cible = st.slider("Taux cible d’UHCD (%)", taux_uhcd_actuel, 30, 8)

col4, _ = st.columns(2)
with col4:
    taux_mono_rum = st.slider("Proportion des UHCD mono-RUM (%)", 0, 100, 70)

st.markdown(f"<h4 style='text-align:center;'>📈 Taux d’UHCD mono-RUM</h4>", unsafe_allow_html=True)
uhcd_mono_rum_init = (nb_uhcd_actuel * (taux_mono_rum / 100)) / nb_passages * 100
uhcd_mono_rum_cible = (nb_uhcd_cible * (taux_mono_rum / 100)) / nb_passages * 100
st.markdown(f"<div style='text-align: center;'>Taux initial : <strong>{uhcd_mono_rum_init:.2f}%</strong> &nbsp;&nbsp;|&nbsp;&nbsp; Taux cible : <strong>{uhcd_mono_rum_cible:.2f}%</strong></div><br>", unsafe_allow_html=True)

# Constantes tarifaires
TARIF_AVIS_SPE = 24.56
TARIF_CCMU2 = 14.53
TARIF_CCMU3 = 19.38
TARIF_UHCD = 400
BONUS_MONORUM = 0.05 * TARIF_UHCD

# Calculs
nb_uhcd_actuel = (taux_uhcd_actuel / 100) * nb_passages
nb_uhcd_cible = (taux_uhcd_cible / 100) * nb_passages
nb_uhcd_nouveaux = max(0, nb_uhcd_cible - nb_uhcd_actuel)

nb_uhcd_mono_rum_cible = nb_uhcd_cible * (taux_mono_rum / 100)
nb_uhcd_mono_rum_nouveaux = nb_uhcd_nouveaux * (taux_mono_rum / 100)
cs_ext = nb_passages - nb_uhcd_actuel

nb_avis_spe = 0.05 * cs_ext
nb_ccmu2 = 0.03 * cs_ext
nb_ccmu3 = 0.03 * cs_ext

# Gains
gain_avis_spe = nb_avis_spe * TARIF_AVIS_SPE
gain_ccmu2 = nb_ccmu2 * TARIF_CCMU2
gain_ccmu3 = nb_ccmu3 * TARIF_CCMU3
uhcd_valorisation_base = nb_uhcd_mono_rum_nouveaux * TARIF_UHCD
uhcd_valorisation_bonus = nb_uhcd_mono_rum_cible * BONUS_MONORUM

gain_uhcd_total = uhcd_valorisation_base + uhcd_valorisation_bonus
total_gain = gain_avis_spe + gain_ccmu2 + gain_ccmu3 + gain_uhcd_total

# Construction du DataFrame
labels = [
    "Avis spécialisés",
    "CCMU 2+",
    "CCMU 3+",
    "UHCD mono-RUM (base)",
    "Majoration 5% UHCD mono-RUM"
]
volumes = [
    int(nb_avis_spe),
    int(nb_ccmu2),
    int(nb_ccmu3),
    int(nb_uhcd_mono_rum_nouveaux),
    int(nb_uhcd_mono_rum_cible)
]
gains = [
    round(gain_avis_spe, 2),
    round(gain_ccmu2, 2),
    round(gain_ccmu3, 2),
    round(uhcd_valorisation_base, 2),
    round(uhcd_valorisation_bonus, 2)
]

# Ne pas afficher la ligne UHCD (base) si le taux cible = taux actuel
if taux_uhcd_actuel == taux_uhcd_cible:
    labels.pop(3)
    volumes.pop(3)
    gains.pop(3)

# Mise en forme du DataFrame
data = pd.DataFrame({
    "Levier": labels,
    "Volume estimé": volumes,
    "Gain total estimé (€)": gains
})

st.subheader("📋 Résumé des estimations")
st.dataframe(data.set_index("Levier"), use_container_width=True)

# Graphique interactif moderne avec Plotly
fig = px.bar(
    data,
    x="Gain total estimé (€)",
    y="Levier",
    orientation="h",
    text="Gain total estimé (€)",
    color="Levier",
    color_discrete_sequence=px.colors.qualitative.Set3,
    title="Impact financier des leviers optimisés par Sclépios I.A."
)
fig.update_traces(
    texttemplate='%{text:,.0f} €',
    textposition='outside',
    hovertemplate='<b>%{y}</b><br>Gain : %{x:,.0f} €<extra></extra>'
)
fig.update_layout(
    xaxis_title="Montant estimé (€)",
    yaxis_title="",
    plot_bgcolor="#f5f5f5",
    paper_bgcolor="#ffffff",
    font=dict(size=14),
    transition_duration=500,
    height=500
)

st.plotly_chart(fig, use_container_width=True)

st.markdown(f"### 💰 Valorisation totale estimée : **{total_gain:,.2f} €**")

st.markdown("""
---
Développé par **Sclépios I.A.** pour révéler la valeur cachée des données médicales.
""")
