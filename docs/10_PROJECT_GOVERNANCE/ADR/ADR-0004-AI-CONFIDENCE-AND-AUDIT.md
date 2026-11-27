# ADR-0004: Confidence semantics, review policy và audit sink

- Trạng thái: Accepted for initial implementation by delegated Master Prompt
- Ngày quyết định: 2026-11-27
- Phạm vi: Semantics dùng xuyên suốt NLP API/Database/UI và audit local; production sink vẫn TBD

## Confidence semantics

Không dùng một field chung để giả định mọi model output đều là xác suất.

- Naive Bayes: predict_proba output được lưu là MODEL_PROBABILITY_UNCALIBRATED nếu chưa có calibration evidence.
- SVM: decision_function được lưu là RAW_DECISION_SCORE. Không diễn giải raw margin thành phần trăm.
- CNN 1D/LSTM: softmax output mặc định là MODEL_PROBABILITY_UNCALIBRATED, không phải calibrated probability.
- Chỉ dùng CALIBRATED_PROBABILITY sau khi thực hiện calibration trên tập dữ liệu calibration/validation phù hợp và lưu phương pháp/version.
- Không dùng test set để fit calibration hoặc tune threshold.
- UI chỉ hiển thị tỷ lệ phần trăm khi confidence_type là CALIBRATED_PROBABILITY. Các score khác phải ghi rõ nhãn "điểm mô hình chưa hiệu chỉnh" hoặc không hiển thị thành phần trăm.

## Review policy

- Mặc định needs_review = true cho mọi prediction trong baseline local cho đến khi có dataset được xác nhận, đánh giá held-out theo lớp và threshold policy được phê duyệt.
- Không tự đặt confidence threshold để tự động bỏ qua cán bộ.
- Không có active model hoặc inference lỗi không làm mất report; lưu trạng thái lỗi và cho phép cán bộ xử lý bằng quy trình phù hợp.
- Không ép INVALID_INPUT, INSUFFICIENT_INFORMATION hoặc INFERENCE_FAILED thành category OTHER.

## Dataset và metrics

- Chưa có dataset thật được cung cấp trong repository.
- Dữ liệu synthetic chỉ phục vụ test/demo, phải đánh dấu provenance và không dùng để báo cáo chất lượng mô hình thực tế.
- Metrics chỉ được trình bày khi thực sự chạy trên Dataset version có nguồn/quyền sử dụng rõ và test split độc lập.
- Dataset source/license, privacy/de-identification và labeling adjudication cần được xác minh trước khi dùng phản ánh thật để huấn luyện.

## Audit sink

- Giữ chính xác 12 bảng relational; không tạo audit_logs.
- Local baseline: structured JSON Lines (JSONL) trên named volume riêng, mỗi event một dòng, mở file ở chế độ append, giới hạn quyền file/container. Không log raw_content đầy đủ, ảnh, password, token, cookie hoặc secret.
- Event tối thiểu: actor_id, action, resource_type, resource_id, timestamp UTC, outcome, request_id và before/after tối thiểu đã lọc.
- Application phải xử lý write failure rõ ràng; các thao tác nhạy cảm không được âm thầm giả định audit thành công.
- JSONL volume local không được coi là tamper-proof hoặc durable audit cho production. Production sink, backup, retention, access control và tamper-evidence vẫn TBD.

## Hệ quả

- API/Database/UI phải giữ confidence_type cùng confidence_value.
- Tất cả prediction đều human-review trong giai đoạn đầu.
- Không có ML quality claim nếu thiếu dataset thật và evidence.
