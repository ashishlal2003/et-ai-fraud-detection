"""Fraud Network Intelligence — SafeNet India."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import streamlit as st

from common import apply_page_config, render_sidebar

apply_page_config("Fraud Network", "🕸️")
render_sidebar()

# ---------------------------------------------------------------------------
# Task 3: Ensure fraud_network.json exists before rendering
# ---------------------------------------------------------------------------

_DATA_JSON = Path(__file__).parent.parent / "data" / "fraud_network.json"
_GENERATOR = Path(__file__).parent.parent / "data" / "synthetic_fraud_network.py"

if not _DATA_JSON.exists():
    if _GENERATOR.exists():
        with st.spinner("Generating fraud network data…"):
            try:
                result = subprocess.run(
                    [sys.executable, str(_GENERATOR)],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
                if result.returncode != 0:
                    st.warning(
                        f"Data generator exited with code {result.returncode}. "
                        "The visualiser will use built-in synthetic data instead."
                    )
            except subprocess.TimeoutExpired:
                st.warning(
                    "Data generation timed out. "
                    "The visualiser will use built-in synthetic data instead."
                )
            except Exception as exc:
                st.warning(
                    f"Could not run data generator ({exc}). "
                    "The visualiser will use built-in synthetic data instead."
                )
    else:
        st.info(
            "fraud_network.json not found and generator script is missing. "
            "The visualiser will use built-in synthetic data."
        )

# ---------------------------------------------------------------------------
# Task 2: Header section
# ---------------------------------------------------------------------------

st.markdown(
    """
    <div style="margin-bottom: 2px;">
        <span style="font-size: 32px; font-weight: 900; color: #FF6B35;
                     letter-spacing: -0.5px;">
            Fraud Network Intelligence
        </span>
    </div>
    <p style="color: #8b949e; font-size: 15px; margin-top: 4px; margin-bottom: 18px;">
        Map organised fraud rings — trace scammers, mule accounts, and victims across India.
    </p>
    """,
    unsafe_allow_html=True,
)

# Context callout
st.markdown(
    """
    <div style="
        background: rgba(255, 107, 53, 0.08);
        border-left: 4px solid #FF6B35;
        border-radius: 4px;
        padding: 12px 16px;
        margin-bottom: 24px;
        color: #c9d1d9;
        font-size: 13px;
        line-height: 1.6;
    ">
        <b style="color: #FF6B35;">Demo Data Notice:</b>&nbsp;
        Data shown is synthetic and generated for demonstration purposes.
        In production, this system would ingest real NCRB complaint data,
        telecom call records, and financial transaction intelligence.
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Delegate to module
# ---------------------------------------------------------------------------

try:
    from modules.fraud_graph import render_streamlit_tab  # type: ignore

    render_streamlit_tab()

except ImportError as exc:
    st.error(
        f"**Missing dependency:** {exc}\n\n"
        "Install required packages and restart the app:"
    )
    st.code("pip install networkx pyvis", language="bash")

except Exception as exc:
    st.error(f"**Fraud Network Visualizer encountered an error:** {exc}")
    with st.expander("Show full traceback"):
        import traceback
        st.code(traceback.format_exc(), language="python")
