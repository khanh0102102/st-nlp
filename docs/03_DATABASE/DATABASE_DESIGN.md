# DATABASE DESIGN — THIẾT KẾ CƠ SỞ DỮ LIỆU

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 2.0 |
| Trạng thái | Proposed physical baseline — 12 bảng theo đề xuất của chủ dự án |
| ORM định hướng | SQLAlchemy |
| Database engine | TBD; PostgreSQL là ứng viên cần đánh giá |
| Số bảng nghiệp vụ chính | Chính xác 12 |
| Danh mục phân loại | 11 danh mục theo CLASSIFICATION_SPECIFICATION.md |

## 1. Mục tiêu và phạm vi

Thiết kế này cụ thể hóa cấu trúc 12 bảng do chủ dự án đề xuất cho ba nhóm nghiệp vụ: quản lý phản ánh, NLP/AI và quản lý dữ liệu/thực nghiệm ML. Đây là **đặc tả schema đề xuất để triển khai**, chưa phải schema đã tồn tại trong repository: backend, SQLAlchemy model và migration chưa được tạo ở thời điểm cập nhật.

Nguồn chuẩn về nhãn là [CLASSIFICATION_SPECIFICATION](../01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md). Tên và thứ tự 11 danh mục được giữ nguyên theo danh sách chủ dự án; các category_code tiếng Anh là mã kỹ thuật được chuẩn hóa trong tài liệu đó.

## 2. Quyết định thiết kế chính

1. Dùng đúng 12 bảng: users, incident_categories, reports, report_attachments, preprocessing_runs, model_versions, predictions, prediction_reviews, datasets, dataset_samples, training_runs và training_metrics.
2. Không thêm bảng roles, permissions, dataset_versions hoặc audit_logs trong baseline 12 bảng. Vai trò được lưu trong users.role_codes; mỗi hàng datasets đại diện một phiên bản bất biến; audit tổng quát được ghi qua audit sink append-only bên ngoài 12 bảng quan hệ.
3. Dùng khóa chính ổn định; UUID được khuyến nghị nhưng kiểu vật lý cuối cùng phụ thuộc Database Engine được duyệt.
4. Tất cả khóa ngoại phải có constraint và index phù hợp. Không dùng tên hiển thị của category làm khóa.
5. Lưu thời gian có timezone, chuẩn hóa UTC.
6. Ảnh và model artifact lưu ngoài Database; Database chỉ lưu storage key/URI, metadata và checksum.
7. reports.raw_content là nội dung gốc bất biến. Preprocessing tạo bản ghi mới và không sửa nội dung gốc.
8. predictions là lịch sử kết quả AI; prediction_reviews là lịch sử cán bộ; reports.final_category_id là nhãn nghiệp vụ hiện hành đã được cán bộ xác nhận.
9. Dataset version sau khi đóng băng là bất biến. Tạo phiên bản mới bằng một hàng datasets mới, không sửa dữ liệu của version đã được dùng huấn luyện.
10. Training và inference dài không giữ transaction Database mở.

## 3. Danh sách chính xác 12 bảng

| STT | Nhóm | Bảng | Trách nhiệm |
|---:|---|---|---|
| 1 | Quản lý phản ánh | users | Tài khoản người dân và cán bộ, định danh đăng nhập, vai trò |
| 2 | Quản lý phản ánh | incident_categories | Catalog cố định gồm đúng 11 danh mục |
| 3 | Quản lý phản ánh | reports | Phản ánh gốc, chủ sở hữu, nội dung, vị trí, trạng thái và nhãn cuối cùng |
| 4 | Quản lý phản ánh | report_attachments | Metadata file/hình ảnh, tham chiếu storage ngoài DB |
| 5 | NLP/AI | preprocessing_runs | Mỗi lần tiền xử lý, cấu hình/version và kết quả xử lý |
| 6 | NLP/AI | model_versions | Phiên bản thuật toán/mô hình, cấu hình và artifact |
| 7 | NLP/AI | predictions | Kết quả AI, confidence, model/preprocessing reference và trạng thái |
| 8 | NLP/AI | prediction_reviews | Lịch sử cán bộ xác nhận/chỉnh sửa dự đoán |
| 9 | Dữ liệu/ML | datasets | Metadata và từng phiên bản Dataset |
| 10 | Dữ liệu/ML | dataset_samples | Mẫu văn bản, nhãn, nguồn gốc và split |
| 11 | Dữ liệu/ML | training_runs | Lần huấn luyện, cấu hình và trạng thái |
| 12 | Dữ liệu/ML | training_metrics | Metrics tổng thể và theo từng danh mục/split |

