# (continues)
                "Gain Baseline (€)",
                "Gain Sclépios (€)",
            ]].round(2)
            st.dataframe(detail_proj.set_index("Levier"), use_container_width=True)

            bar = detail_proj.melt(
                id_vars="Levier",
                value_vars=["Gain Baseline (€)", "Gain Sclépios (€)"],
                var_name="Scenario",
                value_name="Gain (€)",
            )
            fig = px.bar(
                bar,
                x="Gain (€)",
                y="Levier",
                color="Scenario",
                orientation="h",
                template="plotly_white",
                text="Gain (€)",
            )
            fig.update_traces(texttemplate="%{text:,.0f}")
            st.plotly_chart(fig, use_container_width=True)

    # FOOTER ONGLET 2
    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;'><a href='https://sclepios-ia.com' style='color:#2E86AB;'>https://sclepios-ia.com</a></div>",
        unsafe_allow_html=True,
    )
