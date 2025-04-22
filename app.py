"""
Simulateur de Valorisation des Urgences – Sclépios I.A.
Version multi‑onglet avec analytics UHCD & projections interactives
Exécutez : streamlit run simulateur_urgences.py
Auteur : Rémi Moreau – remi.moreau@sclepios-ia.com
Mise à jour : 22 avril 2025
• Migration vers st.query_params (fin de l’API expérimentale)
• Volumes toujours entiers (arrondi commercial)
• Calculs ROI détaillés après projection annuelle + option projection passages
"""

import math
import streamlit as st
import pandas as pd
import plotly.express as px

# -------------------------------------------------
# CONFIGURATION GÉNÉRALE
# -------------------------------------------------
st.set_page_config(page_title="Simulateur Urgences – Sclépios I.A.", layout="wide")

# -------------------------------------------------
# FONCTIONS UTILITAIRES
# -------------------------------------------------

def qp_int(qp: dict, key: str, default: int) -> int:
    """Récupère un entier depuis les query params."""
    try:
        return int(qp.get(key, default))
    except Exception:
        return default


def revenues(uhcd: int | float, consult: int | float, tarifs: dict) -> tuple:
    """Calcule les différentes composantes de recettes."""
    avis = consult * 0.07
    ccmu2 = consult * 0.03
    ccmu3 = consult * 0.03
    rev_uhcd = uhcd * tarifs["UHCD"]
    rev_avis = avis * tarifs["AVIS"]
    rev_ccmu2 = ccmu2 * tarifs["CCMU2"]
    rev_ccmu3 = ccmu3 * tarifs["CCMU3"]
    rev_total = rev_uhcd + rev_avis + rev_ccmu2 + rev_ccmu3
    return (
        rev_total,
        rev_uhcd,
        rev_avis,
        rev_ccmu2,
        rev_ccmu3,
        avis,
        ccmu2,
        ccmu3,
    )


def to_int(value: float | int) -> int:
    """Arrondi commercial puis convertit en int (volumes)."""
    return int(round(value))


# -------------------------------------------------
# PARAMÈTRES COMMUNS (SIDEBAR)
# -------------------------------------------------
st.sidebar.header("⚙️ Paramètres de simulation")
with st.sidebar.expander("Modifier les tarifs", expanded=False):
    TARIF_AVIS_SPE = st.number_input("Tarif Avis Spécialisé (€)", 0.0, 1000.0, 24.56, 0.01)
    TARIF_CCMU2 = st.number_input("Tarif CCMU 2+ (€)", 0.0, 1000.0, 14.53, 0.01)
    TARIF_CCMU3 = st.number_input("Tarif CCMU 3+ (€)", 0.0, 1000.0, 19.38, 0.01)
    TARIF_UHCD = st.number_input("Tarif UHCD (€)", 0.0, 2000.0, 400.0, 1.0)
    BONUS_MONORUM = (
        st.number_input("Majoration UHCD mono‑RUM (%)", 0.0, 100.0, 5.0, 0.1) / 100.0
    )

tarifs = {
    "AVIS": TARIF_AVIS_SPE,
    "CCMU2": TARIF_CCMU2,
    "CCMU3": TARIF_CCMU3,
    "UHCD": TARIF_UHCD,
}

baseline = st.sidebar.slider("Taux actuel d’UHCD (%)", 0, 50, 5)
default_cible = min(50, baseline + 6)
cible = st.sidebar.slider("Taux cible d’UHCD (%)", baseline, 50, default_cible)
taux_mono = st.sidebar.slider("Proportion UHCD mono‑RUM (%)", 0, 100, 70)
passages = st.sidebar.number_input(
    "Nombre total de passages",
    min_value=0,
    max_value=1_000_000,
    value=40_000,
    step=100,
    format="%d",
)

# -------------------------------------------------
# ONGLET 1 : SIMULATION HISTORIQUE
# -------------------------------------------------
tab_simulation, tab_uhcd = st.tabs(["Simulation", "UHCD Analytics"])

