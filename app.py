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
st.markdown(
    "<h1 style='text-align: center; margin-top: -20px;'>📊 Simulateur de Valorisation des Urgences</h1>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- SIDEBAR PARAMÈTRES ---
st.sidebar.header("⚙️ Paramètres de simulation")
# Tarifs personnalisables
tarif_expander = st.sidebar.expander("Modifier les tarifs de valorisation", expanded=False)
with tarif_expander:
    TARIF_AVIS_SPE = st.number_input("Tarif Avis Spécialisé (€)", value=24.56, step=0.01)
    TARIF_CCMU2 = st.number_input("Tarif CCMU 2+ (€)", value=14.53, step=0.01)
    TARIF_CCMU3 = st.number_input("Tarif CCMU 3+ (€)", value=19.38, step=0.01)
    TARIF_UHCD = st.number_input("Tarif UHCD (€)", value=400.0, step=1.0)
    BONUS_MONORUM = st.number_input("Majoration UHCD mono-RUM (%)", value=5.0, step=0.1) / 100.0

# Scénario de base et cible
baseline = st.sidebar.slider("Taux actuel d’UHCD (%)", 0, 50, 5)
default_cible = min(50, baseline + 6)
cible = st.sidebar.slider("Taux cible d’UHCD (%)", baseline, 50, default_cible)
taux_mono = st.sidebar.slider("Proportion UHCD mono-RUM (%)", 0, 100, 70)
passages = st.sidebar.number_input("Nombre total de passages", 0, 1000000, 40000, step=100)

# --- CALCULS ---
# Volumes UHCD
uhcd_base_vol = passages * baseline / 100
uhcd_cible_vol = passages * cible / 100
uhcd_suppl_vol = max(0, uhcd_cible_vol - uhcd_base_vol)
# Volumes Mono-RUM
mono_base_vol = uhcd_base_vol * taux_mono / 100
mono_suppl_vol = uhcd_suppl_vol * taux_mono / 100

# Consultations externes hors UHCD
consult_ext = passages - uhcd_base_vol
# Autres volumes
avis_vol = consult_ext * 0.07
ccmu2_vol = consult_ext * 0.03
ccmu3_vol = consult_ext * 0.03

# Gains par levier
gain_avis = avis_vol * TARIF_AVIS_SPE
gain_ccmu2 = ccmu2_vol * TARIF_CCMU2
gain_ccmu3 = ccmu3_vol * TARIF_CCMU3
# Gains UHCD
gain_uhcd_base = mono_suppl_vol * TARIF_UHCD
# Majoration sur initiaux + suppléments
gain_uhcd_bonus = (mono_base_vol + mono_suppl_vol) * TARIF_UHCD * BONUS_MONORUM
gain_uhcd = gain_uhcd_base + gain_uhcd_bonus

# Gain total
total_gain = gain_avis + gain_ccmu2 + gain_ccmu3 + gain_uhcd

# --- AFFICHAGE METRICS ---
st.markdown("### 🔍 Indicateurs clés")
kpis = st.columns(4)
kpis[0].metric("Avis spé (€)", f"{gain_avis:,.0f}")
kpis[1].metric("CCMU2+ (€)", f"{gain_ccmu2:,.0f}")
kpis[2].metric("CCMU3+ (€)", f"{gain_ccmu3:,.0f}")
kpis[3].metric("UHCD (€)", f"{gain_uhcd:,.0f}")
st.markdown(
    f"<h3 style='text-align:center;'>💰 Total estimé : <strong>{total_gain:,.0f} €</strong></h3>",
    unsafe_allow_html=True,
)
st.markdown("---")

# --- TABLEAU DÉTAILLÉ ---
st.subheader("📋 Détail par levier")
labels = ["Avis spécialisés", "CCMU 2+", "CCMU 3+", "UHCD mono-RUM base", "Majoration UHCD mono-RUM"]
volumes = [int(avis_vol), int(ccmu2_vol), int(ccmu3_vol), int(mono_suppl_vol), int(mono_base_vol + mono_suppl_vol)]
gains = [gain_avis, gain_ccmu2, gain_ccmu3, gain_uhcd_base, gain_uhcd_bonus]
data = pd.DataFrame({"Levier": labels, "Volume": volumes, "Gain (€)": gains})
data["Gain (€)"] = data["Gain (€)"].round(2)
st.dataframe(data.set_index("Levier"), use_container_width=True)

# --- GRAPHIQUE ---
st.subheader("📈 Impact financier par levier")
fig = px.bar(
    data, x="Gain (€)", y="Levier", orientation="h", text="Gain (€)",
    color="Levier", color_discrete_sequence=px.colors.qualitative.Set2, template="plotly_white"
)
fig.update_traces(textposition='outside', texttemplate='%{text:,.0f}')
fig.update_layout(margin=dict(l=100, r=20, t=50, b=20))
st.plotly_chart(fig, use_container_width=True)

# --- EXPORT PDF ---
st.markdown("---")
st.markdown("### 📄 Génération du rapport PDF")

# Formulaire de saisie des infos prospect pour PDF
with st.form("pdf_form"):
    prospect = st.text_input("Établissement prospect :")
    email = st.text_input("Email prospect :")
    submitted = st.form_submit_button("Générer PDF")

if submitted:
    # Création du PDF en mémoire
    pdf = FPDF()
    pdf.add_page()
    pdf.image("logo_complet.png", x=(210-50)/2, w=50)
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Simulation valorisation Urgences", ln=True, align='C')
    if prospect:
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Prospect : {prospect}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    for _, row in data.iterrows():
        pdf.cell(0, 8, f"{row.name} : {row['Volume']} => {row['Gain (€)']:.2f} EUR", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Total estimé : {total_gain:,.2f} EUR", ln=True, align='C')
    # Export du PDF
    pdf_bytes = pdf.output(dest='S').encode('latin1')
    st.download_button(
        label="📥 Télécharger le PDF",
        data=pdf_bytes,
        file_name="simulation.pdf",
        mime="application/pdf"
    )
    st.success("PDF généré avec succès !")

# Footer
st.markdown("---")
st.markdown("<div style='text-align:center; color:#2E86AB; font-weight:bold;'>Rémi Moreau : remi.moreau@sclepios-ia.com</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'><a href='https://sclepios-ia.com' style='color:#2E86AB;'>Visitez notre site</a></div>", unsafe_allow_html=True)
