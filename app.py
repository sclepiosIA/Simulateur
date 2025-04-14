# Simulateur Streamlit de valorisation des urgences en ligne avec interface graphique

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

st.set_page_config(page_title="Simulateur Urgences - Sclépios I.A.", layout="centered")
st.title("📊 Simulateur de Valorisation des Urgences")

st.markdown("""
Ce simulateur permet d’estimer les **gains financiers potentiels** liés à une meilleure valorisation des passages aux urgences.
""")

# Interface utilisateur
nb_passages = st.slider("Nombre total de passages aux urgences", min_value=10000, max_value=100000, value=40000, step=1000)
taux_uhcd_base = 2
taux_uhcd_opt = st.slider("Taux optimisé d’orientation UHCD (%)", min_value=2, max_value=30, value=8)
cs_ext = int(nb_passages * 0.8)

# Tarification
TARIF_AVIS_SPE = 24.56
TARIF_CCMU2 = 14.53
TARIF_CCMU3 = 19.38
TARIF_UHCD = 400

# Calculs
nb_avis_spe = 0.07 * cs_ext
nb_ccmu2 = 0.03 * cs_ext
nb_ccmu3 = 0.03 * cs_ext
uhcd_suppl = max(0, ((taux_uhcd_opt - taux_uhcd_base) / 100) * nb_passages)

# Gains
gain_avis_spe = nb_avis_spe * TARIF_AVIS_SPE
gain_ccmu2 = nb_ccmu2 * TARIF_CCMU2
gain_ccmu3 = nb_ccmu3 * TARIF_CCMU3
gain_uhcd = uhcd_suppl * TARIF_UHCD
total_gain = gain_avis_spe + gain_ccmu2 + gain_ccmu3 + gain_uhcd

# Tableau résultats
data = {
    "Levier": ["Avis spécialisés (7%)", "CCMU 2+ (3%)", "CCMU 3+ (3%)", "UHCD (supplémentaires)", "TOTAL"],
    "Volume": [int(nb_avis_spe), int(nb_ccmu2), int(nb_ccmu3), int(uhcd_suppl), "-"],
    "Gain estimé (€)": [
        round(gain_avis_spe, 2),
        round(gain_ccmu2, 2),
        round(gain_ccmu3, 2),
        round(gain_uhcd, 2),
        round(total_gain, 2)
    ]
}
results = pd.DataFrame(data)

st.subheader("🧮 Résultats estimés")
st.dataframe(results.set_index("Levier"))

# Graphique
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(results["Levier"], results["Gain estimé (€)"], color=['#4ba3c7', '#8ac6d1', '#c3e0e5', '#92b4ec', '#1d3557'])

for bar in bars:
    width = bar.get_width()
    ax.text(width + 1000, bar.get_y() + bar.get_height()/2, f"{int(width):,} €", va='center', fontsize=10)

ax.set_xlabel("Gain en euros")
ax.set_title("💶 Impact financier par levier de valorisation")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,} €'))
plt.tight_layout()
plt.grid(axis='x', linestyle='--', alpha=0.5)
st.pyplot(fig)

st.markdown("""
---
Développé par **Sclépios I.A.** pour valoriser la donnée médicale aux urgences.
""")
