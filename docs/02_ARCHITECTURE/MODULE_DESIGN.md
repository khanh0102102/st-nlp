# MODULE DESIGN — THIẾT KẾ MODULE

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Proposed |

## 1. Mục đích

Định nghĩa trách nhiệm, đầu vào/đầu ra và ranh giới phụ thuộc của các module ST-NLP để nhiều người/AI agent có thể phát triển song song mà không tạo logic trùng lặp.

## 2. Module Backend

| Module | Trách nhiệm | Không chịu trách nhiệm |
|---|---|---|
| Identity & Auth | OAuth callback, session, identity mapping | Quyết định nghiệp vụ của report |
| Authorization | Role, permission, policy checks | Ẩn nút UI thay cho bảo vệ API |
| Citizen Profile | Hồ sơ người dân | Quản lý tài khoản cán bộ nếu policy khác |
| Incident | Tạo, đọc, cập nhật trạng thái phản ánh | Dự đoán NLP |
| Attachment | Validate metadata, upload, download có quyền | Xử lý nội dung ảnh bằng AI trong baseline |
| Location | Validate tọa độ, chuẩn hóa dữ liệu vị trí | Thay thế dịch vụ map |
| Classification Catalog | Quản lý 11 danh mục và trạng thái | Tự đặt nhãn theo code |
| NLP Pipeline | Normalize, tokenize/vectorize, preprocess | Quản lý phiên đăng nhập |
| Prediction | Điều phối inference, lưu kết quả và model reference | Quyết định review của cán bộ |
| Review | Xác nhận/sửa nhãn, history và audit | Ghi đè prediction gốc |
| Dashboard | Aggregate/filter/statistics | Tạo bản sao dữ liệu nghiệp vụ không đồng bộ |
| Dataset | Dataset metadata, version và source | Thực hiện training trong request API |
| Dataset Sample | Quản lý sample, label, validation | Thay đổi dataset version đã đóng băng âm thầm |
| Training | Tạo/theo dõi training run | Chạy tác vụ dài trong HTTP request |
| Metrics & Evaluation | Tính/lưu metrics và report | Kích hoạt model không qua policy |
| Model Registry | Model version, artifact reference, activation | Lưu secret hoặc artifact tùy tiện trong DB |
| Audit | Ghi sự kiện nhạy cảm có cấu trúc | Ghi toàn bộ payload nhạy cảm |

Tên package cuối cùng có thể khác nhưng trách nhiệm phải giữ nhất quán.

## 3. Module Frontend

### Citizen Portal
- Auth pages/layout.
- Profile.
- Report create form.
- Attachment preview/upload.
- Location picker.
- Report list/detail/history.
- Prediction/status presentation.

### Admin Portal
- Admin auth/layout/navigation.
- Dashboard.
- Incident list/detail.
- Map view.
- Prediction review.
- Review history.
- User/role administration theo permission.
- Dataset, sample, training run, metrics và model management.

Frontend nên chia feature theo nghiệp vụ; component dùng chung không chứa policy bảo mật.

## 4. Hợp đồng giữa module

| Module nguồn | Module đích | Hợp đồng |
|---|---|---|
| Auth | Authorization | Actor identity và session claims đã xác minh |
| Incident | Attachment | Incident ID và metadata file |
| Incident | Prediction | Incident ID, text snapshot/version và request context |
| NLP Pipeline | Prediction | Preprocessed representation và pipeline version |
| Prediction | Review | Prediction ID, label, score, model version |
| Review | Dataset | Reviewed label và provenance có thể được chọn |
| Dataset | Training | Immutable dataset version đã validate |
| Training | Metrics | Run ID, metric name/value/split/class |
| Training | Model Registry | Artifact, config và evaluation reference |
| Dashboard | Incident/Review | Read model hoặc truy vấn aggregate có quyền |

## 5. Quy tắc phụ thuộc

- API layer gọi application/use case, không truy cập trực tiếp model ORM ngoài repository pattern đã chọn.
- Domain không phụ thuộc framework web, provider bên ngoài hoặc ORM cụ thể.
- Module không import private internals của nhau; dùng public service/schema.
- Không tạo circular dependency.
- Không để Frontend tự quyết định role/owner.
- Không để Training module gọi trực tiếp bảng nghiệp vụ tùy tiện; dùng service/contract.
- Adapter bên ngoài phải có mock/fake cho test.

## 6. Quy tắc song song hóa

Có thể phát triển song song khi đã chốt:
- API schema và error contract.
- ID/type và quan hệ dữ liệu.
- Role/permission.
- State transition.
- Prediction/review semantics.
- Dataset/sample schema.

Mỗi nhiệm vụ phải ghi các module bị ảnh hưởng và PR không nên sửa quá nhiều module không liên quan.

## 7. Definition of Done theo module

- Public interface được mô tả.
- Unit test cho domain/service.
- API test cho endpoint liên quan.
- Permission test nếu có tài nguyên bảo vệ.
- Logging/audit đúng policy.
- Không vi phạm dependency rule.
- Tài liệu module/API/database được cập nhật.
