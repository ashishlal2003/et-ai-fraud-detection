"""
FraudShield AI — Home
======================
Landing page. Each module lives on its own page (see sidebar):
  1. Citizen Fraud Shield    — Multilingual text fraud classifier
  2. Counterfeit Detector    — Currency note authenticity via CV
  3. Fraud Network Visualizer — Interactive fraud graph explorer

Run:
    streamlit run app.py
"""

from __future__ import annotations

import streamlit as st

from common import apply_page_config, render_sidebar

apply_page_config("Home", "🛡️")
render_sidebar()

st.markdown(
    "<div class='section-header'>🛡️ FraudShield AI</div>"
    "<div class='section-sub'>"
    "Indian Digital Public Safety — pick a module from the sidebar to get started."
    "</div>",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class='module-card'>
            <div class='module-card-icon'>🛡️</div>
            <div class='module-card-title'>Citizen Fraud Shield</div>
            <div class='module-card-desc'>
                Paste a suspicious SMS, WhatsApp message, or call script in any Indian
                language. Detects digital arrest scams, KYC scams, and investment fraud.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Citizen_Fraud_Shield.py", label="Open Fraud Shield →", use_container_width=True)

with col2:
    st.markdown(
        """
        <div class='module-card'>
            <div class='module-card-icon'>💵</div>
            <div class='module-card-title'>Counterfeit Detector</div>
            <div class='module-card-desc'>
                Upload a photo of an Indian currency note to check authenticity.
                Highlights suspicious regions with Grad-CAM.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Counterfeit_Detector.py", label="Open Counterfeit Detector →", use_container_width=True)

with col3:
    st.markdown(
        """
        <div class='module-card'>
            <div class='module-card-icon'>🕸️</div>
            <div class='module-card-title'>Fraud Network</div>
            <div class='module-card-desc'>
                Trace a phone number through a fraud ring — scammers, mules,
                and victims — in an interactive network graph.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_Fraud_Network.py", label="Open Fraud Network →", use_container_width=True)
