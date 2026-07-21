# FraudShield AI — Build Tracker

## Week 1 — Done
- [x] Project scaffold + all directories
- [x] `app.py` — 3-tab Streamlit app (runs in demo mode)
- [x] `modules/fraud_shield.py` — IndicBERT loader + GPT-4.1 explanation
- [x] `modules/counterfeit_detector.py` — EfficientNet + Grad-CAM
- [x] `modules/fraud_graph.py` — 265 nodes, phone lookup, Pyvis graph
- [x] `data/prepare_dataset.py` — 1,200 fraud messages (EN/HI/KN/Hinglish)
- [x] `models/train_indicbert.py` — ready to run on Colab Pro
- [x] `models/train_counterfeit.py` — ready (needs currency dataset)
- [x] `data/synthetic_fraud_network.py` — Rs 7.8M losses, 29 states, 265 nodes

## Week 2 — Train Models
- [x] Run `models/train_indicbert.py` on Colab Pro (GPU runtime) — trained, confirmed loading + predicting locally (not demo mode)
- [x] Target >85% weighted F1 on test set — actual: 1.0 F1 on synthetic test set (240 examples), see training logs
- [ ] Known issue: model misclassifies non-templated investment fraud text as "safe" (e.g. casual/typo-laden phrasing outside synthetic training patterns) — decide: patch `data/prepare_dataset.py` with more varied/adversarial examples + retrain, or accept as v1 limitation for demo
- [x] Source Indian currency note dataset from Kaggle — used `iayushanand/currency-dataset500-inr-note-real-fake` (₹500-specific, ~60MB); filtered a separate 7.81GB multi-denomination dataset down to just the `real/500` (649 imgs) and `fake/500` (807 imgs) subfolders on Colab as an alternative source
- [x] Run `models/train_counterfeit.py` on Colab Pro — trained, 99.66% val accuracy (290 val samples, 1 misclassification). Note: val accuracy may be inflated since many "fake" images are `_aug*` augmented duplicates of a smaller base set, and random_split likely leaked near-duplicates across train/val — not fixed, acceptable for hackathon scope
- [x] Verify Grad-CAM overlay renders correctly on uploaded note image — confirmed working, heatmap correctly localizes to portrait/security-feature regions
- [x] Fixed real bug in `modules/counterfeit_detector.py`: was loading the raw training checkpoint dict directly into `model.load_state_dict()`, but `train_counterfeit.py` saves a wrapper dict (`{"model_state_dict": ..., "epoch": ..., "val_acc": ..., "class_names": ...}`) — silently fell back to demo mode with no visible error. Now unwraps `model_state_dict` first.
- [ ] Known issue: model misclassifies novelty/prop currency notes (e.g. joke notes like "Manoranjan Bank of India") as GENUINE with high confidence — training data (photoshopped/edited real-note forgeries) doesn't cover this failure mode. Decided: accept as v1 limitation, do NOT demo with novelty notes, stick to genuine notes or forgery-style fakes similar to training distribution

## Week 3 — Polish + Integration
- [x] Restructured `app.py` from single-page 3-tab layout into a multi-page Streamlit app (`common.py` shared chrome + `pages/1_Citizen_Fraud_Shield.py`, `2_Counterfeit_Detector.py`, `3_Fraud_Network.py`) — sequential sidebar nav instead of tabs
- [x] Hindi + Kannada language toggle in Fraud Shield UI
- [x] Polish all 3 tabs — consistent colors, verdict cards, spacing
- [x] End-to-end integration test (all 3 modules together) — all 3 modules load real models and return predictions; smoke tested 2026-07-21
- [ ] Deploy to Streamlit Cloud — plan: do this LAST once everything else works end-to-end. Model weights are gitignored, so will need Git LFS (or committing binaries directly) before Streamlit Cloud can deploy a working (non-demo-mode) build

## Week 4 — Demo + Submission
- [ ] Architecture diagram (draw.io or Excalidraw)
- [ ] Presentation deck (10 slides max)
- [ ] Demo video script + recording (5 min):
  - Open with digital arrest scam news stat
  - Module 1: paste scam message → verdict in Hindi
  - Module 2: upload Rs 500 note → fake detected + Grad-CAM
  - Module 3: phone number → fraud ring graph expands
  - Close: architecture + scale vision
- [ ] Final Streamlit Cloud smoke test
- [ ] Buffer: edge case tuning, false positive reduction

## Notes / gotchas
- Local dev machine is an Intel Mac (x86_64) — PyTorch dropped Intel Mac wheels after 2.2.2, so `requirements.txt` pins `torch<2.3.0` and `transformers<4.45.0` (which bumped its torch floor to 2.4+). Don't blindly bump these floors without checking platform support again.
- Always run streamlit via the project venv (`source venv/bin/activate` then `which streamlit` should show `.../fraud-shield/venv/bin/streamlit`) — the global-env streamlit install caused a `KeyError: 'url_pathname'` crash and silently ran demo-mode models even with trained weights present.
- Synthetic training data (`data/prepare_dataset.py`) is fully LLM-generated/templated — no real-world "digital arrest"/"KYC scam"/"investment fraud" labeled dataset exists publicly yet (checked; only generic ham/spam sets exist, wrong taxonomy, wrong era). This is the likely root cause of the safe-misclassification issue above.
- Same "narrow training distribution → confident wrong answers on out-of-distribution input" pattern showed up twice now: once on IndicBERT (casual/typo'd investment fraud text → "safe"), once on the counterfeit detector (novelty/prop notes → "GENUINE"). Both models are accurate within their training distribution but will confidently misfire outside it — worth stating as a known scope limitation in the demo/deck rather than discovering it live during judging.
- When wiring a newly trained model into its loader module, check exactly what shape the training script's `torch.save(...)` call wrote (plain state_dict vs. a wrapper dict with metadata) before assuming `torch.load(...)` + `load_state_dict(...)` will just work — this bit us on the counterfeit detector.
