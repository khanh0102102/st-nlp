# TEST CASES — DANH SÁCH CA KIỂM THỬ BAN ĐẦU

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Initial test inventory |
| Quy ước | Expected result là yêu cầu; kết quả thực tế được ghi khi chạy |

## 1. Authentication và Authorization

| ID | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-AUTH-001 | Người dân đăng nhập Google hợp lệ | Tạo phiên và vào Citizen Portal |
| TC-AUTH-002 | Người dùng từ chối OAuth | Không tạo phiên; hiển thị thông báo |
| TC-AUTH-003 | OAuth state/nonce không hợp lệ | Callback bị từ chối |
| TC-AUTH-004 | Token hết hạn/chữ ký sai | Backend từ chối xác thực |
| TC-AUTH-005 | Citizen truy cập Admin API | 403 hoặc phản hồi an toàn tương đương |
| TC-AUTH-006 | Citizen đọc report của người khác | Không tiết lộ tài nguyên |
| TC-AUTH-007 | Staff thiếu permission review | Không thể sửa nhãn |
| TC-AUTH-008 | Đăng xuất | Phiên bị vô hiệu hóa theo cơ chế đã chọn |

## 2. Citizen Report

| ID | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-INC-001 | Tạo report với nội dung hợp lệ | Lưu report và trả mã định danh |
| TC-INC-002 | Gửi nội dung rỗng | Validation error |
| TC-INC-003 | Nội dung vượt giới hạn | Validation error rõ trường |
| TC-INC-004 | Chọn ảnh hợp lệ | Preview xuất hiện ngay |
| TC-INC-005 | Bỏ ảnh sau preview | Ảnh không được upload/đính kèm |
| TC-INC-006 | Thay ảnh đã chọn | Preview mới hiển thị đúng |
| TC-INC-007 | File sai MIME/extension | Server từ chối |
| TC-INC-008 | File vượt giới hạn | Server trả lỗi kích thước |
| TC-INC-009 | Upload thất bại sau khi lưu metadata | Không để trạng thái mồ côi không xử lý |
| TC-INC-010 | Tọa độ ngoài miền | Validation error |
| TC-INC-011 | Người dùng nhấn submit nhiều lần | Không tạo report duplicate ngoài policy |
| TC-INC-012 | Xem lịch sử | Chỉ report thuộc user hiện tại |

## 3. NLP và Prediction

| ID | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-AI-001 | Văn bản tiếng Việt hợp lệ | Pipeline trả output có label thuộc 11 nhóm |
| TC-AI-002 | Văn bản rỗng/không hợp lệ | Không gọi model hoặc trả trạng thái phù hợp |
| TC-AI-003 | Unicode tiếng Việt có dấu | Không lỗi encoding |
| TC-AI-004 | Nội dung nhiều khoảng trắng/ký tự lạ | Preprocess xử lý theo policy |
| TC-AI-005 | Model không load được | Report vẫn được lưu; prediction báo failed |
| TC-AI-006 | Inference timeout | Có trạng thái lỗi và retry policy |
| TC-AI-007 | Prediction thành công | Lưu label, score, model và pipeline version |
| TC-AI-008 | Score không đúng miền/NaN | Output bị validate/từ chối |
| TC-AI-009 | Dùng model version cũ cho prediction lịch sử | Có thể truy vết version đã dùng |

## 4. Admin và Review

| ID | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-ADM-001 | Moderator mở danh sách report | Chỉ thấy dữ liệu trong scope quyền |
| TC-ADM-002 | Filter theo status/category/time | Kết quả đúng filter |
| TC-REV-001 | Xác nhận nhãn AI | Lưu review action và audit |
| TC-REV-002 | Chọn nhãn khác | Lưu nhãn reviewed; giữ prediction gốc |
| TC-REV-003 | Chọn category không active | Backend từ chối |
| TC-REV-004 | Review thiếu permission | 403 |
| TC-REV-005 | Hai cán bộ sửa cùng lúc | Conflict được phát hiện, không ghi đè âm thầm |
| TC-REV-006 | Mở review history | Hiển thị actor/time/previous/new label theo quyền |
| TC-REV-007 | Cập nhật status không hợp lệ | Backend từ chối transition |

## 5. Dashboard và Map

| ID | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-DASH-001 | Dashboard không có dữ liệu | Empty state, số liệu bằng 0 hoặc biểu diễn rõ |
| TC-DASH-002 | Thống kê 11 category | Tổng và phân bố khớp dữ liệu nguồn theo định nghĩa |
| TC-DASH-003 | Thay đổi date filter | Chart/list/map đồng bộ filter |
| TC-MAP-001 | Report có tọa độ hợp lệ | Marker xuất hiện đúng vị trí |
| TC-MAP-002 | Report không có tọa độ | Không tạo marker giả |
| TC-MAP-003 | Người không có quyền xem chi tiết marker | Không lộ PII |

