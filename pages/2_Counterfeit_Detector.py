"""Counterfeit Currency Detector — CV-based note authenticity check."""

from __future__ import annotations

import streamlit as st

from common import apply_page_config, render_sidebar, load_counterfeit_model

apply_page_config("Counterfeit Detector", "💵")
render_sidebar()

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    "<div class='section-header'>💵 Currency Authenticity Detector</div>"
    "<div class='section-sub'>"
    "Upload a photo of an Indian currency note to verify its authenticity. "
    "EfficientNet highlights suspicious regions via Grad-CAM visualization."
    "</div>",
    unsafe_allow_html=True,
)

# ── Model loading ─────────────────────────────────────────────────────────────
with st.spinner("Loading currency detection model…"):
    cc_model = load_counterfeit_model()

cc_model_loaded = cc_model is not None

# ── Upload controls ───────────────────────────────────────────────────────────
denomination = "₹500"  # model trained on ₹500 notes only

st.markdown(
    "<div style='display:inline-block; background:#21262d; border:1px solid #30363d; "
    "border-radius:6px; padding:4px 12px; font-size:0.82rem; color:#8b949e; margin-bottom:12px;'>"
    "💵 ₹500 notes &nbsp;·&nbsp; <span style='color:#484f58;'>₹100 / ₹200 support coming in v2</span>"
    "</div>",
    unsafe_allow_html=True,
)

uploaded_file = st.file_uploader(
    "Upload ₹500 currency note image",
    type=["jpg", "jpeg", "png", "webp"],
    help="Upload front side of note, well-lit, flat surface. 1 MP+ recommended.",
    label_visibility="visible",
)

st.markdown(
    "<p style='color:#8b949e; font-size:0.82rem; margin-top:-8px; margin-bottom:16px;'>"
    "Tip: place the note on a plain background, ensure good lighting, and keep the camera flat above the note."
    "</p>",
    unsafe_allow_html=True,
)

