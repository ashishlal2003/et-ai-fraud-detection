"""Citizen Fraud Shield — SafeNet India multilingual text fraud classifier."""

from __future__ import annotations

import streamlit as st

from common import apply_page_config, render_sidebar, load_fraud_shield_model

apply_page_config("Citizen Fraud Shield", "🛡️")
render_sidebar()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='section-header'>🛡️ Citizen Fraud Shield</div>"
    "<div class='section-sub'>"
    "Paste any suspicious SMS, WhatsApp message, or call script. "
    "AI detects fraud patterns across Indian languages instantly."
    "</div>",
    unsafe_allow_html=True,
)

# ── Language selector ─────────────────────────────────────────────────────────
lang = st.radio(
    "UI Language",
    ["English", "हिंदी", "ಕನ್ನಡ"],
    horizontal=True,
    label_visibility="collapsed",
)

# Label maps per language — classifier handles multilingual input natively
_LABELS: dict[str, dict[str, str]] = {
    "English": {
        "placeholder":      "Paste suspicious message here… (supports English, Hindi and Kannada)",
        "button":           "🔍 Analyze Message",
        "clear":            "Clear",
        "load_btn":         "Load Example",
        "SCAM":             "SCAM",
        "SAFE":             "SAFE",
        "SUSPICIOUS":       "SUSPICIOUS",
        "digital_arrest":   "Digital Arrest Scam",
        "kyc_scam":         "KYC / Document Scam",
        "investment_fraud": "Investment Fraud",
        "safe":             "Safe Message",
        "safe_note":        "Message appears safe",
        "risk_note":        "High risk — do not respond or send money",
    },
    "हिंदी": {
        "placeholder":      "संदिग्ध संदेश यहाँ पेस्ट करें...",
        "button":           "संदेश विश्लेषण करें",
        "clear":            "साफ करें",
        "load_btn":         "उदाहरण लोड करें",
        "SCAM":             "घोटाला",
        "SAFE":             "सुरक्षित",
        "SUSPICIOUS":       "संदिग्ध",
        "digital_arrest":   "डिजिटल गिरफ्तारी घोटाला",
        "kyc_scam":         "KYC / दस्तावेज़ घोटाला",
        "investment_fraud": "निवेश धोखाधड़ी",
        "safe":             "सुरक्षित संदेश",
        "safe_note":        "संदेश सुरक्षित प्रतीत होता है",
        "risk_note":        "उच्च जोखिम — जवाब न दें, पैसे न भेजें",
    },
    "ಕನ್ನಡ": {
        "placeholder":      "ಅನುಮಾನಾಸ್ಪದ ಸಂದೇಶವನ್ನು ಇಲ್ಲಿ ಅಂಟಿಸಿ...",
        "button":           "ಸಂದೇಶ ವಿಶ್ಲೇಷಿಸಿ",
        "clear":            "ತೆರವುಗೊಳಿಸಿ",
        "load_btn":         "ಉದಾಹರಣೆ ಲೋಡ್ ಮಾಡಿ",
        "SCAM":             "ವಂಚನೆ",
        "SAFE":             "ಸುರಕ್ಷಿತ",
        "SUSPICIOUS":       "ಅನುಮಾನಾಸ್ಪದ",
        "digital_arrest":   "ಡಿಜಿಟಲ್ ಬಂಧನ ವಂಚನೆ",
        "kyc_scam":         "KYC / ದಾಖಲಾತಿ ವಂಚನೆ",
        "investment_fraud": "ಹೂಡಿಕೆ ವಂಚನೆ",
        "safe":             "ಸುರಕ್ಷಿತ ಸಂದೇಶ",
        "safe_note":        "ಸಂದೇಶ ಸುರಕ್ಷಿತವಾಗಿ ಕಾಣುತ್ತದೆ",
        "risk_note":        "ಹೆಚ್ಚಿನ ಅಪಾಯ — ಪ್ರತಿಕ್ರಿಯಿಸಬೇಡಿ, ಹಣ ಕಳುಹಿಸಬೇಡಿ",
    },
}
L = _LABELS[lang]

