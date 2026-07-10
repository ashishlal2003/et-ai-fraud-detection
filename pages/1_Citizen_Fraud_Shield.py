"""Citizen Fraud Shield — multilingual text fraud classifier."""

from __future__ import annotations

import streamlit as st

from common import apply_page_config, render_sidebar, load_fraud_shield_model, load_openai_client

apply_page_config("Citizen Fraud Shield", "🛡️")
render_sidebar()

st.markdown(
    "<div class='section-header'>🛡️ Citizen Fraud Shield</div>"
    "<div class='section-sub'>"
    "Paste any suspicious SMS, WhatsApp message, or call script in any Indian language. "
    "Our AI will detect fraud patterns and explain the risk."
    "</div>",
    unsafe_allow_html=True,
)

with st.spinner("Loading fraud detection model…"):
    fs_model, fs_tokenizer = load_fraud_shield_model()
    openai_client = load_openai_client()

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

        if is_safe:
            verdict_class = "verdict-safe"
            verdict_icon = "✅"
            verdict_bg_bar = "#2ea043"
        elif confidence > 0.75:
            verdict_class = "verdict-danger"
            verdict_icon = "🚨"
            verdict_bg_bar = "#f85149"
        else:
            verdict_class = "verdict-warning"
            verdict_icon = "⚠️"
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
