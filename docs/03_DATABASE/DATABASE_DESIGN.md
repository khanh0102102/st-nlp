# DATABASE DESIGN — THIẾT KẾ CƠ SỞ DỮ LIỆU

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Conceptual baseline — chưa phải schema vật lý đã duyệt |
| ORM định hướng | SQLAlchemy |
| Database engine | TBD |

## 1. Mục tiêu

Thiết kế dữ liệu phải hỗ trợ ba phân hệ, đảm bảo toàn vẹn, truy vết, bảo mật theo quyền và khả năng mở rộng. Cấu trúc cụ thể cần thống nhất với SQLAlchemy models và migration thực tế.

## 2. Lưu ý về trạng thái schema

Trong các trao đổi triển khai trước, thiết kế làm việc được nhắc đến với mục tiêu 12 bảng. Tuy nhiên repository này ban đầu trống, chưa có migration/model để đối chiếu. Vì vậy tài liệu này không tự đặt tên hoặc gán cột cho 12 bảng đó. Khi đưa schema hiện có vào repository, phải rà soát và đồng bộ DATABASE_DESIGN, ERD và DATA_DICTIONARY theo đúng model/migration đã được duyệt; không tự tạo thêm bảng chỉ vì sơ đồ khái niệm.

## 3. Miền dữ liệu

- Identity: tài khoản và role/permission mapping.
- Incident: phản ánh và trạng thái nghiệp vụ.
- Attachment: metadata file và storage reference.
- Location: tọa độ/địa chỉ hoặc dữ liệu địa lý được hỗ trợ.
- Classification: 11 danh mục chuẩn.
- Prediction: kết quả AI, score, model/pipeline version.
- Review: kết quả cán bộ xác nhận/điều chỉnh và lịch sử.
- Dataset: metadata, version và nguồn.
- Dataset Sample: nội dung/mã tham chiếu, nhãn, trạng thái validate.
- Training Run: cấu hình, trạng thái, thời điểm và artifact.
- Training Metrics: metric tổng thể/per-class/per-split.
- Model Version: artifact, config, dataset source và trạng thái active/retired.

Các miền trên là logical concepts, không phải khẳng định mỗi miền tương ứng một bảng vật lý.

## 4. Nguyên tắc thiết kế

1. Dùng khóa chính ổn định, không dùng tên hiển thị làm khóa.
2. Khóa ngoại phải được khai báo để bảo vệ quan hệ.
3. Có unique/check constraints cho các quy tắc dữ liệu quan trọng.
4. Dùng timestamp rõ nghĩa; lưu UTC và chuyển timezone tại tầng trình bày.
5. Dùng numeric/decimal cho score nếu cần độ chính xác; không dùng float tùy tiện cho dữ liệu nghiệp vụ.
6. Không lưu file binary lớn trong bảng nếu object storage phù hợp hơn.
7. Lưu prediction riêng với reviewed label.
8. Model version và dataset version phải bất biến sau khi được đóng băng.
9. Audit/history không bị ghi đè khi thay đổi nghiệp vụ.
10. Dùng transaction cho thay đổi liên quan nhiều bản ghi.
11. Chỉ soft-delete khi có yêu cầu khôi phục/audit; không dùng soft-delete thay thế policy retention.
12. Migration phải có upgrade/downgrade hoặc giải thích rõ nếu thao tác không thể đảo ngược.

## 5. Quan hệ logic

- Một Citizen có thể tạo nhiều Incident.
- Một Incident có thể có nhiều Attachment.
- Incident có vị trí theo mô hình vị trí được chốt.
- Một Incident có thể có nhiều Prediction theo thời gian/model version.
- Prediction tham chiếu Category và Model Version.
- Incident/Prediction có thể có các Review; review history không bị ghi đè.
- Dataset có nhiều Dataset Samples theo version.
- Training Run sử dụng một Dataset Version và cấu hình preprocessing/model.
- Training Run có nhiều Training Metrics.
- Model Version tham chiếu Training Run/artifact nguồn.
- Role và permission được liên kết với account theo mô hình RBAC.

## 6. Ràng buộc dữ liệu cần thiết

- Email/Google subject mapping phải tuân theo tính duy nhất phù hợp.
- Mã category phải unique và ổn định.
- Tọa độ phải nằm trong miền hợp lệ; hệ tọa độ phải xác định.
- Sample label phải thuộc danh mục hợp lệ hoặc trạng thái unlabeled được cho phép.
- Prediction score phải nằm trong miền hợp lệ theo semantics được định nghĩa.
- Training metric phải có tên, giá trị, split và class context khi áp dụng.
- Chỉ có một model version active cho một deployment target tại một thời điểm, nếu policy yêu cầu single-active.
- Mọi review cần actor và timestamp.

## 7. Indexing

Các index dự kiến xem xét:
- Incident: created_at, status, category/reviewed category, owner_id.
- Attachment: incident_id, storage_key unique nếu phù hợp.
- Prediction: incident_id, model_version_id, created_at.
- Review: incident_id, reviewer_id, reviewed_at.
- Dataset/Sample: dataset_id, version_id, label, validation_status.
- Training Run: dataset_version_id, status, created_at.
- Metrics: training_run_id, metric_name, split.
- Account: provider_subject unique; normalized email index nếu policy cho phép.

Chỉ tạo index sau khi đo query thực tế; tránh index trùng hoặc quá nhiều.

## 8. Vị trí địa lý

Cần chốt cách lưu:
- Latitude/longitude dạng numeric với CRS xác định; hoặc
- Geometry/geography type nếu database/provider hỗ trợ.

Không trộn hệ tọa độ. Tài liệu cần ghi rõ SRID, đơn vị, precision và cách hiển thị. Nếu có reverse geocoding, địa chỉ trả về chỉ là metadata gợi ý; tọa độ gốc do người dân xác nhận vẫn phải được giữ.

## 9. Attachment và storage

Bảng metadata (nếu có) nên lưu storage key, original filename đã sanitize, MIME đã xác minh, size, checksum, uploaded_at và owner/report reference. Không lưu URL public vĩnh viễn nếu file private. Storage cleanup phải có cơ chế xử lý bản ghi mồ côi.

## 10. Migration và seed

- Migration có tên mô tả và chạy tuần tự.
- Seed danh mục 11 nhóm phải idempotent, giữ category code ổn định.
- Không đưa dữ liệu người dân thật vào seed.
- Test migration trên DB rỗng và DB phiên bản trước.
- Backup trước migration có rủi ro.
- Không sửa migration đã chạy ở môi trường chia sẻ; tạo migration mới.

## 11. Transaction boundary

- Create Incident: record + metadata file reference + initial status.
- Create Review: review + current reviewed state + audit.
- Activate Model: update active reference + audit trong transaction.
- Dataset freeze: kiểm tra validation + tạo immutable version.
- Training status/metrics: cập nhật theo run ID, không giữ transaction dài trong quá trình huấn luyện.

## 12. TBD trước khi chốt physical schema

- Tên và số lượng bảng chính thức.
- Database engine/version và extension địa lý.
- Quy ước UUID/integer ID.
- Tên cột, kiểu dữ liệu, nullable/default.
- Trạng thái và lifecycle.
- Delete/retention policy.
- Cấu trúc dataset version/sample split.
- Artifact storage và transaction/outbox strategy.