## 4. Thiết kế từng bảng

Kiểu dữ liệu dưới đây là kiểu logic đề xuất; cần ánh xạ sang SQL dialect sau khi chốt Database Engine.

### 4.1. users

Quản lý tài khoản người dân và tài khoản cán bộ trong một bảng.

Trường chính đề xuất:
- id: khóa chính.
- auth_provider, provider_subject: định danh từ nhà cung cấp đăng nhập; cặp này unique khi có giá trị.
- email, display_name, avatar_url: thông tin hồ sơ cần thiết.
- password_hash: nullable, chỉ dùng nếu phương thức đăng nhập cán bộ được duyệt có mật khẩu; không lưu password dạng rõ.
- role_codes: JSON array các mã role được allow-list; baseline gồm CITIZEN, RECEIVER, ADMIN. Role AI/Data Manager có thể được cấp bằng permission policy cho tài khoản được ủy quyền, chưa tạo role/table mới.
- account_status, created_at, updated_at, last_login_at.

Một tài khoản có thể có nhiều role code theo định hướng Overview. Do baseline không có bảng role mapping riêng, Backend phải validate từng giá trị role_codes theo allow-list và kiểm tra quyền tập trung. JSON array là đánh đổi để giữ giới hạn 12 bảng; nếu sau này cần RBAC nhiều-nhiều và permission động ở mức DB, phải xin duyệt mở rộng schema.

Người dân xác thực bằng Google theo SRS. Cách đăng nhập cán bộ còn TBD; không cấp quyền cán bộ chỉ vì tài khoản có email Google.

### 4.2. incident_categories

Catalog chuẩn, có đúng 11 bản ghi seed:
- id: khóa chính.
- category_code: unique, stable machine code.
- category_name: tên hiển thị tiếng Việt nguyên văn.
- description: mô tả phạm vi.
- sort_order: thứ tự 1..11, unique.
- is_active: trạng thái hiệu lực; baseline đủ 11 danh mục active.
- created_at, updated_at.

Không cung cấp CRUD tạo/xóa danh mục tùy ý. Danh mục và mã chỉ được thay đổi qua change approval, label schema version và kế hoạch migration/relabel.

### 4.3. reports

Phản ánh gốc:
- id, user_id (FK users).
- raw_content: nội dung người dân gửi, không bị preprocessing hay review ghi đè.
- address, latitude, longitude: vị trí do người gửi cung cấp/xác nhận; CRS và precision cần chốt cùng DB/map.
- final_category_id (nullable FK incident_categories): nhãn cuối cùng do cán bộ xác nhận; NULL khi chưa được kiểm duyệt.
- status: trạng thái quy trình phản ánh; tập code và transition vẫn TBD.
- created_at, submitted_at, updated_at.

Không thêm cột predicted_category_id vào reports; nhãn dự đoán nằm trong predictions. Không tự cho người dân gửi final_category_id.

### 4.4. report_attachments

Metadata file ảnh/tài liệu đính kèm:
- id, report_id (FK reports), uploaded_by (FK users, nullable nếu kế thừa owner).
- storage_key: key nội bộ ở private storage, không phải filesystem path của host.
- original_filename đã sanitize, verified_mime_type, file_size_bytes, checksum_sha256.
- upload_status, created_at.

Binary file lưu ngoài Database. Download phải kiểm tra quyền; không lưu URL public lâu dài. Quy trình upload phải xử lý file mồ côi khi DB/storage lỗi lệch pha.

### 4.5. preprocessing_runs

Lưu từng lần chạy pipeline tiền xử lý:
- id, report_id (FK reports).
- preprocessing_version, pipeline_name, tokenizer_name/tokenizer_version.
- normalization_config_json, stopword_config_json hoặc reference/version của bộ stopwords.
- processed_text hoặc processed_artifact_key (chọn phương án phù hợp privacy/retention).
- input_fingerprint, processing_status, error_code.
- processing_time_ms, created_at.