## 6. Dataset và Training

| ID | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-DATA-001 | Tạo Dataset | Dataset được lưu |
| TC-DATA-002 | Import sample có label hợp lệ | Sample được ghi nhận |
| TC-DATA-003 | Sample có label không tồn tại | Validation fail |
| TC-DATA-004 | Sample rỗng/duplicate | Được cảnh báo hoặc loại theo policy |
| TC-DATA-005 | Freeze dataset version | Version không bị sửa âm thầm |
| TC-DATA-006 | Sample trùng giữa train/test | Validation cảnh báo leakage |
| TC-TRAIN-001 | Tạo training run với dataset ready | Run được tạo và có trạng thái |
| TC-TRAIN-002 | Huấn luyện thành công | Metrics và artifact reference được lưu |
| TC-TRAIN-003 | Worker thất bại | Run chuyển failed, có error metadata |
| TC-TRAIN-004 | Lấy metrics | Trả metric tổng và per-class theo schema |
| TC-MODEL-001 | Đăng ký model version | Liên kết training run/artifact |
| TC-MODEL-002 | Kích hoạt model chưa được duyệt | Bị từ chối |
| TC-MODEL-003 | Rollback về version trước | Active model đổi và audit được ghi |

## 7. Non-functional và Security

| ID | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-SEC-001 | Thử SQL injection qua filter | Không thực thi SQL ngoài ý muốn |
| TC-SEC-002 | Thử XSS qua report text | Nội dung được escape/sanitize phù hợp |
| TC-SEC-003 | Upload path traversal | File bị từ chối |
| TC-SEC-004 | Kiểm tra log sau auth/upload | Không có secret/token |
| TC-SEC-005 | Truy cập file không có quyền | Bị từ chối |
| TC-PERF-001 | Đo API phổ biến dưới tải mục tiêu | Đạt ngưỡng NFR được duyệt |
| TC-REL-001 | DB hoặc inference tạm thời lỗi | Lỗi được xử lý, không mất dữ liệu đã commit |
| TC-DEP-001 | Cài mới từ hướng dẫn | Tạo được môi trường đúng theo guide |

## 8. Cột ghi kết quả khi chạy

Khi thực thi, bổ sung: Actual Result, Pass/Fail/Blocked, Build/Commit, Tester, Executed At, Evidence Link, Defect ID. Không thay Expected Result để hợp thức hóa lỗi thực tế.


## 9. Classification Catalog — 11 danh mục

| ID | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-CAT-001 | Seed catalog trên DB rỗng | Có chính xác 11 bản ghi |
| TC-CAT-002 | Chạy seed lần thứ hai | Không sinh duplicate, dữ liệu không đổi |
| TC-CAT-003 | Đọc catalog từ API | Trả đúng 11 mã/tên/thứ tự theo Classification Specification |
| TC-CAT-004 | Hiển thị Dashboard không có dữ liệu | Vẫn hiển thị đủ 11 nhóm với count 0 |
| TC-CAT-005 | Gửi review với category_code không tồn tại | Backend từ chối validation |
| TC-CAT-006 | Đổi category_name nhưng giữ code trong migration có kiểm soát | FK/API/model mapping vẫn ổn định |
| TC-CAT-007 | Model trả mã ngoài 11 category_code | Prediction mapping báo lỗi, không lưu nhãn sai |
| TC-CAT-008 | Phản ánh hợp lệ ngoài 10 nhóm đầu | Có thể gán OTHER sau đánh giá/kiểm duyệt |
| TC-CAT-009 | Nội dung thiếu thông tin | Không ép thành OTHER; lưu trạng thái phù hợp |

## 10. Database 12 bảng và tính nhất quán