# ── Upload placeholder (no file yet) ─────────────────────────────────────────
if uploaded_file is None:
    if not cc_model_loaded:
        st.markdown(
            """
            <div style="border:1px dashed #30363d; border-radius:12px;
                        padding:40px 32px; text-align:center; margin:12px 0;
                        background:#161b22;">
                <span style="font-size:40px;">💵</span>
                <p style="color:#8b949e; margin-top:12px; font-size:15px;">
                    Upload a currency note photo above to begin analysis
                </p>
                <p style="color:#484f58; font-size:0.8rem; font-style:italic; margin-top:8px;">
                    EfficientNet model not found at
                    <code style="color:#484f58;">models/efficientnet_currency.pth</code>
                    — running in demo mode.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="border:2px dashed #21262d; border-radius:12px;
                        padding:48px; text-align:center; margin:20px 0;">
                <span style="font-size:48px;">💵</span>
                <p style="color:#8b949e; margin-top:12px; font-size:15px;">
                    Upload a currency note photo above to begin analysis
                </p>
                <p style="color:#30363d; font-size:12px;">
                    Supported: JPG, PNG, WebP &middot; Recommended: 1 MP+ resolution, good lighting
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ── Analysis when file uploaded ───────────────────────────────────────────────
if uploaded_file is not None:
    image_bytes = uploaded_file.read()

    # Run inference first so result is available for layout
    with st.spinner("Analyzing currency note…"):
        try:
            from modules.counterfeit_detector import predict, get_gradcam, get_analysis_details  # type: ignore

            cc_result   = predict(image_bytes, cc_model)
            gradcam_img = get_gradcam(image_bytes, cc_model)
            img_details = get_analysis_details(image_bytes)
        except ImportError as exc:
            st.error(f"Module import error: {exc}")
            cc_result   = None
            gradcam_img = None
            img_details = {}

    # ── Image pair: original + Grad-CAM ──────────────────────────────────────
    col_orig, col_cam = st.columns(2)
    with col_orig:
        st.markdown(
            f"<p style='font-weight:600; color:#c9d1d9; margin-bottom:6px;'>"
            f"Original — {denomination}</p>",
            unsafe_allow_html=True,
        )
        st.image(image_bytes, use_container_width=True)

    with col_cam:
        st.markdown(
            "<p style='font-weight:600; color:#c9d1d9; margin-bottom:6px;'>"
            "Grad-CAM — suspicious regions highlighted</p>",
            unsafe_allow_html=True,
        )
        if gradcam_img is not None:
            st.image(gradcam_img, use_container_width=True)
        else:
            st.markdown(
                """
                <div style="background:#161b22; border:1px solid #21262d; border-radius:8px;
                            height:200px; display:flex; align-items:center; justify-content:center;">
                    <span style="color:#484f58; font-style:italic; font-size:0.875rem;">
                        Grad-CAM visualization unavailable
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # ── Verdict box ───────────────────────────────────────────────────────────
    if cc_result:
        verdict       = cc_result["verdict"]
        cc_confidence = cc_result["confidence"]
        scores        = cc_result.get("scores", {})

        is_genuine = verdict == "REAL"
        if is_genuine:
            vdict_word   = "GENUINE"
            verdict_icon = "✅"
            box_bg       = "#0d2b1d"
            box_border   = "#2ea043"
            box_color    = "#2ea043"
            verdict_note = "Note appears authentic based on visual analysis. Always verify security features physically for high-value transactions."
        else:
            vdict_word   = "COUNTERFEIT"
            verdict_icon = "🚨"
            box_bg       = "#2b0d0d"
            box_border   = "#f85149"
            box_color    = "#f85149"
            verdict_note = "Note shows signs of being counterfeit. Do not accept or use this note."

        st.markdown(
            f"""
            <div style="
                background:{box_bg};
                border:2px solid {box_border};
                border-radius:12px;
                padding:24px 28px;
                margin:20px 0 12px;
            ">
                <div style="font-size:2rem; font-weight:800; color:{box_color}; letter-spacing:1px;">
                    {verdict_icon}&nbsp;{vdict_word}
                </div>
                <div style="font-size:1.5rem; font-weight:700; color:{box_color}; margin-top:4px;">
                    {cc_confidence:.1%} confidence
                </div>
                <div style="color:#8b949e; font-size:0.875rem; margin-top:8px;">
                    {verdict_note}
                </div>
                <div style="background:#21262d; border-radius:6px; height:8px; margin-top:14px;">
                    <div style="
                        width:{cc_confidence*100:.1f}%;
                        background:{box_color};
                        height:8px;
                        border-radius:6px;
                    "></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ── Probability metrics ───────────────────────────────────────────────
        col_r, col_f = st.columns(2)
        with col_r:
            st.metric("Genuine Probability", f"{scores.get('REAL', 0):.1%}")
        with col_f:
            st.metric("Counterfeit Probability", f"{scores.get('FAKE', 0):.1%}")

        # ── Image details ─────────────────────────────────────────────────────
        if img_details:
            with st.expander("📐 Image Analysis Details"):
                d1, d2, d3 = st.columns(3)
                d1.metric("Resolution", f"{img_details.get('width', 0)}×{img_details.get('height', 0)}")
                d2.metric("File Size", f"{img_details.get('file_size_kb', 0):.1f} KB")
                d3.metric("Brightness", f"{img_details.get('mean_brightness', 0):.0f}/255")

        # ── Physical checklist ────────────────────────────────────────────────
        st.markdown("---")
        st.markdown("**✅ Physical Security Feature Checklist** *(verify manually)*")
        features = [
            ("Watermark",           "Hold note against light — Mahatma Gandhi portrait should appear"),
            ("Security Thread",     "Embedded thread reads 'भारत' and 'RBI' alternately"),
            ("Colour-shifting Ink", "Number panel shifts from green to blue when tilted"),
            ("Micro-lettering",     "'RBI' and 'भारत' visible under magnification on ₹100+"),
            ("Raised Print",        "Intaglio printing — feel raised texture on portrait and numerals"),
            ("See-through Register","Floral design on obverse and reverse align perfectly"),
        ]
        chk_col1, chk_col2 = st.columns(2)
        for i, (feature, desc) in enumerate(features):
            col = chk_col1 if i % 2 == 0 else chk_col2
            col.checkbox(f"**{feature}** — {desc}", key=f"feat_{i}")

        if cc_result.get("demo_mode"):
            st.markdown(
                "<p style='color:#484f58; font-style:italic; font-size:0.8rem; margin-top:20px;'>"
                "Prediction is illustrative — demo mode, not based on a trained model."
                "</p>",
                unsafe_allow_html=True,
            )

# ── Advisory note ─────────────────────────────────────────────────────────────
st.markdown(
    "<p style='color:#484f58; font-style:italic; font-size:0.8rem; margin-top:32px;'>"
    "This tool is for advisory use only. Report suspected FICN (Fake Indian Currency Notes) "
    "to your nearest bank branch or police station."
    "</p>",
    unsafe_allow_html=True,
)
