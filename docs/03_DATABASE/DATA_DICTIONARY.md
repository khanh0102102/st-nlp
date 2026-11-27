# DATA DICTIONARY — TỪ ĐIỂN DỮ LIỆU ST-NLP

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 2.0 |
| Trạng thái | Proposed physical data dictionary — 12 bảng |
| Kiểu ORM | SQLAlchemy |
| Database Engine | TBD |
| Danh mục | 11 lớp trong CLASSIFICATION_SPECIFICATION.md |

## 1. Quy ước

- Kiểu dữ liệu dưới đây là logical SQL types; cần ánh xạ sang Database Engine được duyệt.
- UUID được khuyến nghị cho khóa chính/khóa ngoại; có thể đổi theo quyết định stack trước khi viết migration.
- Timestamp là timezone-aware và lưu UTC.
- Nullable = Có nghĩa là có thể NULL theo điều kiện nghiệp vụ.
- JSON/JSONB chỉ dùng cho cấu hình/metadata có cấu trúc; không thay thế quan hệ cần JOIN/FK.
- Mã trạng thái và enum là code ổn định; tập giá trị TBD phải được chốt trước khi implementation.
- Mọi bảng có id, created_at/updated_at theo nhu cầu; không bắt buộc mọi bảng đều có cả hai.
- Raw content, ảnh và processed text được xếp Confidential; access phải có authorization.

## 2. Danh mục cố định: incident_categories

Seed chính xác 11 record theo [CLASSIFICATION_SPECIFICATION](../01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md). Không tự tạo/đổi/xóa label. category_code unique và không phụ thuộc category_name. sort_order unique từ 1 đến 11. Dashboard hiển thị đủ 11 record kể cả count = 0.

## 3. Chi tiết 12 bảng

### 3.1. users

| Column | Logical type | Null | Key/constraint | Ý nghĩa |
|---|---|---:|---|---|
| id | UUID | No | PK | Định danh tài khoản |
| auth_provider | VARCHAR(30) | Yes | Một phần unique với provider_subject | Nhà cung cấp đăng nhập, ví dụ GOOGLE |
| provider_subject | VARCHAR(255) | Yes | Một phần unique với auth_provider | Subject ổn định từ IdP |
| email | VARCHAR(320) | Yes | Index theo policy | Email đã xác minh nếu có |
| display_name | VARCHAR(150) | Yes | — | Tên hiển thị |
| avatar_url | TEXT | Yes | — | URL ảnh hồ sơ nếu được phép |
| password_hash | TEXT | Yes | — | Hash mật khẩu cán bộ nếu auth policy có mật khẩu |
| role_codes | JSON | No | Default allow-listed array | Các role code: CITIZEN, RECEIVER, ADMIN; Backend validate |
| account_status | VARCHAR(30) | No | Check theo status catalog | Trạng thái tài khoản |
| last_login_at | TIMESTAMPTZ | Yes | — | Lần đăng nhập gần nhất |
| created_at | TIMESTAMPTZ | No | Default UTC now | Ngày tạo |
| updated_at | TIMESTAMPTZ | No | Default UTC now | Ngày cập nhật |

Không lưu Google access/refresh token nếu không có nhu cầu và phê duyệt riêng. Cặp provider/subject unique khi cả hai có giá trị. Người dân dùng Google; auth cán bộ TBD. Không tin role/user_id do client gửi.

### 3.2. incident_categories

| Column | Logical type | Null | Key/constraint | Ý nghĩa |
|---|---|---:|---|---|
| id | UUID | No | PK | ID danh mục |
| category_code | VARCHAR(50) | No | UNIQUE | Mã kỹ thuật ổn định |
| category_name | VARCHAR(150) | No | UNIQUE đề xuất | Tên tiếng Việt |
| description | TEXT | Yes | — | Phạm vi/mô tả |
| sort_order | SMALLINT | No | UNIQUE, CHECK 1..11 | Thứ tự hiển thị |
| is_active | BOOLEAN | No | Default true | Trạng thái hiệu lực |
| created_at | TIMESTAMPTZ | No | Default UTC now | Ngày tạo |
| updated_at | TIMESTAMPTZ | No | Default UTC now | Ngày cập nhật |

