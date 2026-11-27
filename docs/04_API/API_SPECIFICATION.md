# API SPECIFICATION — ĐẶC TẢ API

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Proposed Contract — cần chốt cùng Backend |
| API prefix đề xuất | /api/v1 |
| Data format | JSON; multipart/form-data hoặc signed upload cho file |

## 1. Mục tiêu và nguyên tắc

Tài liệu định nghĩa hợp đồng giao tiếp giữa Citizen Portal, Admin Portal và Backend. Danh sách route dưới đây là endpoint dự kiến để thiết kế; chưa phải cam kết rằng code đã triển khai. Khi API được chốt, phải bổ sung schema request/response đầy đủ, OpenAPI và ví dụ thực tế.

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
