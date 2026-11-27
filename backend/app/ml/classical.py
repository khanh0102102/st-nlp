from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.svm import LinearSVC

from app.ml.preprocessing import PREPROCESSING_VERSION, preprocess_many, preprocess_text

SUPPORTED_CLASSICAL_FAMILIES = {"NB", "SVM"}


def _build_pipeline(model_family: str, random_seed: int) -> Pipeline:
    if model_family == "NB":
        classifier = MultinomialNB(alpha=1.0)
    elif model_family == "SVM":
        classifier = LinearSVC(
            C=1.0,
            class_weight="balanced",
            dual="auto",
            random_state=random_seed,
        )
    else:
        raise ValueError("Classical model family must be NB or SVM.")

    return Pipeline(
        steps=[
            (
                "preprocess",
                FunctionTransformer(preprocess_many, validate=False),
            ),
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=False,
                    token_pattern=r"(?u)\b\w+\b",
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                ),
            ),
            ("classifier", classifier),
        ]
    )


def fit_classical(
    model_family: str,
    train_texts: list[str],
    train_labels: list[str],
    random_seed: int = 42,
) -> tuple[Pipeline, dict[str, Any]]:
    """Fit a reproducible TF-IDF + NB/SVM pipeline on raw training text."""
    family = model_family.upper()
    if family not in SUPPORTED_CLASSICAL_FAMILIES:
        raise ValueError("model_family must be NB or SVM.")
    if not train_texts or len(train_texts) != len(train_labels):
        raise ValueError("Training texts and labels must be non-empty and equally sized.")
    if len(set(train_labels)) < 2:
        raise ValueError("Classical training requires at least two distinct labels.")
    if any(not isinstance(text, str) or not text.strip() for text in train_texts):
        raise ValueError("Training texts must be non-empty strings.")
    if any(not isinstance(label, str) or not label.strip() for label in train_labels):
        raise ValueError("Training labels must be non-empty strings.")

    pipeline = _build_pipeline(family, random_seed)
    pipeline.fit(train_texts, train_labels)
    classifier = pipeline.named_steps["classifier"]
    metadata = {
        "model_family": family,
        "algorithm_name": "MultinomialNB" if family == "NB" else "LinearSVC",
        "class_codes": [str(value) for value in classifier.classes_],
        "preprocessing_version": PREPROCESSING_VERSION,
        "text_representation": "TFIDF_WORD_NGRAM_1_2",
        "vectorizer": {
            "type": "TfidfVectorizer",
            "ngram_range": [1, 2],
            "sublinear_tf": True,
            "lowercase": False,
            "token_pattern": r"(?u)\b\w+\b",
        },
        "hyperparameters": (
            {"alpha": 1.0}
            if family == "NB"
            else {"C": 1.0, "class_weight": "balanced", "random_seed": random_seed}
        ),
        "confidence_type": (
            "MODEL_PROBABILITY_UNCALIBRATED"
            if family == "NB"
            else "RAW_DECISION_SCORE"
        ),
    }
    return pipeline, metadata


def predict_classical(
    model: Pipeline,
    metadata: dict[str, Any],
    raw_text: str,
) -> dict[str, Any]:
    """Predict one raw report while preserving model-specific score semantics."""
    if not isinstance(raw_text, str) or not raw_text.strip():
        raise ValueError("Prediction text must be a non-empty string.")

    category_code = str(model.predict([raw_text])[0])
    classifier = model.named_steps["classifier"]
    confidence_type = metadata["confidence_type"]

    if confidence_type == "MODEL_PROBABILITY_UNCALIBRATED":
        probabilities = model.predict_proba([raw_text])[0]
        confidence_value = float(np.max(probabilities))
    elif confidence_type == "RAW_DECISION_SCORE":
        decision_values = np.asarray(model.decision_function([raw_text]))
        confidence_value = float(np.max(decision_values))
    else:
        raise ValueError(f"Unsupported confidence type: {confidence_type}")

    if category_code not in set(metadata["class_codes"]):
        raise RuntimeError("Model returned a label outside its stored label mapping.")

    return {
        "category_code": category_code,
        "confidence_value": confidence_value,
        "confidence_type": confidence_type,
        "processed_text": preprocess_text(raw_text),
        "preprocessing_version": metadata["preprocessing_version"],
    }


def save_classical_artifact(
    model: Pipeline,
    metadata: dict[str, Any],
    artifact_path: Path,
) -> None:
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump({"pipeline": model, "metadata": metadata}, artifact_path, compress=3)


def load_classical_artifact(artifact_path: Path) -> tuple[Pipeline, dict[str, Any]]:
    artifact = joblib.load(artifact_path)
    if not isinstance(artifact, dict) or not {"pipeline", "metadata"} <= artifact.keys():
        raise ValueError("Invalid classical model artifact.")
    model = artifact["pipeline"]
    metadata = artifact["metadata"]
    if not isinstance(model, Pipeline) or not isinstance(metadata, dict):
        raise ValueError("Classical model artifact has invalid contents.")
    if metadata.get("model_family") not in SUPPORTED_CLASSICAL_FAMILIES:
        raise ValueError("Classical model artifact has an unsupported family.")
    return model, metadata
