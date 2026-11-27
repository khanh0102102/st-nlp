# IMPLEMENTATION STATUS — ST-NLP

Ngày cập nhật: 2026-11-27

## Repository và bằng chứng

- Repository: https://github.com/khanh0102102/st-nlp
- Base branch: main — chưa được thay đổi trong đợt triển khai này.
- Working branch: feature/project-foundation.
- Code snapshot đã được CI xác minh: 4af33cedd814c69784a47fe37cc4b8924668a02f.
- Branch compare sau commit code: ahead 17, behind 0 so với main.
- Không tự tạo/merge PR; việc đưa feature vào main cần được chủ dự án duyệt.

### CI evidence

GitHub Actions run #14 (46035149937), conclusion success, trên commit 4af33cedd814c69784a47fe37cc4b8924668a02f.

| Hạng mục | Kết quả | Ghi chú |
|---|---|---|
| Compose validation | PASS | docker compose config --quiet |
| Docker builds | PASS | app, backend test và CPU ML test/training stages |
| Fresh PostgreSQL migration | PASS | Alembic initial schema |
| Seed danh mục | PASS | Xác minh đúng 11 categories |
| Backend pytest | PASS | 33 passed, 1 skipped trong API runtime image |
| Neural component tests | PASS | 8 passed trong image có CPU PyTorch |
| ML trainer CLI smoke | PASS | python -m app.ml.cli --help qua Compose profile |
| Application startup | PASS | API và web khởi động |
| Health checks | PASS | frontend /health, API /health/live và /health/ready |

Test bị skip trong backend image là module phụ thuộc PyTorch; phần neural tương ứng được chạy riêng trong CPU ML test image và có 8 test pass. CI là kiểm thử foundation trên GitHub runner, không chứng minh training run dùng dataset thật hoặc Google OAuth với credentials thật.

## Trạng thái theo subsystem

| Subsystem | Trạng thái | Bằng chứng / giới hạn |
|---|---|---|
| Docker/local foundation | DONE cho local CI baseline | Compose validation/build/start và health checks pass trong run #14; production deployment chưa nghiệm thu |
| Database | DONE cho schema foundation | 12 SQLAlchemy business models, initial migration, integrity constraints/triggers; CI migrate database mới |
| Category catalog | DONE | Đúng 11 category code và order; seed verified trong CI |
| Backend core/auth | PARTIAL | Session/CSRF/role checks, staff login và Google OIDC flow có code; Google OAuth thật chưa xác minh |
| Citizen APIs | PARTIAL | Profile/report/attachment foundations hiện có; full citizen workflow chưa nghiệm thu |
| Admin APIs | PARTIAL | Report review/history, dashboard/map, dataset/model APIs hiện có; coverage authorization và workflow còn thiếu |
| Dataset management | PARTIAL | Dataset/sample CRUD, validation và freeze protections có nền tảng; chưa có dataset thật được cung cấp và duyệt |
| Model registry | PARTIAL | Registry API/model version schema có; chưa có active model được đánh giá trên dữ liệu thật |
| Vietnamese preprocessing | DONE ở mức module | NFC/lowercase/whitespace, Underthesea tokenizer, version metadata và fingerprint; tests pass |
| Metrics | DONE ở mức module | Accuracy, macro/weighted precision-recall-F1, per-class support và confusion matrix; tests pass |
| Classical NLP | DONE ở mức model component | TF-IDF word n-gram + MultinomialNB/LinearSVC, fit/predict parity và artifact save/load tests; chưa đánh giá chất lượng trên dataset thực |
| CNN 1D / BiLSTM | PARTIAL | Model components, CPU artifact load/predict, short-sequence tests; 8 tests pass; training lifecycle trên dataset/database chưa E2E verified |
| Training orchestration | PARTIAL | Frozen dataset guard, split checks, metrics/registry persistence và Docker CLI đã có; CLI --help smoke pass; train execution với real/approved dataset chưa xác minh |
| Inference integration | NOT_STARTED / BLOCKED | Chưa có authenticated inference service hoàn chỉnh và active model; không tạo prediction giả khi thiếu model |
| Frontend | PARTIAL | React/Vite/Nginx status foundation; Citizen Portal, Admin Portal, interactive map và operational dashboards chưa hoàn thành |
| Full integration / E2E | NOT_STARTED | Chưa chứng minh trọn luồng citizen report → review → frozen dataset → training → active inference |
| Production readiness | NOT_READY | OAuth, secrets, persistent storage, monitoring, backups, security review, NFR và deployment còn mở |

