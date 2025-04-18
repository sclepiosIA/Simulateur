# Simulateur web Streamlit de valorisation des urgences

import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Simulateur Urgences - Sclépios I.A.", layout="wide")

# --- HEADER ---
h1, h2, h3 = st.columns([1, 2, 1])
with h2:
    st.image("logo_complet.png", width=200)
st.markdown(
    "<h1 style='text-align:center;'>📊 Simulateur de Valorisation des Urgences</h1>", unsafe_allow_html=True
)
st.markdown("---")

# --- SIDEBAR PARAMÈTRES ---
st.sidebar.header("⚙️ Paramètres de simulation")
with st.sidebar.expander("Modifier les tarifs", expanded=False):
    TARIF_AVIS_SPE = st.number_input("Tarif Avis Spécialisé (€)", 0.0, 1000.0, 24.56, 0.01)
    TARIF_CCMU2 = st.number_input("Tarif CCMU 2+ (€)", 0.0, 1000.0, 14.53, 0.01)
    TARIF_CCMU3 = st.number_input("Tarif CCMU 3+ (€)", 0.0, 1000.0, 19.38, 0.01)
    TARIF_UHCD = st.number_input("Tarif UHCD (€)", 0.0, 2000.0, 400.0, 1.0)
    BONUS_MONORUM = st.number_input("Majoration UHCD mono-RUM (%)", 0.0, 100.0, 5.0, 0.1) / 100.0

baseline = st.sidebar.slider("Taux actuel d’UHCD (%)", 0, 50, 5)
default_cible = min(50, baseline + 6)
cible = st.sidebar.slider("Taux cible d’UHCD (%)", baseline, 50, default_cible)
taux_mono = st.sidebar.slider("Proportion UHCD mono-RUM (%)", 0, 100, 70)
passages = st.sidebar.number_input("Nombre total de passages", 0, 1000000, 40000, 100)

# --- CALCULS ---
uhcd_base = passages * baseline / 100
uhcd_target = passages * cible / 100
uhcd_diff = max(0, uhcd_target - uhcd_base)
mono_base = uhcd_base * taux_mono / 100
mono_diff = uhcd_diff * taux_mono / 100
consult_ext = passages - uhcd_base
avis = consult_ext * 0.07
ccmu2 = consult_ext * 0.03
ccmu3 = consult_ext * 0.03

gain_avis = avis * TARIF_AVIS_SPE
gain_ccmu2 = ccmu2 * TARIF_CCMU2
gain_ccmu3 = ccmu3 * TARIF_CCMU3
gain_uhcd_base = mono_diff * TARIF_UHCD
gain_uhcd_bonus = (mono_base + mono_diff) * TARIF_UHCD * BONUS_MONORUM
gain_uhcd = gain_uhcd_base + gain_uhcd_bonus
total_gain = gain_avis + gain_ccmu2 + gain_ccmu3 + gain_uhcd

# --- KPIs ---
st.markdown("### 🔍 Indicateurs clés")
cols = st.columns(4)
cols[0].metric("Avis spécialisés (€)", f"{gain_avis:,.0f}")
cols[1].metric("CCMU 2+ (€)", f"{gain_ccmu2:,.0f}")
cols[2].metric("CCMU 3+ (€)", f"{gain_ccmu3:,.0f}")
cols[3].metric("UHCD (€)", f"{gain_uhcd:,.0f}")
st.markdown(f"<h2 style='text-align:center;'>💰 Total estimé : <strong>{total_gain:,.0f} €</strong></h2>", unsafe_allow_html=True)
st.markdown("---")

# --- DÉTAIL ---
st.subheader("📋 Détail par levier")
labels = ["Avis spécialisés", "CCMU 2+", "CCMU 3+", "UHCD mono-RUM base", "Majoration UHCD mono-RUM"]
vols = [int(avis), int(ccmu2), int(ccmu3), int(mono_diff), int(mono_base + mono_diff)]
gains_list = [gain_avis, gain_ccmu2, gain_ccmu3, gain_uhcd_base, gain_uhcd_bonus]
data = pd.DataFrame({"Levier": labels, "Volume": vols, "Gain (€)": gains_list})
data["Gain (€)" ] = data["Gain (€)"].round(2)
st.dataframe(data.set_index("Levier"), use_container_width=True)

# --- GRAPHIQUE ---
st.subheader("📈 Impact financier par levier")
fig = px.bar(data, x="Gain (€)", y="Levier", orientation="h", text="Gain (€)", color="Levier", color_discrete_sequence=px.colors.qualitative.Set2, template="plotly_white")
fig.update_traces(textposition='outside', texttemplate='%{text:,.0f}')
fig.update_layout(margin=dict(l=100, r=20, t=50, b=20))
st.plotly_chart(fig, use_container_width=True)

# --- FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align:center;'><strong>Rémi Moreau</strong>: remi.moreau@sclepios-ia.com</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'><a href='https://sclepios-ia.com' style='color:#2E86AB;'>Visitez notre site</a></div>", unsafe_allow_html=True)