### 3.3. reports

| Column | Logical type | Null | Key/constraint | Ý nghĩa |
|---|---|---:|---|---|
| id | UUID | No | PK | ID phản ánh |
| user_id | UUID | No | FK users.id, index | Người gửi |
| raw_content | TEXT | No | Check không rỗng sau validation | Nội dung gốc bất biến |
| address | TEXT | Yes | — | Địa chỉ do người gửi xác nhận |
| latitude | NUMERIC(9,6) | Yes | CHECK -90..90 | Vĩ độ |
| longitude | NUMERIC(9,6) | Yes | CHECK -180..180 | Kinh độ |
| final_category_id | UUID | Yes | FK incident_categories.id, index | Nhãn cuối cùng được cán bộ duyệt |
| status | VARCHAR(40) | No | Check/transition do domain policy | Trạng thái phản ánh; tập code TBD |
| submitted_at | TIMESTAMPTZ | No | Default UTC now | Thời điểm gửi thành công |
| created_at | TIMESTAMPTZ | No | Default UTC now | Thời điểm tạo |
| updated_at | TIMESTAMPTZ | No | Default UTC now | Thời điểm cập nhật |

Không lưu nhãn AI vào bảng này. final_category_id phải NULL khi chưa có xác nhận, không lấy dự đoán AI thay thế.

### 3.4. report_attachments

| Column | Logical type | Null | Key/constraint | Ý nghĩa |
|---|---|---:|---|---|
| id | UUID | No | PK | ID tệp |
| report_id | UUID | No | FK reports.id, index | Phản ánh sở hữu |
| uploaded_by | UUID | Yes | FK users.id | Tài khoản upload |
| storage_key | TEXT | No | UNIQUE | Key private storage |
| original_filename | VARCHAR(255) | Yes | Đã sanitize | Tên file gốc an toàn |
| verified_mime_type | VARCHAR(120) | No | Server verified | MIME thực tế đã xác minh |
| file_size_bytes | BIGINT | No | CHECK > 0 | Kích thước byte |
| checksum_sha256 | CHAR(64) | Yes | — | Hash kiểm tra toàn vẹn |
| upload_status | VARCHAR(30) | No | Check theo upload lifecycle | Trạng thái upload |
| created_at | TIMESTAMPTZ | No | Default UTC now | Thời điểm upload |

### 3.5. preprocessing_runs

| Column | Logical type | Null | Key/constraint | Ý nghĩa |
|---|---|---:|---|---|
| id | UUID | No | PK | ID lần tiền xử lý |
| report_id | UUID | No | FK reports.id, index | Phản ánh nguồn |
| preprocessing_version | VARCHAR(80) | No | Index | Phiên bản pipeline |
| pipeline_name | VARCHAR(100) | No | — | Tên pipeline |
| tokenizer_name | VARCHAR(100) | Yes | — | Thư viện/tokenizer |
| tokenizer_version | VARCHAR(80) | Yes | — | Phiên bản tokenizer |
| normalization_config_json | JSON | No | — | Cấu hình Unicode NFC, whitespace, normalization |
| stopword_config_json | JSON | Yes | — | Danh sách/version stopword và ngoại lệ |
| processed_text | TEXT | Yes | Confidential, retention policy | Văn bản sau tiền xử lý nếu lưu trực tiếp |
| processed_artifact_key | TEXT | Yes | — | Storage key thay thế processed_text |
| input_fingerprint | CHAR(64) | Yes | Index | Fingerprint nội dung input |
| processing_status | VARCHAR(30) | No | Check theo lifecycle | SUCCEEDED/FAILED/không xử lý tương đương |
| error_code | VARCHAR(80) | Yes | — | Mã lỗi đã làm sạch |
| processing_time_ms | BIGINT | Yes | CHECK >= 0 | Thời gian xử lý |
| created_at | TIMESTAMPTZ | No | Default UTC now | Thời điểm chạy |

