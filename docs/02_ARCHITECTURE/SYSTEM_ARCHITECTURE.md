# SYSTEM ARCHITECTURE — KIẾN TRÚC TỔNG THỂ

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Proposed Architecture |
| Kiểu kiến trúc đề xuất | Modular Monolith + tách tiến trình tác vụ nặng khi cần |

## 1. Mục tiêu kiến trúc

- Tách rõ Citizen Portal, Admin Portal và AI/Data Management.
- Giữ nghiệp vụ, API, persistence và ML pipeline có ranh giới trách nhiệm.
- Dễ phát triển, kiểm thử và thay thế model/provider.
- Bảo vệ dữ liệu người dân và thao tác quản trị.
- Bắt đầu với độ phức tạp vận hành vừa phải; chỉ tách microservice khi có nhu cầu thực tế.

## 2. Nguyên tắc

1. API-first: Frontend không truy cập trực tiếp Database.
2. Server-side authorization: mọi quyền được kiểm tra tại Backend.
3. Separation of concerns: UI, API, nghiệp vụ, persistence và ML không trộn lẫn.
4. Single source of truth: Database lưu dữ liệu nghiệp vụ; object storage lưu file; model registry lưu metadata/artifact.
5. Human-in-the-loop: prediction không tự thay thế review.
6. Version everything: dataset, preprocessing, model và API contract cần truy vết.
7. Secure by default: cấu hình theo môi trường, secret ngoài Git.
8. Observable: log, metrics và audit phải phục vụ debug nhưng không làm lộ dữ liệu.

## 3. Sơ đồ ngữ cảnh

```mermaid
flowchart LR
```
      Citizen[Người dân] --> CP[Citizen Portal]
      Staff[Cán bộ] --> AP[Admin Portal]
      CP --> API[Backend API]
      AP --> API
      API --> DB[(Relational Database)]
      API --> FS[(Object/File Storage)]
      API --> NLP[NLP Inference]
      NLP --> MR[(Model Registry / Model Artifacts)]
      API --> MAP[Map Provider]
      Google[Google OAuth] <--> API
      AIUser[AI/Data Manager] --> AP
      API --> AUD[Audit & Application Logs]

Sơ đồ là logic triển khai; công nghệ cụ thể và cách deploy từng thành phần cần được chốt trong Technology Stack/Deployment.

## 4. Thành phần chính

### 4.1. Citizen Portal

Ứng dụng web dành cho người dân. Chịu trách nhiệm hiển thị form, preview file, chọn vị trí, lịch sử và kết quả. Không giữ bí mật hoặc tự quyết định quyền nghiệp vụ.

### 4.2. Admin Portal

Ứng dụng web quản trị. Cung cấp dashboard, danh sách/chi tiết phản ánh, bản đồ, kiểm duyệt, quản trị dữ liệu và model theo permission. Nên có route root riêng, ví dụ /admin; tên domain/route cuối cùng TBD.

### 4.3. Backend API

Điểm thực thi xác thực, authorization, validation, nghiệp vụ và persistence. Chia phiên bản API; cung cấp contract ổn định cho hai portal.

### 4.4. Relational Database

Lưu tài khoản, vai trò, phản ánh, file metadata, vị trí, danh mục, predictions, reviews, datasets, samples, training runs, metrics và model metadata theo schema được duyệt.

### 4.5. File/Object Storage

Lưu ảnh đính kèm và artifact lớn. Database chỉ lưu metadata/key/URL nội bộ cần thiết; không lưu binary lớn trong bảng nếu không có quyết định khác. Quyền truy cập file phải được kiểm soát.

### 4.6. NLP Inference

Tiền xử lý văn bản và gọi model version được chọn. Có thể chạy trong process của Backend ở giai đoạn nhỏ hoặc worker riêng khi cần scale/queue. Thiết kế phải tránh phụ thuộc UI.

### 4.7. Training Worker / Model Registry

