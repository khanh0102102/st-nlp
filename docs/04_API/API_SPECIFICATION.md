# API SPECIFICATION — ĐẶC TẢ API

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.1 |
| Trạng thái | Baseline mixed contract — một phần endpoints đã triển khai; API tổng thể tiếp tục mở rộng |
| API prefix đề xuất | /api/v1 |
| Data format | JSON; multipart/form-data hoặc signed upload cho file |

## 1. Mục tiêu và nguyên tắc

Tài liệu định nghĩa hợp đồng giao tiếp giữa Citizen Portal, Admin Portal và Backend. Một phần route dưới đây đang có trong feature branch; đây không phải tuyên bố mọi route/workflow SRS đã hoàn tất. Schema/OpenAPI và authorization tiếp tục đồng bộ theo milestone.

- API dùng version prefix.
- HTTPS ngoài local.
- JSON UTF-8 cho dữ liệu thông thường.
- Date/time dùng ISO 8601 và timezone rõ ràng; Backend lưu UTC.
- Danh sách dữ liệu lớn phải phân trang.
- Backend kiểm tra authentication, role, permission và resource ownership.
- File upload có giới hạn, xác minh nội dung file.
- Không trả internal stack trace hoặc secret.

## 2. Quy ước response đề xuất

Thành công:
    {
      "data": {},
      "meta": {},
      "request_id": "..."
    }

Lỗi:
    {
      "error": {
        "code": "VALIDATION_ERROR",
        "message": "Dữ liệu không hợp lệ",
        "details": []
      },
      "request_id": "..."
    }

Đây là envelope đề xuất; chỉ chốt sau khi thống nhất với code và OpenAPI. Không trả thông tin nhạy cảm trong message/details.

## 3. HTTP status

| Code | Ý nghĩa |
|---|---|
| 200 | Thành công |
| 201 | Tạo tài nguyên thành công |
| 202 | Đã tiếp nhận tác vụ bất đồng bộ |
| 204 | Thành công, không có response body |
| 400 | Request sai định dạng/logic |
| 401 | Chưa xác thực |
| 403 | Không đủ quyền |
| 404 | Không tìm thấy hoặc không được phép tiết lộ tài nguyên |
| 409 | Conflict/concurrency/idempotency conflict |
| 413 | Payload quá lớn |
| 415 | Media type không hỗ trợ |
| 422 | Validation error theo convention đã chọn |
| 429 | Rate limit |
| 500 | Lỗi nội bộ |
| 502/503/504 | External provider hoặc service tạm thời không khả dụng |

Cần chọn thống nhất 400/422 cho validation; không dùng hai kiểu tùy tiện.

## 4. Authentication API dự kiến

| Method | Endpoint | Mục đích | Quyền |
|---|---|---|---|
| GET | /api/v1/auth/google/start | Bắt đầu OAuth Google | Public |
| GET | /api/v1/auth/google/callback | Xử lý callback | OAuth state |
| GET | /api/v1/auth/me | Lấy identity/session hiện tại | Authenticated |
| POST | /api/v1/auth/logout | Đăng xuất | Authenticated |

Cơ chế session/cookie hoặc bearer token còn TBD. Endpoint quản trị phải kiểm tra staff role; không mặc định login Google được cấp quyền Admin.

## 5. Citizen API dự kiến

| Method | Endpoint | Mục đích |
|---|---|---|
| GET | /api/v1/citizen/profile | Xem hồ sơ của mình |
| PATCH | /api/v1/citizen/profile | Cập nhật trường được phép |
| POST | /api/v1/citizen/reports | Tạo phản ánh |
| GET | /api/v1/citizen/reports | Danh sách phản ánh của mình |
| GET | /api/v1/citizen/reports/{report_id} | Chi tiết phản ánh của mình |
| GET | /api/v1/citizen/reports/{report_id}/prediction | Kết quả AI được phép hiển thị |
| GET | /api/v1/citizen/reports/{report_id}/history | Trạng thái/lịch sử được phép hiển thị |

