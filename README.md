# FraudShield AI

Indian Digital Public Safety — Streamlit multi-tab application.

## Modules

| Tab | Module | Description |
|-----|--------|-------------|
| Citizen Fraud Shield | IndicBERT | Multilingual fraud text classifier (digital arrest, KYC, investment fraud) |
| Counterfeit Detector | EfficientNet-B0 | Currency note authenticity detection with Grad-CAM |
| Fraud Network | NetworkX + Pyvis | Interactive fraud graph — trace scammers, mules, victims |

## Setup

```bash
git clone <repo-url>
cd fraud-shield
pip install -r requirements.txt
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
streamlit run app.py
```

The app runs in demo mode (no trained models required). Add your OpenAI key for GPT-4.1 explanations.

## Model Training

- **Fraud Shield**: Fine-tune `ai4bharat/indic-bert` on labelled fraud SMS data → save to `models/indicbert_fraud/`
- **Counterfeit Detector**: Fine-tune EfficientNet-B0 on currency dataset → save to `models/efficientnet_currency.pth`

## Report Fraud

- Helpline: **1930**
- Portal: https://cybercrime.gov.in