with tab_simulation:
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

    gain_avis = avis * tarifs["AVIS"]
    gain_ccmu2 = ccmu2 * tarifs["CCMU2"]
    gain_ccmu3 = ccmu3 * tarifs["CCMU3"]
    gain_uhcd_base = mono_diff * tarifs["UHCD"]
    gain_uhcd_bonus = (mono_base + mono_diff) * tarifs["UHCD"] * BONUS_MONORUM
    gain_uhcd = gain_uhcd_base + gain_uhcd_bonus
    total_gain = gain_avis + gain_ccmu2 + gain_ccmu3 + gain_uhcd

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
    with st.expander("Détail par levier"):
        labels = [
            "Avis spécialisés",
            "CCMU 2+",
            "CCMU 3+",
            "UHCD mono‑RUM base",
            "Majoration UHCD mono‑RUM",
        ]
        vols = [
            to_int(avis),
            to_int(ccmu2),
            to_int(ccmu3),
            to_int(mono_diff),
            to_int(mono_base + mono_diff),
        ]
        gains_list = [
            gain_avis,
            gain_ccmu2,
            gain_ccmu3,
            gain_uhcd_base,
            gain_uhcd_bonus,
        ]
        data = pd.DataFrame({"Levier": labels, "Volume": vols, "Gain (€)": gains_list})
        data["Gain (€)"] = data["Gain (€)"].round(2)
        st.dataframe(data.set_index("Levier"), use_container_width=True)

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
        st.plotly_chart(fig, use_container_width=True)

    # --- FOOTER ---
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;'><strong>Rémi Moreau</strong>: remi.moreau@sclepios-ia.com</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div style='text-align:center;'>https://sclepios-ia.com</div>",
        unsafe_allow_html=True,
    )