Không nhận owner_id từ client để quyết định chủ sở hữu. Backend lấy owner từ principal đã xác thực.

## 6. Attachment API dự kiến

Có thể chọn một trong hai chiến lược sau khi chốt storage:
- Multipart upload qua Backend: POST /api/v1/attachments.
- Signed upload: POST /api/v1/uploads/presign → upload đến storage → POST /api/v1/uploads/complete.

Chưa chọn chiến lược. Trong cả hai trường hợp Backend phải xác minh quyền, loại file, kích thước, checksum nếu có và trạng thái hoàn tất upload. Download file private phải kiểm tra quyền.

## 7. Admin API dự kiến

| Method | Endpoint | Mục đích |
|---|---|---|
| GET | /api/v1/admin/reports | Danh sách và bộ lọc |
| GET | /api/v1/admin/reports/{report_id} | Chi tiết report |
| GET | /api/v1/admin/reports/{report_id}/predictions | Lịch sử prediction |
| POST | /api/v1/admin/reports/{report_id}/reviews | Tạo review |
| GET | /api/v1/admin/reports/{report_id}/reviews | Lịch sử review |
| PATCH | /api/v1/admin/reports/{report_id}/status | Chuyển trạng thái hợp lệ |
| GET | /api/v1/admin/dashboard/summary | Số liệu tổng quan |
| GET | /api/v1/admin/dashboard/categories | Thống kê theo 11 danh mục |
| GET | /api/v1/admin/map/reports | Dữ liệu marker/cluster theo filter |
| GET | /api/v1/admin/categories | Danh mục phân loại |

Mọi filter phải được whitelist; response map không được trả dữ liệu cá nhân không cần thiết.

## 8. AI & Data Management API dự kiến

| Method | Endpoint | Mục đích |
|---|---|---|
| GET/POST | /api/v1/admin/datasets | Danh sách/tạo Dataset |
| GET/PATCH | /api/v1/admin/datasets/{dataset_id} | Chi tiết/cập nhật metadata |
| GET/POST | /api/v1/admin/datasets/{dataset_id}/samples | Danh sách/thêm samples |
| PATCH/DELETE | /api/v1/admin/dataset-samples/{sample_id} | Sửa/loại sample theo policy |
| POST | /api/v1/admin/datasets/{dataset_id}/validate | Validate dataset |
| POST | /api/v1/admin/datasets/{dataset_id}/versions | Đóng băng/tạo version |
| GET/POST | /api/v1/admin/training-runs | Danh sách/tạo training run |
| GET | /api/v1/admin/training-runs/{run_id} | Chi tiết trạng thái run |
| GET | /api/v1/admin/training-runs/{run_id}/metrics | Metrics của run |
| GET | /api/v1/admin/models | Danh sách model versions |
| POST | /api/v1/admin/models | Đăng ký model version |
| POST | /api/v1/admin/models/{model_id}/activate | Kích hoạt model có quyền |
| POST | /api/v1/admin/models/{model_id}/rollback | Rollback theo policy |

Training nên được điều phối bất đồng bộ; API trả 202 và run ID khi phù hợp.

## 9. Query và pagination

- Hỗ trợ page/limit hoặc cursor theo quyết định chung.
- Có giới hạn max page size.
- Sort field phải nằm trong whitelist.
- Filter date dùng ISO 8601; timezone được xác định.
- Dashboard và map dùng cùng semantics bộ lọc.
- Tổng số bản ghi chỉ trả khi cần và không gây query quá tốn kém.

## 10. Request validation

- Validate kiểu, độ dài, required/optional, enum và nested object.
- Normalize input theo policy; không âm thầm sửa nội dung gốc.
- Tọa độ có miền hợp lệ và hệ tọa độ rõ.
- Upload giới hạn số file, size, extension và MIME đã xác minh.
- Review chỉ nhận category code active.
- Không cho client gửi field server-managed như owner, role, status override hoặc model active.

