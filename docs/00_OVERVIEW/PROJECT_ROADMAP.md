# PROJECT ROADMAP — LỘ TRÌNH PHÁT TRIỂN

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Proposed baseline |
| Phương pháp | Phát triển theo module, có cổng kiểm tra và tích hợp thường xuyên |

## 1. Nguyên tắc lập lộ trình

Lộ trình được chia theo đầu ra có thể kiểm tra, không chỉ theo số lượng file code. Thứ tự có thể điều chỉnh khi phát hiện phụ thuộc, nhưng không bỏ qua cổng thống nhất nghiệp vụ, dữ liệu, bảo mật và API. Những công việc có thể làm song song phải có hợp đồng giao tiếp rõ ràng.

## 2. Các giai đoạn

### Giai đoạn 0 — Khởi tạo và chốt yêu cầu

**Công việc**
- Hoàn thiện Project Overview, Scope và BRD.
- Chốt 11 danh mục và quy tắc nhãn.
- Chốt actor, vai trò, URL/route của hai cổng.
- Chốt workflow phản ánh và workflow kiểm duyệt.
- Chốt stack công nghệ, môi trường và quyết định lưu file/bản đồ.
- Rà soát SRS, use case và acceptance criteria.

**Đầu ra**
- Bộ yêu cầu baseline được duyệt.
- Decision log và backlog ưu tiên.
- Danh mục câu hỏi TBD có người chịu trách nhiệm.

**Cổng hoàn thành**
- Không còn mâu thuẫn nghiệp vụ nghiêm trọng.
- Mọi yêu cầu Must có ID và tiêu chí nghiệm thu.
- Phạm vi và ngoài phạm vi được xác nhận.

### Giai đoạn 1 — Thiết kế nền tảng

**Công việc**
- Chốt kiến trúc ứng dụng và ranh giới module.
- Chốt ERD, Data Dictionary, constraints, migration strategy.
- Chốt API contract và error model.
- Thiết kế UI/UX và trạng thái rỗng/loading/error/success.
- Thiết kế security/RBAC, OAuth, upload và audit.
- Chuẩn hóa repository, CI và coding standards.

**Đầu ra**
- Kiến trúc và thiết kế kỹ thuật được duyệt.
- Database/API/UI contract có version.
- Skeleton frontend/backend/database/tests.
- CI chạy lint/test cơ bản.

**Cổng hoàn thành**
- Các nhóm có thể phát triển song song mà không phải tự suy đoán schema/API.
- Đã xác định các rủi ro bảo mật dữ liệu và upload.

### Giai đoạn 2 — Backend và Database Foundation

**Công việc**
- Tạo cấu hình ứng dụng, kết nối DB, ORM và migration.
- Xây dựng xác thực, authorization và role policy.
- Xây dựng model/repository/service nền tảng.
- Tạo upload/storage abstraction và audit logging.
- Thiết lập health/readiness checks và xử lý lỗi chuẩn.

**Đầu ra**
- Backend khởi động được trong môi trường local.
- Migration chạy được trên database sạch.
- Test cho xác thực, phân quyền và persistence.

**Cổng hoàn thành**
- API health hoạt động; schema tái tạo được từ migration.
- Truy cập trái quyền bị từ chối ở server-side.

### Giai đoạn 3 — Citizen Portal

**Công việc**
- Google login/callback/session.
- Hồ sơ người dân.
- Form tạo phản ánh, validate nội dung.
- Upload ảnh, preview ngay khi chọn, xóa/thay ảnh.
- Chọn vị trí trên bản đồ và xác nhận.
- Trang lịch sử, chi tiết, kết quả AI và trạng thái.

**Đầu ra**
- Luồng người dân hoàn chỉnh trên dữ liệu test.
- Test quyền sở hữu tài nguyên và upload.

**Cổng hoàn thành**
- Người dân A không thể truy cập dữ liệu của người dân B.
- Ảnh preview hiển thị trước submit; file không hợp lệ bị từ chối.
- Dữ liệu được lưu và tra cứu đúng.

### Giai đoạn 4 — NLP Inference

**Công việc**
- Chuẩn hóa pipeline preprocess/inference.
- Tích hợp baseline Naive Bayes và SVM trước.
- Bổ sung CNN 1D và LSTM theo kế hoạch thí nghiệm.
- Chuẩn hóa output, confidence, model version và lỗi inference.
- Lưu prediction history và liên kết phản ánh.

**Đầu ra**
- Prediction service có test và contract ổn định.
- Kết quả dự đoán có thể truy vết model version.

**Cổng hoàn thành**
- Văn bản hợp lệ được phân loại vào đúng tập 11 nhãn.
- Không lưu confidence như xác suất tin cậy đã hiệu chỉnh nếu chưa calibration.
- Lỗi mô hình không làm mất phản ánh gốc.

### Giai đoạn 5 — Admin Portal và kiểm duyệt

