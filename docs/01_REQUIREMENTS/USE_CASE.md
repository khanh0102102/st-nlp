# USE CASE SPECIFICATION

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Draft |
| Phạm vi | Citizen Portal, Admin Portal, AI & Data Management |

## 1. Tác nhân

- **Citizen:** người dân đã xác thực Google.
- **Moderator:** cán bộ tiếp nhận/kiểm duyệt.
- **Administrator:** người quản trị tài khoản, vai trò và cấu hình.
- **AI/Data Manager:** người quản lý dữ liệu và mô hình.
- **Google Identity:** hệ thống nhận dạng bên ngoài.
- **Map Provider:** dịch vụ bản đồ/geocoding được lựa chọn.
- **File Storage:** nơi lưu file ảnh/artifact.

Một tài khoản có thể có nhiều role; việc gán quyền phải được quản lý rõ ràng.

## 2. Sơ đồ ca sử dụng tổng quan

```mermaid
graph LR
```
      Citizen[Citizen] --> UC1((Đăng nhập Google))
      Citizen --> UC2((Tạo phản ánh))
      Citizen --> UC3((Xem lịch sử và chi tiết))
      Citizen --> UC4((Xem kết quả AI và trạng thái))
      Staff[Moderator] --> UC5((Quản lý phản ánh))
      Staff --> UC6((Kiểm duyệt nhãn))
      Staff --> UC7((Xem Dashboard và bản đồ))
      Admin[Administrator] --> UC8((Quản lý người dùng và quyền))
      Data[AI/Data Manager] --> UC9((Quản lý Dataset))
      Data --> UC10((Quản lý Training Run))
      Data --> UC11((Quản lý Model Version))

## 3. Danh mục use case

| ID | Tên | Tác nhân chính | Ưu tiên |
|---|---|---|---|
| UC-01 | Đăng nhập người dân bằng Google | Citizen, Google Identity | Must |
| UC-02 | Đăng xuất | Citizen/Staff | Must |
| UC-03 | Tạo phản ánh | Citizen | Must |
| UC-04 | Chọn vị trí phản ánh | Citizen, Map Provider | Must |
| UC-05 | Đính kèm và xem trước ảnh | Citizen, File Storage | Must |
| UC-06 | Xem lịch sử phản ánh | Citizen | Must |
| UC-07 | Xem chi tiết/kết quả AI/trạng thái | Citizen | Must |
| UC-08 | Đăng nhập cổng quản trị | Moderator/Admin | Must |
| UC-09 | Tìm kiếm và xem danh sách phản ánh | Moderator | Must |
| UC-10 | Xem chi tiết và bản đồ phản ánh | Moderator | Must |
| UC-11 | Kiểm duyệt kết quả AI | Moderator | Must |
| UC-12 | Xem lịch sử kiểm duyệt | Moderator/Admin | Must |
| UC-13 | Xem Dashboard | Moderator/Admin | Must |
| UC-14 | Quản lý người dùng và quyền | Administrator | Should |
| UC-15 | Quản lý Dataset | AI/Data Manager | Must |
| UC-16 | Quản lý Dataset Samples | AI/Data Manager | Must |
| UC-17 | Kiểm tra/validate Dataset | AI/Data Manager | Must |
| UC-18 | Tạo và theo dõi Training Run | AI/Data Manager | Must |
| UC-19 | Xem và so sánh Metrics | AI/Data Manager | Should |
| UC-20 | Quản lý/đăng ký Model Version | AI/Data Manager | Should |
| UC-21 | Kích hoạt hoặc rollback Model Version | Người được cấp quyền triển khai model | Should |

## 4. Đặc tả các use case trọng yếu

### UC-01 — Đăng nhập người dân bằng Google

**Mục tiêu:** xác thực người dân thông qua Google và tạo phiên ứng dụng an toàn.

**Tiền điều kiện:** Citizen Portal khả dụng; OAuth client và callback đã cấu hình.

**Luồng chính**
1. Người dân chọn Đăng nhập bằng Google.
2. Frontend điều hướng đến luồng OAuth do Backend khởi tạo.
3. Google xác thực người dùng và trả callback.
4. Backend xác minh state/nonce và thông tin token theo chuẩn.
5. Backend tìm hoặc tạo tài khoản dựa trên định danh provider ổn định.
6. Backend tạo session/token theo cơ chế được chọn.
7. Người dân được chuyển về Citizen Portal.

