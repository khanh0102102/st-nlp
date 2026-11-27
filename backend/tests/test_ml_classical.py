import pytest

from app.ml.classical import fit_classical, predict_classical


@pytest.mark.parametrize(
    ("family", "confidence_type"),
    [
        ("NB", "MODEL_PROBABILITY_UNCALIBRATED"),
        ("SVM", "RAW_DECISION_SCORE"),
    ],
)
def test_classical_pipeline_trains_and_preserves_confidence_semantics(
    family: str,
    confidence_type: str,
) -> None:
    texts = [
        "Đường có nhiều ổ gà và mặt đường bị hư hỏng",
        "Mặt đường xuất hiện vết nứt và ổ gà",
        "Đèn đường không sáng vào ban đêm",
        "Hệ thống chiếu sáng bị mất điện",
    ]
    labels = ["ROAD_BRIDGE_INFRA_DAMAGE", "ROAD_BRIDGE_INFRA_DAMAGE",
              "POWER_LIGHTING", "POWER_LIGHTING"]

    model, metadata = fit_classical(family, texts, labels, random_seed=7)
    result = predict_classical(model, metadata, "Đèn đường không sáng")

    assert metadata["confidence_type"] == confidence_type
    assert result["category_code"] == "POWER_LIGHTING"
    assert result["confidence_type"] == confidence_type
    assert isinstance(result["confidence_value"], float)
    assert result["preprocessing_version"] == "vi-nfc-lower-underthesea-v1"


def test_classical_training_rejects_single_class_and_mismatched_rows() -> None:
    with pytest.raises(ValueError):
        fit_classical("NB", ["đường hư"], ["ROAD"])
    with pytest.raises(ValueError):
        fit_classical("SVM", ["đường hư"], ["ROAD", "POWER"])


def test_classical_artifact_round_trip(tmp_path) -> None:
    from app.ml.classical import load_classical_artifact, save_classical_artifact

    model, metadata = fit_classical(
        "NB",
        [
            "Đường có ổ gà",
            "Mặt đường bị nứt",
            "Đèn đường không sáng",
            "Đèn tín hiệu bị hỏng",
        ],
        ["ROAD", "ROAD", "POWER", "POWER"],
    )
    path = tmp_path / "models" / "nb.joblib"

    save_classical_artifact(model, metadata, path)
    restored_model, restored_metadata = load_classical_artifact(path)

    assert restored_metadata == metadata
    assert predict_classical(restored_model, restored_metadata, "Đèn đường hỏng")[
        "category_code"
    ] == "POWER"
