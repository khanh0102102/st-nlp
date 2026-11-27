# DATA DICTIONARY — TỪ ĐIỂN DỮ LIỆU

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Template + logical definitions |
| Nguồn chuẩn | Physical schema được duyệt trong SQLAlchemy models/migrations |

## 1. Mục đích

Data Dictionary giải thích ý nghĩa nghiệp vụ, kiểu dữ liệu, constraint, nullable, default, index và quyền truy cập của từng trường. Đây là tài liệu cần đồng bộ với model và migration; không được xem các gợi ý dưới đây là tên cột vật lý đã chốt.

## 2. Quy tắc đặt tên và kiểu dữ liệu

- Table: snake_case, số ít hoặc số nhiều phải chọn một quy ước thống nhất.
- Column: snake_case, tên thể hiện ý nghĩa; tránh viết tắt không rõ.
- Primary key: kiểu ID thống nhất trên toàn schema.
- Foreign key: tên theo entity đích, có constraint rõ.
- Timestamp: dùng timezone-aware timestamp, lưu UTC.
- Boolean: đặt tên thể hiện trạng thái, ví dụ is_active.
- Enum/status: ưu tiên code ổn định; không lưu chuỗi hiển thị tùy tiện.
- Money/decimal: dùng numeric/decimal nếu có.
- JSON: chỉ dùng cho metadata linh hoạt; không thay thế quan hệ cần truy vấn.
- Text: xác định giới hạn, encoding Unicode và quy tắc normalization.

## 3. Logical data dictionary

### User / Identity
- Định danh nội bộ: khóa chính ổn định.
- Provider: nguồn đăng nhập, baseline là Google cho Citizen.
- Provider subject: định danh duy nhất từ provider; không dùng email thay thế nếu có subject.
- Display name/email/avatar: chỉ lưu trường cần thiết.
- Created/updated/last_login: timestamp UTC.
- Status: account active/disabled theo policy.
- Không lưu Google access token nếu không có nhu cầu và quyết định bảo mật cụ thể.

### Role / Permission
- Role code: mã ổn định, unique.
- Permission code: action/resource rõ nghĩa.
- Mapping: unique theo cặp principal-role hoặc role-permission.
- Thay đổi quyền cần audit.

### Incident
- Owner reference: tài khoản tạo phản ánh.
- Description: nội dung văn bản gốc; cần policy độ dài và lưu trữ.
- Status: code từ state machine được duyệt.
- Created/submitted/updated timestamp: UTC.
- Location: tọa độ và/hoặc địa chỉ theo CRS đã chốt.
- Không lưu reviewed label đè lên original prediction.

### Attachment
- Incident reference.
- Storage key/reference.
- Original filename đã sanitize.
- Verified MIME type, file size, checksum.
- Upload timestamp và uploader.
- Không lưu secret hoặc đường dẫn filesystem nội bộ công khai.

### Category
- Category code: unique, ổn định.
- Display name: tên hiển thị.
- Description/guideline: định nghĩa và ranh giới nhãn.
- Active flag/status và version/effective date nếu cần.
- 11 category records phải được seed idempotent từ danh mục đã duyệt.

### Prediction
- Incident reference.
- Predicted category reference.
- Score/confidence và semantics rõ ràng.
- Model version và preprocessing version.
- Prediction status, created_at, duration nếu cần.
- Input fingerprint/version để truy vết mà không phải copy dữ liệu nhạy cảm tùy tiện.

### Review / Review History
- Incident và prediction reference.
- Reviewer reference.
- Previous category và selected/final category.
- Action: confirmed/corrected theo enum được duyệt.
- Note/reason nếu policy yêu cầu.
- Reviewed timestamp và concurrency/version.
- Lưu lịch sử append-only hoặc cơ chế bảo toàn lịch sử tương đương.

### Dataset / Dataset Version
- Name, description, owner/source.
- Version identifier và status.
- Created/frozen timestamp.
- Label schema version.
- Data provenance và license/permission note.
- Immutable sau khi freeze trừ khi tạo version mới.

### Dataset Sample
- Dataset version reference.
- Text content hoặc secure source reference.
- Label/category reference và labeling status.
- Split (train/validation/test) nếu split lưu ở sample.
- Source/provenance, reviewer, validation flags.
- Duplicate/fingerprint metadata; không lưu raw PII không cần thiết.

### Training Run
- Dataset version reference.
- Algorithm/model family.
- Hyperparameters/config snapshot.
- Preprocessing version, random seed, code/environment version.
- Status, started_at, finished_at.
- Artifact reference và failure reason đã làm sạch.

### Training Metric
- Training run reference.
- Metric name, value, split, class label nếu per-class.
- Step/epoch và timestamp nếu lưu history.
- Hệ quy chiếu metric và averaging method phải rõ.

### Model Version
- Model family, version label và artifact reference.
- Source training run/dataset version.
- Preprocessing/label mapping version.
- Metrics summary và checksum.
- Status/active flag theo deployment target.
- Created/approved/activated timestamp và actor.

## 4. Template mô tả trường vật lý

Mỗi trường trong schema thực tế phải có các cột mô tả:

| Thuộc tính | Ý nghĩa |
|---|---|
| Table / Column | Tên vật lý chính xác |
| Business name | Tên nghiệp vụ |
| Data type | Kiểu SQL/ORM và độ dài/precision |
| PK/FK | Khóa chính/khóa ngoại và bảng đích |
| Nullable | Có cho phép NULL không |
| Default | Giá trị mặc định |
| Unique/Check | Constraint |
| Index | Index và mục đích |
| Description | Định nghĩa, đơn vị, semantics |
| Example | Ví dụ giả lập, không dùng dữ liệu thật |
| Security | Phân loại và quyền truy cập |
| Retention | Thời hạn lưu/xóa nếu áp dụng |

## 5. Quy tắc chất lượng dữ liệu

- Không dùng NULL và chuỗi rỗng thay thế nhau nếu semantics khác.
- Không dùng 0 để đại diện dữ liệu chưa biết nếu 0 là giá trị hợp lệ.
- Tọa độ phải có CRS và miền hợp lệ.
- Score phải ghi rõ là probability, calibrated probability hay raw decision score.
- Status phải là tập giá trị có tài liệu và transition.
- Timestamp phải nhất quán timezone.
- Category code không đổi khi đổi tên hiển thị.

## 6. Đồng bộ tài liệu và schema

Mọi migration thay đổi bảng/cột/constraint phải cập nhật Data Dictionary và ERD trong cùng PR. CI nên kiểm tra migration và test schema trên DB rỗng. Khi đưa schema 12 bảng hiện có vào repository, thay phần logical definitions bằng bảng/cột thật sau khi đối chiếu.
