# Simulateur web Streamlit de valorisation des urgences

import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64
import os
import tempfile

# Configuration de la page
st.set_page_config(page_title="Simulateur Urgences - Sclépios I.A.", layout="wide", initial_sidebar_state="expanded")

# --- HEADER ---
header_col1, header_col2, header_col3 = st.columns([1, 2, 1])
with header_col2:
    st.image("logo_complet.png", width=200)
st.markdown("<h1 style='text-align: center; margin-top: -20px;'>📊 Simulateur de Valorisation des Urgences</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- SIDEBAR PARAMÈTRES ---
st.sidebar.header("⚙️ Paramètres de simulation")
# Tarif personnalisables
tarif_expander = st.sidebar.expander("Modifier les tarifs de valorisation", expanded=False)
with tarif_expander:
    TARIF_AVIS_SPE = st.number_input("Tarif Avis Spécialisé (€)", value=24.56, step=0.01)
    TARIF_CCMU2 = st.number_input("Tarif CCMU 2+ (€)", value=14.53, step=0.01)
    TARIF_CCMU3 = st.number_input("Tarif CCMU 3+ (€)", value=19.38, step=0.01)
    TARIF_UHCD = st.number_input("Tarif UHCD (€)", value=400.0, step=1.0)
    BONUS_MONORUM = st.number_input("Majoration UHCD mono-RUM (%)", value=5.0, step=0.1) / 100.0

# Scénario
taux_baseline = st.sidebar.slider("Taux actuel d’UHCD (%)", min_value=0, max_value=50, value=5)
default_cible = min(50, taux_baseline + 6)
taux_cible = st.sidebar.slider(
    "Taux cible d’UHCD (%)", min_value=taux_baseline, max_value=50, value=default_cible
)
taux_mono_rum = st.sidebar.slider("Proportion UHCD mono-RUM (%)", min_value=0, max_value=100, value=70)
nb_passages = st.sidebar.number_input("Nombre total de passages", min_value=0, value=40000, step=100)

# --- CALCULS ---
# UHCD volumes
nb_uhcd_actuel = nb_passages * taux_baseline / 100
nb_uhcd_cible = nb_passages * taux_cible / 100
nb_uhcd_suppl = max(0, nb_uhcd_cible - nb_uhcd_actuel)
# Mono-RUM volumes
nb_mono_actuel = nb_uhcd_actuel * taux_mono_rum / 100
nb_mono_suppl = nb_uhcd_suppl * taux_mono_rum / 100

# Consultations externes hors UHCD
cs_ext = nb_passages - nb_uhcd_actuel
# Volumes avis et CCMU
nb_avis = cs_ext * 0.07
nb_ccmu2 = cs_ext * 0.03
nb_ccmu3 = cs_ext * 0.03

# Gains
gain_avis = nb_avis * TARIF_AVIS_SPE
gain_ccmu2 = nb_ccmu2 * TARIF_CCMU2
gain_ccmu3 = nb_ccmu3 * TARIF_CCMU3
# UHCD gains
gain_uhcd_base = nb_mono_suppl * TARIF_UHCD
gain_uhcd_bonus = nb_mono_suppl * TARIF_UHCD * BONUS_MONORUM
gain_uhcd = gain_uhcd_base + gain_uhcd_bonus

# Total
total_gain = gain_avis + gain_ccmu2 + gain_ccmu3 + gain_uhcd

# --- AFFICHAGE DES MÉTRIQUES ---
st.markdown("### 🔍 Indicateurs clés")
metric_cols = st.columns(4)
metric_cols[0].metric("Gains Avis spé (€)", f"{gain_avis:,.0f}")
metric_cols[1].metric("Gains CCMU2+ (€)", f"{gain_ccmu2:,.0f}")
metric_cols[2].metric("Gains CCMU3+ (€)", f"{gain_ccmu3:,.0f}")
metric_cols[3].metric("Gains UHCD (€)", f"{gain_uhcd:,.0f}")
st.markdown(f"<h3 style='text-align:center;'>💰 Total estimé : <strong>{total_gain:,.0f} €</strong></h3>", unsafe_allow_html=True)
st.markdown("---")

# --- TABLEAU DÉTAILLÉ ---
st.subheader("📋 Détail par levier")
data = pd.DataFrame({
    "Levier": ["Avis spécialisés", "CCMU 2+", "CCMU 3+", "UHCD mono-RUM base", "Majoration UHCD mono-RUM"],
    "Volume": [int(nb_avis), int(nb_ccmu2), int(nb_ccmu3), int(nb_mono_suppl), int(nb_mono_suppl)],
    "Gain (€)": [gain_avis, gain_ccmu2, gain_ccmu3, gain_uhcd_base, gain_uhcd_bonus]
})
data["Gain (€)"] = data["Gain (€)"].round(2)
st.dataframe(data.set_index("Levier"), use_container_width=True)

# --- GRAPHIQUE INTERACTIF ---
st.subheader("📈 Impact financier par levier")
fig = px.bar(
    data,
    x="Gain (€)",
    y="Levier",
    orientation="h",
    text="Gain (€)",
    color="Levier",
    color_discrete_sequence=px.colors.qualitative.Set2,
    template="plotly_white"
)
fig.update_traces(textposition='outside', texttemplate='%{text:,.0f}')
fig.update_layout(margin=dict(l=100, r=20, t=50, b=20))
st.plotly_chart(fig, use_container_width=True)

# --- EXPORT PDF ---
st.markdown("---")
center_col1, center_col2, center_col3 = st.columns([1,2,1])
with center_col2:
    if st.button("📄 Télécharger PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.image("logo_complet.png", x=(210-50)/2, w=50)
        pdf.ln(20)
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "Simulation valorisation Urgences", ln=True, align='C')
        pdf.ln(5)
        pdf.set_font("Arial", size=12)
        for _, row in data.iterrows():
            pdf.cell(0, 8, f"{row.name}: {row['Volume']} unités => {row['Gain (€)']:.2f} €", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, f"Total estimé: {total_gain:,.2f} €", ln=True, align='C')
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        pdf.output(tmp.name)
        with open(tmp.name, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
            st.markdown(f"<a href='data:application/pdf;base64,{b64}' download='simulation_urgentistes.pdf'>📥 Télécharger le rapport PDF</a>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<div style='text-align:center; font-size:10px;'>Développé par <strong>Sclépios I.A.</strong></div>", unsafe_allow_html=True)
