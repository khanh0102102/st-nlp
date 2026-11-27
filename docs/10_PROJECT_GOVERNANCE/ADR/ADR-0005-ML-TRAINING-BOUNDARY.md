# ADR-0005: Tách ML training dependencies khỏi API runtime

- Trạng thái: Accepted for local implementation
- Ngày quyết định: 2026-11-27
- Phạm vi: Docker local development và CI; production inference deployment vẫn mở.

## Bối cảnh

API FastAPI phục vụ request, auth, report, review và registry. Training NLP/ML có dependencies lớn hơn (scikit-learn, Underthesea, PyTorch) và workload khác với HTTP request. Cài tất cả thư viện vào API image làm tăng image size và runtime surface.

## Quyết định

1. API runtime chỉ cài backend/requirements.txt; không cài scikit-learn, Underthesea hoặc PyTorch.
2. Classical/tokenizer dependencies nằm trong backend/requirements-ml.txt.
3. Neural dependency nằm trong backend/requirements-neural.txt; local baseline cài Torch từ PyTorch CPU wheel index.
4. backend/Dockerfile có các target runtime, test, ml-training và ml-test.
5. Docker Compose dùng profiles test (api-test, ml-test) và training (one-shot ml-trainer).
6. ml-trainer và API chia sẻ named volume model_artifacts_data.
7. ADR này chưa tạo inference service hoặc activate model. Khi chưa có authenticated active model, API không được trả prediction giả.

## Hệ quả

- API image không chứa PyTorch.
- ML image build lâu hơn và dùng CPU-only PyTorch wheel.
- Neural tests chạy trong image chuyên biệt.
- Training là explicit opt-in; không chạy worker nền khi không cần.
- CLI smoke test chỉ chứng minh entrypoint/argument parsing, không chứng minh training trên dataset thật.
- Model volume cần được bảo vệ/backup; docker compose down -v có thể xóa artifacts và database.
- Production inference topology, model loading isolation, queue, artifact storage signing, verification và resource limits vẫn cần quyết định riêng.

## Bằng chứng

GitHub Actions run #17 (https://github.com/khanh0102102/st-nlp/actions/runs/46036493691) trên commit 58b6acf5890c416b9d55812afdacf6739d74c560:
- Backend suite: 37 passed, 1 skipped (Torch-only suite được tách khỏi API runtime).
- DB-backed NB/SVM training integration: frozen synthetic dataset; TrainingRun, 120 TrainingMetric rows, ModelVersion, artifact checksum và artifact reload passed.
- Neural CPU suite: 8 passed.
- ML trainer CLI --help: passed.
- Docker Compose application startup và health checks: passed.

Đây là bằng chứng local CI, không phải production approval hoặc real-dataset model evaluation.