## ML implementation detail

- Preprocessing version hiện tại: vi-nfc-lower-underthesea-v1.
- Giữ dấu tiếng Việt, số và từ phủ định; không áp dụng stopword removal mặc định.
- Classical pipeline: preprocessing → TF-IDF unigram/bigram → NB hoặc LinearSVC.
- NB dùng MODEL_PROBABILITY_UNCALIBRATED; SVM dùng RAW_DECISION_SCORE.
- CNN/LSTM chạy trong training/test image riêng; API runtime không cài PyTorch.
- CPU neural dependency được cài từ PyTorch CPU wheel index.
- Artifacts được ghi dưới MODEL_ARTIFACTS_DIR và lưu checksum/metadata trong model registry khi training transaction hoàn tất.
- Không được xem test model component là bằng chứng model đạt chất lượng phân loại đô thị thực tế.

## Invariants bắt buộc

- Chính xác 11 category codes theo classification specification.
- Chính xác 12 bảng nghiệp vụ được phê duyệt.
- reports.raw_content bất biến.
- Predictions và prediction reviews append-only.
- reports.final_category_id chỉ được đặt sau authorized human review.
- Dataset FROZEN và samples của nó bất biến.
- Training chỉ dùng dataset FROZEN.
- Không tạo nhãn OTHER mặc định cho input lỗi/thiếu thông tin.
- Không bịa confidence; giữ riêng raw decision score, uncalibrated probability và calibrated probability.
- Ảnh là bằng chứng hỗ trợ, không tự biến thành input Computer Vision.

## Recent implementation commits

| Commit | Nội dung |
|---|---|
| 5b3ae936407d5bf3f1067e8f1c1cc207596d114b | Gỡ ML Compose service chưa có Dockerfile; tránh prediction giả khi không có ML service |
| a56f6acd2fa2c5f729313f76873c57f7571f37a2 | Sửa invocation pytest qua python -m pytest |
| 9c1abc7857b0fb73317407c963493db2fecc9051 | Ghi nhận baseline status và gap |
| dca5c53d38b381c8b6eff1896f560ff3b51f347d | Preprocessing, metrics, classical NB/SVM, training integration và ML Docker image |
| 0bec1c5c5b519b03064c83420c118292266f1a2e | Thêm neural CPU test stage và xử lý input ngắn |
| 590d1cbb2c6727a16edda5e8f885116d62d60d23 | Sửa newline trong CPU PyTorch requirements |
| cbc903252d82dfa256f828d019119feadc1d204d | Điều chỉnh tách install commands; CI run trung gian bị cancel |
| 5ead264e5411b6ec184e3ae3813f416ce235ba27 | Tách PyPI và PyTorch CPU index install đúng cách; CI #13 pass |
| 4af33cedd814c69784a47fe37cc4b8924668a02f | Thêm trainer CLI smoke test; CI #14 pass |

Một số commit trung gian có CI fail do cấu hình dependency; lỗi đã được sửa ở các commit sau. Không dùng các commit trung gian đó làm release baseline.

## Next implementation work

1. Viết DB integration tests cho frozen-dataset training orchestration: tạo sample đủ 11 classes/3 splits trong CI DB, chạy NB/SVM end-to-end, xác minh TrainingRun, TrainingMetric, ModelVersion, checksum và artifact.
2. Bổ sung kiểm thử lỗi/rollback và ngăn rò rỉ fingerprint giữa data splits.
3. Hoàn thiện authenticated inference boundary: chỉ load model approved/active, verify checksum/schema/preprocessing, append prediction history; giữ no-active-model behavior rõ ràng.
4. Mở rộng API authorization/integration tests cho report submission, attachment ownership, review, dataset freeze và model lifecycle.
5. Xây dựng Citizen Portal và Admin Portal thật, kết nối API; thêm E2E workflow và map.
6. Xác minh Google OAuth bằng credentials do chủ dự án cấu hình.
7. Tạo lockfiles/transitive dependency review và bổ sung observability, security, backup/production deployment.

## Verification policy

- DONE chỉ khi code + test thích hợp + kết quả kiểm thử có bằng chứng.
- PARTIAL khi module có code nhưng chưa đủ workflow hoặc chưa có data-backed verification.
- NOT_STARTED khi chưa triển khai.
- BLOCKED khi thiếu dữ liệu, credentials hoặc quyết định cần chủ dự án.
- CI xanh cho foundation không đồng nghĩa toàn dự án hoàn tất.
- Không tự merge feature/project-foundation vào main.