## 11. Idempotency và concurrency

POST tạo report/review/trigger training có thể cần idempotency key. Update cần version/If-Match hoặc cơ chế optimistic locking khi nhiều người thao tác. Endpoint activate model phải atomic và audit.

## 12. OpenAPI và contract testing

- OpenAPI là tài liệu kỹ thuật máy đọc được sau khi framework được chọn.
- Mỗi endpoint cần request schema, response schema, auth requirement, permission, error code và ví dụ.
- Frontend và Backend dùng contract test.
- Breaking changes phải tăng API version hoặc có migration period.
- Không cập nhật bảng endpoint mà bỏ quên code/tests.


## 13. Contract danh mục và nhãn phân loại

Nguồn chuẩn: [CLASSIFICATION_SPECIFICATION](../01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md). API phải dùng category_code ổn định và trả category object có tối thiểu id, category_code, category_name, sort_order. Không dùng category_name làm khóa.

Endpoint catalog read-only dùng chung cho hai portal:

| Method | Endpoint | Mục đích | Quyền |
|---|---|---|---|
| GET | /api/v1/categories | Lấy đủ 11 danh mục theo sort_order | Public hoặc authenticated theo policy triển khai; không trả dữ liệu nhạy cảm |

GET /api/v1/admin/categories hiện có trong danh sách admin có thể giữ làm route tương thích nếu cần, nhưng không tạo catalog khác. Seed Database phải có đúng 11 bản ghi.

POST /api/v1/citizen/reports không nhận category_id/category_code do Citizen cung cấp ở baseline; Backend tạo report và gọi NLP. Response prediction tối thiểu gồm predicted_category (id/code/name nếu có), confidence_value, confidence_type, model_version, preprocessing_version, inference_status và needs_review. Không trả phần trăm confidence nếu score là raw decision score chưa calibration.

POST /api/v1/admin/reports/{report_id}/reviews nhận category_code hoặc category ID thuộc catalog hiện hành, action CONFIRMED/CORRECTED và note nếu policy yêu cầu. Backend tự lấy reviewer từ principal, xác minh report/prediction thuộc nhau, ghi prediction_reviews và cập nhật reports.final_category_id trong một transaction. Client không được gửi reviewer_id hoặc ép final_category_id trực tiếp.

Dataset sample API chỉ chấp nhận category_code thuộc 11 danh mục hoặc labeling_status được phép nếu chưa gán nhãn. OTHER là class hợp lệ; INSUFFICIENT_INFORMATION/NEEDS_REVIEW/UNLABELED là trạng thái sample, không phải category.

## 14. Database persistence contract

Database baseline đúng 12 bảng theo [DATABASE_DESIGN](../03_DATABASE/DATABASE_DESIGN.md). predictions phải truy được report, preprocessing run và model version; prediction_reviews là lịch sử append-only; mỗi row datasets là một version; training_metrics hỗ trợ metric tổng thể/per-class/per-split. API contract không được yêu cầu bảng phụ không có trong baseline.

Audit event nhạy cảm được gửi qua audit sink append-only ngoài 12 bảng. Việc gửi audit cần xử lý lỗi/retry theo chính sách; không ghi secret, token hoặc raw report vào audit.


---

## Implementation mapping — Foundation API (2026-11-27)

Các route dưới đây đã được tạo trên feature branch; đây là hiện trạng mã nguồn, không đồng nghĩa đã vượt Docker CI.

