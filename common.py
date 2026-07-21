"""
Shared UI chrome and cached model loaders used across all SafeNet India pages.
"""

from __future__ import annotations

import os

import streamlit as st

GLOBAL_CSS = """
<style>
/* ---- Base ---- */
*, *::before, *::after {
    font-family: system-ui, "Inter", -apple-system, BlinkMacSystemFont, sans-serif;
}
[data-testid="stAppViewContainer"] {
    background: #0d1117;
}
[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #30363d;
}
[data-testid="stSidebar"] * {
    color: #c9d1d9;
}
/* ---- Metric cards ---- */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 18px 22px;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    font-size: 12px;
    color: #8b949e;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    font-size: 28px;
    font-weight: 800;
    color: #FF6B35;
}
/* ---- Verdict boxes ---- */
.verdict-danger {
    background: rgba(248, 81, 73, 0.10);
    border: 1px solid rgba(248, 81, 73, 0.35);
    border-left: 4px solid #f85149;
    border-radius: 8px;
    padding: 18px 22px;
    margin: 14px 0;
}
.verdict-warning {
    background: rgba(210, 153, 34, 0.10);
    border: 1px solid rgba(210, 153, 34, 0.35);
    border-left: 4px solid #d29922;
    border-radius: 8px;
    padding: 18px 22px;
    margin: 14px 0;
}
.verdict-safe {
    background: rgba(46, 160, 67, 0.10);
    border: 1px solid rgba(46, 160, 67, 0.35);
    border-left: 4px solid #2ea043;
    border-radius: 8px;
    padding: 18px 22px;
    margin: 14px 0;
}
.verdict-title {
    font-size: 20px;
    font-weight: 800;
    color: #e6edf3;
    letter-spacing: -0.3px;
}
.verdict-sub {
    font-size: 13px;
    color: #8b949e;
    margin-top: 6px;
}
/* ---- Confidence bar ---- */
.conf-bar-wrap {
    background: #21262d;
    border-radius: 100px;
    height: 6px;
    margin: 10px 0;
    overflow: hidden;
}
.conf-bar-fill {
    height: 6px;
    border-radius: 100px;
    transition: width 0.5s ease;
}
/* ---- Section headers ---- */
.section-header {
    font-size: 1.4rem;
    font-weight: 800;
    color: #e6edf3;
    letter-spacing: -0.4px;
    margin-bottom: 4px;
}
.section-sub {
    color: #8b949e;
    font-size: 14px;
    margin-bottom: 20px;
    line-height: 1.5;
}
/* ---- Info banner ---- */
.info-banner {
    background: rgba(255, 107, 53, 0.08);
    border: 1px solid rgba(255, 107, 53, 0.25);
    border-left: 4px solid #FF6B35;
    border-radius: 8px;
    padding: 12px 16px;
    color: #c9d1d9;
    font-size: 13px;
    margin: 12px 0;
    line-height: 1.5;
}
/* ---- Sidebar stat pill ---- */
.sidebar-stat {
    background: #21262d;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 13px;
    color: #c9d1d9;
    border-left: 3px solid #FF6B35;
}
/* ---- Home module cards ---- */
.module-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-left: 4px solid #FF6B35;
    border-radius: 12px;
    padding: 28px 24px;
    height: 100%;
    box-shadow: 0 2px 8px rgba(0,0,0,0.4);
    transition: box-shadow 0.2s ease;
}
.module-card:hover {
    box-shadow: 0 4px 18px rgba(255,107,53,0.18);
}
.module-card-icon {
    font-size: 40px;
    line-height: 1;
}
.module-card-title {
    font-size: 18px;
    font-weight: 700;
    color: #e6edf3;
    margin: 12px 0 6px 0;
}
.module-card-desc {
    color: #8b949e;
    font-size: 13px;
    line-height: 1.6;
}
.module-card-hint {
    margin-top: 14px;
    font-size: 13px;
    color: #FF6B35;
    font-weight: 600;
}
/* ---- Impact stat cards ---- */
.stat-card {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 12px;
    padding: 22px 20px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}
.stat-card-value {
    font-size: 32px;
    font-weight: 900;
    color: #FF6B35;
    line-height: 1.1;
    letter-spacing: -1px;
}
.stat-card-label {
    font-size: 12px;
    color: #8b949e;
    margin-top: 8px;
    line-height: 1.4;
    font-weight: 500;
}
/* ---- Hero section ---- */
.hero-title {
    font-size: 3.2rem;
    font-weight: 900;
    color: #e6edf3;
    text-align: center;
    letter-spacing: -2px;
    line-height: 1.1;
    margin-bottom: 12px;
}
.hero-title span {
    color: #FF6B35;
}
.hero-subtitle {
    font-size: 1.1rem;
    color: #8b949e;
    text-align: center;
    max-width: 620px;
    margin: 0 auto 24px auto;
    line-height: 1.6;
}
.hero-divider {
    height: 3px;
    background: linear-gradient(90deg, transparent, #FF6B35, transparent);
    border: none;
    margin: 0 auto 36px auto;
    max-width: 180px;
    border-radius: 2px;
}
.stats-section-label {
    font-size: 11px;
    font-weight: 700;
    color: #FF6B35;
    text-transform: uppercase;
    letter-spacing: 2px;
    text-align: center;
    margin-bottom: 16px;
}
.modules-label {
    font-size: 11px;
    font-weight: 700;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 16px;
    margin-top: 36px;
}
.home-footer {
    text-align: center;
    color: #30363d;
    font-size: 12px;
    margin-top: 48px;
    padding-top: 20px;
    border-top: 1px solid #21262d;
}
.home-footer a {
    color: #FF6B35;
    text-decoration: none;
}
</style>
"""


