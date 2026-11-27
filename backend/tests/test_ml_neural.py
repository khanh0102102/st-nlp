import pytest

torch = pytest.importorskip("torch")

from app.ml.neural import TextCNN, TextLSTM, load_neural_artifact, predict_neural


@pytest.mark.parametrize("model_class", [TextCNN, TextLSTM])
@pytest.mark.parametrize("token_ids", [[[2]], [[2, 3]], [[2, 3, 4, 5]]])
def test_neural_models_accept_short_and_normal_sequences(model_class, token_ids):
    values = torch.tensor(token_ids, dtype=torch.long)
    lengths = torch.tensor([len(token_ids[0])], dtype=torch.long)
    model = model_class(vocab_size=16, class_count=11)
    logits = model(values, lengths)

    assert tuple(logits.shape) == (1, 11)
    assert torch.isfinite(logits).all()


@pytest.mark.parametrize("model_family", ["CNN_1D", "LSTM"])
def test_neural_artifact_round_trip_and_prediction(model_family, tmp_path):
    from app.ml.neural import _build_model

    class_codes = [f"CATEGORY_{index}" for index in range(11)]
    vocabulary = {"<PAD>": 0, "<UNK>": 1, "đèn": 2, "đường": 3}
    model = _build_model(model_family, len(vocabulary), len(class_codes))
    artifact_path = tmp_path / f"{model_family.lower()}.pt"
    artifact = {
        "model_family": model_family,
        "state_dict": model.state_dict(),
        "vocabulary": vocabulary,
        "class_codes": class_codes,
        "max_length": 160,
        "embedding_dim": 128,
        "random_seed": 42,
        "best_epoch": 1,
        "preprocessing_version": "vi-nfc-lower-underthesea-v1",
    }
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(artifact, artifact_path)

    loaded_model, loaded_artifact = load_neural_artifact(artifact_path)
    prediction = predict_neural(loaded_model, loaded_artifact, "đèn")

    assert prediction["category_code"] in class_codes
    assert prediction["confidence_type"] == "MODEL_PROBABILITY_UNCALIBRATED"
    assert prediction["preprocessing_version"] == artifact["preprocessing_version"]
