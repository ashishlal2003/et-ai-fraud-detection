"""
SafeNet India — Home
====================
Landing page. Each module lives on its own page (see sidebar):
  1. Citizen Fraud Shield    — Multilingual text fraud classifier
  2. Counterfeit Detector    — Currency note authenticity via CV
  3. Fraud Network Visualizer — Interactive fraud graph explorer

Run:
    streamlit run Home.py
"""

from __future__ import annotations

import streamlit as st

from common import apply_page_config, render_sidebar

apply_page_config("Home", "🛡️")
render_sidebar()

# ── Hero ──────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div style="padding: 32px 0 8px 0;">
        <div class="hero-title">SafeNet <span>India</span></div>
        <div class="hero-subtitle">
            AI-powered protection against digital fraud, counterfeit currency,
            and organised crime networks.
        </div>
        <hr class="hero-divider">
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Impact Stats ──────────────────────────────────────────────────────────────
st.markdown(
    "<div class='stats-section-label'>India Cybercrime at a Glance — 2024</div>",
    unsafe_allow_html=True,
)

s1, s2, s3, s4 = st.columns(4)

with s1:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-card-value">₹1,776 Cr</div>
            <div class="stat-card-label">Lost to digital arrest scams (Jan–Sep 2024)</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with s2:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-card-value">1.14M</div>
            <div class="stat-card-label">Cybercrime complaints filed in 2023</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with s3:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-card-value">60%</div>
            <div class="stat-card-label">Year-on-year rise in cybercrime reports</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with s4:
    st.markdown(
        """
        <div class="stat-card">
            <div class="stat-card-value">29</div>
            <div class="stat-card-label">States affected by organised fraud networks</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ── Module Cards ──────────────────────────────────────────────────────────────
st.markdown(
    "<div class='modules-label'>AI Modules — Pick one to get started</div>",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        """
        <div class="module-card">
            <div class="module-card-icon">🛡️</div>
            <div class="module-card-title">Citizen Fraud Shield</div>
            <div class="module-card-desc">
                Paste a suspicious SMS, WhatsApp message, or call script in any Indian
                language. Detects digital arrest scams, KYC scams, and investment fraud.
            </div>
            <div class="module-card-hint">→ Open</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/1_Citizen_Fraud_Shield.py", label="Open Citizen Fraud Shield →", use_container_width=True)

with col2:
    st.markdown(
        """
        <div class="module-card">
            <div class="module-card-icon">💵</div>
            <div class="module-card-title">Counterfeit Detector</div>
            <div class="module-card-desc">
                Upload a photo of an Indian currency note to check authenticity.
                Highlights suspicious regions with Grad-CAM heatmap overlay.
            </div>
            <div class="module-card-hint">→ Open</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/2_Counterfeit_Detector.py", label="Open Counterfeit Detector →", use_container_width=True)

with col3:
    st.markdown(
        """
        <div class="module-card">
            <div class="module-card-icon">🕸️</div>
            <div class="module-card-title">Fraud Network</div>
            <div class="module-card-desc">
                Trace a phone number through a fraud ring — scammers, mules,
                and victims — in an interactive network graph.
            </div>
            <div class="module-card-hint">→ Open</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.page_link("pages/3_Fraud_Network.py", label="Open Fraud Network →", use_container_width=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="home-footer">
        Built for ET AI Hackathon 2026 &nbsp;·&nbsp; All analysis is advisory only
        &nbsp;·&nbsp; Cybercrime Helpline: <b>1930</b>
        &nbsp;·&nbsp; <a href="https://cybercrime.gov.in" target="_blank">cybercrime.gov.in</a>
    </div>
    """,
    unsafe_allow_html=True,
)
