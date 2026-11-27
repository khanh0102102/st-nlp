# PROJECT OVERVIEW
# SMART TRAFFIC & URBAN INCIDENT CLASSIFIER (ST-NLP)

| Thuộc tính | Giá trị |
|---|---|
| Tên dự án | Smart Traffic & Urban Incident Classifier |
| Tên viết tắt | ST-NLP |
| Loại hệ thống | Nền tảng tiếp nhận phản ánh và hỗ trợ phân loại bằng NLP/ML |
| Phiên bản tài liệu | 1.0 |
| Trạng thái | Baseline tổng quan đã được chủ dự án thống nhất; chi tiết chuyên ngành tiếp tục được đặc tả |
| Ngôn ngữ nghiệp vụ chính | Tiếng Việt |

## 1. Giới thiệu

ST-NLP là hệ thống phần mềm tiếp nhận, quản lý và hỗ trợ phân loại các phản ánh liên quan đến giao thông và hạ tầng đô thị. Người dân gửi phản ánh bằng văn bản, hình ảnh và vị trí xảy ra sự việc. Hệ thống sử dụng Natural Language Processing (NLP) và Machine Learning (ML) để phân tích nội dung văn bản và đề xuất phân loại vào 11 nhóm danh mục.

Kết quả phân loại AI được cung cấp cho cán bộ tiếp nhận để xem xét, xác nhận hoặc điều chỉnh. AI là công cụ hỗ trợ, không thay thế quyết định nghiệp vụ của cán bộ.

ST-NLP đồng thời cung cấp phân hệ quản lý dữ liệu và vòng đời mô hình, gồm Dataset, Dataset Samples, Training Runs, Training Metrics và phiên bản mô hình.

## 2. Bài toán và lý do thực hiện

Phản ánh của người dân có thể khác nhau về cách diễn đạt, độ dài, chính tả, mức độ đầy đủ của thông tin và vị trí xảy ra. Khi số lượng phản ánh tăng, cán bộ phải dành thời gian đọc, hiểu, phân nhóm và tổng hợp thủ công. Việc quản lý văn bản, ảnh, vị trí và kết quả phân loại tách rời cũng gây khó khăn cho tra cứu và thống kê.

ST-NLP hướng đến:
- Chuẩn hóa và tập trung thông tin phản ánh.
- Hỗ trợ phân loại văn bản tự động.
- Rút ngắn thao tác phân loại ban đầu của cán bộ.
- Tạo công cụ kiểm duyệt có lưu vết.
- Khai thác dữ liệu đã kiểm duyệt để đánh giá và cải thiện mô hình.

## 3. Mục tiêu

### 3.1. Mục tiêu tổng quát

Xây dựng hệ thống tiếp nhận và quản lý phản ánh giao thông, hạ tầng đô thị, kết hợp NLP/ML để hỗ trợ phân loại thành 11 nhóm và cung cấp công cụ kiểm duyệt, thống kê, quản lý dữ liệu huấn luyện.

### 3.2. Mục tiêu cụ thể

1. Cung cấp cổng người dân với xác thực Google theo định hướng đã thống nhất.
2. Cho phép gửi nội dung phản ánh, ảnh minh chứng và vị trí.
3. Hiển thị xem trước ảnh ngay sau khi người dùng chọn file, trước khi gửi.
4. Xử lý văn bản tiếng Việt và đề xuất một trong 11 nhóm phân loại.
5. Lưu kết quả dự đoán, confidence, phiên bản mô hình và thời điểm dự đoán.
6. Cho phép người dân xem phản ánh, kết quả AI, trạng thái và lịch sử thuộc tài khoản của mình theo quyền.
7. Cung cấp cổng quản trị riêng biệt về URL/route.
8. Cho phép cán bộ xem, tìm kiếm, lọc, kiểm duyệt và chỉnh sửa kết quả AI.
9. Cung cấp dashboard và bản đồ phân bố phản ánh.
10. Quản lý dataset, mẫu dữ liệu, lần huấn luyện, metrics và phiên bản mô hình.
11. Lưu lịch sử thay đổi quan trọng để truy vết và phục vụ cải tiến.

## 4. Nhóm người dùng

### 4.1. Người dân (Citizen)

Người dân đăng nhập bằng Google, tạo phản ánh, tải ảnh, chọn vị trí, xem kết quả AI được phép công khai cho chính họ và theo dõi lịch sử/trạng thái phản ánh của mình.

### 4.2. Cán bộ tiếp nhận/kiểm duyệt (Moderator/Staff)

Cán bộ truy cập cổng quản trị, xem phản ánh, bản đồ, kết quả AI, xác nhận hoặc sửa nhãn và cập nhật trạng thái nghiệp vụ theo quyền.

### 4.3. Quản trị hệ thống (Administrator)

Quản trị tài khoản nội bộ, vai trò, quyền, danh mục và cấu hình được phân quyền. Quyền quản trị không mặc nhiên bao gồm quyền huấn luyện mô hình.

### 4.4. Quản lý AI và dữ liệu (AI/Data Manager)

Quản lý dataset, mẫu dữ liệu, kiểm tra dữ liệu, tạo hoặc theo dõi training run, xem metrics và quản lý phiên bản mô hình theo quyền.

Một người có thể mang nhiều vai trò; phân quyền phải được thực thi ở Backend. Danh sách vai trò cuối cùng cần được chốt trong Security Design.

