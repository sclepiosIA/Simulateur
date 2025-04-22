"""
Simulateur de Valorisation des Urgences – Sclépios I.A.
Version multi‑onglet avec analyse UHCD mensuelle & projection annuelle
Pour exécuter :  streamlit run simulateur_urgences.py
Auteur : Rémi Moreau – remi.moreau@sclepios-ia.com
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# CONFIGURATION GÉNÉRALE
# -------------------------------------------------
st.set_page_config(page_title="Simulateur Urgences – Sclépios I.A.", layout="wide")

# -------------------------------------------------
# PARAMÈTRES COMMUNS (SIDEBAR)
# -------------------------------------------------
st.sidebar.header("⚙️ Paramètres de simulation")
with st.sidebar.expander("Modifier les tarifs", expanded=False):
    TARIF_AVIS_SPE = st.number_input("Tarif Avis Spécialisé (€)", 0.0, 1000.0, 24.56, 0.01)
    TARIF_CCMU2 = st.number_input("Tarif CCMU 2+ (€)", 0.0, 1000.0, 14.53, 0.01)
    TARIF_CCMU3 = st.number_input("Tarif CCMU 3+ (€)", 0.0, 1000.0, 19.38, 0.01)
    TARIF_UHCD = st.number_input("Tarif UHCD (€)", 0.0, 2000.0, 400.0, 1.0)
    BONUS_MONORUM = st.number_input("Majoration UHCD mono‑RUM (%)", 0.0, 100.0, 5.0, 0.1) / 100.0

baseline = st.sidebar.slider("Taux actuel d’UHCD (%)", 0, 50, 5)
default_cible = min(50, baseline + 6)
cible = st.sidebar.slider("Taux cible d’UHCD (%)", baseline, 50, default_cible)
taux_mono = st.sidebar.slider("Proportion UHCD mono‑RUM (%)", 0, 100, 70)
passages = st.sidebar.number_input("Nombre total de passages", 0, 1_000_000, 40_000, 100)

# -------------------------------------------------
# ONGLET 1 : SIMULATION HISTORIQUE (Code d’origine)
# -------------------------------------------------
tab_simulation, tab_uhcd = st.tabs(["Simulation", "UHCD Analytics"])

with tab_simulation:
    # --- HEADER ---
    h1, h2, h3 = st.columns([1, 2, 1])
    with h2:
        st.image("logo_complet.png", width=200)
    st.markdown(
        "<h1 style='text-align:center;'>📊 Simulateur de Valorisation des Urgences</h1>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # --- CALCULS D’ORIGINE ---
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
    kpi_cols = st.columns(4)
    kpi_cols[0].metric("Avis spécialisés (€)", f"{gain_avis:,.0f}")
    kpi_cols[1].metric("CCMU 2+ (€)", f"{gain_ccmu2:,.0f}")
    kpi_cols[2].metric("CCMU 3+ (€)", f"{gain_ccmu3:,.0f}")
    kpi_cols[3].metric("UHCD (€)", f"{gain_uhcd:,.0f}")
    st.markdown(
        f"<h2 style='text-align:center;'>💰 Total estimé : <strong>{total_gain:,.0f} €</strong></h2>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # --- DÉTAIL ---
    st.subheader("📋 Détail par levier")
    labels = [
        "Avis spécialisés",
        "CCMU 2+",
        "CCMU 3+",
        "UHCD mono‑RUM base",
        "Majoration UHCD mono‑RUM",
    ]
    vols = [int(avis), int(ccmu2), int(ccmu3), int(mono_diff), int(mono_base + mono_diff)]
    gains_list = [gain_avis, gain_ccmu2, gain_ccmu3, gain_uhcd_base, gain_uhcd_bonus]
    data = pd.DataFrame({"Levier": labels, "Volume": vols, "Gain (€)": gains_list})
    data["Gain (€)"] = data["Gain (€)"].round(2)
    st.dataframe(data.set_index("Levier"), use_container_width=True)

    # --- GRAPHIQUE ---
    st.subheader("📈 Impact financier par levier")
    fig = px.bar(
        data,
        x="Gain (€)",
        y="Levier",
        orientation="h",
        text="Gain (€)",
        color="Levier",
        color_discrete_sequence=px.colors.qualitative.Set2,
        template="plotly_white",
    )
    fig.update_traces(textposition="outside", texttemplate="%{text:,.0f}")
    fig.update_layout(margin=dict(l=100, r=20, t=50, b=20))
    st.plotly_chart(fig, use_container_width=True)

    # --- FOOTER ---
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;'><strong>Rémi Moreau</strong>: "
        "remi.moreau@sclepios-ia.com</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align:center;'><a href='https://sclepios-ia.com' "
        "style='color:#2E86AB;'>Visitez notre site</a></div>",
        unsafe_allow_html=True,
    )

# -------------------------------------------------
# ONGLET 2 : UHCD ANALYTICS (NOUVELLE FONCTIONNALITÉ)
# -------------------------------------------------
with tab_uhcd:
    st.header("📊 Analyse UHCD mensuelle & projection annuelle")
    st.markdown("---")

    # -------- Saisie des données mensuelles --------
    st.markdown("### 📥 Données mensuelles")
    col_a, col_b, col_c = st.columns(3)
    uhcd_mois = col_a.number_input("UHCD valorisées (mois)", 0, 100_000, 100)
    consult_mois = col_b.number_input("Consultations externes (mois)", 0, 100_000, 1_000)
    uhcd_sclepios_mois = col_c.number_input("UHCD supplémentaires Sclépios I.A. (mois)", 0, 100_000, 20)

    total_mois = uhcd_mois + consult_mois

    if total_mois == 0:
        st.warning("Veuillez saisir un nombre de passages > 0 pour afficher les résultats.")
    else:
        # -------- Pourcentages mensuels --------
        pct_uhcd = uhcd_mois / total_mois * 100
        pct_uhcd_plus = (uhcd_mois + uhcd_sclepios_mois) / total_mois * 100

        st.markdown("### 📌 Indicateurs mensuels")
        m1, m2 = st.columns(2)
        m1.metric("Taux UHCD valorisées", f"{pct_uhcd:.2f} %")
        m2.metric("Taux UHCD après Sclépios", f"{pct_uhcd_plus:.2f} %")

        # -------- Projection annuelle --------
        st.markdown("### 📅 Projection annuelle (×12)")
        uhcd_an = uhcd_mois * 12
        uhcd_sclepios_an = uhcd_sclepios_mois * 12
        total_passages_proj = st.number_input(
            "Nombre total de passages projeté sur l'année",
            value=int(passages),
            min_value=0,
            step=100,
        )

        uhcd_proj = total_passages_proj * pct_uhcd / 100
        uhcd_plus_proj = total_passages_proj * pct_uhcd_plus / 100

        p1, p2, p3 = st.columns(3)
        p1.metric("UHCD/an (actuel)", f"{uhcd_an:,.0f}")
        p2.metric("UHCD/an projeté", f"{uhcd_proj:,.0f}")
        p3.metric("UHCD/an après Sclépios", f"{uhcd_plus_proj:,.0f}")

        # -------- ROI / Recettes --------
        st.markdown("### 💶 ROI UHCD")
        revenue_base = uhcd_proj * TARIF_UHCD
        revenue_plus = uhcd_plus_proj * TARIF_UHCD
        revenue_gain = revenue_plus - revenue_base
        roi_pct = (revenue_gain / revenue_base * 100) if revenue_base else 0

        r1, r2, r3 = st.columns(3)
        r1.metric("Recette UHCD actuelle (€)", f"{revenue_base:,.0f}")
        r2.metric("Recette UHCD après Sclépios (€)", f"{revenue_plus:,.0f}")
        r3.metric("ROI sur UHCD (%)", f"{roi_pct:.1f} %")

        # -------- Graphe de comparaison --------
        rev_df = pd.DataFrame(
            {
                "Scenario": ["Actuel", "Après Sclépios"],
                "Recette (€)": [revenue_base, revenue_plus],
            }
        )
        fig2 = px.bar(
            rev_df,
            x="Scenario",
            y="Recette (€)",
            text="Recette (€)",
            template="plotly_white",
        )
        fig2.update_traces(texttemplate="%{text:,.0f}")
        fig2.update_layout(margin=dict(l=40, r=40, t=60, b=40))
        st.plotly_chart(fig2, use_container_width=True)

    # FOOTER SPÉCIFIQUE ONGLET 2
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;'><a href='https://sclepios-ia.com' style='color:#2E86AB;'>https://sclepios-ia.com</a></div>",
        unsafe_allow_html=True,
    )
