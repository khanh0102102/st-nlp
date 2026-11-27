# BRD — BUSINESS REQUIREMENTS DOCUMENT

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Draft |
| Chủ sở hữu nghiệp vụ | Chủ dự án ST-NLP / đại diện đơn vị tiếp nhận (TBD) |

## 1. Mục đích

BRD mô tả nhu cầu nghiệp vụ và giá trị mà ST-NLP cần tạo ra. Tài liệu tập trung vào vấn đề, người liên quan, kết quả mong muốn và quy trình nghiệp vụ; chi tiết kỹ thuật nằm trong SRS và tài liệu thiết kế.

## 2. Bối cảnh nghiệp vụ

Người dân phản ánh các vấn đề giao thông và hạ tầng đô thị bằng ngôn ngữ tự nhiên, thường kèm hình ảnh và vị trí. Cán bộ cần tiếp nhận, hiểu nội dung, phân nhóm, xác minh và tổng hợp. Khi lượng phản ánh tăng hoặc cách diễn đạt đa dạng, phân loại thủ công có thể tốn thời gian và khó thống nhất.

ST-NLP cung cấp kênh tiếp nhận tập trung và bộ phân loại văn bản hỗ trợ cán bộ. Hệ thống không thay thế quy trình nghiệp vụ có thẩm quyền.

## 3. Vấn đề cần giải quyết

- Thông tin phản ánh phân tán hoặc thiếu cấu trúc.
- Cán bộ phải đọc và phân loại từng phản ánh.
- Cách diễn đạt tiếng Việt đa dạng gây khó khăn cho phân loại nhất quán.
- Ảnh và vị trí cần được liên kết với nội dung phản ánh.
- Khó tổng hợp số lượng và phân bố vấn đề theo danh mục/khu vực.
- Chưa có vòng phản hồi có cấu trúc từ kết quả kiểm duyệt về dữ liệu AI.
- Việc đánh giá các lần huấn luyện cần được lưu trữ và so sánh.

## 4. Mục tiêu nghiệp vụ

- Một kênh tiếp nhận phản ánh số hóa.
- Phân loại tự động mang tính hỗ trợ vào 11 danh mục.
- Cán bộ có thể xác nhận hoặc sửa kết quả AI.
- Tăng khả năng truy vết từ phản ánh → dự đoán → kiểm duyệt → dữ liệu được chọn cho huấn luyện.
- Cung cấp dashboard/bản đồ để tra cứu và tổng hợp.
- Quản lý dataset, training run, metrics và phiên bản model có kiểm soát.

## 5. Stakeholders

| Bên liên quan | Quan tâm | Trách nhiệm/ảnh hưởng |
|---|---|---|
| Người dân | Gửi thuận tiện, biết trạng thái, bảo vệ thông tin | Cung cấp dữ liệu phản ánh |
| Cán bộ tiếp nhận | Thông tin đầy đủ, phân loại nhanh, dễ duyệt | Tiếp nhận và kiểm duyệt |
| Quản trị hệ thống | Tài khoản, quyền, cấu hình, vận hành | Quản trị kỹ thuật/người dùng |
| Quản lý AI/Data | Dữ liệu chất lượng, huấn luyện và đánh giá | Dataset và model lifecycle |
| Chủ dự án | Phạm vi, chất lượng và nghiệm thu | Phê duyệt yêu cầu/ưu tiên |
| Đơn vị vận hành | Bảo mật, backup, tính sẵn sàng | Vận hành môi trường |

## 6. Business Requirements

