import pytest

from app.ml.metrics import evaluate_predictions, flatten_metrics


def test_evaluate_predictions_reports_macro_weighted_and_per_class_metrics() -> None:
    result = evaluate_predictions(
        y_true=["A", "A", "B", "C"],
        y_pred=["A", "B", "B", "C"],
        class_codes=["A", "B", "C"],
    )

    assert result["accuracy"] == pytest.approx(0.75)
    assert result["support"] == 4
    assert result["per_class"]["A"]["support"] == 2
    assert result["per_class"]["B"]["support"] == 1
    assert result["per_class"]["C"]["support"] == 1
    assert result["confusion_matrix"] == [[1, 1, 0], [0, 1, 0], [0, 0, 1]]
    assert 0.0 <= result["f1_macro"] <= 1.0
    assert 0.0 <= result["f1_weighted"] <= 1.0


def test_evaluation_uses_all_declared_classes_even_when_one_is_absent() -> None:
    result = evaluate_predictions(
        y_true=["A", "A"],
        y_pred=["A", "A"],
        class_codes=["A", "B", "C"],
    )

    assert result["per_class"]["C"]["support"] == 0
    assert result["per_class"]["C"]["f1"] == 0.0
    assert len(result["confusion_matrix"]) == 3


def test_invalid_evaluation_inputs_are_rejected() -> None:
    with pytest.raises(ValueError):
        evaluate_predictions([], [], ["A", "B"])
    with pytest.raises(ValueError):
        evaluate_predictions(["A"], ["B", "A"], ["A", "B"])
    with pytest.raises(ValueError):
        evaluate_predictions(["A"], ["UNKNOWN"], ["A", "B"])


def test_flatten_metrics_matches_training_metric_contract() -> None:
    metrics = {
        "TRAIN": evaluate_predictions(
            ["A", "A", "B"], ["A", "B", "B"], ["A", "B", "C"]
        ),
        "TEST": evaluate_predictions(
            ["A", "B"], ["A", "B"], ["A", "B", "C"]
        ),
    }

    rows = flatten_metrics(metrics)
    assert any(
        row["metric_name"] == "accuracy"
        and row["data_split"] == "TRAIN"
        and row["metric_details_json"]["confusion_matrix"]
        for row in rows
    )
    assert any(
        row["metric_name"] == "f1"
        and row["averaging"] == "MACRO"
        and row["data_split"] == "TEST"
        for row in rows
    )
    assert any(
        row["category_code"] == "C"
        and row["metric_name"] == "recall"
        and row["support_count"] == 0
        for row in rows
    )
