import unicodedata

import pytest

from app.ml.preprocessing import (
    PREPROCESSING_VERSION,
    normalize_text,
    preprocess_text,
    text_fingerprint,
)


def test_normalize_text_uses_nfc_and_collapses_whitespace() -> None:
    composed = "Đường giao thông không sáng\r\n  số 12"
    decomposed = unicodedata.normalize("NFD", composed)

    assert normalize_text(composed) == normalize_text(decomposed)
    assert normalize_text(composed) == "đường giao thông không sáng số 12"


def test_preprocessing_preserves_vietnamese_diacritics_numbers_and_negation() -> None:
    processed = preprocess_text("Đèn đường KHÔNG sáng tại số 12, phường An Hải.")

    assert "không" in processed
    assert "12" in processed
    assert "đèn" in processed
    assert PREPROCESSING_VERSION == "vi-nfc-lower-underthesea-v1"


def test_preprocessing_is_deterministic() -> None:
    text = "Cống thoát nước bị nghẹt ở trước nhà."

    assert preprocess_text(text) == preprocess_text(text)


@pytest.mark.parametrize("value", ["", "   ", "\n\t"])
def test_blank_text_is_rejected(value: str) -> None:
    with pytest.raises(ValueError):
        preprocess_text(value)


def test_non_string_text_is_rejected() -> None:
    with pytest.raises(TypeError):
        normalize_text(None)  # type: ignore[arg-type]


def test_text_fingerprint_uses_normalized_source() -> None:
    assert text_fingerprint("  Đường Hư Hỏng  ") == text_fingerprint("đường hư hỏng")