| ID | Yêu cầu nghiệp vụ | Ưu tiên |
|---|---|---|
| BR-01 | Cung cấp kênh để người dân gửi phản ánh giao thông/hạ tầng đô thị | Must |
| BR-02 | Một phản ánh cần lưu nội dung, thời điểm, người gửi và vị trí khi có | Must |
| BR-03 | Cho phép đính kèm hình ảnh minh chứng | Must |
| BR-04 | Hỗ trợ phân loại văn bản vào 11 danh mục bằng NLP/ML | Must |
| BR-05 | Kết quả AI phải là đề xuất có thông tin confidence và nguồn model | Must |
| BR-06 | Cán bộ được phân quyền có thể xác nhận hoặc sửa nhãn | Must |
| BR-07 | Lưu lịch sử kiểm duyệt và thay đổi nhãn | Must |
| BR-08 | Người dân chỉ xem phản ánh của mình và thông tin được phép công bố | Must |
| BR-09 | Cung cấp Dashboard và bản đồ phản ánh | Should |
| BR-10 | Quản lý Dataset và Dataset Samples | Must |
| BR-11 | Quản lý Training Runs và Training Metrics | Must |
| BR-12 | Theo dõi Model Versions và lựa chọn model triển khai | Should |
| BR-13 | Dữ liệu kiểm duyệt có thể được chọn làm nguồn dữ liệu huấn luyện sau kiểm tra | Should |
| BR-14 | Hệ thống có audit cho thao tác nhạy cảm | Must |

## 7. Quy tắc nghiệp vụ

- Người dân phải xác thực trước khi gửi phản ánh.
- Tài nguyên của người dân được giới hạn theo chủ sở hữu.
- Nhãn AI là nhãn dự đoán; nhãn sau kiểm duyệt là kết quả nghiệp vụ riêng.
- Không ghi đè dự đoán gốc khi cán bộ sửa nhãn; lưu cả lịch sử và nhãn cuối cùng.
- Mỗi prediction cần tham chiếu model version.
- Mọi thay đổi nhãn cần xác định actor và timestamp.
- Chỉ dữ liệu hợp lệ, có nguồn và quyền sử dụng phù hợp mới đưa vào dataset.
- Chỉ model vượt tiêu chí đánh giá và được phê duyệt mới được kích hoạt.
- Các trạng thái phản ánh và chuyển trạng thái phải được quy định tập trung, tránh xử lý tùy ý theo từng màn hình.

## 8. Chỉ số giá trị (KPI)

KPI cần đo lường sau khi có baseline:
- Thời gian trung bình từ gửi phản ánh đến khi có đề xuất AI.
- Thời gian cán bộ dành cho phân loại một phản ánh.
- Tỷ lệ cán bộ chấp nhận nhãn AI không cần chỉnh sửa.
- Tỷ lệ dự đoán đúng trên tập test độc lập.
- Macro-F1 và F1 từng lớp.
- Tỷ lệ phản ánh có đủ nội dung/ảnh/vị trí theo yêu cầu.
- Tỷ lệ lỗi truy cập trái quyền.
- Thời gian tải Dashboard và bản đồ.

Giá trị mục tiêu số học: TBD; không đặt KPI giả định khi chưa có baseline và dữ liệu đo.

## 9. Rủi ro nghiệp vụ

| Rủi ro | Ảnh hưởng | Hướng giảm thiểu |
|---|---|---|
| Dữ liệu thiếu hoặc nhãn không thống nhất | Model dự đoán kém | Labeling guideline, kiểm tra dữ liệu |
| Lớp mất cân bằng | Bỏ sót nhóm hiếm | Báo cáo từng lớp, chiến lược sampling |
| Người dùng nhập nội dung thiếu thông tin | Kết quả khó chính xác | Gợi ý trường thông tin, validation |
| Ảnh chứa dữ liệu cá nhân | Rủi ro riêng tư | Cảnh báo, quyền truy cập, retention |
| Vị trí sai | Dashboard/map sai | Cho phép xác nhận/chỉnh marker |
| Cán bộ quá tin AI | Quyết định sai | Human review, hiển thị confidence và giới hạn |
| Model drift | Chất lượng giảm | Monitoring, versioning, đánh giá định kỳ |

## 10. Giả định và câu hỏi mở

- Đơn vị nghiệp vụ chính thức và quy trình phê duyệt: TBD.
- Từ điển 11 danh mục: cần cung cấp và duyệt.
- Quy tắc SLA/trạng thái phản ánh: TBD.
- Quy định lưu trữ, xử lý dữ liệu cá nhân và ảnh: cần xác minh.
- Ngưỡng AI, KPI và mức độ tự động hóa: chưa chốt.
