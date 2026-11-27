# ERD — SƠ ĐỒ QUAN HỆ CƠ SỞ DỮ LIỆU ST-NLP

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 2.0 |
| Trạng thái | Proposed physical ERD — đúng 12 bảng |
| Nguồn danh mục | [CLASSIFICATION_SPECIFICATION](../01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md) |
| ORM định hướng | SQLAlchemy |

## 1. Phạm vi

Sơ đồ biểu diễn 12 bảng nghiệp vụ do chủ dự án đề xuất. Không có bảng roles, permissions, dataset_versions hoặc audit_logs trong baseline. Audit tổng quát được chuyển qua audit sink append-only ngoài 12 bảng; chi tiết tại DATABASE_DESIGN.md.

Một hàng trong datasets đại diện cho một phiên bản cụ thể của Dataset. Dataset version đóng băng không được sửa; phiên bản mới là hàng mới, có thể tham chiếu parent_dataset_id.

## 2. ERD vật lý đề xuất

~~~mermaid
erDiagram
    users ||--o{ reports : submits
    users ||--o{ report_attachments : uploads
    users ||--o{ prediction_reviews : reviews
    users ||--o{ datasets : creates
    users ||--o{ training_runs : starts
    users o|--o{ model_versions : registers
    incident_categories ||--o{ reports : final_label
    incident_categories ||--o{ predictions : predicted_label
    incident_categories ||--o{ prediction_reviews : previous_label
    incident_categories ||--o{ prediction_reviews : selected_label
    incident_categories ||--o{ dataset_samples : labels
    incident_categories ||--o{ training_metrics : per_class_metric

    reports ||--o{ report_attachments : has
    reports ||--o{ preprocessing_runs : preprocesses
    reports ||--o{ predictions : receives
    reports ||--o{ prediction_reviews : reviewed
    reports o|--o{ dataset_samples : optional_source

    preprocessing_runs ||--o{ predictions : input_for
    model_versions o|--o{ predictions : produces
    predictions ||--o{ prediction_reviews : reviewed_as

    datasets ||--o{ dataset_samples : contains
    datasets ||--o{ training_runs : used_by
    datasets o|--o{ datasets : previous_version

    training_runs ||--o{ training_metrics : reports
    training_runs o|--o{ model_versions : creates
    prediction_reviews o|--o{ dataset_samples : optional_label_source

    users {
        UUID id PK
        string auth_provider
        string provider_subject
        string email
        JSON role_codes
        string account_status
    }
    incident_categories {
        UUID id PK
        string category_code UK
        string category_name
        int sort_order UK
        boolean is_active
    }
    reports {
        UUID id PK
        UUID user_id FK
        text raw_content
        string address
        decimal latitude
        decimal longitude
        UUID final_category_id FK
        string status
    }
    report_attachments {
        UUID id PK
        UUID report_id FK
        UUID uploaded_by FK
        string storage_key UK
        string verified_mime_type
        bigint file_size_bytes
    }
    preprocessing_runs {
        UUID id PK
        UUID report_id FK
        string preprocessing_version
        JSON normalization_config_json
        text processed_text
        string processing_status
    }
    model_versions {
        UUID id PK
        string model_family
        string version_label
        UUID training_run_id FK
        string artifact_uri
        string artifact_checksum
        string model_status
    }
    predictions {
        UUID id PK
        UUID report_id FK
        UUID preprocessing_run_id FK
        UUID model_version_id FK
        UUID predicted_category_id FK
        decimal confidence_value
        string inference_status
    }
    prediction_reviews {
        UUID id PK
        UUID report_id FK
        UUID prediction_id FK
        UUID reviewer_id FK
        UUID previous_category_id FK
        UUID selected_category_id FK
        string action_code
    }
    datasets {
        UUID id PK
        string dataset_name
        string version_label
        UUID parent_dataset_id FK
        string dataset_status
        string label_schema_version
    }
    dataset_samples {
        UUID id PK
        UUID dataset_id FK
        text text_content
        UUID category_id FK
        string labeling_status
        string split
        UUID source_report_id FK
        UUID source_review_id FK
    }
    training_runs {
        UUID id PK
        UUID dataset_id FK
        string model_family
        string algorithm_name
        JSON hyperparameters_json
        string preprocessing_version
        string run_status
    }
    training_metrics {
        UUID id PK
        UUID training_run_id FK
        string metric_name
        decimal metric_value
        string data_split
        string averaging
        UUID category_id FK
    }
~~~

## 3. Quan hệ chính

| Quan hệ | Cardinality | Ý nghĩa |
|---|---|---|
| users → reports | 1:N | Một tài khoản người dân có nhiều phản ánh |
| reports → report_attachments | 1:N | Một phản ánh có nhiều file đính kèm |
| reports → preprocessing_runs | 1:N | Một phản ánh có nhiều lần tiền xử lý |
| reports → predictions | 1:N | Một phản ánh có nhiều lần dự đoán/model retry |
| preprocessing_runs → predictions | 1:N | Một kết quả preprocess có thể được dùng trong nhiều lần inference |
| model_versions → predictions | 1:N | Một phiên bản model tạo nhiều prediction |
| predictions → prediction_reviews | 1:N | Một prediction có thể được xác nhận/chỉnh sửa qua nhiều review |
| users → prediction_reviews | 1:N | Một cán bộ có thể thực hiện nhiều review |
| incident_categories → các bảng nhãn | 1:N | Danh mục được tham chiếu bởi report, prediction, review, sample và metric |
| datasets → dataset_samples | 1:N | Mỗi dataset version chứa nhiều mẫu |
| datasets → training_runs | 1:N | Một version có thể dùng trong nhiều lần huấn luyện |
| training_runs → training_metrics | 1:N | Một run có nhiều metric |
| training_runs → model_versions | 1:N | Run thành công có thể sinh model version/artifact |
| datasets → datasets | 1:N | parent_dataset_id mô tả lineage giữa các phiên bản |

## 4. Invariants cần kiểm tra ngoài quan hệ FK

- predictions.report_id phải khớp reports của preprocessing_runs.report_id.
- prediction_reviews.report_id phải khớp reports của prediction_id.
- Sau review thành công, reports.final_category_id phải bằng selected_category_id của review hiện hành.
- prediction_reviews là append-only; không sửa/xóa lịch sử.
- category_code phải thuộc đúng catalog 11 lớp.
- dataset_samples.category_id NULL chỉ khi labeling_status cho phép chưa có nhãn.
- dataset_samples.source_review_id (nếu có) phải thuộc cùng source_report_id.
- model_versions.training_run_id (nếu có) phải tham chiếu run thành công và artifact đã được xác minh.

## 5. Ngoài ERD 12 bảng

Audit event tổng quát không có bảng trong Database baseline. Các event bắt buộc phải gửi tới audit sink append-only riêng; không được coi application debug log thông thường là đủ. Audit sink và retention provider vẫn TBD.

## 6. Quy tắc cập nhật

Khi code được triển khai, SQLAlchemy models và migration sẽ trở thành căn cứ đối chiếu physical schema thực tế. Mọi thay đổi phải cập nhật ERD và Data Dictionary cùng PR. Sơ đồ này là thiết kế đề xuất, không phải bằng chứng rằng bảng đã được tạo trong Database.