| ID | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-DB-001 | Tạo Citizen, report và attachments | FK owner/report đúng; file chỉ lưu storage reference trong DB |
| TC-DB-002 | Preprocess report | Tạo preprocessing_runs; reports.raw_content không đổi |
| TC-DB-003 | Tạo prediction thành công | Gắn đúng report, preprocessing run, model version và category |
| TC-DB-004 | Inference thất bại | Report vẫn còn; prediction có trạng thái lỗi và category nullable |
| TC-DB-005 | Review xác nhận nhãn AI | Thêm prediction_reviews và cập nhật reports.final_category_id atomically |
| TC-DB-006 | Review sửa nhãn | Giữ prediction cũ; ghi nhãn trước/sau và actor/time |
| TC-DB-007 | Review lần hai | Thêm hàng history mới; không update/xóa review trước |
| TC-DB-008 | Dataset version đóng băng | Sample/config không thể bị sửa; tạo version mới cho thay đổi |
| TC-DB-009 | Sample chưa gán nhãn | category_id NULL chỉ khi labeling_status cho phép |
| TC-DB-010 | Training run tham chiếu dataset version | Run lưu đúng dataset/version, cấu hình và status |
| TC-DB-011 | Training metrics per-class | Có category_id, split, averaging và support đúng |
| TC-DB-012 | Schema migration | Có đúng 12 bảng baseline; không tự thêm bảng thứ 13 |
| TC-DB-013 | Review/audit sink tạm thời lỗi | Không làm mất dữ liệu review đã commit; audit event retry/được cảnh báo theo policy |


## 11. Citizen Profile

| ID | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-CIT-001 | Citizen xem hồ sơ sau khi đăng nhập | Chỉ trả hồ sơ gắn với principal hiện tại; không nhận user_id tùy ý từ client |
| TC-CIT-002 | Citizen cập nhật field hồ sơ được phép và thử field bị cấm | Field allow-list được chấp nhận; role/provider subject/account status bị từ chối sửa |

## 12. Audit Event Coverage

| ID | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-AUD-001 | Đăng nhập quan trọng/thất bại xác thực | Audit event có actor/context, action, time và outcome; không chứa secret/token |
| TC-AUD-002 | Review hoặc sửa nhãn phản ánh | Audit event liên kết report/prediction/review và ghi actor/time/outcome; không ghi toàn bộ raw_content |
| TC-AUD-003 | Cán bộ thay đổi trạng thái report hoặc role | Event ghi before/after tối thiểu, actor và request ID |
| TC-AUD-004 | Kích hoạt hoặc rollback model version | Event ghi model version cũ/mới, actor, timestamp và outcome |
| TC-AUD-005 | Người không có quyền đọc audit | Backend từ chối; không lộ thông tin audit |


## 14. Report, attachment, review and dashboard API

| ID | Kịch bản | Kết quả mong đợi |
|---|---|---|
| TC-REPORT-001 | Citizen gửi nội dung hợp lệ | Report được lưu raw_content nguyên bản; tạo preprocessing status SKIPPED và prediction INFERENCE_FAILED nếu chưa có active model |
| TC-REPORT-002 | Citizen gửi nội dung trắng | API từ chối 422; không tạo report |
| TC-REPORT-003 | Chỉ cung cấp latitude hoặc longitude | API từ chối 422 |
| TC-REPORT-004 | Citizen đọc report người khác | Trả 404, không tiết lộ report tồn tại |
| TC-UPLOAD-001 | Upload JPEG/PNG/WebP hợp lệ | Xác minh signature, lưu private volume và metadata |
| TC-UPLOAD-002 | File giả ảnh/đổi MIME header | Từ chối 415 |
| TC-UPLOAD-003 | File lớn hơn 10 MiB | Từ chối 413 |
| TC-UPLOAD-004 | Upload quá 5 file/report | Từ chối 422 |
| TC-UPLOAD-005 | User khác tải attachment | Từ chối 404 |
| TC-REVIEW-001 | RECEIVER xác nhận category trùng predicted category | Thêm review CONFIRMED và cập nhật final_category_id atomically |
| TC-REVIEW-002 | RECEIVER chọn category khác | Thêm review CORRECTED và cập nhật final_category_id atomically |
| TC-REVIEW-003 | Prediction thuộc report khác | Từ chối; không đổi final_category_id |
| TC-REVIEW-004 | Cán bộ xem review history | Các review cũ còn nguyên; không update/delete history |
| TC-WORKFLOW-001 | Chuyển SUBMITTED -> UNDER_REVIEW | Cho phép |
| TC-WORKFLOW-002 | Chuyển CLOSED -> trạng thái khác | Từ chối 409 |
| TC-WORKFLOW-003 | RECEIVER reopen RESOLVED -> IN_PROGRESS | Từ chối 403 |
| TC-WORKFLOW-004 | ADMIN reopen RESOLVED -> IN_PROGRESS | Cho phép |
| TC-DASH-001 | Dashboard summary/category distribution | Giá trị truy vấn PostgreSQL; trả đủ 11 danh mục kể cả danh mục 0 report |
| TC-MAP-001 | Map report filtering | Chỉ trả report có đủ latitude/longitude và áp dụng filter hợp lệ |