## 5. Ba phân hệ chính

### 5.1. Citizen Portal — Cổng người dân

- Đăng nhập Google và quản lý phiên.
- Quản lý thông tin hồ sơ tối thiểu cần thiết.
- Tạo phản ánh bằng văn bản.
- Chọn một hoặc nhiều ảnh theo giới hạn được cấu hình.
- Xem trước, loại bỏ hoặc thay ảnh trước khi gửi.
- Chọn vị trí trên bản đồ và xác nhận vị trí.
- Xem kết quả phân loại AI được phép hiển thị.
- Xem danh sách, chi tiết, lịch sử và trạng thái phản ánh của bản thân.

### 5.2. Admin Portal — Cổng quản trị

- Xác thực và kiểm tra quyền cán bộ.
- Dashboard tổng quan và thống kê theo 11 nhóm.
- Danh sách, tìm kiếm, lọc và xem chi tiết phản ánh.
- Bản đồ vị trí phản ánh.
- Xem nhãn dự đoán và confidence.
- Xác nhận hoặc điều chỉnh nhãn; ghi nhận người duyệt và thời điểm.
- Quản lý trạng thái nghiệp vụ theo workflow được phê duyệt.
- Tra cứu lịch sử kiểm duyệt và thao tác liên quan.

### 5.3. AI & Data Management — Quản lý AI và dữ liệu

- Quản lý Dataset và phiên bản Dataset.
- Quản lý Dataset Samples và nhãn.
- Kiểm tra dữ liệu, trùng lặp, thiếu nhãn và mất cân bằng.
- Tạo và theo dõi Training Runs.
- Lưu Training Metrics và artifact huấn luyện.
- So sánh kết quả các mô hình/lần huấn luyện.
- Quản lý Model Version và trạng thái triển khai.

## 6. Quy trình tổng quát

1. Người dân đăng nhập và gửi phản ánh kèm văn bản, ảnh, vị trí.
2. Backend xác thực, kiểm tra dữ liệu, lưu phản ánh và file theo chính sách.
3. NLP pipeline tiền xử lý văn bản và gọi mô hình được cấu hình.
4. Hệ thống lưu dự đoán, confidence, model version và trạng thái xử lý AI.
5. Cán bộ xem phản ánh trong Admin Portal và kiểm tra đề xuất AI.
6. Cán bộ xác nhận hoặc sửa nhãn; hệ thống lưu audit/review history.
7. Dashboard và bản đồ tổng hợp dữ liệu theo quyền.
8. Dữ liệu được phép sử dụng có thể được đưa vào quy trình tạo dataset/huấn luyện mới sau khi đáp ứng quy tắc chất lượng và quyền riêng tư.

## 7. Phạm vi AI

Bài toán chính trong phiên bản nền tảng là phân loại văn bản phản ánh vào 11 nhóm. Các mô hình đã được định hướng nghiên cứu gồm Naive Bayes, SVM, CNN 1D và LSTM. Việc lựa chọn mô hình triển khai phải dựa trên kết quả đánh giá trên tập dữ liệu phù hợp, không mặc định mô hình phức tạp nhất là tốt nhất.

Đầu vào chính của bộ phân loại là văn bản đã được tiền xử lý. Ảnh và vị trí được quản lý như thông tin minh chứng/ngữ cảnh của phản ánh; không suy diễn rằng hệ thống đã có mô hình computer vision phân tích ảnh.

## 8. Dữ liệu chính

Các miền dữ liệu gồm tài khoản/vai trò, phản ánh, file đính kèm, vị trí, danh mục, dự đoán, kiểm duyệt/lịch sử, dataset/mẫu dữ liệu, training run/metrics và model version. Cấu trúc vật lý chi tiết được quy định trong Database Design, ERD và Data Dictionary.

## 9. Nguyên tắc sản phẩm

- Tách cổng người dân và quản trị về URL/route và quyền.
- AI hỗ trợ, con người chịu trách nhiệm xác nhận nghiệp vụ.
- Dữ liệu người dân chỉ được truy cập theo quyền và mục đích hợp lệ.
- Mỗi kết quả dự đoán phải truy được model version và lần chạy liên quan khi có.
- Thay đổi nhãn phải có lịch sử, người thực hiện và thời điểm.
- Thiết kế module rõ ràng, API có hợp đồng, database có migration.
- Có test cho logic nghiệp vụ, phân quyền và luồng dữ liệu quan trọng.
- Không mở rộng phạm vi sang điều phối hiện trường khi chưa được phê duyệt.

## 10. Kết quả dự kiến

Một hệ thống có ba phân hệ hoạt động thống nhất: cổng người dân, cổng quản trị, và quản lý AI/dữ liệu; có pipeline phân loại văn bản, cơ chế human-in-the-loop, dashboard/bản đồ, lịch sử kiểm duyệt và công cụ theo dõi chất lượng mô hình.

## 11. Tài liệu liên quan

- [Phạm vi dự án](PROJECT_SCOPE.md)
- [Lộ trình dự án](PROJECT_ROADMAP.md)
- [Đặc tả yêu cầu](../01_REQUIREMENTS/SRS.md)
- [Kiến trúc tổng thể](../02_ARCHITECTURE/SYSTEM_ARCHITECTURE.md)
- [Thiết kế Database](../03_DATABASE/DATABASE_DESIGN.md)
- [Thiết kế AI/ML](../09_AI_ML/MODEL_DESIGN.md)
