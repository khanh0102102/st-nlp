# SYSTEM DESIGN — THIẾT KẾ HỆ THỐNG

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Proposed |
| Tài liệu cha | SYSTEM_ARCHITECTURE.md |

## 1. Thiết kế phân lớp Backend

Các lớp đề xuất:

1. **API/Presentation:** route/controller, parse request, response schema, status code.
2. **Application/Use Case:** điều phối use case, transaction boundary và permission policy.
3. **Domain:** entity/rule nghiệp vụ, transition hợp lệ, validation không phụ thuộc framework.
4. **Infrastructure:** SQLAlchemy repositories, storage adapter, OAuth provider, map provider, model loader, queue và logging.
5. **ML:** preprocessing, feature generation, inference, training/evaluation và model metadata.

Không bắt buộc tạo quá nhiều abstraction cho một CRUD đơn giản. Abstraction chỉ nên tồn tại khi có ranh giới cần kiểm soát hoặc thay thế.

## 2. Thiết kế Frontend

- Portal người dân và portal quản trị phải có route root, navigation, layout và guard riêng.
- Auth state không thay thế authorization tại Backend.
- Mỗi màn hình phải có loading, empty, error, success và access-denied state.
- Form submit phải disable nút hợp lý và tránh gửi trùng.
- Preview ảnh thực hiện phía client trước submit; file vẫn phải được kiểm tra phía server.
- API client tập trung xử lý auth, timeout, lỗi chuẩn và request correlation nếu có.

## 3. Luồng tạo phản ánh và inference

**Luồng đồng bộ tối thiểu**
1. Client gửi nội dung, tọa độ và metadata file.
2. Backend xác thực, validate và lưu phản ánh.
3. Backend xác nhận tiếp nhận cho Client.
4. Hệ thống thực hiện inference theo một trong hai chiến lược:
   - synchronous nếu model nhỏ và SLA đáp ứng được;
   - asynchronous worker nếu inference chậm hoặc cần retry/queue.
5. Lưu prediction độc lập với phản ánh.
6. Client lấy trạng thái/prediction qua API.

**Nguyên tắc bắt buộc:** việc inference thất bại không rollback phản ánh đã được lưu thành công. Prediction cần status và error category đã làm sạch.

## 4. Luồng kiểm duyệt

1. Backend tải phản ánh, prediction hiện hành và lịch sử.
2. Moderator gửi quyết định review với nhãn mới/xác nhận và ghi chú.
3. Backend kiểm tra permission, category active và concurrency/version.
4. Trong một transaction, tạo review record, cập nhật current reviewed state nếu có, ghi audit.
5. Giữ nguyên prediction gốc để phân tích chất lượng model.
6. Trả review result và version mới cho client.

## 5. Luồng Dataset/Training

1. Dataset có định danh và version.
2. Sample được validate trước khi đóng băng version.
3. Training Run tham chiếu dataset version, preprocessing version, algorithm, hyperparameters, random seed và môi trường khi có.
4. Worker cập nhật trạng thái queued/running/succeeded/failed.
5. Metrics ghi cả metric tổng thể và per-class.
6. Artifact lưu ở storage; DB lưu metadata và reference.
7. Model Version liên kết run nguồn, artifact, label mapping và preprocessing.
8. Chỉ version được phép mới có thể active; activation/rollback ghi audit.

## 6. Transaction và nhất quán

- Tạo report và metadata liên quan cần atomic trong Database.
- Upload file và ghi DB là hai hệ thống khác nhau; thiết kế quy trình cleanup/orphan-file nếu bước sau thất bại.
- Tạo review phải atomic với cập nhật trạng thái hiện hành và audit ở mức DB.
- Không giữ transaction DB mở trong khi training/inference dài.
- Dùng idempotency key cho thao tác có thể retry khi tạo report/upload nếu cần.
- Dùng optimistic concurrency/version column cho thao tác review và đổi model active nếu có nhiều người thao tác.

