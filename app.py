# (continued)
                ],
                "Volume Sclépios": [
                    avis_ann_plus,
                    ccmu2_ann_plus,
                    ccmu3_ann_plus,
                    uhcd_an + uhcd_sclepios_an,
                ],
                "Gain Sclépios (€)": [
                    rev_ann_plus_avis,
                    rev_ann_plus_ccmu2,
                    rev_ann_plus_ccmu3,
                    rev_ann_plus_uhcd,
                ],
            }
        )
        detail_ann["Gain Baseline (€)"] = detail_ann["Gain Baseline (€)"].round(2)
        detail_ann["Gain Sclépios (€)"] = detail_ann["Gain Sclépios (€)"].round(2)
        st.dataframe(detail_ann.set_index("Levier"), use_container_width=True)

    # ========= PROJECTION SUR VOLUME PERSONNALISÉ =========
    st.markdown("### 🔄 Projection sur un volume annuel de passages")
    new_total_passages = st.number_input(
        "Nombre total de passages projeté sur l'année",
        min_value=1,
        step=100,
        value=total_passages_init,
        key="total_proj",
    )
    if new_total_passages != total_passages_init:
        scale = new_total_passages / total_passages_init

        uhcd_proj = integer(uhcd_an * scale)
        uhcd_plus_proj = integer((uhcd_an + uhcd_sclepios_an) * scale)
        consult_proj_base = integer(consult_an * scale)
        consult_proj_plus = consult_proj_base - uhcd_sclepios_an * scale
        consult_proj_plus = max(0, integer(consult_proj_plus))

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

        st.markdown("#### ROI après projection passages personnalisés")
        r1, r2, r3 = st.columns(3)
        r1.metric("Recette UHCD actuelle (€)", f"{rev_base_uhcd:,.0f}")
        r2.metric("Recette UHCD après Sclépios (€)", f"{rev_plus_uhcd:,.0f}")
        r3.metric("ROI UHCD (%)", f"{roi_uhcd_pct:.1f} %")

        r4, r5 = st.columns(2)
        r4.metric("Recette totale actuelle (€)", f"{rev_base_total:,.0f}")
        r5.metric("ROI total (%)", f"{roi_total_pct:.1f} %")

        with st.expander("Détail levier – projection personnalisée"):
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
                    "Volume Sclépios": [
                        avis_plus,
                        ccmu2_plus,
                        ccmu3_plus,
                        uhcd_plus_proj,
                    ],
                    "Gain Sclépios (€)": [
                        rev_plus_avis,
                        rev_plus_ccmu2,
                        rev_plus_ccmu3,
                        rev_plus_uhcd,
                    ],
                }
            )
            detail_df[["Gain Baseline (€)", "Gain Sclépios (€)"]] = detail_df[[
                "Gain Baseline (€)",
                "Gain Sclépios (€)",
            ]].round(2)
            st.dataframe(detail_df.set_index("Levier"), use_container_width=True)

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
    st.markdown(
        "<div style='text-align:center;'><a href='https://sclepios-ia.com' style='color:#2E86AB;'>https://sclepios-ia.com</a></div>",
        unsafe_allow_html=True,
    )
