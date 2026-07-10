"""
Shared UI chrome and cached model loaders used across all FraudShield AI pages.
"""

from __future__ import annotations

import os

import streamlit as st

GLOBAL_CSS = """
<style>
/* ---- Base ---- */
[data-testid="stAppViewContainer"] {
    background: #0d1117;
}
[data-testid="stSidebar"] {
    background: #161b22;
    border-right: 1px solid #21262d;
}
/* ---- Metric cards ---- */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 10px;
    padding: 16px 20px;
}
/* ---- Verdict boxes ---- */
.verdict-danger {
    background: rgba(248, 81, 73, 0.12);
    border: 1px solid rgba(248, 81, 73, 0.4);
    border-left: 4px solid #f85149;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 12px 0;
}
.verdict-warning {
    background: rgba(210, 153, 34, 0.12);
    border: 1px solid rgba(210, 153, 34, 0.4);
    border-left: 4px solid #d29922;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 12px 0;
}
.verdict-safe {
    background: rgba(46, 160, 67, 0.12);
    border: 1px solid rgba(46, 160, 67, 0.4);
    border-left: 4px solid #2ea043;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 12px 0;
}
.verdict-title {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.3px;
}
.verdict-sub {
    font-size: 13px;
    color: #8b949e;
    margin-top: 4px;
}
/* ---- Confidence bar ---- */
.conf-bar-wrap {
    background: #21262d;
    border-radius: 6px;
    height: 8px;
    margin: 8px 0;
    overflow: hidden;
}
.conf-bar-fill {
    height: 8px;
    border-radius: 6px;
    transition: width 0.4s ease;
}
/* ---- Section headers ---- */
.section-header {
    font-size: 26px;
    font-weight: 800;
    color: #e6edf3;
    letter-spacing: -0.4px;
    margin-bottom: 4px;
}
.section-sub {
    color: #8b949e;
    font-size: 14px;
    margin-bottom: 18px;
}
/* ---- Info banner ---- */
.info-banner {
    background: rgba(56, 139, 253, 0.1);
    border: 1px solid rgba(56, 139, 253, 0.3);
    border-radius: 8px;
    padding: 12px 16px;
    color: #79c0ff;
    font-size: 13px;
    margin: 10px 0;
}
/* ---- Sidebar stat pill ---- */
.sidebar-stat {
    background: #21262d;
    border-radius: 8px;
    padding: 10px 14px;
    margin: 6px 0;
    font-size: 13px;
    color: #c9d1d9;
    border-left: 3px solid #f85149;
}
/* ---- Home module cards ---- */
.module-card {
    background: #161b22;
    border: 1px solid #21262d;
    border-radius: 12px;
    padding: 24px;
    height: 100%;
}
.module-card-icon {
    font-size: 36px;
}
.module-card-title {
    font-size: 18px;
    font-weight: 700;
    color: #e6edf3;
    margin: 10px 0 6px 0;
}
.module-card-desc {
    color: #8b949e;
    font-size: 13px;
    line-height: 1.5;
}
</style>
"""


def apply_page_config(title: str, icon: str) -> None:
    st.set_page_config(page_title=f"{title} · FraudShield AI", page_icon=icon, layout="wide")
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


def render_sidebar() -> None:
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center; padding: 12px 0 8px 0;">
                <span style="font-size:48px;">🛡️</span>
                <h1 style="font-size:22px; font-weight:800; color:#e6edf3;
                           margin:4px 0 2px 0; letter-spacing:-0.5px;">
                    FraudShield AI
                </h1>
                <p style="color:#8b949e; font-size:12px; margin:0;">
                    Indian Digital Public Safety
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
            "style='color:#79c0ff;'>cybercrime.gov.in</a></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            "<p style='color:#30363d; font-size:11px; margin-top:20px; text-align:center;'>"
            "v1.0.0 · Built for Hackathon 2024<br>"
            "All analysis is advisory only."
            "</p>",
            unsafe_allow_html=True,
        )


def load_openai_client():
    """Create OpenAI client if OPENAI_API_KEY is set, else return None."""
    try:
        from openai import OpenAI  # type: ignore

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return None
        return OpenAI(api_key=api_key)
    except ImportError:
        return None


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