**Ngoại lệ:** người dùng từ chối; state không hợp lệ; callback hết hạn; email/subject không hợp lệ; provider lỗi. Không tạo phiên trong các trường hợp không xác minh được.

**Hậu điều kiện:** phiên hợp lệ được tạo; audit tối thiểu được ghi; không lưu token provider không cần thiết.

### UC-03 — Tạo phản ánh

**Tiền điều kiện:** người dân đã đăng nhập; danh mục đang hoạt động; hệ thống tiếp nhận được yêu cầu.

**Luồng chính**
1. Người dân mở form tạo phản ánh.
2. Nhập nội dung.
3. Chọn ảnh; UI hiển thị preview, cho phép bỏ/thay ảnh.
4. Chọn vị trí trên bản đồ hoặc nhập vị trí theo phương thức được hỗ trợ.
5. Kiểm tra và gửi.
6. Backend xác thực, validate nội dung/file/tọa độ.
7. Backend lưu phản ánh và file tham chiếu trong transaction/quy trình nhất quán.
8. Hệ thống ghi nhận trạng thái tiếp nhận và đưa yêu cầu sang pipeline AI.
9. UI hiển thị mã phản ánh/kết quả tiếp nhận.

**Ngoại lệ:** thiếu nội dung; file không hợp lệ; vượt giới hạn; vị trí không hợp lệ; lỗi lưu file/DB; gửi lặp. Có cơ chế tránh tạo phản ánh trùng do retry khi phù hợp.

**Hậu điều kiện:** phản ánh được lưu hoặc thông báo lỗi rõ ràng; không tạo bản ghi nửa vời không thể khôi phục.

### UC-05 — Đính kèm và xem trước ảnh

**Tiền điều kiện:** đang tạo/chỉnh sửa phản ánh và người dùng có quyền.

**Luồng chính**
1. Người dùng chọn ảnh.
2. Frontend kiểm tra sơ bộ định dạng/kích thước.
3. Frontend tạo preview cục bộ.
4. Người dùng có thể xóa hoặc thay ảnh.
5. Khi submit, Backend kiểm tra lại và lưu file.
6. Hệ thống liên kết file với phản ánh.

**Ngoại lệ:** file không hỗ trợ, hỏng, quá dung lượng hoặc upload thất bại. Preview cục bộ phải được giải phóng khi bỏ file/rời màn hình.

### UC-07 — Xem chi tiết, kết quả AI và trạng thái

**Tiền điều kiện:** người dân đã đăng nhập.

**Luồng chính**
1. Người dân mở lịch sử.
2. Chọn một phản ánh.
3. Backend kiểm tra chủ sở hữu.
4. UI hiển thị nội dung, ảnh, vị trí, kết quả AI được công khai, trạng thái và mốc lịch sử được phép.

**Ngoại lệ:** không tồn tại hoặc không thuộc quyền → trả phản hồi không tiết lộ dữ liệu của người khác.

### UC-09/UC-10 — Cán bộ tìm kiếm và xem phản ánh

**Tiền điều kiện:** cán bộ đã đăng nhập và có quyền.

**Luồng chính**
1. Cán bộ mở danh sách.
2. Lọc theo danh mục, trạng thái, thời gian hoặc tiêu chí được cấp.
3. Chọn phản ánh.
4. Hệ thống hiển thị nội dung, file, vị trí, prediction, confidence và lịch sử.
5. Cán bộ xem marker trên bản đồ hoặc mở chi tiết.

### UC-11 — Kiểm duyệt kết quả AI

**Tiền điều kiện:** cán bộ có permission review; phản ánh có thể được kiểm duyệt.

**Luồng chính**
1. Cán bộ mở prediction.
2. Xem nội dung và nhãn AI đề xuất.
3. Chọn xác nhận nhãn hoặc chọn nhãn khác trong danh mục hợp lệ.
4. Nhập ghi chú/lý do nếu policy yêu cầu.
5. Backend kiểm tra quyền, phiên bản dữ liệu hiện tại và danh mục.
6. Hệ thống lưu review mới và audit, giữ nguyên prediction gốc.
7. UI hiển thị kết quả kiểm duyệt mới.

