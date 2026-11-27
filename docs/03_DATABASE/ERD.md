# ERD — ENTITY RELATIONSHIP DIAGRAM

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Conceptual ERD — không phải physical schema |
| Nguồn chuẩn vật lý | SQLAlchemy models + migrations đã được duyệt |

## 1. Lưu ý

Sơ đồ dưới đây mô tả các khái niệm và quan hệ nghiệp vụ ở mức khái niệm. Nó không khóa số lượng bảng, tên bảng, tên cột hoặc kiểu dữ liệu vật lý. Thiết kế làm việc trước đây có nhắc mục tiêu 12 bảng; cần đối chiếu với schema thực tế trước khi biến sơ đồ này thành ERD vật lý.

## 2. ERD khái niệm

```mermaid
erDiagram
```
      USER ||--o{ INCIDENT : submits
      USER }o--o{ ROLE : assigned
      INCIDENT ||--o{ ATTACHMENT : has
      INCIDENT ||--o{ PREDICTION : receives
      INCIDENT ||--o{ REVIEW : reviewed
      CATEGORY ||--o{ PREDICTION : classifies
      CATEGORY ||--o{ REVIEW : selected_as
      MODEL_VERSION ||--o{ PREDICTION : produced
      DATASET ||--o{ DATASET_SAMPLE : contains
      DATASET ||--o{ TRAINING_RUN : source_for
      TRAINING_RUN ||--o{ TRAINING_METRIC : reports
      TRAINING_RUN ||--o| MODEL_VERSION : produces
      USER ||--o{ REVIEW : performs

## 3. Mô tả quan hệ

| Quan hệ | Ý nghĩa |
|---|---|
| User — Incident | Một người dân có thể gửi nhiều phản ánh; mỗi phản ánh có chủ sở hữu |
| User — Role | Tài khoản được gán một hoặc nhiều role tùy RBAC |
| Incident — Attachment | Một phản ánh có thể có nhiều ảnh |
| Incident — Prediction | Một phản ánh có thể có nhiều lần dự đoán theo model/version/retry |
| Category — Prediction | Prediction tham chiếu nhãn trong danh mục |
| Model Version — Prediction | Mỗi prediction phải biết model version đã tạo ra nó |
| Incident — Review | Một phản ánh có thể có lịch sử review |
| User — Review | Review phải truy được cán bộ thực hiện |
| Dataset — Dataset Sample | Dataset/version quản lý các sample |
| Dataset — Training Run | Training run sử dụng dataset/version xác định |
| Training Run — Training Metric | Một run có nhiều metric |
| Training Run — Model Version | Run thành công có thể sinh model artifact/version |

## 4. Các điểm cần quyết định trong ERD vật lý

- Có bảng account chung hay tách citizen/staff.
- Role/permission được biểu diễn bằng role-permission mapping hay policy.
- Vị trí nằm trực tiếp trên Incident hay thực thể riêng.
- Prediction/review là lịch sử append-only hay có current pointer.
- Có tách Review và Review History không.
- Dataset và Dataset Version là một hay hai thực thể.
- Dataset Sample lưu text trực tiếp hay lưu reference đến nguồn dữ liệu.
- Training Metric có bảng chuẩn hóa hay JSON metrics.
- Model artifact metadata và deployment target có cần entity riêng không.
- Audit log dùng bảng DB hay hệ thống log ngoài.
- Tổng số bảng phải phù hợp schema SQLAlchemy đã được chủ dự án duyệt.

## 5. Quy tắc cập nhật

Khi schema vật lý được chốt:
1. Trích xuất quan hệ từ ORM/migration.
2. Cập nhật ERD với tên bảng/cột chính xác.
3. Kiểm tra mỗi foreign key và cardinality.
4. Cập nhật Data Dictionary.
5. Đưa hình/sơ đồ render vào review.
6. Cập nhật version và liên kết migration.
