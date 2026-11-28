# IMPLEMENTATION STATUS — ST-NLP

Ngày cập nhật: 2026-11-28

## Repository và bằng chứng

- Repository: https://github.com/khanh0102102/st-nlp
- Base branch: main — chưa được thay đổi trong đợt triển khai này.
- Working branch: feature/project-foundation.
- Code snapshot đã được Docker CI xác minh: `e89f9287ac07e83094eda0aa3f7cc65b9ec15963`.
- Branch compare snapshot trước commit tài liệu: feature/project-foundation ahead 28, behind 0 so với main.
- Không tự tạo/merge PR; việc đưa feature vào main cần được chủ dự án duyệt.

### CI evidence

GitHub Actions run #26 (46146303002), conclusion success, trên commit `e89f9287ac07e83094eda0aa3f7cc65b9ec15963`.

| Hạng mục | Kết quả | Ghi chú |
|---|---|---|
| Compose validation | PASS | Run #26: docker compose config --quiet |
| Docker builds | PASS | App, backend test, CPU ML test và training images |
| Fresh PostgreSQL migration | PASS | `0001 -> 0002` trên PostgreSQL Docker |
| Upgrade/downgrade | PASS | `0002 -> 0001 -> 0002` |
| Seed danh mục | PASS | Xác minh chính xác 11 category sau migration |
| Backend pytest | PASS | **61 passed, 1 skipped** trong API runtime image |
| Neural component tests | PASS | **8 passed** trong CPU ML test image |
| Report/review DB integrity | PASS | TestClient + PostgreSQL; raw content, role guard, transaction pair và append-only review |
| Model Registry | PASS | Unique ACTIVE index, concurrent activation và rollback lifecycle tests |
| ML trainer CLI smoke | PASS | `python -m app.ml.cli --help` qua Compose profile |
| Application startup | PASS | API và web khởi động trong Docker Compose |
| Health checks | PASS | frontend `/health`, API `/health/live` và `/health/ready` |

Test bị skip trong backend image là module phụ thuộc PyTorch; neural tests tương ứng chạy riêng trong CPU ML test image. Run #26 dùng GitHub Actions Docker runner; phiên môi trường này không có Docker CLI để chạy Docker local. DB-backed training integration dùng synthetic samples để xác minh mechanics, không đánh giá chất lượng mô hình trên dữ liệu thật. Google OAuth credentials thật chưa được xác minh.

## Trạng thái theo subsystem

| Subsystem | Trạng thái | Bằng chứng / giới hạn |
|---|---|---|
| Docker/local foundation | DONE cho local CI baseline | Compose validation/build/start và health checks pass trong run #17; production deployment chưa nghiệm thu |
| Database | DONE cho Milestone 1 scope | Đúng 12 business tables; migration 0001+0002; seed 11 categories; PostgreSQL guards cho raw_content/review và single ACTIVE model; upgrade/downgrade/re-upgrade CI PASS |
| Category catalog | DONE | Đúng 11 category code và order; seed verified trong CI |
| Backend core/auth | PARTIAL | Session/CSRF/role checks, staff login và Google OIDC flow có code; Google OAuth thật chưa xác minh |
| Citizen APIs | PARTIAL | Profile/report/attachment foundations hiện có; full citizen workflow chưa nghiệm thu |
| Admin APIs | PARTIAL | Report review/history và model registry có authorization/integrity tests; dashboard/map/dataset portal và full workflow chưa nghiệm thu |
| Dataset management | PARTIAL | Dataset/sample CRUD, validation và freeze protections có nền tảng; chưa có dataset thật được cung cấp và duyệt |
| Model registry | DONE cho local lifecycle baseline | DB single-ACTIVE index, advisory-lock concurrency, approve/activate/rollback tests; chưa có model được đánh giá trên dữ liệu thật |
| Vietnamese preprocessing | DONE ở mức module | NFC/lowercase/whitespace, Underthesea tokenizer, version metadata và fingerprint; tests pass |
| Metrics | DONE ở mức module | Accuracy, macro/weighted precision-recall-F1, per-class support và confusion matrix; tests pass |
| Classical NLP | DONE ở mức model component | TF-IDF word n-gram + MultinomialNB/LinearSVC, fit/predict parity và artifact save/load tests; chưa đánh giá chất lượng trên dataset thực |
| CNN 1D / BiLSTM | PARTIAL | Model components, CPU artifact load/predict, short-sequence tests; 8 tests pass; training lifecycle trên dataset/database chưa E2E verified |
| Training orchestration | PARTIAL | NB/SVM end-to-end trên synthetic frozen DB dataset đã test, gồm run/metrics/model/artifact; CNN/LSTM và real/approved dataset training vẫn chưa E2E verified |
| Inference integration | NOT_STARTED / BLOCKED | Chưa có authenticated inference service hoàn chỉnh và active model; không tạo prediction giả khi thiếu model |
| Frontend | PARTIAL | React/Vite/Nginx status foundation; Citizen Portal, Admin Portal, interactive map và operational dashboards chưa hoàn thành |
| Full integration / E2E | NOT_STARTED | Chưa chứng minh trọn luồng citizen report → review → frozen dataset → training → active inference |
| Production readiness | NOT_READY | OAuth, secrets, persistent storage, monitoring, backups, security review, NFR và deployment còn mở |

