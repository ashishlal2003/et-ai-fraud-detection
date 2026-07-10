"""Fraud Network Visualizer — interactive fraud ring graph explorer."""

from __future__ import annotations

import streamlit as st

from common import apply_page_config, render_sidebar, load_openai_client

apply_page_config("Fraud Network", "🕸️")
render_sidebar()

try:
    from modules.fraud_graph import render_streamlit_tab  # type: ignore

    render_streamlit_tab(openai_client=load_openai_client())

except ImportError as exc:
    st.error(f"Failed to load Fraud Network module: {exc}")
    st.markdown(
        "<div class='info-banner'>"
        "Ensure <code>networkx</code> and <code>pyvis</code> are installed:<br>"
        "<code>pip install networkx pyvis</code>"
        "</div>",
        unsafe_allow_html=True,
    )
except Exception as exc:
    st.error(f"Fraud Network Visualizer error: {exc}")
    import traceback
    with st.expander("Error details"):
        st.code(traceback.format_exc())