# ── Model loading ─────────────────────────────────────────────────────────────
with st.spinner("Loading fraud detection model…"):
    fs_model, fs_tokenizer = load_fraud_shield_model()

model_loaded = fs_model is not None

# ── Example messages ──────────────────────────────────────────────────────────
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
    selected_example = st.selectbox("Select example:", list(examples.keys()), label_visibility="collapsed")
    if st.button(L["load_btn"], key="load_example"):
        st.session_state["fraud_text_input"] = examples[selected_example]

# ── Text input + action buttons ───────────────────────────────────────────────
text_input = st.text_area(
    "Message to analyze",
    value=st.session_state.get("fraud_text_input", ""),
    height=150,
    placeholder=L["placeholder"],
    label_visibility="collapsed",
)

col_analyze, col_clear = st.columns([3, 1])
with col_analyze:
    analyze_clicked = st.button(
        L["button"],
        type="primary",
        use_container_width=True,
        disabled=not text_input.strip(),
    )
with col_clear:
    if st.button(L["clear"], use_container_width=True):
        st.session_state["fraud_text_input"] = ""
        st.rerun()

# ── Analysis result ───────────────────────────────────────────────────────────
if analyze_clicked and text_input.strip():
    with st.spinner("Analyzing message…"):
        try:
            from modules.fraud_shield import predict  # type: ignore

            result = predict(text_input, fs_model, fs_tokenizer)
        except ImportError as exc:
            st.error(f"Module import error: {exc}")
            result = None

    if result:
        label      = result["label"]
        confidence = result["confidence"]
        is_safe    = label == "safe"

        # Verdict tier
        if is_safe:
            verdict_word = L["SAFE"]
            verdict_icon = "✅"
            box_bg       = "#0d2b1d"
            box_border   = "#2ea043"
            box_color    = "#2ea043"
        elif confidence > 0.75:
            verdict_word = L["SCAM"]
            verdict_icon = "🚨"
            box_bg       = "#2b0d0d"
            box_border   = "#f85149"
            box_color    = "#f85149"
        else:
            verdict_word = L["SUSPICIOUS"]
            verdict_icon = "⚠️"
            box_bg       = "#2b2006"
            box_border   = "#d29922"
            box_color    = "#d29922"

        # ── Big verdict box ───────────────────────────────────────────────────
        st.markdown(
            f"""
            <div style="
                background:{box_bg};
                border:2px solid {box_border};
                border-radius:12px;
                padding:24px 28px;
                margin:16px 0;
            ">
                <div style="font-size:2rem; font-weight:800; color:{box_color}; letter-spacing:1px;">
                    {verdict_icon}&nbsp;{verdict_word}
                </div>
                <div style="font-size:1.5rem; font-weight:700; color:{box_color}; margin-top:4px;">
                    {confidence:.1%} confidence
                </div>
                <div style="color:#8b949e; font-size:0.875rem; margin-top:8px;">
                    {L["safe_note"] if is_safe else L["risk_note"]}
                </div>
                <div style="background:#21262d; border-radius:6px; height:8px; margin-top:14px;">
                    <div style="
                        width:{confidence*100:.1f}%;
                        background:{box_color};
                        height:8px;
                        border-radius:6px;
                    "></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Trigger word badges ───────────────────────────────────────────────
        top_tokens = result.get("top_tokens", [])
        if top_tokens and not is_safe:
            suspicious_set = {
                "arrest", "court", "cbi", "police", "kyc", "block", "suspend",
                "verify", "otp", "account", "investment", "profit", "crore",
                "lakh", "urgent", "immediately", "गिरफ्तार", "अकाउंट", "निवेश",
            }
            st.markdown("**Trigger words detected**")
            badge_html = " ".join(
                f"<span style='"
                f"display:inline-block; padding:2px 10px; margin:3px 2px; border-radius:20px; "
                f"font-size:0.8rem; font-weight:600; "
                f"background:{'#2b0d0d' if token in suspicious_set else '#1c2128'}; "
                f"color:{'#f85149' if token in suspicious_set else '#8b949e'}; "
                f"border:1px solid {'#f85149' if token in suspicious_set else '#30363d'};"
                f"'>{token}</span>"
                for token, _ in top_tokens
            )
            st.markdown(badge_html, unsafe_allow_html=True)

        # ── Category score breakdown ──────────────────────────────────────────
        st.markdown("**Fraud Category Scores**")
        scores = result.get("scores", {})
        for lbl, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
            display_name = L.get(lbl, lbl)
            col_lbl, col_bar, col_pct = st.columns([2, 5, 1])
            with col_lbl:
                st.markdown(
                    f"<span style='font-size:13px; color:#8b949e;'>{display_name}</span>",
                    unsafe_allow_html=True,
                )
            with col_bar:
                color = "#f85149" if lbl == label and not is_safe else (
                    "#2ea043" if lbl == "safe" else "#30363d"
                )
                st.markdown(
                    f"<div style='background:#21262d; border-radius:4px; height:8px; margin-top:10px;'>"
                    f"<div style='width:{score*100:.1f}%; background:{color}; height:8px; border-radius:4px;'>"
                    f"</div></div>",
                    unsafe_allow_html=True,
                )
            with col_pct:
                st.markdown(
                    f"<span style='font-size:13px; font-weight:700; color:#c9d1d9;'>{score:.0%}</span>",
                    unsafe_allow_html=True,
                )

        # ── AI explanation + actions (non-safe only) ──────────────────────────
        if not is_safe:
            st.markdown("---")
            st.markdown("**🤖 Why this is flagged**")
            from modules.fraud_shield import _fallback_explanation  # type: ignore
            st.info(_fallback_explanation(label, confidence))

            st.markdown("---")
            st.markdown("**📋 What to do next**")
            action_col1, action_col2 = st.columns(2)
            with action_col1:
                st.markdown(
                    """
                    <div style="background:#2b0d0d; border:1px solid #f85149; border-radius:10px;
                                padding:16px 18px;">
                        <div style="font-weight:700; color:#f85149; margin-bottom:8px;">🚫 Do NOT</div>
                        <div style="color:#c9d1d9; font-size:0.875rem; line-height:1.8;">
                            Share OTP, password, or Aadhaar details<br>
                            Transfer money to unknown accounts<br>
                            Click any links in the message
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with action_col2:
                st.markdown(
                    """
                    <div style="background:#0d2b1d; border:1px solid #2ea043; border-radius:10px;
                                padding:16px 18px;">
                        <div style="font-weight:700; color:#2ea043; margin-bottom:8px;">✅ Do THIS</div>
                        <div style="color:#c9d1d9; font-size:0.875rem; line-height:1.8;">
                            Call cybercrime helpline: <strong>1930</strong><br>
                            File complaint at <strong>cybercrime.gov.in</strong><br>
                            Block the sender immediately
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        if result.get("demo_mode"):
            st.markdown(
                "<p style='color:#484f58; font-style:italic; font-size:0.8rem; margin-top:24px;'>"
                "Results are keyword-based approximations — train the IndicBERT model for full deep-learning inference."
                "</p>",
                unsafe_allow_html=True,
            )

elif analyze_clicked:
    st.warning("Please enter a message to analyze.")

# ── Subtle model-not-loaded note ──────────────────────────────────────────────
if not model_loaded:
    st.markdown(
        "<p style='color:#484f58; font-style:italic; font-size:0.8rem; margin-top:32px;'>"
        "IndicBERT model not found at <code>models/indicbert_fraud/</code> — "
        "running keyword-based classifier."
        "</p>",
        unsafe_allow_html=True,
    )
