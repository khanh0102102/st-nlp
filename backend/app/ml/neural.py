from __future__ import annotations

import random
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence
from torch.utils.data import DataLoader, Dataset

from app.ml.metrics import evaluate_predictions
from app.ml.preprocessing import PREPROCESSING_VERSION, preprocess_text

PAD = "<PAD>"
UNK = "<UNK>"
MAX_LENGTH = 160
EMBEDDING_DIM = 128
BATCH_SIZE = 32


class EncodedTextDataset(Dataset):
    def __init__(self, sequences: list[list[int]], labels: list[int]):
        self.sequences = sequences
        self.labels = labels

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, index: int):
        sequence = self.sequences[index]
        return (
            torch.tensor(sequence, dtype=torch.long),
            len(sequence),
            torch.tensor(self.labels[index], dtype=torch.long),
        )


def build_vocabulary(texts: list[str]) -> dict[str, int]:
    counts = Counter(
        token
        for text in texts
        for token in preprocess_text(text).split()
    )
    vocabulary = {PAD: 0, UNK: 1}
    for token, _ in counts.most_common():
        if token not in vocabulary:
            vocabulary[token] = len(vocabulary)
    return vocabulary


def encode_text(
    text: str,
    vocabulary: dict[str, int],
    max_length: int = MAX_LENGTH,
) -> list[int]:
    tokens = preprocess_text(text).split()[:max_length]
    encoded = [vocabulary.get(token, vocabulary[UNK]) for token in tokens]
    return encoded or [vocabulary[UNK]]


def collate_batch(batch):
    sequences, lengths, labels = zip(*batch)
    maximum = max(lengths)
    padded = torch.zeros((len(batch), maximum), dtype=torch.long)
    for index, sequence in enumerate(sequences):
        padded[index, : len(sequence)] = sequence
    return padded, torch.tensor(lengths), torch.stack(labels)


class TextCNN(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        class_count: int,
        embedding_dim: int = EMBEDDING_DIM,
        filters: int = 96,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.convolutions = nn.ModuleList(
            [nn.Conv1d(embedding_dim, filters, kernel_size=k) for k in (2, 3, 4)]
        )
        self.dropout = nn.Dropout(0.35)
        self.output = nn.Linear(filters * 3, class_count)

    def forward(self, token_ids: torch.Tensor, lengths: torch.Tensor):
        embedded = self.embedding(token_ids).transpose(1, 2)
        minimum_length = max(convolution.kernel_size[0] for convolution in self.convolutions)
        if embedded.size(2) < minimum_length:
            embedded = nn.functional.pad(
                embedded,
                (0, minimum_length - embedded.size(2)),
            )
        pooled = []
        for kernel, convolution in zip((2, 3, 4), self.convolutions):
            activations = torch.relu(convolution(embedded))
            valid_lengths = torch.clamp(lengths - kernel + 1, min=1)
            positions = torch.arange(
                activations.size(2), device=activations.device
            ).unsqueeze(0)
            mask = positions >= valid_lengths.to(activations.device).unsqueeze(1)
            activations = activations.masked_fill(mask.unsqueeze(1), float("-inf"))
            pooled.append(activations.max(dim=2).values)
        return self.output(self.dropout(torch.cat(pooled, dim=1)))


class TextLSTM(nn.Module):
    def __init__(
        self,
        vocab_size: int,
        class_count: int,
        embedding_dim: int = EMBEDDING_DIM,
        hidden_size: int = 96,
    ):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embedding_dim,
            hidden_size,
            batch_first=True,
            bidirectional=True,
        )
        self.dropout = nn.Dropout(0.35)
        self.output = nn.Linear(hidden_size * 2, class_count)

    def forward(self, token_ids: torch.Tensor, lengths: torch.Tensor):
        embedded = self.embedding(token_ids)
        packed = pack_padded_sequence(
            embedded,
            lengths.cpu(),
            batch_first=True,
            enforce_sorted=False,
        )
        _, (hidden, _) = self.lstm(packed)
        representation = torch.cat((hidden[-2], hidden[-1]), dim=1)
        return self.output(self.dropout(representation))


def _build_model(
    model_family: str,
    vocab_size: int,
    class_count: int,
) -> nn.Module:
    if model_family == "CNN_1D":
        return TextCNN(vocab_size, class_count)
    if model_family == "LSTM":
        return TextLSTM(vocab_size, class_count)
    raise ValueError("Deep model family must be CNN_1D or LSTM.")


def _encode_many(
    texts: list[str],
    vocabulary: dict[str, int],
) -> list[list[int]]:
    return [encode_text(text, vocabulary) for text in texts]


def _predict_batches(
    model: nn.Module,
    texts: list[str],
    vocabulary: dict[str, int],
    class_codes: list[str],
    device: torch.device,
) -> tuple[list[str], list[float]]:
    dataset = EncodedTextDataset(
        _encode_many(texts, vocabulary),
        [0] * len(texts),
    )
    loader = DataLoader(
        dataset,
        batch_size=BATCH_SIZE,
        shuffle=False,
        collate_fn=collate_batch,
    )
    predictions: list[str] = []
    confidence: list[float] = []
    model.eval()
    with torch.no_grad():
        for token_ids, lengths, _ in loader:
            logits = model(token_ids.to(device), lengths.to(device))
            probabilities = torch.softmax(logits, dim=1)
            values, indices = probabilities.max(dim=1)
            predictions.extend(class_codes[int(index)] for index in indices.cpu())
            confidence.extend(float(value) for value in values.cpu())
    return predictions, confidence