Chỉ một trong processed_text và processed_artifact_key được dùng theo cấu hình đã chọn; không ghi raw_content vào log.

### 3.6. model_versions

| Column | Logical type | Null | Key/constraint | Ý nghĩa |
|---|---|---:|---|---|
| id | UUID | No | PK | ID phiên bản mô hình |
| model_family | VARCHAR(40) | No | Index | NB, SVM, CNN_1D, LSTM |
| algorithm_name | VARCHAR(100) | No | — | Thuật toán cụ thể |
| version_label | VARCHAR(80) | No | Unique theo model_family | Nhãn phiên bản |
| text_representation | VARCHAR(80) | No | — | TF-IDF, token sequence/embedding... |
| preprocessing_version | VARCHAR(80) | No | — | Pipeline tương thích |
| label_schema_version | VARCHAR(40) | No | — | Phiên bản mapping 11 nhãn |
| training_run_id | UUID | Yes | FK training_runs.id, index | Run đã tạo artifact |
| artifact_uri | TEXT | No | — | URI/storage key private |
| artifact_checksum | CHAR(64) | No | — | Checksum artifact |
| hyperparameters_json | JSON | Yes | — | Snapshot tham số |
| metrics_summary_json | JSON | Yes | Metadata tóm tắt | Metrics đã đo |
| model_status | VARCHAR(30) | No | Check theo lifecycle | Trạng thái model |
| registered_by | UUID | Yes | FK users.id | Người đăng ký |
| approved_by | UUID | Yes | FK users.id | Người duyệt |
| created_at | TIMESTAMPTZ | No | Default UTC now | Thời điểm đăng ký |
| approved_at | TIMESTAMPTZ | Yes | — | Thời điểm duyệt |
| activated_at | TIMESTAMPTZ | Yes | — | Lần kích hoạt |
| retired_at | TIMESTAMPTZ | Yes | — | Lần ngừng hoạt động |

### 3.7. predictions

| Column | Logical type | Null | Key/constraint | Ý nghĩa |
|---|---|---:|---|---|
| id | UUID | No | PK | ID kết quả dự đoán |
| report_id | UUID | No | FK reports.id, index | Phản ánh được phân loại |
| preprocessing_run_id | UUID | No | FK preprocessing_runs.id | Lần tiền xử lý dùng để infer |
| model_version_id | UUID | No | FK model_versions.id | Phiên bản mô hình |
| predicted_category_id | UUID | Yes | FK incident_categories.id, index | Nhãn AI dự đoán; NULL nếu không thành công/không thể phân loại |
| confidence_value | NUMERIC(12,10) | Yes | CHECK theo confidence_type | Score/confidence |
| confidence_type | VARCHAR(40) | Yes | — | calibrated_probability, probability hoặc raw_decision_score |
| needs_review | BOOLEAN | No | Default true theo policy | Cờ cảnh báo cần kiểm duyệt |
| inference_status | VARCHAR(30) | No | Check theo lifecycle | Trạng thái inference |
| error_code | VARCHAR(80) | Yes | — | Mã lỗi đã làm sạch |
| processing_time_ms | BIGINT | Yes | CHECK >= 0 | Thời gian inference |
| created_at | TIMESTAMPTZ | No | Default UTC now | Thời điểm dự đoán |

Backend phải kiểm tra predictions.report_id khớp preprocessing_runs.report_id. Model/preprocess/label schema phải tương thích.

### 3.8. prediction_reviews

