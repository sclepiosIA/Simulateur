# Simulateur console de valorisation des urgences avec interface interactive (sans Streamlit)

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick

# Paramètres modifiables
nb_passages = 40000
TARIF_AVIS_SPE = 24.56
TARIF_CCMU2 = 14.53
TARIF_CCMU3 = 19.38
TARIF_UHCD = 400
BONUS_MONORUM = 0.05 * TARIF_UHCD

# Valeurs par défaut utilisateur
taux_uhcd_actuel = 5
taux_uhcd_cible = 8
taux_mono_rum = 70

# Calculs dérivés
nb_uhcd_actuel = (taux_uhcd_actuel / 100) * nb_passages
nb_uhcd_cible = (taux_uhcd_cible / 100) * nb_passages
nb_uhcd_nouveaux = nb_uhcd_cible - nb_uhcd_actuel

nb_uhcd_mono_rum_actuel = nb_uhcd_actuel * (taux_mono_rum / 100)
nb_uhcd_mono_rum_nouveaux = nb_uhcd_nouveaux * (taux_mono_rum / 100)
nb_uhcd_mono_rum_total = nb_uhcd_mono_rum_actuel + nb_uhcd_mono_rum_nouveaux

# Déduire le nombre de consultations externes (hors UHCD mono-RUM)
cs_ext = nb_passages - nb_uhcd_actuel

# Volumes estimés
nb_avis_spe = 0.07 * cs_ext
nb_ccmu2 = 0.03 * cs_ext
nb_ccmu3 = 0.03 * cs_ext

# Gains standards
gain_avis_spe = nb_avis_spe * TARIF_AVIS_SPE
gain_ccmu2 = nb_ccmu2 * TARIF_CCMU2
gain_ccmu3 = nb_ccmu3 * TARIF_CCMU3

# Détail UHCD : distinguer gain par valorisation de base vs gain issu du bonus
uhcd_valorisation_base = (nb_uhcd_mono_rum_actuel + nb_uhcd_mono_rum_nouveaux) * TARIF_UHCD
uhcd_valorisation_bonus = (nb_uhcd_mono_rum_actuel + nb_uhcd_mono_rum_nouveaux) * BONUS_MONORUM

gain_uhcd_total = uhcd_valorisation_base + uhcd_valorisation_bonus
total_gain = gain_avis_spe + gain_ccmu2 + gain_ccmu3 + gain_uhcd_total

# Affichage tableau
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

print("\n=== Résumé des estimations de valorisation ===")
print(data.to_string(index=False))
print(f"\n💰 Valorisation totale estimée : {total_gain:,.2f} €")

# Graphique matplotlib
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
plt.show()

print("\nDéveloppé par Sclépios I.A. pour révéler la valeur cachée des données médicales.")
