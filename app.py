"""
FraudShield AI — Main Streamlit Application
============================================
Multi-tab app for Indian Digital Public Safety.

Tabs:
  1. Citizen Fraud Shield    — Multilingual text fraud classifier
  2. Counterfeit Detector    — Currency note authenticity via CV
  3. Fraud Network Visualizer — Interactive fraud graph explorer

Run:
    streamlit run app.py
"""

from __future__ import annotations

import os
from pathlib import Path

import streamlit as st

# ---------------------------------------------------------------------------
# Page config — MUST be the first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="FraudShield AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ---- Base ---- */
    [data-testid="stAppViewContainer"] {
        background: #0d1117;
    }
    [data-testid="stSidebar"] {
        background: #161b22;
        border-right: 1px solid #21262d;
    }
    /* ---- Tabs ---- */
    button[data-baseweb="tab"] {
        font-size: 14px !important;
        font-weight: 600 !important;
        padding: 10px 20px !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        border-bottom: 3px solid #f85149 !important;
        color: #f85149 !important;
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
        font-size: 22px;
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
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Load environment and OpenAI client
# ---------------------------------------------------------------------------

def _load_openai_client():
    """Create OpenAI client if OPENAI_API_KEY is set, else return None."""
    try:
        from openai import OpenAI  # type: ignore

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key:
            return None
        return OpenAI(api_key=api_key)
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Model loading (cached per session)
# ---------------------------------------------------------------------------

@st.cache_resource(show_spinner=False)
def _load_fraud_shield_model():
    """Load IndicBERT text classification model (cached)."""
    try:
        from modules.fraud_shield import load_model  # type: ignore

        return load_model()
    except Exception as exc:
        st.toast(f"Fraud Shield model error: {exc}", icon="⚠️")
        return None, None


@st.cache_resource(show_spinner=False)
def _load_counterfeit_model():
    """Load EfficientNet currency model (cached)."""
    try:
        from modules.counterfeit_detector import load_model  # type: ignore

        return load_model()
    except Exception as exc:
        st.toast(f"Counterfeit model error: {exc}", icon="⚠️")
        return None


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

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

    st.markdown(
        "<p style='color:#8b949e; font-size:13px; line-height:1.6;'>"
        "Detect digital fraud, counterfeit currency, and visualize scam networks "
        "— powered by IndicBERT, EfficientNet, and GPT-4.1."
        "</p>",
        unsafe_allow_html=True,
    )

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

    st.divider()

    openai_key_input = st.text_input(
        "OpenAI API Key (optional)",
        type="password",
        placeholder="sk-...",
        help="Required for GPT-4.1 explanations. Leave blank for rule-based fallback.",
    )
    if openai_key_input:
        os.environ["OPENAI_API_KEY"] = openai_key_input

    st.markdown(
        "<p style='color:#30363d; font-size:11px; margin-top:20px; text-align:center;'>"
        "v1.0.0 · Built for Hackathon 2024<br>"
        "All analysis is advisory only."
        "</p>",
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Main — tabs
# ---------------------------------------------------------------------------

tab1, tab2, tab3 = st.tabs([
    "🛡️  Citizen Fraud Shield",
    "💵  Counterfeit Detector",
    "🕸️  Fraud Network",
])

# ===========================================================================
# TAB 1 — Citizen Fraud Shield
# ===========================================================================

with tab1:
    st.markdown(
        "<div class='section-header'>🛡️ Citizen Fraud Shield</div>"
        "<div class='section-sub'>"
        "Paste any suspicious SMS, WhatsApp message, or call script in any Indian language. "
        "Our AI will detect fraud patterns and explain the risk."
        "</div>",
        unsafe_allow_html=True,
    )

    # Load models
    with st.spinner("Loading fraud detection model…"):
        fs_model, fs_tokenizer = _load_fraud_shield_model()
        openai_client = _load_openai_client()

    model_loaded = fs_model is not None
    if not model_loaded:
        st.markdown(
            "<div class='info-banner'>"
            "⚡ Running in <b>Demo Mode</b> — IndicBERT model not found at "
            "<code>models/indicbert_fraud/</code>. Using keyword-based classifier. "
            "Train the model to enable full deep-learning inference."
            "</div>",
            unsafe_allow_html=True,
        )

    # Example messages for quick testing
    with st.expander("💡 Try an example message", expanded=False):
        examples = {
            "Digital Arrest Scam (Hindi)": (
                "नमस्ते, मैं CBI ऑफिसर राजेश कुमार बोल रहा हूँ। "
                "आपके आधार कार्ड से मनी लॉन्ड्रिंग का मामला दर्ज हुआ है। "
                "अगर अभी 50,000 रुपये ट्रांसफर नहीं किए तो गिरफ्तारी होगी।"
            ),
            "KYC Scam (English)": (
                "URGENT: Your SBI account will be suspended within 24 hours. "
                "Your KYC verification is pending. Click here to update immediately: "
                "http://sbi-kyc-update.xyz/verify?id=8821"
            ),
            "Investment Fraud (English)": (
                "Guaranteed 40% monthly returns! Join our exclusive trading group. "
                "Already 5000+ members earning daily. WhatsApp us NOW. "
                "Minimum investment Rs 10,000. Limited slots!"
            ),
            "Safe Message (English)": (
                "Dear Customer, your OTP for logging into net banking is 847291. "
                "This OTP is valid for 10 minutes. Do not share this OTP with anyone."
            ),
        }
        selected_example = st.selectbox("Select example:", list(examples.keys()))
        if st.button("Load Example", key="load_example"):
            st.session_state["fraud_text_input"] = examples[selected_example]

    # Text input
    text_input = st.text_area(
        "Message to analyze",
        value=st.session_state.get("fraud_text_input", ""),
        height=150,
        placeholder="Paste suspicious message here… (supports Hindi, Tamil, Telugu, Bengali, English, etc.)",
        label_visibility="collapsed",
    )

    col_analyze, col_clear = st.columns([3, 1])
    with col_analyze:
        analyze_clicked = st.button(
            "🔍 Analyze Message",
            type="primary",
            use_container_width=True,
            disabled=not text_input.strip(),
        )
    with col_clear:
        if st.button("Clear", use_container_width=True):
            st.session_state["fraud_text_input"] = ""
            st.rerun()

    if analyze_clicked and text_input.strip():
        with st.spinner("Analyzing message…"):
            try:
                from modules.fraud_shield import predict, get_explanation  # type: ignore

                result = predict(text_input, fs_model, fs_tokenizer)
            except ImportError as exc:
                st.error(f"Module import error: {exc}")
                result = None

        if result:
            label = result["label"]
            confidence = result["confidence"]
            label_display = result.get("label_display", label)
            is_safe = label == "safe"

            # Verdict box
            if is_safe:
                verdict_class = "verdict-safe"
                verdict_icon = "✅"
                verdict_color = "#2ea043"
                verdict_bg_bar = "#2ea043"
            elif confidence > 0.75:
                verdict_class = "verdict-danger"
                verdict_icon = "🚨"
                verdict_color = "#f85149"
                verdict_bg_bar = "#f85149"
            else:
                verdict_class = "verdict-warning"
                verdict_icon = "⚠️"
                verdict_color = "#d29922"
                verdict_bg_bar = "#d29922"

            st.markdown(
                f"""
                <div class='{verdict_class}'>
                    <div class='verdict-title'>
                        {verdict_icon} {label_display}
                    </div>
                    <div class='verdict-sub'>
                        Confidence: {confidence:.1%} —
                        {"Message appears safe" if is_safe else "High risk — do not respond or send money"}
                    </div>
                    <div class='conf-bar-wrap' style='margin-top:10px;'>
                        <div class='conf-bar-fill'
                             style='width:{confidence*100:.1f}%; background:{verdict_bg_bar};'>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Score breakdown
            st.markdown("**Fraud Category Scores**")
            scores = result.get("scores", {})
            label_display_map = {
                "digital_arrest": "Digital Arrest",
                "kyc_scam": "KYC Scam",
                "investment_fraud": "Investment Fraud",
                "safe": "Safe",
            }
            for lbl, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
                col_lbl, col_bar, col_pct = st.columns([2, 5, 1])
                with col_lbl:
                    st.markdown(
                        f"<span style='font-size:13px; color:#8b949e;'>"
                        f"{label_display_map.get(lbl, lbl)}</span>",
                        unsafe_allow_html=True,
                    )
                with col_bar:
                    color = "#f85149" if lbl == label and not is_safe else (
                        "#2ea043" if lbl == "safe" else "#30363d"
                    )
                    st.markdown(
                        f"<div class='conf-bar-wrap' style='margin-top:8px;'>"
                        f"<div class='conf-bar-fill' style='width:{score*100:.1f}%; background:{color};'>"
                        f"</div></div>",
                        unsafe_allow_html=True,
                    )
                with col_pct:
                    st.markdown(
                        f"<span style='font-size:13px; color:#c9d1d9;'>{score:.0%}</span>",
                        unsafe_allow_html=True,
                    )

            # GPT explanation
            if not is_safe:
                st.markdown("---")
                st.markdown("**🤖 AI Explanation**")
                with st.spinner("Generating explanation…"):
                    try:
                        explanation = get_explanation(  # type: ignore
                            text_input, label, confidence, openai_client
                        )
                    except Exception as exc:
                        explanation = f"Explanation unavailable: {exc}"
                st.info(explanation)

                # Reporting guidance
                st.markdown("---")
                st.markdown("**📋 What to do next?**")
                action_col1, action_col2 = st.columns(2)
                with action_col1:
                    st.error("🚫 Do NOT share OTP, password, or transfer money")
                    st.error("🚫 Do NOT click any links in the message")
                with action_col2:
                    st.success("✅ Call cybercrime helpline: **1930**")
                    st.success("✅ File complaint at **cybercrime.gov.in**")

            if result.get("demo_mode"):
                st.caption("⚡ Demo mode — results are keyword-based approximations.")

    elif analyze_clicked:
        st.warning("Please enter a message to analyze.")


# ===========================================================================
# TAB 2 — Counterfeit Currency Detector
# ===========================================================================

with tab2:
    st.markdown(
        "<div class='section-header'>💵 Counterfeit Currency Detector</div>"
        "<div class='section-sub'>"
        "Upload a photo of an Indian currency note to verify its authenticity. "
        "Our EfficientNet model highlights suspicious regions using Grad-CAM visualization."
        "</div>",
        unsafe_allow_html=True,
    )

    with st.spinner("Loading currency detection model…"):
        cc_model = _load_counterfeit_model()

    cc_model_loaded = cc_model is not None
    if not cc_model_loaded:
        st.markdown(
            "<div class='info-banner'>"
            "⚡ Running in <b>Demo Mode</b> — EfficientNet model not found at "
            "<code>models/efficientnet_currency.pth</code>. "
            "Upload any image to see the demo prediction flow."
            "</div>",
            unsafe_allow_html=True,
        )

    # Upload widget
    uploaded_file = st.file_uploader(
        "Upload currency note image",
        type=["jpg", "jpeg", "png", "webp"],
        help="Upload a clear, well-lit photo of the currency note (front preferred).",
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        image_bytes = uploaded_file.read()

        col_img, col_result = st.columns([1, 1])

        with col_img:
            st.markdown("**Original Image**")
            st.image(image_bytes, use_column_width=True)

        with st.spinner("Analyzing currency note…"):
            try:
                from modules.counterfeit_detector import predict, get_gradcam, get_analysis_details  # type: ignore

                cc_result = predict(image_bytes, cc_model)
                gradcam_img = get_gradcam(image_bytes, cc_model)
                img_details = get_analysis_details(image_bytes)
            except ImportError as exc:
                st.error(f"Module import error: {exc}")
                cc_result = None
                gradcam_img = None
                img_details = {}

        if cc_result:
            verdict = cc_result["verdict"]
            cc_confidence = cc_result["confidence"]
            scores = cc_result.get("scores", {})

            with col_result:
                if gradcam_img is not None:
                    st.markdown("**Grad-CAM Heatmap** *(suspicious regions highlighted)*")
                    st.image(gradcam_img, use_column_width=True)
                else:
                    st.markdown("**Grad-CAM**")
                    st.info("Grad-CAM visualization unavailable.")

            # Verdict display
            if verdict == "FAKE":
                st.error(
                    f"🚨 **COUNTERFEIT DETECTED** — Confidence: {cc_confidence:.1%}\n\n"
                    "This note shows signs of being counterfeit. "
                    "Do not accept or use this note. Report to your nearest police station or bank."
                )
            else:
                st.success(
                    f"✅ **GENUINE NOTE** — Confidence: {cc_confidence:.1%}\n\n"
                    "This note appears to be authentic based on visual analysis. "
                    "Always verify security features physically for high-value transactions."
                )

            # Score breakdown
            col_r, col_f = st.columns(2)
            with col_r:
                st.metric(
                    "Real Probability",
                    f"{scores.get('REAL', 0):.1%}",
                    delta=None,
                )
            with col_f:
                st.metric(
                    "Fake Probability",
                    f"{scores.get('FAKE', 0):.1%}",
                    delta=None,
                )

            # Image metadata
            if img_details:
                with st.expander("📐 Image Analysis Details"):
                    d1, d2, d3 = st.columns(3)
                    d1.metric("Resolution", f"{img_details.get('width', 0)}×{img_details.get('height', 0)}")
                    d2.metric("File Size", f"{img_details.get('file_size_kb', 0):.1f} KB")
                    d3.metric("Brightness", f"{img_details.get('mean_brightness', 0):.0f}/255")

            # RBI security feature checklist
            st.markdown("---")
            st.markdown("**✅ Physical Security Feature Checklist (verify manually)**")
            features = [
                ("Watermark", "Hold note against light — Mahatma Gandhi portrait should appear"),
                ("Security Thread", "Embedded thread reads 'भारत' and 'RBI' alternately"),
                ("Colour-shifting Ink", "Number panel shifts from green to blue when tilted"),
                ("Micro-lettering", "'RBI' and 'भारत' visible under magnification on ₹100+"),
                ("Raised Print", "Intaglio printing — feel raised texture on portrait and numerals"),
                ("See-through Register", "Floral design on obverse and reverse align perfectly"),
            ]
            chk_col1, chk_col2 = st.columns(2)
            for i, (feature, desc) in enumerate(features):
                col = chk_col1 if i % 2 == 0 else chk_col2
                col.checkbox(f"**{feature}** — {desc}", key=f"feat_{i}")

            if cc_result.get("demo_mode"):
                st.caption("⚡ Demo mode — prediction is illustrative, not based on a trained model.")

    else:
        # Placeholder state
        st.markdown(
            """
            <div style="border: 2px dashed #21262d; border-radius: 12px;
                        padding: 48px; text-align: center; margin: 20px 0;">
                <span style="font-size:48px;">💵</span>
                <p style="color:#8b949e; margin-top:12px; font-size:15px;">
                    Upload a currency note photo above to begin analysis
                </p>
                <p style="color:#30363d; font-size:12px;">
                    Supported: JPG, PNG, WebP · Recommended: 1MP+ resolution, good lighting
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ===========================================================================
# TAB 3 — Fraud Network Visualizer
# ===========================================================================

with tab3:
    try:
        from modules.fraud_graph import render_streamlit_tab  # type: ignore

        render_streamlit_tab(openai_client=_load_openai_client())

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
