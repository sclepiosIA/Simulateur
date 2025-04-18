# Simulateur web Streamlit de valorisation des urgences

import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64
import os
import tempfile
import smtplib
from email.message import EmailMessage

# --- FONCTIONS UTILITAIRES ---
def generate_pdf_bytes(df, total, prospect, logo_file):
    pdf = FPDF()
    pdf.add_page()
    pdf.image(logo_file, x=(210-50)/2, w=50)
    pdf.ln(15)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Simulation valorisation Urgences", ln=True, align='C')
    if prospect:
        pdf.set_font("Arial", '', 12)
        pdf.cell(0, 8, f"Prospect : {prospect}", ln=True, align='C')
    pdf.ln(5)
    pdf.set_font("Arial", size=12)
    for _, row in df.iterrows():
        pdf.cell(0, 8, f"{row.name} : {row['Volume']} => {row['Gain (€)']:.2f} EUR", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Total : {total:,.2f} EUR", ln=True, align='C')
    return pdf.output(dest='S').encode('latin1')

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

taux_actuel = st.sidebar.slider("Taux actuel d’UHCD (%)", 0, 50, 5)
default_cible = min(50, taux_actuel + 6)
taux_cible = st.sidebar.slider("Taux cible d’UHCD (%)", taux_actuel, 50, default_cible)
taux_mono = st.sidebar.slider("Proportion UHCD mono-RUM (%)", 0, 100, 70)
passages = st.sidebar.number_input("Nombre total de passages", 0, 1000000, 40000, 100)

# --- CALCULS ---
uhcd_actuel_vol = passages * taux_actuel / 100
uhcd_cible_vol = passages * taux_cible / 100
uhcd_suppl_vol = max(0, uhcd_cible_vol - uhcd_actuel_vol)
mono_actuel_vol = uhcd_actuel_vol * taux_mono / 100
mono_suppl_vol = uhcd_suppl_vol * taux_mono / 100
consult_ext_vol = passages - uhcd_actuel_vol
avis_vol = consult_ext_vol * 0.07
ccmu2_vol = consult_ext_vol * 0.03
ccmu3_vol = consult_ext_vol * 0.03

gain_avis = avis_vol * TARIF_AVIS_SPE
gain_ccmu2 = ccmu2_vol * TARIF_CCMU2
gain_ccmu3 = ccmu3_vol * TARIF_CCMU3
# Valorisation UHCD
gain_uhcd_base = mono_suppl_vol * TARIF_UHCD
# Majoration sur initiaux + nouveaux
gain_uhcd_bonus = (mono_actuel_vol + mono_suppl_vol) * TARIF_UHCD * BONUS_MONORUM
gain_uhcd = gain_uhcd_base + gain_uhcd_bonus

total_gain = gain_avis + gain_ccmu2 + gain_ccmu3 + gain_uhcd

# --- AFFICHAGE KPIs ---
st.markdown("### 🔍 Indicateurs clés")
cols = st.columns(4)
cols[0].metric("Avis spécialisés (€)", f"{gain_avis:,.0f}")
cols[1].metric("CCMU 2+ (€)", f"{gain_ccmu2:,.0f}")
cols[2].metric("CCMU 3+ (€)", f"{gain_ccmu3:,.0f}")
cols[3].metric("UHCD (€)", f"{gain_uhcd:,.0f}")
st.markdown(
    f"<h2 style='text-align:center;'>💰 Total estimé : <strong>{total_gain:,.0f} €</strong></h2>",
    unsafe_allow_html=True
)
st.markdown("---")

# --- TABLEAU DÉTAILLÉ ---
st.subheader("📋 Détail par levier")
labels = ["Avis spécialisés", "CCMU 2+", "CCMU 3+", "UHCD mono-RUM base", "Majoration UHCD mono-RUM"]
vols = [int(avis_vol), int(ccmu2_vol), int(ccmu3_vol), int(mono_suppl_vol), int(mono_actuel_vol + mono_suppl_vol)]
gains_list = [gain_avis, gain_ccmu2, gain_ccmu3, gain_uhcd_base, gain_uhcd_bonus]
data = pd.DataFrame({"Levier": labels, "Volume": vols, "Gain (€)": gains_list})
data["Gain (€)"] = data["Gain (€)"].round(2)
st.dataframe(data.set_index("Levier"), use_container_width=True)

# --- GRAPHIQUE ---
st.subheader("📈 Impact financier par levier")
fig = px.bar(data, x="Gain (€)", y="Levier", orientation="h", text="Gain (€)", color="Levier", color_discrete_sequence=px.colors.qualitative.Set2, template="plotly_white")
fig.update_traces(textposition='outside', texttemplate='%{text:,.0f}')
fig.update_layout(margin=dict(l=100, r=20, t=50, b=20))
st.plotly_chart(fig, use_container_width=True)

# --- EXPORT PDF et EMAIL ---
st.markdown("---")
left, right = st.columns(2)
with left:
    prospect_name = st.text_input("Établissement prospect :")
    pdf_data = generate_pdf_bytes(data, total_gain, prospect_name, "logo_complet.png")
    st.download_button(
        label="📥 Télécharger PDF",
        data=pdf_data,
        file_name="simulation.pdf",
        mime="application/pdf",
    )
with right:
    prospect_email = st.text_input("Email prospect :")
    if st.button("✉️ Envoyer par email"):
        try:
            msg = EmailMessage()
            msg['Subject'] = "Rapport Simulation Urgences"
            msg['From'] = "contact@sclepios-ia.com"
            msg['To'] = prospect_email
            msg.set_content("Veuillez trouver le rapport en pièce jointe.")
            msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename='simulation.pdf')
            server = smtplib.SMTP_SSL('ssl0.ovh.net', 465)
            server.login('contact@sclepios-ia.com', '7HMsyrL5nXDRz5MB$F66')
            server.send_message(msg)
            server.quit()
            st.success(f"Email envoyé à {prospect_email}")
        except Exception as e:
            st.error(f"Échec envoi email: {e}")

# --- FOOTER ---
st.markdown("---")
st.markdown("<div style='text-align:center; color:#2E86AB;'><strong>Rémi Moreau</strong>: remi.moreau@sclepios-ia.com</div>", unsafe_allow_html=True)
st.markdown("<div style='text-align:center;'><a href='https://sclepios-ia.com' style='color:#2E86AB;'>Visitez notre site</a></div>", unsafe_allow_html=True)
