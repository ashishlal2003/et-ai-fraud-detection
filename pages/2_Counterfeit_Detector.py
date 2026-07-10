"""Counterfeit Currency Detector — CV-based note authenticity check."""

from __future__ import annotations

import streamlit as st

from common import apply_page_config, render_sidebar, load_counterfeit_model

apply_page_config("Counterfeit Detector", "💵")
render_sidebar()

st.markdown(
    "<div class='section-header'>💵 Counterfeit Currency Detector</div>"
    "<div class='section-sub'>"
    "Upload a photo of an Indian currency note to verify its authenticity. "
    "Our EfficientNet model highlights suspicious regions using Grad-CAM visualization."
    "</div>",
    unsafe_allow_html=True,
)

with st.spinner("Loading currency detection model…"):
    cc_model = load_counterfeit_model()

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

        col_r, col_f = st.columns(2)
        with col_r:
            st.metric("Real Probability", f"{scores.get('REAL', 0):.1%}", delta=None)
        with col_f:
            st.metric("Fake Probability", f"{scores.get('FAKE', 0):.1%}", delta=None)

        if img_details:
            with st.expander("📐 Image Analysis Details"):
                d1, d2, d3 = st.columns(3)
                d1.metric("Resolution", f"{img_details.get('width', 0)}×{img_details.get('height', 0)}")
                d2.metric("File Size", f"{img_details.get('file_size_kb', 0):.1f} KB")
                d3.metric("Brightness", f"{img_details.get('mean_brightness', 0):.0f}/255")

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