def train_neural(
    *,
    model_family: str,
    train_texts: list[str],
    train_labels: list[str],
    validation_texts: list[str],
    validation_labels: list[str],
    test_texts: list[str],
    test_labels: list[str],
    class_codes: list[str],
    output_path: Path,
    random_seed: int = 42,
    epochs: int = 15,
    patience: int = 4,
) -> tuple[dict[str, Any], dict[str, Any]]:
    if model_family not in {"CNN_1D", "LSTM"}:
        raise ValueError("Neural model family must be CNN_1D or LSTM.")
    if not (len(train_texts) == len(train_labels) and train_texts):
        raise ValueError("Neural training data must be non-empty and aligned.")
    if len(validation_texts) != len(validation_labels) or not validation_texts:
        raise ValueError("Neural validation data must be non-empty and aligned.")
    if len(test_texts) != len(test_labels) or not test_texts:
        raise ValueError("Neural test data must be non-empty and aligned.")
    if set(train_labels + validation_labels + test_labels) - set(class_codes):
        raise ValueError("Neural data contains labels outside class_codes.")
    if set(train_labels) != set(class_codes):
        raise ValueError("TRAIN split must contain every configured class.")
    if epochs < 1 or patience < 1:
        raise ValueError("epochs and patience must be positive.")

    random.seed(random_seed)
    np.random.seed(random_seed)
    torch.manual_seed(random_seed)
    device = torch.device("cpu")

    vocabulary = build_vocabulary(train_texts)
    label_to_index = {label: index for index, label in enumerate(class_codes)}
    train_indices = [label_to_index[label] for label in train_labels]
    train_dataset = EncodedTextDataset(
        _encode_many(train_texts, vocabulary), train_indices
    )
    train_loader = DataLoader(
        train_dataset,
        batch_size=BATCH_SIZE,
        shuffle=True,
        collate_fn=collate_batch,
    )

    model = _build_model(model_family, len(vocabulary), len(class_codes)).to(device)
    class_counts = Counter(train_indices)
    weights = torch.tensor(
        [
            len(train_indices) / max(1, class_counts[index] * len(class_codes))
            for index in range(len(class_codes))
        ],
        dtype=torch.float,
    )
    criterion = nn.CrossEntropyLoss(weight=weights)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)

    best_f1 = -1.0
    best_state = None
    best_epoch = 0
    waiting = 0
    for epoch in range(1, epochs + 1):
        model.train()
        for token_ids, lengths, labels in train_loader:
            optimizer.zero_grad(set_to_none=True)
            logits = model(token_ids.to(device), lengths.to(device))
            loss = criterion(logits, labels.to(device))
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            optimizer.step()

        validation_predictions, _ = _predict_batches(
            model, validation_texts, vocabulary, class_codes, device
        )
        validation_metrics = evaluate_predictions(
            validation_labels, validation_predictions, class_codes
        )
        if validation_metrics["f1_macro"] > best_f1:
            best_f1 = validation_metrics["f1_macro"]
            best_epoch = epoch
            best_state = {
                key: value.detach().cpu().clone()
                for key, value in model.state_dict().items()
            }
            waiting = 0
        else:
            waiting += 1
            if waiting >= patience:
                break

    if best_state is None:
        raise RuntimeError("Neural training did not produce a valid checkpoint.")

    model.load_state_dict(best_state)
    model.eval()
    test_predictions, _ = _predict_batches(
        model, test_texts, vocabulary, class_codes, device
    )
    train_predictions, _ = _predict_batches(
        model, train_texts, vocabulary, class_codes, device
    )
    validation_predictions, _ = _predict_batches(
        model, validation_texts, vocabulary, class_codes, device
    )
    metrics = {
        "TRAIN": evaluate_predictions(train_labels, train_predictions, class_codes),
        "VALIDATION": evaluate_predictions(
            validation_labels, validation_predictions, class_codes
        ),
        "TEST": evaluate_predictions(test_labels, test_predictions, class_codes),
    }

    artifact = {
        "model_family": model_family,
        "state_dict": best_state,
        "vocabulary": vocabulary,
        "class_codes": class_codes,
        "max_length": MAX_LENGTH,
        "embedding_dim": EMBEDDING_DIM,
        "random_seed": random_seed,
        "best_epoch": best_epoch,
        "preprocessing_version": PREPROCESSING_VERSION,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(artifact, output_path)
    metadata = {
        "model_family": model_family,
        "class_codes": class_codes,
        "preprocessing_version": PREPROCESSING_VERSION,
        "random_seed": random_seed,
        "best_epoch": best_epoch,
        "confidence_type": "MODEL_PROBABILITY_UNCALIBRATED",
    }
    return metadata, metrics


def load_neural_artifact(path: Path) -> tuple[nn.Module, dict[str, Any]]:
    artifact = torch.load(path, map_location="cpu", weights_only=False)
    class_codes = artifact["class_codes"]
    model = _build_model(
        artifact["model_family"],
        len(artifact["vocabulary"]),
        len(class_codes),
    )
    model.load_state_dict(artifact["state_dict"])
    model.eval()
    return model, artifact


def predict_neural(
    model: nn.Module,
    artifact: dict[str, Any],
    raw_text: str,
) -> dict[str, Any]:
    vocabulary = artifact["vocabulary"]
    encoded = encode_text(raw_text, vocabulary, artifact["max_length"])
    token_ids = torch.tensor([encoded], dtype=torch.long)
    lengths = torch.tensor([len(encoded)])
    model.eval()
    with torch.no_grad():
        logits = model(token_ids, lengths)
        probabilities = torch.softmax(logits, dim=1)[0]
        score, index = probabilities.max(dim=0)
    return {
        "category_code": artifact["class_codes"][int(index)],
        "confidence_value": float(score),
        "confidence_type": "MODEL_PROBABILITY_UNCALIBRATED",
        "processed_text": preprocess_text(raw_text),
        "preprocessing_version": artifact["preprocessing_version"],
    }
