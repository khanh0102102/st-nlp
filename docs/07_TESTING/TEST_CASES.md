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