Training worker chạy công việc nặng ngoài request đồng bộ. Registry lưu metadata, artifact location, trạng thái và phiên bản model. Cơ chế hàng đợi/registry provider còn TBD.

### 4.8. External Providers

Google Identity cho OAuth; Map Provider cho bản đồ/geocoding; storage và dịch vụ triển khai. Mỗi provider phải được bọc bằng adapter để giảm khóa chặt vào nhà cung cấp.

## 5. Luồng dữ liệu mức cao

1. Portal gửi request có access context đến Backend.
2. Backend xác thực và kiểm tra permission.
3. Backend validate dữ liệu, lưu dữ liệu nghiệp vụ.
4. Khi phản ánh được tạo, Backend tạo tác vụ dự đoán hoặc gọi inference theo chiến lược đã chọn.
5. Inference tải đúng preprocessing/model version, trả label và score.
6. Backend ghi prediction liên kết phản ánh/model.
7. Moderator review, Backend lưu nhãn đã duyệt và audit.
8. Dashboard truy vấn dữ liệu tổng hợp theo quyền.
9. AI/Data Manager tạo dataset từ nguồn dữ liệu được phép, chạy training, lưu metrics/artifacts và đăng ký model version.

## 6. Kiểu triển khai đề xuất

**Proposed:** bắt đầu bằng một Backend modular monolith, hai portal có thể là hai ứng dụng frontend hoặc một ứng dụng có hai route root nhưng phải tách quyền. Tách inference/training thành worker/process khi tác vụ dài hoặc cần scale độc lập.

Không khuyến nghị triển khai microservices ngay khi chưa có tải, team hoặc ranh giới vận hành chứng minh nhu cầu. Cần giữ module boundary để có thể tách sau.

## 7. Ranh giới tin cậy

- Browser/client là môi trường không tin cậy.
- Backend là nơi xác minh identity và permission.
- Database không công khai trực tiếp.
- Storage không public-write; file private cần URL ký hạn ngắn hoặc proxy được kiểm soát.
- Model artifact chỉ được nạp từ nguồn tin cậy đã kiểm tra.
- External provider có thể lỗi hoặc trả dữ liệu không hợp lệ; cần timeout/retry có giới hạn.

## 8. Quyết định còn TBD

- Frontend framework và cách tách deployment hai portal.
- Backend framework và ASGI/WSGI server.
- Database engine/geospatial extension.
- Queue/worker technology.
- Object storage provider.
- Map/geocoding provider.
- Model registry/experiment tracking.
- Hạ tầng hosting, domain, TLS, CI/CD và monitoring.

## 9. Tiêu chí kiến trúc

- Không có truy cập DB từ Frontend.
- Module có API nội bộ rõ ràng.
- Provider-specific code không lan vào domain layer.
- Mỗi prediction truy xuất được model version.
- Review không ghi đè prediction gốc.
- Có thể chạy test module mà không cần gọi Google/Map provider thật.


## 10. Database and classification baseline

Relational persistence baseline gồm đúng 12 bảng được đặc tả tại [DATABASE_DESIGN](../03_DATABASE/DATABASE_DESIGN.md): users, incident_categories, reports, report_attachments, preprocessing_runs, model_versions, predictions, prediction_reviews, datasets, dataset_samples, training_runs và training_metrics. ERD chính thức của baseline ở [ERD](../03_DATABASE/ERD.md).

Catalog có đúng 11 danh mục, dùng category_code ổn định theo [CLASSIFICATION_SPECIFICATION](../01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md). API, Frontend, Dashboard, Dataset và model label mapping phải dùng cùng catalog/version.

Audit event tổng quát không được thêm vào bảng thứ 13 trong baseline. Các event cần audit đi qua audit sink append-only bên ngoài relational schema; sink phải được triển khai bền vững và kiểm soát quyền trước production. Chọn provider còn TBD.