## Milestone 1 — acceptance evidence

Bằng chứng: GitHub Actions [run #26](https://github.com/khanh0102102/st-nlp/actions/runs/46146303002), code commit `e89f9287ac07e83094eda0aa3f7cc65b9ec15963`.

| ID | Tiêu chí | Trạng thái | Bằng chứng / giới hạn |
|---|---|---|---|
| M1-01 | recorded luôn được khởi tạo | DONE | Audit event tính cả khi ML_SERVICE_URL rỗng; endpoint regression test |
| M1-02 | Tạo report khi ML_SERVICE_URL rỗng | DONE | FastAPI TestClient + PostgreSQL trả 201 |
| M1-03 | Không tạo prediction giả | DONE | INFERENCE_FAILED; category/confidence NULL khi service thiếu, unavailable hoặc body sai schema |
| M1-04 | Regression report tests | DONE | Endpoint tests chạy trong backend Docker suite |
| M1-05 | Giữ nguyên raw_content | DONE | Không trim trước persist; DB trigger từ chối UPDATE |
| M1-06 | Test nguyên văn Unicode/raw text | DONE | Whitespace, newline, tiếng Việt NFC/NFD và DB immutability |
| M1-07 | Review + final category cùng transaction | DONE | Insert/flush review, transaction-local marker, update report, commit/rollback |
| M1-08 | Quyền review | DONE | API guard và PostgreSQL trigger chỉ chấp nhận ACTIVE RECEIVER/ADMIN |
| M1-09 | DB enforce invariant | DONE trong phạm vi M1 | Review/final-category pair, append-only review, raw_content immutable; chưa exhaustive 12 bảng |
| M1-10 | Activation concurrency/rollback | DONE | Partial unique index, advisory lock, concurrent activation và rollback tests |
| M1-11 | Migration + seed 11 categories | DONE | PostgreSQL fresh/upgrade/downgrade/re-upgrade và seed PASS |
| M1-12 | Giữ đúng 12 business tables | DONE | Schema test xác minh 12; alembic_version là bảng kỹ thuật |
| M1-13 | Docker suite + health | DONE | 61 passed, 1 skipped; neural 8 passed; build, CLI, startup và health PASS |
| M1-14 | Tài liệu theo bằng chứng | PARTIAL | Tài liệu được đồng bộ trong commit tiếp theo; CI trên snapshot tài liệu đang chờ |

Milestone 1 tổng thể: **PARTIAL trong snapshot tài liệu này** cho đến khi CI chạy trên commit tài liệu hoàn tất. Không suy rộng sang Citizen/Admin Portal, OAuth thật, inference service hoặc chất lượng mô hình.
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
| 9042291a8309fc984c858309c791d3d80bca615f | Thêm ADR-0005 về ML training/runtime boundary |
| b2fb080a9c32724ae83d048269995d5b52605420 | Đồng bộ README, deployment, implementation status và AI/ML docs |
| 58b6acf5890c416b9d55812afdacf6739d74c560 | DB integration tests cho NB/SVM training lifecycle; CI #17 pass |
| c36d29a313b58e78314ff244071743d7af924f11 | Fix report audit/raw_content khi ML URL rỗng; CI #21 pass |
| 6f656025117325afd71ef42a8c80e5290b65f5ba | Review DB guard, single-active index, advisory lock và Docker migration test |
| 1a7859cb7dd49fe30ceb836c2cc417683b209a58 | Test report bằng TestClient/PostgreSQL, raw_content immutable và flush order |
| a5922470d497ca12958af397533d59810ac4674e | Bind final_category update với review row bằng transaction-local marker |
| 917c887745a7f02a49d7b403c1959b30d8c79a12 | Sửa PL/pgSQL delimiter; CI #25: 60 backend pass, 1 skip; 8 neural pass |
| e89f9287ac07e83094eda0aa3f7cc65b9ec15963 | Model rollback lifecycle test; CI #26: 61 backend pass, 1 skip; 8 neural pass |

Một số commit trung gian có CI fail do cấu hình dependency; lỗi đã được sửa ở các commit sau. Không dùng các commit trung gian đó làm release baseline.

## Next implementation work

1. Mở rộng DB integration tests cho CNN/LSTM training lifecycle và kiểm tra rollback/cleanup khi training thất bại; NB/SVM synthetic-data path đã có test end-to-end.
2. Chuẩn hóa fingerprint giữa Dataset API và preprocessing, bổ sung kiểm thử duplicate gần giống và đảm bảo không rò rỉ giữa data splits.
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
