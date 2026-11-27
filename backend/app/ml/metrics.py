from __future__ import annotations

from collections.abc import Sequence
from typing import Any

from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_recall_fscore_support,
)


def evaluate_predictions(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    class_codes: Sequence[str],
) -> dict[str, Any]:
    """Calculate fixed-label multiclass metrics and a deterministically ordered matrix."""
    true_labels = list(y_true)
    predicted_labels = list(y_pred)
    labels = list(class_codes)

    if not true_labels:
        raise ValueError("Evaluation requires at least one labeled example.")
    if len(true_labels) != len(predicted_labels):
        raise ValueError("y_true and y_pred must have the same length.")
    if len(labels) < 2 or len(labels) != len(set(labels)):
        raise ValueError("class_codes must contain at least two unique labels.")
    if any(not isinstance(label, str) or not label.strip() for label in labels):
        raise ValueError("class_codes must contain non-empty strings.")

    allowed = set(labels)
    unknown = (set(true_labels) | set(predicted_labels)) - allowed
    if unknown:
        raise ValueError("Evaluation contains labels outside class_codes: "
                         + ", ".join(sorted(unknown)))

    precision_macro, recall_macro, f1_macro, _ = precision_recall_fscore_support(
        true_labels, predicted_labels, labels=labels, average="macro", zero_division=0
    )
    (
        precision_weighted,
        recall_weighted,
        f1_weighted,
        _,
    ) = precision_recall_fscore_support(
        true_labels,
        predicted_labels,
        labels=labels,
        average="weighted",
        zero_division=0,
    )
    precision_by_class, recall_by_class, f1_by_class, support_by_class = (
        precision_recall_fscore_support(
            true_labels,
            predicted_labels,
            labels=labels,
            average=None,
            zero_division=0,
        )
    )

    per_class = {
        code: {
            "precision": float(precision_by_class[index]),
            "recall": float(recall_by_class[index]),
            "f1": float(f1_by_class[index]),
            "support": int(support_by_class[index]),
        }
        for index, code in enumerate(labels)
    }

    return {
        "accuracy": float(accuracy_score(true_labels, predicted_labels)),
        "precision_macro": float(precision_macro),
        "recall_macro": float(recall_macro),
        "f1_macro": float(f1_macro),
        "precision_weighted": float(precision_weighted),
        "recall_weighted": float(recall_weighted),
        "f1_weighted": float(f1_weighted),
        "support": len(true_labels),
        "class_codes": labels,
        "per_class": per_class,
        "confusion_matrix": confusion_matrix(
            true_labels, predicted_labels, labels=labels
        ).tolist(),
    }


def flatten_metrics(metrics_by_split: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Convert evaluation results into rows matching the training_metrics table."""
    flattened: list[dict[str, Any]] = []
    for split, result in metrics_by_split.items():
        data_split = split.upper()
        if data_split not in {"TRAIN", "VALIDATION", "TEST"}:
            raise ValueError(f"Unsupported evaluation split: {split}")

        flattened.append(
            {
                "metric_name": "accuracy",
                "metric_value": result["accuracy"],
                "data_split": data_split,
                "averaging": None,
                "category_code": None,
                "support_count": result["support"],
                "metric_details_json": {
                    "class_codes": result["class_codes"],
                    "confusion_matrix": result["confusion_matrix"],
                },
            }
        )
        for metric_name in ("precision", "recall", "f1"):
            for averaging in ("MACRO", "WEIGHTED"):
                key = f"{metric_name}_{averaging.lower()}"
                flattened.append(
                    {
                        "metric_name": metric_name,
                        "metric_value": result[key],
                        "data_split": data_split,
                        "averaging": averaging,
                        "category_code": None,
                        "support_count": result["support"],
                    }
                )

        for category_code, values in result["per_class"].items():
            for metric_name in ("precision", "recall", "f1"):
                flattened.append(
                    {
                        "metric_name": metric_name,
                        "metric_value": values[metric_name],
                        "data_split": data_split,
                        "averaging": None,
                        "category_code": category_code,
                        "support_count": values["support"],
                    }
                )
    return flattened
