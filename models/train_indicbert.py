# Run this on Google Colab Pro with GPU runtime
"""
Fine-tune IndicBERT (ai4bharat/indic-bert) for Indian fraud SMS classification.
Labels: digital_arrest=0, kyc_scam=1, investment_fraud=2, safe=3

Usage:
    python models/train_indicbert.py

Expects data/train.csv and data/test.csv (run data/prepare_dataset.py first).
"""

import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import classification_report

# Hugging Face
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    EarlyStoppingCallback,
)
from datasets import Dataset, DatasetDict
import evaluate

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent.parent          # fraud-shield/
DATA_DIR = ROOT / "data"
MODEL_DIR = ROOT / "models" / "indicbert_fraud"
LOG_DIR = ROOT / "models" / "logs"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Label mapping
# ---------------------------------------------------------------------------
LABEL2ID = {
    "digital_arrest": 0,
    "kyc_scam": 1,
    "investment_fraud": 2,
    "safe": 3,
}
ID2LABEL = {v: k for k, v in LABEL2ID.items()}
NUM_LABELS = 4

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

def load_split(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    df = df[["text", "label"]].dropna()
    df["label_id"] = df["label"].map(LABEL2ID)
    df = df.dropna(subset=["label_id"])
    df["label_id"] = df["label_id"].astype(int)
    return df


def df_to_hf_dataset(df: pd.DataFrame) -> Dataset:
    return Dataset.from_dict({"text": df["text"].tolist(), "label": df["label_id"].tolist()})


# ---------------------------------------------------------------------------
# Tokenisation
# ---------------------------------------------------------------------------
MODEL_NAME = "ai4bharat/indic-bert"
MAX_LENGTH = 128


def get_tokenizer():
    return AutoTokenizer.from_pretrained(MODEL_NAME)


def tokenize_fn(examples, tokenizer):
    return tokenizer(
        examples["text"],
        max_length=MAX_LENGTH,
        padding="max_length",
        truncation=True,
    )


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------
accuracy_metric = evaluate.load("accuracy")
f1_metric = evaluate.load("f1")


def compute_metrics(eval_pred):
    logits, labels = eval_pred
    predictions = np.argmax(logits, axis=-1)
    acc = accuracy_metric.compute(predictions=predictions, references=labels)["accuracy"]
    f1 = f1_metric.compute(predictions=predictions, references=labels, average="weighted")["f1"]
    return {"accuracy": acc, "f1": f1}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    train_path = DATA_DIR / "train.csv"
    test_path = DATA_DIR / "test.csv"

    for p in (train_path, test_path):
        if not p.exists():
            print(f"ERROR: {p} not found. Run data/prepare_dataset.py first.")
            sys.exit(1)

    print("Loading data ...")
    train_df = load_split(train_path)
    test_df = load_split(test_path)
    print(f"  Train: {len(train_df)} samples | Test: {len(test_df)} samples")
    print(f"  Label dist (train):\n{train_df['label'].value_counts().to_string()}")

    print(f"\nLoading tokenizer from '{MODEL_NAME}' ...")
    tokenizer = get_tokenizer()

    train_ds = df_to_hf_dataset(train_df)
    test_ds = df_to_hf_dataset(test_df)

    print("Tokenizing ...")
    train_ds = train_ds.map(lambda x: tokenize_fn(x, tokenizer), batched=True, batch_size=256)
    test_ds = test_ds.map(lambda x: tokenize_fn(x, tokenizer), batched=True, batch_size=256)

    format_columns = [c for c in ["input_ids", "attention_mask", "token_type_ids", "label"] if c in train_ds.column_names]
    train_ds.set_format(type="torch", columns=format_columns)
    test_ds.set_format(type="torch", columns=format_columns)

    print(f"\nLoading model from '{MODEL_NAME}' ...")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=NUM_LABELS,
        id2label=ID2LABEL,
        label2id=LABEL2ID,
        ignore_mismatched_sizes=True,
    )

    training_args = TrainingArguments(
        output_dir=str(MODEL_DIR),
        num_train_epochs=5,
        per_device_train_batch_size=16,
        per_device_eval_batch_size=32,
        warmup_steps=100,
        weight_decay=0.01,
        logging_dir=str(LOG_DIR),
        logging_steps=50,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="f1",
        greater_is_better=True,
        report_to="none",         # set to "tensorboard" or "wandb" if needed
        seed=42,
        fp16=False,               # set True if GPU supports it
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_ds,
        eval_dataset=test_ds,
        processing_class=tokenizer,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )

    print("\n=== Starting training ===")
    trainer.train()

    print("\n=== Evaluating on test set ===")
    metrics = trainer.evaluate(test_ds)
    print(f"  Test Accuracy : {metrics.get('eval_accuracy', 'N/A'):.4f}")
    print(f"  Test F1 (wtd) : {metrics.get('eval_f1', 'N/A'):.4f}")

    # Detailed classification report
    print("\n=== Classification Report ===")
    preds_output = trainer.predict(test_ds)
    pred_labels = np.argmax(preds_output.predictions, axis=-1)
    true_labels = preds_output.label_ids
    print(classification_report(
        true_labels,
        pred_labels,
        target_names=[ID2LABEL[i] for i in range(NUM_LABELS)],
    ))

    # Save best model
    print(f"\nSaving model to {MODEL_DIR} ...")
    trainer.save_model(str(MODEL_DIR))
    tokenizer.save_pretrained(str(MODEL_DIR))
    print("Done.")

    # Print example inference
    print("\n=== Quick inference example ===")
    from transformers import pipeline
    clf = pipeline(
        "text-classification",
        model=str(MODEL_DIR),
        tokenizer=str(MODEL_DIR),
        device=-1,  # CPU; change to 0 for GPU
    )
    test_texts = [
        "Aapka Aadhaar number illegal activities mein use hua hai. Digital arrest mein hain.",
        "Your SBI account will be blocked. Update KYC immediately.",
        "Earn Rs 50,000 per day from home. Bitcoin double in 7 days.",
        "Your OTP for SBI net banking is 847293. Do not share with anyone.",
    ]
    for text in test_texts:
        result = clf(text, truncation=True, max_length=MAX_LENGTH)[0]
        print(f"  [{result['label']} | {result['score']:.3f}] {text[:80]}")


if __name__ == "__main__":
    main()
