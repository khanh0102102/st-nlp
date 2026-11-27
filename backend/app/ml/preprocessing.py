from __future__ import annotations

import hashlib
import re
import unicodedata
from importlib.metadata import PackageNotFoundError, version

PREPROCESSING_VERSION = "vi-nfc-lower-underthesea-v1"
TOKENIZER_NAME = "underthesea.word_tokenize"


def normalize_text(raw_text: str) -> str:
    """Normalize text without removing Vietnamese diacritics, numbers or negation."""
    if not isinstance(raw_text, str):
        raise TypeError("raw_text must be a string.")

    normalized = unicodedata.normalize("NFC", raw_text)
    normalized = normalized.replace("\r\n", "\n").replace("\r", "\n")
    normalized = "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Cc" or character in "\n\t"
    )
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized.lower()


def preprocess_text(raw_text: str) -> str:
    """Return the versioned Vietnamese word-tokenized representation."""
    normalized = normalize_text(raw_text)
    if not normalized:
        raise ValueError("Text must not be empty or whitespace-only.")

    try:
        from underthesea import word_tokenize
    except ImportError as exc:
        raise RuntimeError(
            "Vietnamese tokenization requires the pinned 'underthesea' dependency."
        ) from exc

    tokenized = word_tokenize(normalized, format="text")
    result = " ".join(str(tokenized).split())
    if not result:
        raise ValueError("Text contains no usable tokens after preprocessing.")
    return result


def preprocess_many(raw_texts: list[str]) -> list[str]:
    if not isinstance(raw_texts, list):
        raise TypeError("raw_texts must be a list of strings.")
    return [preprocess_text(item) for item in raw_texts]


def text_fingerprint(raw_text: str) -> str:
    """Stable SHA-256 fingerprint of normalized source text."""
    normalized = normalize_text(raw_text)
    if not normalized:
        raise ValueError("Text must not be empty or whitespace-only.")
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def preprocessing_metadata() -> dict[str, str]:
    try:
        tokenizer_version = version("underthesea")
    except PackageNotFoundError:
        tokenizer_version = "not-installed"
    return {
        "preprocessing_version": PREPROCESSING_VERSION,
        "tokenizer_name": TOKENIZER_NAME,
        "tokenizer_version": tokenizer_version,
        "unicode_normalization": "NFC",
        "case_normalization": "lower",
        "whitespace_normalization": "collapse",
        "stopword_policy": "none; preserve negation and function words",
    }