def apply_page_config(title: str, icon: str) -> None:
    st.set_page_config(page_title=f"{title} · SafeNet India", page_icon=icon, layout="wide")
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding: 12px 0 8px 0;">
                <span style="font-size:48px;">🛡️</span>
                <h1 style="font-size:20px; font-weight:900; color:#e6edf3;
                           margin:6px 0 2px 0; letter-spacing:-0.5px;">
                    SafeNet India
                </h1>
                <p style="color:#8b949e; font-size:11px; margin:0; font-weight:500;
                          text-transform:uppercase; letter-spacing:1px;">
                    AI-Powered Fraud Defence
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.divider()

        st.markdown("**📊 India Cybercrime Stats (2024)**")
        st.markdown(
            "<div class='sidebar-stat'>📌 <b>1.14 million</b> cybercrime complaints/year</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='sidebar-stat'>💸 <b>₹1,776 crore</b> lost to digital arrest scams (2024)</div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='sidebar-stat'>📞 Helpline: <b>1930</b></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<div class='sidebar-stat'>🌐 <a href='https://cybercrime.gov.in' target='_blank' "
            "style='color:#FF6B35;'>cybercrime.gov.in</a></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='color:#30363d; font-size:11px; margin-top:20px; text-align:center;'>"
            "v1.0.0 · Built for ET AI Hackathon 2026<br>"
            "All analysis is advisory only."
            "</p>",
            unsafe_allow_html=True,
        )



@st.cache_resource(show_spinner=False)
def load_fraud_shield_model():
    """Load IndicBERT text classification model (cached)."""
    try:
        from modules.fraud_shield import load_model  # type: ignore

        return load_model()
    except Exception as exc:
        st.toast(f"Fraud Shield model error: {exc}", icon="⚠️")
        return None, None


@st.cache_resource(show_spinner=False)
def load_counterfeit_model():
    """Load EfficientNet currency model (cached)."""
    try:
        from modules.counterfeit_detector import load_model  # type: ignore

        return load_model()
    except Exception as exc:
        st.toast(f"Counterfeit model error: {exc}", icon="⚠️")
        return None
