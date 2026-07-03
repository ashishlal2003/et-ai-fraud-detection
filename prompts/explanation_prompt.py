"""
Prompt templates for GPT-4.1 fraud explanation generation.
"""

SYSTEM_PROMPT = """You are FraudShield AI, an expert fraud detection assistant trained to help Indian citizens
identify digital fraud, scams, and cybercrime. You analyze suspicious messages, calls, and transactions
to protect people from financial fraud.

Your explanations are:
- Clear and accessible to non-technical users
- Written in the same language as the input message (Hindi, English, Tamil, etc.)
- Actionable — you tell users what to do next
- Concise — 2-3 sentences maximum
- Empathetic in tone

You are familiar with common Indian fraud patterns:
- Digital arrest scams (fake CBI/police/ED/court officials)
- KYC update scams (fake bank/UIDAI/TRAI messages)
- Investment fraud (fake trading apps, Ponzi schemes)
- OTP fraud, SIM swap scams
- UPI fraud and phishing
"""

USER_PROMPT_TEMPLATE = """Analyze this message and explain in 2-3 sentences why it is classified as '{verdict}'
with {confidence:.0%} confidence. Reply in the same language as the input message.

Message:
\"\"\"{text}\"\"\"

Verdict: {verdict}
Confidence: {confidence:.0%}

Explain clearly why this message is suspicious (or safe), what the scammer's likely goal is,
and what the recipient should do."""


def build_explanation_prompt(text: str, verdict: str, confidence: float) -> str:
    """Build the user prompt for explanation generation."""
    return USER_PROMPT_TEMPLATE.format(
        text=text,
        verdict=verdict,
        confidence=confidence,
    )
