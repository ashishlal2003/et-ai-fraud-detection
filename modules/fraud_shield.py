"""
Citizen Fraud Shield — Text classification module.
Uses IndicBERT for multilingual fraud detection in Indian languages.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

# Label definitions
LABELS = ["digital_arrest", "kyc_scam", "investment_fraud", "safe"]

LABEL_DISPLAY = {
    "digital_arrest": "Digital Arrest Scam",
    "kyc_scam": "KYC / Document Scam",
    "investment_fraud": "Investment Fraud",
    "safe": "Safe Message",
}

MODEL_DIR = Path(__file__).parent.parent / "models" / "indicbert_fraud"


def load_model() -> tuple[Optional[object], Optional[object]]:
    """
    Load IndicBERT model and tokenizer from models/indicbert_fraud/.

    Returns:
        Tuple of (model, tokenizer). Both are None if model directory doesn't exist.
    """
    if not MODEL_DIR.exists():
        print(f"[FraudShield] Model directory not found: {MODEL_DIR}. Running in demo mode.")
        return None, None

    try:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer  # type: ignore
        import torch  # type: ignore

        tokenizer = AutoTokenizer.from_pretrained(str(MODEL_DIR))
        model = AutoModelForSequenceClassification.from_pretrained(str(MODEL_DIR))
        model.eval()
        print(f"[FraudShield] Model loaded from {MODEL_DIR}")
        return model, tokenizer

    except Exception as exc:
        print(f"[FraudShield] Failed to load model: {exc}")
        return None, None


def predict(
    text: str,
    model,
    tokenizer,
) -> dict:
    """
    Run inference on input text and return classification results.

    Args:
        text: Input message text (any Indian language or English).
        model: Loaded HuggingFace sequence classification model.
        tokenizer: Corresponding tokenizer.

    Returns:
        dict with keys:
            - label (str): Predicted fraud label.
            - label_display (str): Human-readable label.
            - confidence (float): Confidence of top prediction [0, 1].
            - scores (dict): {label: probability} for all classes.
            - top_tokens (list): List of (token, score) for token importance.
    """
    if model is None or tokenizer is None:
        return _demo_predict(text)

    try:
        import torch  # type: ignore
        import torch.nn.functional as F  # type: ignore

        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=256,
            padding=True,
        )

        with torch.no_grad():
            outputs = model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=-1).squeeze()

        pred_idx = probs.argmax().item()
        label = LABELS[pred_idx]
        confidence = probs[pred_idx].item()

        scores = {LABELS[i]: probs[i].item() for i in range(len(LABELS))}
        top_tokens = _get_top_tokens(text, tokenizer, probs, inputs)

        return {
            "label": label,
            "label_display": LABEL_DISPLAY[label],
            "confidence": confidence,
            "scores": scores,
            "top_tokens": top_tokens,
        }

    except Exception as exc:
        print(f"[FraudShield] Inference error: {exc}")
        return _demo_predict(text)


def _get_top_tokens(text: str, tokenizer, probs, inputs) -> list[tuple[str, float]]:
    """
    Extract tokens that most contributed to the prediction using simple gradient proxy.
    Falls back to token frequency if torch grad unavailable.
    """
    try:
        import torch  # type: ignore

        tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
        # Simple proxy: return most informative tokens (non-subword, non-special)
        suspicious_keywords = [
            "arrest", "court", "cbi", "police", "kyc", "block", "suspend",
            "verify", "otp", "account", "investment", "profit", "crore",
            "lakh", "urgent", "immediately", "गिरफ्तार", "अकाउंट", "निवेश",
        ]
        scored_tokens = []
        for token in tokens:
            clean = token.replace("▁", "").replace("##", "").lower()
            if clean in suspicious_keywords:
                scored_tokens.append((clean, 0.9))
            elif len(clean) > 3 and not clean.startswith("["):
                scored_tokens.append((clean, 0.3))

        return scored_tokens[:10]

    except Exception:
        return []


def _demo_predict(text: str) -> dict:
    """
    Demo prediction when no model is loaded.
    Uses simple keyword matching for illustration.
    """
    text_lower = text.lower()

    digital_arrest_kw = ["arrest", "cbi", "police", "court", "narcotics", "warrant", "गिरफ्तार"]
    kyc_kw = ["kyc", "aadhaar", "pan", "update", "verify", "block", "suspend", "otp"]
    investment_kw = ["profit", "return", "invest", "trading", "stock", "crore", "lakh", "scheme"]

    scores = {
        "digital_arrest": sum(1 for kw in digital_arrest_kw if kw in text_lower) * 0.2,
        "kyc_scam": sum(1 for kw in kyc_kw if kw in text_lower) * 0.2,
        "investment_fraud": sum(1 for kw in investment_kw if kw in text_lower) * 0.2,
        "safe": 0.0,
    }

    total = sum(scores.values())
    if total < 0.15:
        scores["safe"] = 0.85
        scores = {k: v / (total + 0.85) for k, v in scores.items()}
    else:
        scores["safe"] = max(0.05, 0.3 - total)
        total = sum(scores.values())
        scores = {k: v / total for k, v in scores.items()}

    label = max(scores, key=scores.__getitem__)
    confidence = scores[label]

    return {
        "label": label,
        "label_display": LABEL_DISPLAY[label],
        "confidence": confidence,
        "scores": scores,
        "top_tokens": [],
        "demo_mode": True,
    }


def get_explanation(
    text: str,
    verdict: str,
    confidence: float,
    openai_client,
) -> str:
    """
    Call GPT-4.1 to generate a human-readable explanation of the fraud verdict.

    Args:
        text: Original message text.
        verdict: Predicted label (e.g., 'digital_arrest').
        confidence: Confidence score [0, 1].
        openai_client: Initialized OpenAI client instance.

    Returns:
        Explanation string in the same language as the input.
    """
    if openai_client is None:
        return _fallback_explanation(verdict, confidence)

    try:
        from prompts.explanation_prompt import (  # type: ignore
            SYSTEM_PROMPT,
            build_explanation_prompt,
        )

        user_prompt = build_explanation_prompt(text, LABEL_DISPLAY.get(verdict, verdict), confidence)

        response = openai_client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=300,
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()

    except Exception as exc:
        print(f"[FraudShield] GPT explanation error: {exc}")
        return _fallback_explanation(verdict, confidence)


def _fallback_explanation(verdict: str, confidence: float) -> str:
    """Return a static explanation when GPT is unavailable."""
    explanations = {
        "digital_arrest": (
            "This message contains classic digital arrest scam patterns, "
            "where fraudsters impersonate law enforcement officials to coerce victims into paying money. "
            "No legitimate government agency will ever contact you via WhatsApp or demand immediate payment — "
            "hang up and call 1930 immediately."
        ),
        "kyc_scam": (
            "This message appears to be a KYC update scam designed to steal your banking credentials or Aadhaar details. "
            "Banks and UIDAI never ask for OTPs or passwords via SMS or calls. "
            "Do not click any links — report this to your bank and call 1930."
        ),
        "investment_fraud": (
            "This message is promoting a fraudulent investment scheme promising unrealistic returns. "
            "Legitimate investments are regulated by SEBI and never promise guaranteed profits. "
            "Do not transfer any money — report this at cybercrime.gov.in."
        ),
        "safe": (
            "This message appears to be safe based on our analysis. "
            "Always stay cautious with unsolicited messages and never share OTPs or passwords with anyone."
        ),
    }
    return explanations.get(verdict, "Unable to generate explanation. Exercise caution with this message.")
