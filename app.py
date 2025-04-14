# Simulateur web Streamlit de valorisation des urgences avec affichage interactif

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

st.set_page_config(page_title="Simulateur Urgences - Sclépios I.A.", layout="wide")
# Logo de Sclépios I.A.
st.image("logo_complet.png", width=250)


st.title("📊 Simulateur de Valorisation des Urgences")
st.markdown("""
Ce simulateur permet d’estimer les **gains financiers potentiels** issus d’une meilleure valorisation des passages aux urgences :
- Avis spécialisés
- Cotation CCMU 2+ et 3+
- Valorisation des séjours UHCD (mono-RUM uniquement)
""")

# Interface utilisateur
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

# Tarifs
TARIF_AVIS_SPE = 24.56
TARIF_CCMU2 = 14.53
TARIF_CCMU3 = 19.38
TARIF_UHCD = 400
BONUS_MONORUM = 0.05 * TARIF_UHCD

# Calculs UHCD
nb_uhcd_actuel = (taux_uhcd_actuel / 100) * nb_passages
nb_uhcd_cible = (taux_uhcd_cible / 100) * nb_passages
nb_uhcd_nouveaux = nb_uhcd_cible - nb_uhcd_actuel

nb_uhcd_mono_rum_actuel = nb_uhcd_actuel * (taux_mono_rum / 100)
nb_uhcd_mono_rum_nouveaux = nb_uhcd_nouveaux * (taux_mono_rum / 100)
nb_uhcd_mono_rum_total = nb_uhcd_mono_rum_actuel + nb_uhcd_mono_rum_nouveaux

cs_ext = nb_passages - nb_uhcd_actuel

# Volumes
nb_avis_spe = 0.07 * cs_ext
nb_ccmu2 = 0.03 * cs_ext
nb_ccmu3 = 0.03 * cs_ext

# Gains
gain_avis_spe = nb_avis_spe * TARIF_AVIS_SPE
gain_ccmu2 = nb_ccmu2 * TARIF_CCMU2
gain_ccmu3 = nb_ccmu3 * TARIF_CCMU3

uhcd_valorisation_base = nb_uhcd_mono_rum_total * TARIF_UHCD
uhcd_valorisation_bonus = nb_uhcd_mono_rum_total * BONUS_MONORUM

gain_uhcd_total = uhcd_valorisation_base + uhcd_valorisation_bonus
total_gain = gain_avis_spe + gain_ccmu2 + gain_ccmu3 + gain_uhcd_total

# DataFrame
data = pd.DataFrame({
    "Levier": [
        "Avis spécialisés", 
        "CCMU 2+", 
        "CCMU 3+", 
        "UHCD mono-RUM (base)",
        "Majoration 5% UHCD mono-RUM"
    ],
    "Volume estimé": [
        int(nb_avis_spe), 
        int(nb_ccmu2), 
        int(nb_ccmu3), 
        int(nb_uhcd_mono_rum_total),
        int(nb_uhcd_mono_rum_total)
    ],
    "Gain total estimé (€)": [
        round(gain_avis_spe, 2),
        round(gain_ccmu2, 2),
        round(gain_ccmu3, 2),
        round(uhcd_valorisation_base, 2),
        round(uhcd_valorisation_bonus, 2)
    ]
})

st.subheader("📋 Résumé des estimations")
st.dataframe(data.set_index("Levier"), use_container_width=True)

# Graphique matplotlib via Streamlit
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(data["Levier"], data["Gain total estimé (€)"], color=['#4ba3c7', '#8ac6d1', '#c3e0e5', '#6a9fb5', '#1d3557'])

for bar in bars:
    width = bar.get_width()
    ax.text(width + 1000, bar.get_y() + bar.get_height() / 2, f"{int(width):,} €", va='center', fontsize=10)

ax.set_xlabel("Gain en euros")
ax.set_title("Impact financier total par levier de valorisation")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,} €'))
plt.tight_layout()
plt.grid(axis='x', linestyle='--', alpha=0.4)

st.pyplot(fig)

st.markdown(f"### 💰 Valorisation totale estimée : **{total_gain:,.2f} €**")

st.markdown("""
---
Développé par **Sclépios I.A.** pour révéler la valeur cachée des données médicales.
""")