# -------------------------------------------------
# ONGLET 2 : UHCD ANALYTICS
# -------------------------------------------------
with tab_uhcd:
    st.image("logo_complet.png", width=160)
    st.header("📊 Analyse UHCD mensuelle & projections interactives")
    st.markdown("---")

    # ---------------- Query params ----------------
    qp = st.query_params.to_dict()

    # -------- Saisie des données mensuelles --------
    st.markdown("### 📥 Données mensuelles")
    col_a, col_b, col_c = st.columns(3)
    uhcd_mois = col_a.number_input(
        "UHCD valorisées (mois)",
        min_value=0,
        max_value=100_000,
        value=qp_int(qp, "uhcd", 100),
        key="uhcd_mois",
        format="%d",
    )
    consult_mois = col_b.number_input(
        "Consultations externes (mois)",
        min_value=0,
        max_value=100_000,
        value=qp_int(qp, "consult", 1_000),
        key="consult_mois",
        format="%d",
    )
    uhcd_sclepios_mois = col_c.number_input(
        "UHCD supplémentaires Sclépios I.A. (mois)",
        min_value=0,
        max_value=100_000,
        value=qp_int(qp, "plus", 20),
        key="uhcd_plus_mois",
        format="%d",
    )

    # -------- Lien partageable --------
    if st.button("🔗 Générer un lien partageable avec ces valeurs"):
        st.query_params.clear()
        st.query_params.from_dict(
            {
                "uhcd": uhcd_mois,
                "consult": consult_mois,
                "plus": uhcd_sclepios_mois,
            }
        )
        st.success("Lien mis à jour ! Copiez l'URL de votre navigateur pour la partager à votre client.")

    total_mois = uhcd_mois + consult_mois

    if total_mois == 0:
        st.warning("Veuillez saisir un nombre de passages > 0 pour afficher les résultats.")
        st.stop()

    # -------- Pourcentages mensuels --------
    pct_uhcd = uhcd_mois / total_mois * 100
    pct_uhcd_plus = (uhcd_mois + uhcd_sclepios_mois) / total_mois * 100

    st.markdown("### 📌 Indicateurs mensuels")
    m1, m2 = st.columns(2)
    m1.metric("Taux UHCD valorisées", f"{pct_uhcd:.2f} %")
    m2.metric("Taux UHCD après Sclépios", f"{pct_uhcd_plus:.2f} %")

    # -------- Projection annuelle simple (×12) --------
    st.markdown("### 📅 Projection annuelle (×12)")
    uhcd_an = to_int(uhcd_mois * 12)
    uhcd_sclepios_an = to_int(uhcd_sclepios_mois * 12)
    consult_an = to_int(consult_mois * 12)
    total_passages_init = to_int(total_mois * 12)

    p1, p2, p3 = st.columns(3)
    p1.metric("UHCD/an (actuel)", f"{uhcd_an:,.0f}")
    p2.metric("UHCD/an après Sclépios", f"{uhcd_an + uhcd_sclepios_an:,.0f}")
    p3.metric("Passages/an (base)", f"{total_passages_init:,.0f}")

    # -------- ROI annuel détaillé --------
    (rev_an_base_total, rev_an_base_uhcd, rev_an_base_avis, rev_an_base_ccmu2, rev_an_base_ccmu3, avis_an_base, ccmu2_an_base, ccmu3_an_base,) = revenues(uhcd_an, consult_an, tarifs)

    consult_an_plus = max(0, consult_an - uhcd_sclepios_an)  # évite négatif
    (rev_an_plus_total, rev_an_plus_uhcd, rev_an_plus_avis, rev_an_plus_ccmu2, rev_an_plus_ccmu3, avis_an_plus, ccmu2_an_plus, ccmu3_an_plus,) = revenues(uhcd_an + uhcd_sclepios_an, consult_an_plus, tarifs)

    roi_an_uhcd_pct = (rev_an_plus_uhcd - rev_an_base_uhcd) / rev_an_base_uhcd * 100 if rev_an_base_uhcd else 0
    roi_an_total_pct = (rev_an_plus_total - rev_an_base_total) / rev_an_base_total * 100 if rev_an_base_total else 0

    st.markdown("#### 💶 ROI annuel")
    a1, a2, a3 = st.columns(3)
    a1.metric("Recette UHCD actuelle (€)", f"{rev_an_base_uhcd:,.0f}")
    a2.metric("Recette UHCD après Sclépios (€)", f"{rev_an_plus_uhcd:,.0f}")
    a3.metric("ROI UHCD (%)", f"{roi_an_uhcd_pct:.1f} %")

    a4, a5 = st.columns(2)
    a4.metric("Recette totale actuelle (€)", f"{rev_an_base_total:,.0f}")
    a5.metric("ROI total (%)", f"{roi_an_total_pct:.1f} %")

    with st.expander("Détail par levier – projection annuelle"):
        detail_an_df = pd.DataFrame(
            {
                "Levier": ["Avis spécialisés", "CCMU 2+", "CCMU 3+", "UHCD"],
                "Volume Baseline": [avis_an_base, ccmu2_an_base, ccmu3_an_base, uhcd_an],
                "Gain Baseline (€)": [
                    rev_an_base_avis,
                    rev_an_base_ccmu2,
                    rev_an_base_ccmu3,
                    rev_an_base_uhcd,
                ],
                "Volume Sclépios": [
                    avis_an_plus,
                    ccmu2_an_plus,
                    ccmu3_an_plus,
                    uhcd_an + uhcd_sclepios_an,
                ],
                "Gain Sclépios (€)": [
                    rev_an_plus_avis,
                    rev_an_plus_ccmu2,
                    rev_an_plus_ccmu3,
                    rev_an_plus_uhcd,
                ],
            }
        )
        detail_an_df["ROI (%)"] = (
            (detail_an_df["Gain Sclépios (€)"] - detail_an_df["Gain Baseline (€)"]) / detail_an_df["Gain Baseline (€)"] * 100
        ).replace([math.inf, -math.inf], 0).round(1)
        cols_num = ["Gain Baseline (€)", "Gain Sclépios (€)"]
        detail_an_df[cols_num] = detail_an_df[cols_num].round(2)
        st.dataframe(detail_an_df.set_index("Levier"), use_container_width=True)

    # -------- Projection sur volume de passages --------
    st.markdown("### 🔄 Projection sur un volume annuel de passages")
    new_total_passages = st.number_input(
        "Nombre total de passages projeté sur l'année",
        min_value=1,
        step=100,
        value=total_passages_init,
        key="total_proj",
        format="%d",
    )

    if new_total_passages != total_passages_init:
        scale = new_total_passages / total_passages_init

        uhcd_proj = to_int(uhcd_an * scale)
        uhcd_plus_proj = to_int((uhcd_an + uhcd_sclepios_an) * scale)

        consult_proj_base = to_int(consult_an * scale)
        consult_proj_plus = max(0, consult_proj_base - uhcd_sclepios_an * scale)

        # -------- Revenus & ROI --------
        (
            rev_base_total,
            rev_base_uhcd,
            rev_base_avis,
            rev_base_ccmu2,
            rev_base_ccmu3,
            avis_base,
            ccmu2_base,
            ccmu3_base,
        ) = revenues(uhcd_proj, consult_proj_base, tarifs)

        (
            rev_plus_total,
            rev_plus_uhcd,
            rev_plus_avis,
            rev_plus_ccmu2,
            rev_plus_ccmu3,
            avis_plus,
            ccmu2_plus,
            ccmu3_plus,
        ) = revenues(uhcd_plus_proj, consult_proj_plus, tarifs)

        roi_uhcd_pct = (
            (rev_plus_uhcd - rev_base_uhcd) / rev_base_uhcd * 100 if rev_base_uhcd else 0
        )
        roi_total_pct = (
            (rev_plus_total - rev_base_total) / rev_base_total * 100 if rev_base_total else 0
        )

        st.markdown("### 💶 ROI (projection passages)")
        r1, r2, r3 = st.columns(3)
        r1.metric("Recette UHCD actuelle (€)", f"{rev_base_uhcd:,.0f}")
        r2.metric("Recette UHCD après Sclépios (€)", f"{rev_plus_uhcd:,.0f}")
        r3.metric("ROI UHCD (%)", f"{roi_uhcd_pct:.1f} %")

        r4, r5 = st.columns(2)
        r4.metric("Recette totale actuelle (€)", f"{rev_base_total:,.0f}")
        r5.metric("ROI total après Sclépios (%)", f"{roi_total_pct:.1f} %")

        # -------- Visualisation détaillée --------
        st.markdown("### 📋 Détail par levier (projection passages)")
        detail_df = pd.DataFrame(
            {
                "Levier": ["Avis spécialisés", "CCMU 2+", "CCMU 3+", "UHCD"],
                "Volume Baseline": [avis_base, ccmu2_base, ccmu3_base, uhcd_proj],
                "Gain Baseline (€)": [
                    rev_base_avis,
                    rev_base_ccmu2,
                    rev_base_ccmu3,
                    rev_base_uhcd,
                ],
                "Volume Sclépios": [avis_plus, ccmu2_plus, ccmu3_plus, uhcd_plus_proj],
                "Gain Sclépios (€)": [
                    rev_plus_avis,
                    rev_plus_ccmu2,
                    rev_plus_ccmu3,
                    rev_plus_uhcd,
                ],
            }
        )
        detail_df["ROI (%)"] = (
            (detail_df["Gain Sclépios (€)"] - detail_df["Gain Baseline (€)"]) / detail_df["Gain Baseline (€)"] * 100
        ).replace([math.inf, -math.inf], 0).round(1)
        cols_num = ["Gain Baseline (€)", "Gain Sclépios (€)"]
        detail_df[cols_num] = detail_df[cols_num].round(2)
        st.dataframe(detail_df.set_index("Levier"), use_container_width=True)

        # -------- Graphe comparatif --------
        bar_df = detail_df.melt(
            id_vars="Levier",
            value_vars=["Gain Baseline (€)", "Gain Sclépios (€)"],
            var_name="Scenario",
            value_name="Gain (€)",
        )
        fig2 = px.bar(
            bar_df,
            x="Gain (€)",
            y="Levier",
            color="Scenario",
            orientation="h",
            template="plotly_white",
            text="Gain (€)",
        )
        fig2.update_traces(texttemplate="%{text:,.0f}")
        fig2.update_layout(margin=dict(l=60, r=60, t=40, b=40))
        st.plotly_chart(fig2, use_container_width=True)

    # FOOTER SPÉCIFIQUE ONGLET 2
    st.markdown("---")
    st.markdown("<div style='text-align:center;'>https://sclepios-ia.com</div>", unsafe_allow_html=True)