**Ngoại lệ:** tài nguyên đã bị thay đổi bởi người khác; nhãn không còn hoạt động; thiếu quyền; request trùng. Dùng optimistic locking/idempotency nếu cần.

### UC-13 — Xem Dashboard

**Tiền điều kiện:** cán bộ có quyền dashboard.

**Luồng chính**
1. Người dùng mở Dashboard.
2. Chọn bộ lọc thời gian/danh mục/trạng thái.
3. Backend trả số liệu theo quyền.
4. UI hiển thị tổng quan và biểu đồ theo 11 nhóm.
5. Người dùng mở danh sách hoặc bản đồ tương ứng.

**Ngoại lệ:** chưa có dữ liệu, filter không hợp lệ hoặc query lỗi; phải có trạng thái empty/error phù hợp.

### UC-15/UC-16/UC-17 — Quản lý và validate Dataset

**Tiền điều kiện:** AI/Data Manager có quyền.

**Luồng chính**
1. Tạo/chọn Dataset.
2. Tạo version hoặc nhập samples.
3. Gán nhãn từ danh mục chính thức.
4. Chạy validation về schema, nhãn, rỗng, trùng, phân bố.
5. Xem báo cáo lỗi/cảnh báo.
6. Sửa dữ liệu hoặc loại sample.
7. Đánh dấu phiên bản sẵn sàng khi đạt tiêu chí.

### UC-18/UC-19 — Training Run và Metrics

**Tiền điều kiện:** Dataset version đã validate; model config có sẵn.

**Luồng chính**
1. Người dùng chọn dataset version, thuật toán và cấu hình.
2. Tạo training run.
3. Hệ thống lưu trạng thái và metadata.
4. Worker/process thực hiện huấn luyện.
5. Metrics và artifact được ghi nhận.
6. Người dùng xem kết quả, so sánh với run khác.

**Ngoại lệ:** thiếu dữ liệu, lỗi worker, timeout, thiếu tài nguyên. Run phải lưu trạng thái failed và thông tin lỗi đã được làm sạch.

### UC-20/UC-21 — Model Version

**Tiền điều kiện:** artifact đã được đánh giá và người dùng có quyền quản lý model.

**Luồng chính**
1. Đăng ký model version gắn với training run.
2. Kiểm tra metrics, dataset và artifact.
3. Phê duyệt/kích hoạt theo policy.
4. Prediction service sử dụng phiên bản đang active.
5. Khi có sự cố, người có quyền rollback về phiên bản trước.
6. Lưu audit và thời điểm chuyển đổi.

## 5. Quy tắc chung

- Mỗi use case bảo vệ dữ liệu phải kiểm tra quyền ở Backend.
- Mọi thay đổi nhãn/trạng thái/model active phải có audit.
- Kết quả dự đoán và kết quả kiểm duyệt là hai khái niệm khác nhau.
- Danh mục nhãn là nguồn dữ liệu chuẩn duy nhất.
- Trạng thái và transition chưa chốt phải được hoàn thiện trước khi code workflow.


## 6. Quy tắc phân loại và lưu dữ liệu

Use case tạo phản ánh không yêu cầu Citizen chọn category. Hệ thống dùng nội dung text để đề xuất một nhãn trong 11 nhóm tại [CLASSIFICATION_SPECIFICATION](CLASSIFICATION_SPECIFICATION.md). Citizen cung cấp text/ảnh/vị trí; AI thực hiện phân loại.

Khi kiểm duyệt, Moderator chọn xác nhận nhãn dự đoán hoặc chọn một category khác trong catalog cố định. Mỗi thao tác tạo một prediction_reviews record mới; prediction ban đầu không bị ghi đè. reports.final_category_id là nhãn nghiệp vụ hiện hành và được cập nhật cùng transaction với review.

OTHER chỉ dùng cho phản ánh hợp lệ ngoài 10 nhóm; nội dung thiếu thông tin hoặc lỗi kỹ thuật cần trạng thái riêng. Dataset Samples phải lưu category FK hoặc labeling_status phù hợp và provenance của nguồn dữ liệu.

Database baseline là 12 bảng theo DATABASE_DESIGN.md. Một hàng datasets biểu diễn một Dataset version; version FROZEN không sửa đổi.