| Method | Endpoint | Access | Chức năng |
|---|---|---|---|
| GET | `/api/v1/categories` | Public | Danh mục active, đúng 11 codes |
| POST | `/api/v1/auth/staff/login` | Public | Staff local login |
| GET | `/api/v1/auth/google/start` | Public/config required | Bắt đầu Google OIDC |
| GET | `/api/v1/auth/google/callback` | Provider callback | Google OIDC callback |
| GET | `/api/v1/auth/me` | Authenticated | Principal hiện tại |
| GET | `/api/v1/auth/csrf` | Authenticated | Cấp signed CSRF token |
| POST | `/api/v1/auth/logout` | Authenticated + CSRF | Logout |
| GET/PATCH | `/api/v1/citizen/profile` | Citizen | Xem/cập nhật profile |
| POST/GET | `/api/v1/citizen/reports` | Citizen | Tạo phản ánh / lịch sử phản ánh |
| GET | `/api/v1/citizen/reports/{report_id}` | Owner | Chi tiết phản ánh |
| GET | `/api/v1/citizen/reports/{report_id}/prediction` | Owner | Kết quả prediction gần nhất |
| GET | `/api/v1/citizen/reports/{report_id}/history` | Owner | Timeline từ local audit sink |
| POST | `/api/v1/attachments` | Authenticated + owner check | Multipart upload với `report_id` và `file` |
| GET | `/api/v1/citizen/reports/{report_id}/attachments/{attachment_id}` | Owner | Download minh chứng |
| GET | `/api/v1/admin/categories` | RECEIVER/ADMIN | Catalog cho khu quản trị |
| GET | `/api/v1/admin/reports` | RECEIVER/ADMIN | Tìm kiếm/lọc/phân trang |
| GET | `/api/v1/admin/reports/{report_id}` | RECEIVER/ADMIN | Chi tiết phản ánh và prediction history |
| GET | `/api/v1/admin/reports/{report_id}/predictions` | RECEIVER/ADMIN | Lịch sử dự đoán |
| POST/GET | `/api/v1/admin/reports/{report_id}/reviews` | RECEIVER/ADMIN | Tạo/xem lịch sử kiểm duyệt |
| PATCH | `/api/v1/admin/reports/{report_id}/status` | RECEIVER/ADMIN | Chuyển trạng thái theo workflow |
| GET | `/api/v1/admin/dashboard/summary` | RECEIVER/ADMIN | Thống kê tổng và trạng thái |
| GET | `/api/v1/admin/dashboard/categories` | RECEIVER/ADMIN | Thống kê theo 11 category |
| GET | `/api/v1/admin/map/reports` | RECEIVER/ADMIN | Tọa độ phản ánh để render map |

### Semantics đang áp dụng ở bản foundation

- Report luôn được lưu trước. Khi chưa có active ML model, hệ thống ghi một preprocessing run SKIPPED và prediction `INFERENCE_FAILED` với `NO_ACTIVE_MODEL`; không tự gán `OTHER`.
- `reports.raw_content` không bị sửa bởi preprocessing.
- Review insert/flush, transaction-local marker và update `reports.final_category_id` dùng cùng SQLAlchemy transaction; lỗi rollback. PostgreSQL trigger kiểm tra staff ACTIVE RECEIVER/ADMIN và consistency.
- Prediction/review rows được DB trigger bảo vệ append-only; `reports.raw_content` không cho UPDATE. Model registry chỉ có một ACTIVE nhờ partial unique index/advisory lock.
- Nếu ML_SERVICE_URL rỗng, service lỗi hoặc body sai hợp đồng, POST report vẫn trả 201 khi report đã lưu; prediction INFERENCE_FAILED và category/confidence NULL (không phải inference success).
- PostgreSQL từ chối review do citizen/inactive user và update final_category_id thiếu review marker cùng transaction.
- Activate/rollback giữ đúng một ACTIVE model và không xóa model version lịch sử.
- Dashboard đếm dữ liệu PostgreSQL, không dùng số mẫu cố định.
- Upload kiểm tra magic bytes, JPEG/PNG/WebP, tối đa 10 MiB/file và tối đa 5 file/report; binary lưu ở private local volume.

Những route này chưa thay thế các endpoint còn lại trong API Specification; tiếp tục mở rộng theo RTM và Use Case.