Một report có thể có nhiều preprocessing run do retry, thay pipeline hoặc thí nghiệm. Không sửa reports.raw_content. Dự đoán phải tham chiếu chính xác preprocessing_run đã dùng.

### 4.6. model_versions

Registry phiên bản mô hình:
- id, model_family, algorithm_name, version_label.
- text_representation (ví dụ TF-IDF, token sequence/embedding).
- preprocessing_version, label_schema_version.
- training_run_id (nullable FK training_runs; liên kết run nguồn).
- artifact_uri/storage_key, artifact_checksum.
- hyperparameters_json, metrics_summary_json.
- model_status, registered_by/approved_by (FK users nullable theo policy), created_at, approved_at, activated_at, retired_at.

Artifact không lưu trong Git hoặc BLOB Database; lưu ở private artifact storage. Một training run thành công có thể tạo một model version được đăng ký. Việc activation phải có quyền, audit và quy tắc một active model cho deployment target nếu policy được chốt.

### 4.7. predictions

Mỗi lần inference:
- id, report_id (FK reports).
- preprocessing_run_id (FK preprocessing_runs).
- model_version_id (FK model_versions).
- predicted_category_id (nullable FK incident_categories khi inference thành công).
- confidence_value (nullable numeric), confidence_type.
- needs_review, inference_status, error_code.
- processing_time_ms, created_at.

Một report có thể có nhiều predictions theo retry/model version. Prediction gốc là append-only theo policy; không sửa nhãn sau khi cán bộ review. Confidence phải phân biệt calibrated probability với raw decision score; thất bại/không đủ thông tin không bị ép thành category OTHER.

### 4.8. prediction_reviews

Lịch sử cán bộ kiểm duyệt:
- id, report_id (FK reports), prediction_id (FK predictions), reviewer_id (FK users).
- previous_category_id (nullable FK incident_categories).
- selected_category_id (FK incident_categories).
- action_code: CONFIRMED hoặc CORRECTED trong baseline.
- note, reviewed_at.
- request_version/idempotency reference nếu cần concurrency.

Mỗi thao tác review tạo hàng mới, không update/delete lịch sử cũ. previous_category_id của lần đầu thường bằng predicted_category_id; ở lần sau phải phản ánh nhãn hiện hành trước thao tác. Backend phải đảm bảo report_id khớp report của prediction_id. Trong một transaction, tạo review và cập nhật reports.final_category_id. Audit event tổng quát ghi qua audit sink riêng.

### 4.9. datasets

Mỗi hàng đại diện **một version cụ thể** của một Dataset logic, không cần bảng dataset_versions thứ hai:
- id, dataset_name, version_label.
- parent_dataset_id (nullable self-FK tới version trước để truy vết).
- dataset_status: DRAFT, VALIDATING, READY, FROZEN, ARCHIVED hoặc trạng thái tương đương được chuẩn hóa trước khi code.
- label_schema_version, split_config_json.
- sample_count, class_distribution_json, validation_report_uri, provenance_summary.
- created_by (FK users), created_at, frozen_at.

Unique phù hợp trên dataset_name + version_label. Một version FROZEN không được chỉnh sửa samples/config làm thay đổi dữ liệu huấn luyện; tạo hàng version mới.

### 4.10. dataset_samples

Một mẫu trong một Dataset version:
- id, dataset_id (FK datasets).
- text_content: bản snapshot văn bản đã được phép sử dụng; không mặc định export raw report có PII.
- category_id (nullable FK incident_categories).
- labeling_status: LABELED, UNLABELED, NEEDS_REVIEW, INSUFFICIENT_INFORMATION hoặc trạng thái tương đương.
- split: TRAIN, VALIDATION, TEST hoặc NULL trước khi chia.
- source_type, source_report_id (nullable FK reports), source_review_id (nullable FK prediction_reviews).
- text_fingerprint, label_guideline_version, created_at, updated_at.

