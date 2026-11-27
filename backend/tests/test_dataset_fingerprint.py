import unicodedata

from app.api.datasets import _fingerprint
from app.ml.preprocessing import text_fingerprint


def test_dataset_api_uses_shared_preprocessing_fingerprint() -> None:
    raw_text = "  ĐƯỜNG   giao thông KHÔNG sáng tại số 12. "
    equivalent = unicodedata.normalize(
        "NFD",
        "đường giao thông không\ngiao thông không sáng tại số 12.",
    ).replace("giao thông không giao thông", "giao thông")

    assert _fingerprint(raw_text) == text_fingerprint(raw_text)
    assert _fingerprint(raw_text) == _fingerprint(equivalent)


def test_dataset_fingerprint_does_not_require_tokenizer_dependency() -> None:
    # Fingerprinting uses only normalization/hash logic; it must not import Underthesea.
    assert len(_fingerprint("Cống thoát nước bị nghẹt.")) == 64