## 7. Pagination, filtering và sorting

- Endpoint danh sách phải phân trang.
- Server whitelist các trường sort/filter; không ghép raw SQL từ query client.
- Thống nhất timezone lưu UTC và chuyển đổi tại UI theo timezone cấu hình.
- Các bộ lọc dashboard/list/map cần dùng chung định nghĩa để số liệu nhất quán.
- Với dữ liệu lớn, ưu tiên cursor pagination nếu offset trở nên chậm; chiến lược cụ thể TBD.

## 8. Error handling

Response lỗi phải có mã ổn định, thông điệp an toàn và correlation/request ID. Không trả stack trace hoặc SQL detail cho client. Phân biệt:
- Validation error.
- Authentication/authorization error.
- Resource not found.
- Conflict/concurrency.
- Rate limit.
- External provider error.
- Internal error.
- AI inference/training error.

## 9. Logging và observability

- Log ứng dụng dạng cấu trúc.
- Có request/correlation ID xuyên suốt API và worker nếu khả thi.
- Không ghi access token, secret, ảnh, nội dung phản ánh đầy đủ hoặc thông tin nhạy cảm không cần thiết.
- Metrics tách API latency/error, inference latency/error, training duration và queue status.
- Audit business action tách khỏi application log.

## 10. Versioning

- API sử dụng prefix version, đề xuất /api/v1.
- Dataset, preprocessing và model version phải được lưu.
- Không thay đổi schema/API phá vỡ tương thích mà không migration/versioning.
- Dữ liệu kết quả cũ cần biết model version tạo ra nó.

## 11. Các quyết định phải chốt trước triển khai

- Sync hay async inference cho baseline.
- Cơ chế upload trực tiếp hay upload qua Backend.
- Mô hình session/token và refresh.
- Database isolation/concurrency strategy.
- State machine phản ánh.
- Cách phân trang, timezone và map aggregation.


## 12. Data contract theo baseline 12 bảng

- Report: reports giữ raw_content, user_id, vị trí, status và final_category_id. final_category_id chỉ được ghi sau khi cán bộ xác nhận; ban đầu NULL.
- Attachment: report_attachments giữ metadata và storage_key; file binary nằm ngoài Database.
- Preprocessing: mỗi lần xử lý sinh preprocessing_runs gắn report_id và preprocessing_version. Nội dung gốc không bị biến đổi.
- Prediction: predictions gắn report_id, preprocessing_run_id, model_version_id và predicted_category_id. Prediction thất bại có inference_status/error_code và không bị ép nhãn OTHER.
- Review: prediction_reviews ghi lịch sử append-only. Backend kiểm tra prediction/report nhất quán, rồi trong transaction thêm review và cập nhật reports.final_category_id.
- Dataset: mỗi row datasets đại diện một version; parent_dataset_id thể hiện lineage. Version FROZEN bất biến.
- Dataset Sample: dataset_samples liên kết dataset_id, category_id, split, labeling_status và provenance từ report/review nếu được phép.
- Training: training_runs gắn một dataset version cụ thể; training_metrics lưu metric_name/value/split/averaging/category_id. model_versions giữ artifact và training_run_id nguồn.

## 13. Catalog phân loại dùng chung

Catalog cố định 11 nhóm và code nằm trong [CLASSIFICATION_SPECIFICATION](../01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md). Không hard-code nhiều bản danh sách khác nhau; seed, API, Dashboard và ML label encoder phải đồng bộ. Bài toán baseline single-label; OTHER khác với insufficient information hoặc inference failure.

## 14. Audit khi giữ giới hạn 12 bảng

Không tạo bảng audit_logs trong schema baseline. Các event thay đổi quyền, report status, review, dataset freeze và model activation/rollback phải phát qua audit sink append-only bên ngoài DB. Review history vẫn nằm trong prediction_reviews. Cơ chế bền vững, retention và chống sửa/xóa của sink cần chọn trước production.
