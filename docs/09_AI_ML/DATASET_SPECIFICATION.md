# DATASET SPECIFICATION — ĐẶC TẢ DATASET

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Draft |
| Ngôn ngữ dữ liệu chính | Tiếng Việt |
| Bài toán | Phân loại văn bản thành 11 nhóm |

## 1. Mục tiêu

Quy định nguồn, cấu trúc, nhãn, chất lượng, version và cách chia dữ liệu để huấn luyện/đánh giá model có thể tái lập và không rò rỉ dữ liệu.

## 2. Phạm vi dữ liệu

Dữ liệu supervised chính là nội dung văn bản phản ánh và nhãn category được xác nhận theo guideline. Ảnh và tọa độ thuộc hệ thống phản ánh nhưng không tự động là feature của classifier văn bản trong baseline.

## 3. Nguồn dữ liệu

Nguồn có thể gồm:
- Dataset được chủ dự án cung cấp.
- Phản ánh đã được cán bộ kiểm duyệt và được phép tái sử dụng.
- Dữ liệu tạo thủ công/annotated phục vụ nghiên cứu.
- Nguồn công khai chỉ khi license/điều khoản cho phép.

Mỗi sample cần provenance: nguồn, thời điểm thu thập, phương thức, quyền sử dụng, trạng thái ẩn danh và người gán nhãn/duyệt nếu có. Không thu thập dữ liệu riêng tư vượt mục đích.

## 4. Danh mục 11 lớp

ST-NLP có 11 nhóm phân loại. Tên, mã, mô tả, inclusion/exclusion criteria và ví dụ chuẩn phải lấy từ Classification Specification được chủ dự án duyệt.

Không tự phát minh tên lớp. Trước khi có danh mục chính thức:
- Dùng category_code ổn định do chủ dự án cung cấp.
- Không đưa label text tự đặt vào dataset production.
- Ghi phiên bản label schema.
- Mọi thay đổi mapping phải có kế hoạch migration/relabel.

## 5. Cấu trúc sample logic

Một sample tối thiểu nên có:
- sample_id ổn định.
- text gốc hoặc reference an toàn đến text.
- category_code hoặc trạng thái unlabeled/needs_review.
- dataset_id/version.
- source/provenance.
- labeling_status.
- created_at/updated_at.
- split (train/validation/test) nếu quản lý split ở sample.
- duplicate/fingerprint metadata nếu phù hợp.

Tên field vật lý phụ thuộc Data Dictionary đã duyệt.

## 6. Quy tắc gán nhãn

- Một sample phải gắn với một nhãn chính trong bài toán single-label, trừ khi SRS được đổi sang multi-label.
- Gán nhãn theo định nghĩa, không theo suy đoán về ý định người viết.
- Nếu thiếu thông tin/không thuộc 11 nhóm, cần trạng thái xử lý đã được định nghĩa; không ép nhãn.
- Trường hợp nhập nhằng cần adjudication.
- Lưu người gán nhãn, người duyệt và guideline version nếu quy trình hỗ trợ.
- Theo dõi label changes; không âm thầm ghi đè.

## 7. Chất lượng dữ liệu

Kiểm tra:
- Rỗng/null và text quá ngắn.
- Encoding/Unicode lỗi.
- Duplicate chính xác và duplicate gần đúng.
- Label không tồn tại hoặc không active.
- Mất cân bằng lớp.
- Text quá dài hoặc có nội dung không liên quan.
- PII/địa chỉ/số điện thoại cần xử lý theo policy.
- Nguồn và license không rõ.
- Train/test leakage.
- Label conflicts và sample chưa được kiểm duyệt.

## 8. Chia tập dữ liệu

- Tách train/validation/test trước các bước fit vectorizer/normalizer học tham số.
- Stratified split khi phù hợp với phân bố lớp.
- Cân nhắc group split theo nguồn/người gửi/thời gian để tránh nội dung gần giống rơi vào nhiều tập.
- Test set giữ độc lập, không dùng tune hyperparameters.
- Lưu seed, split ratio, split method và dataset version.
- Nếu có thời gian, tạo holdout theo thời gian để đo khả năng tổng quát hóa.

Tỷ lệ train/validation/test là TBD; cần dựa trên kích thước và phân bố dữ liệu.

## 9. Versioning

Dataset Version nên bất biến sau khi đóng băng. Mỗi version cần:
- ID/version label.
- số lượng sample tổng và theo lớp.
- label schema version.
- split config/seed.
- validation report.
- provenance summary.
- checksum/fingerprint nếu áp dụng.
- người tạo và thời điểm freeze.

Chỉnh sửa tạo version mới thay vì thay đổi âm thầm dữ liệu đã dùng trong training run.

## 10. Privacy và retention

- Ẩn danh hoặc loại bỏ thông tin định danh không cần cho bài toán.
- Giữ quyền truy cập giới hạn.
- Không export raw report sang nơi khác nếu chưa có phê duyệt.
- Có retention/deletion policy.
- Dữ liệu test mẫu không chứa PII.
- Có cách xử lý yêu cầu xóa dữ liệu nguồn và ảnh hưởng tới dataset/model cần được xác định.

## 11. Dataset acceptance criteria

Dataset chỉ được đánh dấu Ready khi:
- Có label schema version.
- Samples hợp lệ theo schema.
- Không còn label không xác định ngoài policy.
- Duplicate và leakage đã được kiểm tra.
- Có phân bố lớp và báo cáo chất lượng.
- Provenance/quyền sử dụng được xác nhận.
- Split đã được tạo và lưu.
- Các cảnh báo được chấp thuận hoặc xử lý.