| Column | Logical type | Null | Key/constraint | Ý nghĩa |
|---|---|---:|---|---|
| id | UUID | No | PK | ID lần kiểm duyệt |
| report_id | UUID | No | FK reports.id, index | Phản ánh |
| prediction_id | UUID | No | FK predictions.id, index | Prediction được xem xét |
| reviewer_id | UUID | No | FK users.id, index | Cán bộ kiểm duyệt |
| previous_category_id | UUID | Yes | FK incident_categories.id | Nhãn trước khi review |
| selected_category_id | UUID | No | FK incident_categories.id | Nhãn được xác nhận/chọn |
| action_code | VARCHAR(30) | No | CONFIRMED/CORRECTED | Hành động |
| note | TEXT | Yes | — | Ghi chú/lý do theo policy |
| reviewed_at | TIMESTAMPTZ | No | Default UTC now | Thời điểm kiểm duyệt |
| request_version | INTEGER | Yes | Concurrency control | Version kiểm soát đồng thời nếu dùng |

Review append-only. Backend xác minh report_id của review khớp report_id của prediction.

### 3.9. datasets

| Column | Logical type | Null | Key/constraint | Ý nghĩa |
|---|---|---:|---|---|
| id | UUID | No | PK | ID dataset version |
| dataset_name | VARCHAR(150) | No | Index | Tên Dataset logic |
| version_label | VARCHAR(60) | No | UNIQUE cùng dataset_name | Phiên bản |
| parent_dataset_id | UUID | Yes | Self-FK datasets.id | Version gốc/tiền nhiệm |
| dataset_status | VARCHAR(30) | No | Check theo lifecycle | DRAFT/VALIDATING/READY/FROZEN/ARCHIVED theo policy |
| label_schema_version | VARCHAR(40) | No | — | Phiên bản catalog/label guideline |
| split_config_json | JSON | Yes | — | Tỷ lệ, seed, method và split config |
| sample_count | BIGINT | No | Default 0, CHECK >= 0 | Tổng số mẫu |
| class_distribution_json | JSON | Yes | — | Phân bố theo category_code |
| validation_report_uri | TEXT | Yes | — | Báo cáo kiểm định |
| provenance_summary | JSON | Yes | — | Tổng quan nguồn/quyền sử dụng |
| created_by | UUID | No | FK users.id | Người tạo |
| created_at | TIMESTAMPTZ | No | Default UTC now | Ngày tạo |
| frozen_at | TIMESTAMPTZ | Yes | — | Ngày đóng băng |

Mỗi hàng là một version. Không chỉnh dữ liệu version FROZEN được training run tham chiếu.

### 3.10. dataset_samples

| Column | Logical type | Null | Key/constraint | Ý nghĩa |
|---|---|---:|---|---|
| id | UUID | No | PK | ID mẫu |
| dataset_id | UUID | No | FK datasets.id, index | Dataset version chứa mẫu |
| text_content | TEXT | No | Confidential | Nội dung snapshot được phép huấn luyện |
| category_id | UUID | Yes | FK incident_categories.id, index | Nhãn class |
| labeling_status | VARCHAR(40) | No | Check theo label lifecycle | LABELED/UNLABELED/NEEDS_REVIEW/INSUFFICIENT_INFORMATION... |
| split | VARCHAR(20) | Yes | TRAIN/VALIDATION/TEST | Phân chia tập |
| source_type | VARCHAR(40) | No | — | Loại nguồn/provenance |
| source_report_id | UUID | Yes | FK reports.id | Phản ánh nguồn |
| source_review_id | UUID | Yes | FK prediction_reviews.id | Review nguồn |
| text_fingerprint | CHAR(64) | Yes | Index | Phát hiện duplicate |
| label_guideline_version | VARCHAR(40) | Yes | — | Version hướng dẫn gán nhãn |
| created_at | TIMESTAMPTZ | No | Default UTC now | Ngày thêm |
| updated_at | TIMESTAMPTZ | No | Default UTC now | Ngày sửa |

### 3.11. training_runs