OTHER là category hợp lệ với category_id trỏ đến danh mục 11. UNLABELED/NEEDS_REVIEW/INSUFFICIENT_INFORMATION là trạng thái gán nhãn, không phải class. Sample gắn nguồn report/review chỉ khi có quyền tái sử dụng; lưu snapshot và provenance để tái lập.

### 4.11. training_runs

Một lần chạy thực nghiệm/huấn luyện:
- id, dataset_id (FK datasets).
- model_family, algorithm_name, text_representation.
- hyperparameters_json, imbalance_strategy, preprocessing_version, random_seed.
- code_version, environment_version, run_status.
- started_at, finished_at, duration_ms, output_artifact_uri, failure_summary.
- created_by (FK users), created_at.

Run phải tham chiếu Dataset version cụ thể ở trạng thái đủ điều kiện. Không giữ transaction DB mở trong lúc training. Run thất bại vẫn được lưu với trạng thái và lỗi đã làm sạch.

### 4.12. training_metrics

Một chỉ số của một training run:
- id, training_run_id (FK training_runs).
- metric_name, metric_value.
- data_split: TRAIN, VALIDATION hoặc TEST.
- averaging: MACRO, WEIGHTED, MICRO hoặc NULL nếu metric không áp dụng averaging.
- category_id (nullable FK incident_categories) cho metric theo lớp.
- support_count, epoch_or_step, recorded_at, metric_details_json (nullable).

Hỗ trợ Accuracy, Precision, Recall, Macro F1, Weighted F1 và F1/Precision/Recall theo từng lớp. Không ghi metrics giả; không dùng test set để tune model. Unique/index cần xác định để không trùng cùng metric context.

## 5. Quan hệ và cardinality

- users 1—N reports; users 1—N prediction_reviews với vai trò reviewer.
- incident_categories 1—N reports qua final_category_id.
- reports 1—N report_attachments, preprocessing_runs, predictions và prediction_reviews.
- preprocessing_runs 1—N predictions.
- model_versions 1—N predictions.
- incident_categories 1—N predictions, prediction_reviews và dataset_samples.
- predictions 1—N prediction_reviews.
- datasets 1—N dataset_samples và training_runs; datasets có self-reference parent_dataset_id cho version lineage.
- training_runs 1—N training_metrics và 1—N model_versions qua model_versions.training_run_id.
- reports và prediction_reviews có thể là nguồn tùy chọn của dataset_samples.

## 6. Ràng buộc toàn vẹn chính

- FK cho mọi quan hệ đã nêu; không chỉ kiểm tra ở Frontend.
- incident_categories.category_code và sort_order unique; seed chính xác 11 hàng.
- reports.final_category_id nullable trước review; nếu có phải thuộc catalog.
- prediction thành công cần model_version_id, preprocessing_run_id và category hợp lệ; inference failed không cần category/confidence.
- prediction_reviews.selected_category_id phải là một trong 11 category; reviewer phải có quyền.
- reports.final_category_id phải khớp selected_category_id của review hiện hành; cập nhật trong transaction.
- dataset_samples.category_id nullable chỉ khi labeling_status cho phép chưa gán nhãn.
- dataset_samples.split chỉ nhận TRAIN/VALIDATION/TEST hoặc NULL trước khi chia.
- training_metrics.metric_value phải hữu hạn, không NaN/Infinity; metric_name, split, averaging và category context phải rõ.
- latitude thuộc [-90, 90], longitude thuộc [-180, 180]; CRS/precision phải được ghi rõ.
- Timestamp lưu UTC.
- Trạng thái DB dùng code ổn định, có validation và transition ở Backend.

## 7. Index đề xuất

- users: unique auth_provider + provider_subject khi có; normalized email index theo policy.
- incident_categories: unique category_code, unique sort_order.
- reports: user_id + created_at; status + created_at; final_category_id + created_at; tọa độ/geospatial index nếu DB hỗ trợ và query cần.
- report_attachments: report_id, unique storage_key.
- preprocessing_runs: report_id + created_at, preprocessing_version.
- predictions: report_id + created_at, model_version_id, predicted_category_id, inference_status.
- prediction_reviews: report_id + reviewed_at, prediction_id + reviewed_at, reviewer_id + reviewed_at.
- datasets: unique dataset_name + version_label, dataset_status.
- dataset_samples: dataset_id + split, dataset_id + category_id, source_report_id, text_fingerprint.
- training_runs: dataset_id + created_at, run_status.
- training_metrics: training_run_id + metric_name + data_split; category_id khi per-class.