**Công việc**
- Admin login và RBAC.
- Danh sách, lọc, chi tiết phản ánh.
- Xem AI result, confidence, ảnh và vị trí.
- Xác nhận/chỉnh sửa nhãn.
- Quản lý trạng thái theo workflow.
- Review history và audit.

**Đầu ra**
- Quy trình human-in-the-loop có thể sử dụng đầu-cuối.

**Cổng hoàn thành**
- Mỗi thay đổi nhãn lưu người thực hiện, thời điểm, nhãn trước/sau và lý do theo chính sách.
- Quyền chỉnh sửa được giới hạn theo vai trò.

### Giai đoạn 6 — Dashboard và bản đồ

**Công việc**
- KPI tổng quan.
- Thống kê theo 11 nhóm, trạng thái và khoảng thời gian.
- Bản đồ marker/cluster và bộ lọc.
- Kiểm tra quyền, hiệu năng truy vấn và dữ liệu tọa độ.

**Đầu ra**
- Dashboard có số liệu nhất quán với truy vấn nguồn.
- Bản đồ thể hiện đúng vị trí phản ánh.

**Cổng hoàn thành**
- Tổng số liệu đối chiếu được với dữ liệu kiểm thử.
- Bộ lọc thống nhất giữa chart, list và map theo yêu cầu.

### Giai đoạn 7 — AI/Data Management

**Công việc**
- CRUD Dataset và Dataset Samples.
- Import/validate dữ liệu.
- Quản lý label/version/split.
- Tạo Training Runs và lưu trạng thái.
- Lưu Training Metrics, artifact và model version.
- So sánh, đăng ký và kích hoạt/rollback model theo quyền.

**Đầu ra**
- Vòng đời dữ liệu và mô hình được ghi nhận có thể truy vết.

**Cổng hoàn thành**
- Một training run liên kết dataset version, cấu hình, code/model version và metrics.
- Không kích hoạt model chưa qua tiêu chí đánh giá/phê duyệt.

### Giai đoạn 8 — Kiểm thử tích hợp, bảo mật và nghiệm thu

**Công việc**
- Unit, API, integration, E2E và UAT.
- Kiểm thử quyền, upload, OAuth, dữ liệu biên và concurrency.
- Kiểm tra hiệu năng và tải theo mục tiêu được chốt.
- Kiểm tra backup/restore, logging, monitoring và lỗi vận hành.
- Khắc phục lỗi, hoàn thiện tài liệu.

**Đầu ra**
- Test report, UAT sign-off và release candidate.

**Cổng hoàn thành**
- Không còn lỗi Critical/High chưa có biện pháp xử lý được chấp nhận.
- Các tiêu chí nghiệm thu đã duyệt đều có bằng chứng.
- Có phương án rollback và backup phù hợp.

### Giai đoạn 9 — Triển khai và vận hành

**Công việc**
- Cấu hình môi trường staging/production.
- Thiết lập secret, domain, TLS, backup và monitoring.
- Deploy ứng dụng, migrate DB và kiểm tra smoke test.
- Hướng dẫn người dùng/quản trị.
- Theo dõi lỗi và chất lượng mô hình.

**Đầu ra**
- Release được nghiệm thu và tài liệu vận hành.

## 3. Phụ thuộc chính

- Citizen submission phụ thuộc Auth, Database, File Storage và Map integration.
- AI inference phụ thuộc nhãn, dataset, preprocessing và model artifact.
- Review phụ thuộc Report, Prediction và RBAC.
- Dashboard/Map phụ thuộc schema, trạng thái và quy tắc thống kê.
- AI Management phụ thuộc Dataset versioning, experiment metadata, metrics và model registry.
- Deployment phụ thuộc stack, secret management, migration và health checks.

## 4. Quy tắc ưu tiên

Ưu tiên theo thứ tự: bảo mật/dữ liệu nền tảng → luồng gửi phản ánh → inference baseline → kiểm duyệt → dashboard/map → quản lý huấn luyện nâng cao. Có thể điều chỉnh theo tiến độ thực tế nhưng không bỏ qua kiểm thử quyền và tính toàn vẹn dữ liệu.

## 5. Theo dõi tiến độ

Mỗi hạng mục backlog cần có: ID, mô tả, ưu tiên, phụ thuộc, người phụ trách, acceptance criteria, trạng thái, PR/commit và test evidence. Không đánh dấu Done chỉ vì code đã được viết.


## 6. Baseline đầu vào cho triển khai

- Danh sách 11 tên và thứ tự đã được chủ dự án cung cấp; [CLASSIFICATION_SPECIFICATION](../01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md) là nguồn chuẩn dùng chung.
- Baseline thiết kế dữ liệu gồm đúng 12 bảng trong [DATABASE_DESIGN](../03_DATABASE/DATABASE_DESIGN.md). Trước khi viết migration phải chốt Database Engine, kiểu dữ liệu cụ thể, status lifecycle và audit sink.
- Không đánh dấu Database Foundation VERIFIED chỉ vì tài liệu đã có ERD; chỉ VERIFIED sau khi SQLAlchemy models, migration, seed 11 danh mục và Docker tests chạy thành công.
