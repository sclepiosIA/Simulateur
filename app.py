# Simulateur console amélioré de valorisation des urgences (version sans Streamlit)

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
 
# Paramètres modifiables
nb_passages = 40000
cs_ext = int(nb_passages * 0.8)
taux_uhcd_global = 8  # Taux total de passages orientés vers l’UHCD (%)

# Tarification unitaire des postes
TARIF_AVIS_SPE = 24.56
TARIF_CCMU2 = 14.53
TARIF_CCMU3 = 19.38
TARIF_UHCD = 400

# Calcul des volumes estimés
nb_avis_spe = 0.07 * cs_ext
nb_ccmu2 = 0.03 * cs_ext
nb_ccmu3 = 0.03 * cs_ext
nb_uhcd = (taux_uhcd_global / 100) * nb_passages

# Calcul des gains totaux
gain_avis_spe = nb_avis_spe * TARIF_AVIS_SPE
gain_ccmu2 = nb_ccmu2 * TARIF_CCMU2
gain_ccmu3 = nb_ccmu3 * TARIF_CCMU3
gain_uhcd = nb_uhcd * TARIF_UHCD
total_gain = gain_avis_spe + gain_ccmu2 + gain_ccmu3 + gain_uhcd

# Création du tableau de résultats
data = {
    "Levier": ["Avis spécialisés (7%)", "CCMU 2+ (3%)", "CCMU 3+ (3%)", "UHCD"],
    "Volume estimé": [int(nb_avis_spe), int(nb_ccmu2), int(nb_ccmu3), int(nb_uhcd)],
    "Gain estimé (€)": [
        round(gain_avis_spe, 2),
        round(gain_ccmu2, 2),
        round(gain_ccmu3, 2),
        round(gain_uhcd, 2)
    ]
}
results = pd.DataFrame(data)

# Affichage texte
print("\n=== Résumé de la valorisation estimée ===")
print(results.to_string(index=False))
print(f"\n💰 Valorisation totale estimée : {round(total_gain, 2):,.2f} €")

# Graphique amélioré
fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.barh(results["Levier"], results["Gain estimé (€)"], color=['#4ba3c7', '#8ac6d1', '#c3e0e5', '#92b4ec'])

# Ajout des valeurs sur les barres
for bar in bars:
    width = bar.get_width()
    ax.text(width + 1000, bar.get_y() + bar.get_height() / 2, f"{int(width):,} €", va='center', fontsize=10)

ax.set_xlabel("Gain total en euros")
ax.set_title("💶 Impact financier total par levier de valorisation")
ax.xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{int(x):,} €'))
plt.tight_layout()
plt.grid(axis='x', linestyle='--', alpha=0.4)
plt.show()

print("\nDéveloppé par Sclépios I.A. pour valoriser la donnée médicale aux urgences.")