Chỉ tạo index theo query thực tế và kiểm tra query plan; tránh index trùng.

## 8. Lịch sử và Audit trong giới hạn 12 bảng

Baseline giữ đúng 12 bảng nên không thêm audit_logs. prediction_reviews là lịch sử kiểm duyệt chuyên biệt; các cột actor/time trong model_versions và training_runs chỉ phản ánh vòng đời tương ứng, **không thay thế audit tổng quát**.

Các thao tác nhạy cảm khác (đăng nhập quan trọng, thay role/quyền, đổi report status, thay đổi cấu hình, activation/rollback model, truy cập file nhạy cảm nếu policy yêu cầu) phải phát ra audit event có actor, action, resource, timestamp, outcome, request_id và before/after tối thiểu qua một **audit sink append-only bên ngoài 12 bảng**. Local có thể dùng structured log trên volume được bảo vệ; production phải chọn nơi lưu bền vững, kiểm soát truy cập, retention và chống sửa/xóa. Provider và cơ chế cụ thể còn TBD trước production. Không ghi secret, token hoặc toàn bộ raw_content vào audit.

Nếu chủ dự án yêu cầu audit phải truy vấn trực tiếp bằng SQL trong cùng Database, khi đó phải xin duyệt thay đổi giới hạn 12 bảng (thường cần bảng audit riêng), không tự lén thêm bảng.

## 9. Storage, privacy và retention

- Ảnh và model artifact ở private storage; Database lưu storage key/URI, metadata và checksum.
- Không lưu file người dân trong Git.
- Truy cập file cần kiểm tra ownership/permission ở Backend; signed URL nếu dùng phải có expiry ngắn.
- processed_text và dataset_samples.text_content có thể chứa dữ liệu cá nhân; cần quyền truy cập, masking/ẩn danh, retention và xóa theo policy.
- Không đưa report thật vào dataset chỉ vì đã được review; cần xác minh quyền tái sử dụng và quality gate.
- Storage cleanup phải xử lý orphan files và không xóa file còn được reference.

## 10. Migration, seed và Docker-only

- ORM định hướng SQLAlchemy; công cụ migration dự kiến Alembic, chờ stack approval.
- Migration/seed/test chạy bên trong Docker container, không cài Python/DB client trên host.
- Seed catalog idempotent: đúng 11 category theo CLASSIFICATION_SPECIFICATION.
- Kiểm thử trên DB rỗng và đường nâng cấp được hỗ trợ.
- Không sửa migration đã chạy ở môi trường chia sẻ; thêm migration mới.
- Seed không chứa dữ liệu người dân thật.
- Migration report status/roles/category changes phải có kế hoạch tương thích dữ liệu.

## 11. Transaction boundary

- Create report: report row và attachment metadata reference được phối hợp; upload storage cần compensation/cleanup nếu không thể atomic với DB.
- Create prediction: lưu preprocessing run và prediction; inference failure không rollback report.
- Create review: append prediction_reviews + update reports.final_category_id trong một transaction; audit sink phát event theo cơ chế outbox/retry đã chọn.
- Freeze dataset: validate + đóng băng version; không cho sửa samples sau freeze.
- Training: run/metrics cập nhật theo run ID, không giữ transaction dài.
- Activate model: thao tác atomic theo deployment target, phát audit event, có rollback.

## 12. Các quyết định vẫn TBD

- Database engine/version, UUID implementation và extension địa lý.
- Column lengths, precision, timezone SQL type và naming constraint cụ thể theo engine.
- Cách đăng nhập cán bộ và policy MFA.
- Cơ chế upload/storage provider và retention file.
- Tập status chính thức và state transitions của reports, preprocessing, predictions, reviews, datasets, training_runs, model_versions.
- Threshold confidence và semantics/calibration.
- Audit sink production, retention và tính chống sửa/xóa.
- Dataset privacy, split ratio, source approval và deletion propagation.
- Model deployment target, artifact storage và policy single-active.
