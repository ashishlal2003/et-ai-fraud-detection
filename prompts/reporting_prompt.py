"""
Prompt templates for generating pre-filled complaint summaries
for the Cybercrime.gov.in portal.
"""

REPORTING_SYSTEM_PROMPT = """You are a legal documentation assistant helping Indian citizens file
cybercrime complaints on the National Cybercrime Reporting Portal (cybercrime.gov.in).

Generate a clear, factual, formal complaint summary in English that can be copy-pasted
into the complaint form. Use proper legal terminology suitable for Indian law enforcement."""

REPORTING_USER_TEMPLATE = """Generate a formal cybercrime complaint summary for the following incident.
The complaint should be suitable for submission to cybercrime.gov.in.

Incident Details:
- Fraud Type: {fraud_type}
- Suspicious Message/Content: \"\"\"{text}\"\"\"
- AI Confidence Score: {confidence:.0%}
- Date Detected: {date}
- Platform/Channel: {channel}

Please generate:
1. A one-line incident title
2. A formal complaint description (3-4 sentences)
3. Relevant IPC/IT Act sections that may apply
4. Recommended immediate actions for the victim

Format the output clearly with labeled sections."""

# Mapping of fraud labels to user-friendly names
FRAUD_TYPE_LABELS = {
    "digital_arrest": "Digital Arrest Scam",
    "kyc_scam": "KYC/Document Update Fraud",
    "investment_fraud": "Investment/Trading Fraud",
    "safe": "No Fraud Detected",
}

# Relevant legal sections for each fraud type
LEGAL_SECTIONS = {
    "digital_arrest": [
        "Section 66C IT Act (Identity theft)",
        "Section 66D IT Act (Cheating by personation using computer resource)",
        "Section 419 IPC (Cheating by personation)",
        "Section 420 IPC (Cheating and dishonestly inducing delivery of property)",
    ],
    "kyc_scam": [
        "Section 66C IT Act (Identity theft)",
        "Section 66D IT Act (Cheating by personation)",
        "Section 43 IT Act (Unauthorized access)",
        "Section 420 IPC (Cheating)",
    ],
    "investment_fraud": [
        "Section 66 IT Act (Computer related offences)",
        "Section 420 IPC (Cheating)",
        "Section 406 IPC (Criminal breach of trust)",
        "Prize Chits and Money Circulation Schemes (Banning) Act 1978",
    ],
    "safe": [],
}

CYBERCRIME_PORTAL_URL = "https://cybercrime.gov.in"
CYBERCRIME_HELPLINE = "1930"


def build_reporting_prompt(
    text: str,
    fraud_type: str,
    confidence: float,
    date: str,
    channel: str = "SMS/WhatsApp",
) -> str:
    """Build the reporting prompt with incident details."""
    friendly_type = FRAUD_TYPE_LABELS.get(fraud_type, fraud_type)
    return REPORTING_USER_TEMPLATE.format(
        fraud_type=friendly_type,
        text=text,
        confidence=confidence,
        date=date,
        channel=channel,
    )


def get_legal_sections(fraud_type: str) -> list[str]:
    """Return applicable legal sections for a fraud type."""
    return LEGAL_SECTIONS.get(fraud_type, [])
