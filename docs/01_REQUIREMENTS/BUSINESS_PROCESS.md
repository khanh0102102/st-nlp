# BUSINESS PROCESS — QUY TRÌNH NGHIỆP VỤ

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Draft |
| Phạm vi | Tiếp nhận, phân loại, kiểm duyệt và quản lý dữ liệu/model |

## 1. Mục đích

Mô tả luồng nghiệp vụ từ khi người dân gửi phản ánh đến khi cán bộ kiểm duyệt và dữ liệu đủ điều kiện được chọn cho hoạt động AI/ML. Quy trình này là baseline; tên trạng thái, SLA và quyền chuyển trạng thái cần được chủ dự án/nghiệp vụ chốt.

## 2. Quy trình tiếp nhận và dự đoán

```mermaid
flowchart TD
```
      A[Người dân đăng nhập Google] --> B[Tạo phản ánh]
      B --> C[Nhập văn bản, chọn ảnh, vị trí]
      C --> D{Dữ liệu hợp lệ?}
      D -- Không --> E[Hiển thị lỗi để người dân sửa]
      E --> C
      D -- Có --> F[Lưu phản ánh và file]
      F --> G[Đưa văn bản vào NLP pipeline]
      G --> H[Tiền xử lý]
      H --> I[Model inference]
      I --> J{Dự đoán thành công?}
      J -- Không --> K[Lưu trạng thái lỗi AI, giữ phản ánh]
      J -- Có --> L[Lưu nhãn, confidence, model version]
      K --> M[Đưa vào hàng đợi cán bộ xử lý]
      L --> M
      M --> N[Hiển thị trạng thái/kết quả theo quyền]

**Quy tắc**
- Lưu phản ánh thành công không phụ thuộc vào việc inference thành công.
- Retry inference phải có kiểm soát và không tạo lịch sử prediction gây nhầm lẫn.
- Mỗi prediction cần có model version/pipeline version.
- Nếu nội dung không phù hợp hoặc không đủ thông tin, hệ thống phải có cách biểu thị lỗi/không thể dự đoán thay vì ép một nhãn hợp lệ.

## 3. Quy trình cán bộ kiểm duyệt

```mermaid
flowchart TD
```
      A[Cán bộ đăng nhập Admin Portal] --> B[Danh sách phản ánh cần xem]
      B --> C[Mở chi tiết]
      C --> D[Xem nội dung, ảnh, vị trí và prediction]
      D --> E{Nhãn AI phù hợp?}
      E -- Có --> F[Xác nhận nhãn]
      E -- Không --> G[Chọn nhãn đúng và ghi chú]
      F --> H[Backend kiểm tra quyền và dữ liệu hiện tại]
      G --> H
      H --> I{Yêu cầu hợp lệ?}
      I -- Không --> J[Trả lỗi/xung đột để xử lý]
      I -- Có --> K[Lưu review và audit]
      K --> L[Cập nhật nhãn đã kiểm duyệt]
      L --> M[Hiển thị lịch sử và trạng thái mới]

**Quy tắc**
- Không ghi đè prediction gốc.
- Lưu nhãn AI, nhãn sau review và người kiểm duyệt riêng biệt.
- Review phải có timestamp; ghi chú/lý do theo policy.
- Tránh hai cán bộ ghi đè kết quả của nhau mà không phát hiện.

## 4. Quy trình quản lý Dataset

```mermaid
flowchart TD
```
      A[AI/Data Manager tạo hoặc chọn Dataset] --> B[Thêm/import samples]
      B --> C[Chuẩn hóa schema và label]
      C --> D[Validate dữ liệu]
      D --> E{Đạt tiêu chí?}
      E -- Không --> F[Báo lỗi/cảnh báo và chỉnh sửa]
      F --> D
      E -- Có --> G[Tạo/đóng băng Dataset Version]
      G --> H[Chia train/validation/test]
      H --> I[Kiểm tra duplicate và leakage]
      I --> J[Đánh dấu sẵn sàng huấn luyện]

**Quy tắc**
- Không thay đổi âm thầm dataset version đã dùng trong một training run.
- Ghi nguồn dữ liệu và lịch sử chỉnh sửa.
- Tách tập dữ liệu trước khi học các tham số từ dữ liệu; tránh leakage.
- Quy tắc gán nhãn và xử lý dữ liệu nhạy cảm phải được ban hành riêng.

## 5. Quy trình huấn luyện và quản lý model

```mermaid
flowchart TD
```
      A[Chọn Dataset Version] --> B[Chọn thuật toán và cấu hình]
      B --> C[Tạo Training Run]
      C --> D[Huấn luyện]
      D --> E[Đánh giá trên validation/test]
      E --> F[Lưu metrics và artifact]
      F --> G{Đạt tiêu chí?}
      G -- Không --> H[Lưu run, phân tích và thử nghiệm lại]
      G -- Có --> I[Đăng ký Model Version]
      I --> J[Review/phê duyệt]
      J --> K{Được duyệt?}
      K -- Không --> L[Giữ ở trạng thái chưa triển khai]
      K -- Có --> M[Kích hoạt model version]
      M --> N[Theo dõi và có phương án rollback]

## 6. Quy trình dữ liệu phản hồi

1. Prediction gốc được lưu riêng.
2. Cán bộ kiểm duyệt tạo bản ghi review.
3. Review đã xác nhận có thể được xem xét để đưa vào dữ liệu huấn luyện.
4. Data Manager kiểm tra nguồn gốc, chất lượng, trùng lặp và quyền sử dụng.
5. Sample được gán vào dataset/version phù hợp.
6. Mỗi lần huấn luyện ghi lại dataset version đã sử dụng.

Không tự động thêm mọi phản ánh vào dataset huấn luyện. Cần có bước kiểm tra và policy chấp thuận.

## 7. Trạng thái nghiệp vụ cần chốt

Không cố định enum trước khi chủ dự án duyệt. Cần định nghĩa:
- Report status: trạng thái tiếp nhận/xử lý của phản ánh.
- Prediction status: pending, succeeded, failed hoặc trạng thái tương đương.
- Review status: chưa xem, đã xác nhận, đã chỉnh sửa hoặc trạng thái nghiệp vụ tương ứng.
- Dataset status: draft, validating, ready, archived hoặc tương đương.
- Training Run status: queued, running, succeeded, failed, cancelled hoặc tương đương.
- Model Version status: registered, evaluated, approved, active, retired hoặc tương đương.

Mỗi trạng thái cần điều kiện vào/ra, actor được phép và audit.

## 8. SLA và thông báo

SLA, thời gian xử lý, thông báo email/push/SMS và cơ chế escalations hiện TBD. Không xây dựng thông báo ngoài phạm vi trước khi có yêu cầu.