| Column | Logical type | Null | Key/constraint | Ý nghĩa |
|---|---|---:|---|---|
| id | UUID | No | PK | ID lần huấn luyện |
| dataset_id | UUID | No | FK datasets.id, index | Dataset version đã dùng |
| model_family | VARCHAR(40) | No | — | Nhóm mô hình |
| algorithm_name | VARCHAR(100) | No | — | Thuật toán |
| text_representation | VARCHAR(80) | No | — | Cách biểu diễn văn bản |
| hyperparameters_json | JSON | No | — | Cấu hình huấn luyện |
| imbalance_strategy | VARCHAR(80) | Yes | — | class_weight/resampling/none... |
| preprocessing_version | VARCHAR(80) | No | — | Pipeline preprocessing |
| random_seed | BIGINT | Yes | — | Seed tái lập |
| code_version | VARCHAR(80) | Yes | — | Commit/tag code |
| environment_version | VARCHAR(120) | Yes | — | Image/dependency version |
| run_status | VARCHAR(30) | No | Check theo lifecycle | QUEUED/RUNNING/SUCCEEDED/FAILED/CANCELLED... |
| started_at | TIMESTAMPTZ | Yes | — | Bắt đầu |
| finished_at | TIMESTAMPTZ | Yes | — | Kết thúc |
| duration_ms | BIGINT | Yes | CHECK >= 0 | Thời lượng |
| output_artifact_uri | TEXT | Yes | — | Artifact sinh ra |
| failure_summary | TEXT | Yes | Đã làm sạch | Mô tả lỗi |
| created_by | UUID | No | FK users.id | Người tạo run |
| created_at | TIMESTAMPTZ | No | Default UTC now | Ngày tạo |

Không cho run sử dụng dataset version chưa đủ điều kiện. Không lưu log chứa raw text hoặc secret trong failure_summary.

### 3.12. training_metrics

| Column | Logical type | Null | Key/constraint | Ý nghĩa |
|---|---|---:|---|---|
| id | UUID | No | PK | ID metric |
| training_run_id | UUID | No | FK training_runs.id, index | Run nguồn |
| metric_name | VARCHAR(60) | No | Index | Accuracy, Precision, Recall, F1... |
| metric_value | NUMERIC(16,10) | No | Hữu hạn | Giá trị metric thực đo |
| data_split | VARCHAR(20) | No | TRAIN/VALIDATION/TEST | Tập đánh giá |
| averaging | VARCHAR(20) | Yes | MACRO/WEIGHTED/MICRO hoặc NULL | Phương thức averaging |
| category_id | UUID | Yes | FK incident_categories.id | NULL cho metric tổng thể; có giá trị cho metric theo lớp |
| support_count | BIGINT | Yes | CHECK >= 0 | Số mẫu hỗ trợ |
| epoch_or_step | INTEGER | Yes | CHECK >= 0 | Epoch/step nếu lưu |
| recorded_at | TIMESTAMPTZ | No | Default UTC now | Thời điểm đo |
| metric_details_json | JSON | Yes | — | Metadata metric bổ sung |

### 3.13. Audit và dữ liệu ngoài bảng

Không thêm audit_logs để giữ đúng 12 bảng. Audit tổng quát đi qua audit sink append-only ngoài Database; không dùng application log tùy tiện thay thế. Cấu hình provider, retention, access control và tamper protection là quyết định TBD trước production. prediction_reviews vẫn là lịch sử kiểm duyệt chính thức trong Database.

## 4. Các quy tắc cross-table

- report_id trong predictions phải cùng report với preprocessing_run_id.
- report_id trong prediction_reviews phải cùng report với prediction_id.
- reports.final_category_id cập nhật cùng transaction với prediction_reviews.
- source_review_id và source_report_id trong dataset_samples phải nhất quán.
- model_versions.training_run_id chỉ trỏ tới run phù hợp đã thành công.
- Dataset FROZEN phải bất biến; training_runs giữ FK tới version đã sử dụng.
- Category FK ở tất cả bảng nhãn phải thuộc catalog 11 lớp.
- Không chuyển prediction hoặc trạng thái không đủ dữ liệu thành OTHER một cách tự động.

## 5. Thông tin còn TBD

Database engine, SQL type mapping, UUID implementation, auth cán bộ, role policy chi tiết, status sets, location CRS, storage provider, audit sink provider, file retention, privacy policy, threshold confidence, dataset split ratio và model activation policy cần được chốt trước khi tạo migration production.
