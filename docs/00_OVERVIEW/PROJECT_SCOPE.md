# PROJECT SCOPE — PHẠM VI DỰ ÁN

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Draft for implementation baseline |
| Phạm vi áp dụng | ST-NLP |

## 1. Mục đích

Tài liệu xác định chức năng thuộc ST-NLP, nội dung không thuộc phạm vi, giới hạn, giả định và tiêu chí nghiệm thu tổng thể. Mọi đề xuất mở rộng phải được đánh giá tác động trước khi bổ sung.

## 2. Trong phạm vi (In Scope)

### 2.1. Citizen Portal

- Xác thực người dân qua Google OAuth.
- Tạo và quản lý hồ sơ người dân ở mức tối thiểu cần thiết.
- Tạo phản ánh bằng nội dung văn bản tiếng Việt.
- Đính kèm hình ảnh; kiểm tra định dạng/kích thước; xem trước ảnh ngay sau khi chọn.
- Chọn, chỉnh sửa và xác nhận vị trí phản ánh trên bản đồ.
- Xem kết quả phân loại AI, lịch sử và trạng thái phản ánh của chính mình theo quyền.
- Xem chi tiết các phản ánh đã gửi.

### 2.2. Admin Portal

- Cổng truy cập quản trị riêng về URL/route.
- Đăng nhập cán bộ và kiểm tra vai trò/quyền.
- Dashboard số lượng phản ánh và thống kê theo 11 danh mục.
- Danh sách, tìm kiếm, lọc và chi tiết phản ánh.
- Hiển thị vị trí phản ánh trên bản đồ.
- Hiển thị đề xuất AI và confidence.
- Xác nhận hoặc điều chỉnh nhãn AI.
- Quản lý trạng thái nghiệp vụ trong phạm vi workflow được duyệt.
- Lưu lịch sử kiểm duyệt và các thay đổi trọng yếu.

### 2.3. AI & Data Management

- Quản lý dataset và dataset samples.
- Quản lý nhãn và kiểm tra tính hợp lệ của dữ liệu.
- Quản lý training runs và training metrics.
- Huấn luyện/thử nghiệm các mô hình Naive Bayes, SVM, CNN 1D và LSTM theo kế hoạch.
- Quản lý artifact và phiên bản mô hình.
- Đánh giá, so sánh và chọn phiên bản mô hình để triển khai.

### 2.4. Nền tảng kỹ thuật

- Backend API phục vụ hai cổng.
- Cơ sở dữ liệu quan hệ và migration.
- Dịch vụ lưu file ảnh.
- Logging, audit, cấu hình môi trường và kiểm thử.
- Docker Compose làm hướng triển khai môi trường phát triển nếu phù hợp với stack đã chốt.

## 3. Ngoài phạm vi (Out of Scope) của baseline

Các hạng mục sau không được mặc định xây dựng trong phiên bản nền tảng:

- Điều phối đội hiện trường, giao việc cho nhân viên sửa chữa hoặc quản lý lịch làm việc.
- Quản lý vật tư, ngân sách, đấu thầu hoặc quy trình hành chính của cơ quan.
- Tự động xử phạt, kết luận vi phạm hoặc ra quyết định hành chính.
- Tích hợp camera giao thông/video streaming hoặc nhận diện đối tượng trong ảnh.
- Dự báo ùn tắc, tối ưu tuyến đường hoặc điều khiển tín hiệu đèn giao thông.
- Ứng dụng di động native riêng; ưu tiên cổng web responsive trừ khi được duyệt khác.
- Chatbot tổng đài, SMS/Zalo notification hoặc tích hợp bên thứ ba chưa có yêu cầu.
- Công khai toàn bộ phản ánh cho người dùng khác.
- Tự động tái huấn luyện và đưa model mới lên production mà không qua đánh giá/phê duyệt.
- Tích hợp hệ thống dữ liệu của cơ quan nhà nước chưa được xác định.

Các hạng mục này có thể trở thành giai đoạn mở rộng sau khi có yêu cầu và đánh giá riêng.

## 4. Ranh giới xử lý

- Bộ phân loại AI xử lý văn bản; ảnh được lưu và hiển thị như minh chứng trong baseline.
- Vị trí được thu thập và hiển thị trên bản đồ; nhà cung cấp bản đồ/geocoding còn TBD.
- AI trả về nhãn đề xuất và confidence; cán bộ được phân quyền thực hiện quyết định kiểm duyệt.
- Người dân chỉ xem tài nguyên thuộc tài khoản của họ.
- Cổng quản trị và API quản trị phải áp dụng RBAC ở Backend.
- Dataset chỉ nhận dữ liệu được phép sử dụng, có nguồn gốc và nhãn rõ ràng.
- Model deployment phải gắn model version và có phương án quay lui.

## 5. Các sản phẩm bàn giao

1. Tài liệu yêu cầu, kiến trúc, database, API, UI/UX và AI/ML.
2. Citizen Portal.
3. Admin Portal.
4. Backend API và tích hợp NLP inference.
5. Database schema và migration.
6. Công cụ quản lý dataset/training/model.
7. Bộ kiểm thử tự động.
8. Docker/configuration cho môi trường được hỗ trợ.
9. Hướng dẫn cài đặt, vận hành và sử dụng.
10. Báo cáo đánh giá mô hình và kết quả nghiệm thu.

## 6. Giả định

- Người dân có tài khoản Google và có thể hoàn tất xác thực OAuth.
- Phản ánh chủ yếu sử dụng tiếng Việt.
- Có danh mục gồm 11 nhãn được định nghĩa thống nhất.
- Cán bộ có nghiệp vụ để kiểm tra và điều chỉnh phân loại.
- Có nguồn dữ liệu đủ quyền sử dụng để huấn luyện/đánh giá.
- Hạ tầng lưu file và dịch vụ bản đồ sẽ được chọn trước khi hoàn thiện triển khai.
- Quy định pháp lý, thời hạn lưu trữ và chính sách quyền riêng tư phải được chủ dự án xác minh theo môi trường triển khai thực tế.

## 7. Ràng buộc

- Không để lộ dữ liệu cá nhân hoặc vị trí nhạy cảm qua API/log.
- Không dùng dữ liệu người thật cho test tự động nếu chưa được ẩn danh và cho phép.
- Không thay đổi nhãn hoặc schema tùy tiện giữa các phiên bản dataset/model.
- Các thay đổi DB cần migration có thể kiểm soát.
- API phải kiểm tra quyền ở server-side.
- Các chỉ số AI cần báo cáo theo từng lớp, không chỉ một chỉ số tổng thể.

## 8. Tiêu chí thành công cấp dự án

- Người dân có thể đăng nhập, gửi phản ánh có văn bản, ảnh và vị trí, sau đó tra cứu dữ liệu của mình.
- Mỗi phản ánh hợp lệ có thể đi qua pipeline NLP và lưu kết quả dự đoán cùng model version.
- Cán bộ có thể xem và kiểm duyệt nhãn; lịch sử thay đổi có thể truy vết.
- Dashboard và bản đồ hiển thị dữ liệu đúng với bộ lọc/quyền.
- Người quản lý AI có thể quản lý dataset, samples, training runs, metrics và model versions.
- Các luồng chính có kiểm thử tự động và không có lỗi nghiêm trọng còn mở tại thời điểm nghiệm thu.
- Các mục tiêu số học về hiệu năng, độ chính xác, availability và RPO/RTO phải được chốt trong NFR/Acceptance Criteria trước khi nghiệm thu chính thức.

## 9. Quy trình thay đổi phạm vi

Mỗi yêu cầu mới phải ghi: lý do, người đề xuất, lợi ích, ảnh hưởng đến dữ liệu/API/UI/AI/bảo mật, công sức, rủi ro và quyết định phê duyệt. Chỉ cập nhật SRS/Roadmap sau khi chủ dự án chấp thuận.

## 10. Điểm còn TBD

- Tên/thứ tự 11 danh mục và category_code đã được ghi trong CLASSIFICATION_SPECIFICATION.md; ranh giới nghiệp vụ và hướng dẫn adjudication cho các nhóm giao nhau cần tiếp tục được hoàn thiện/phê duyệt.
- Danh sách trạng thái phản ánh, quyền chuyển trạng thái và quy tắc hiển thị cho người dân.
- Có/không thông báo khi trạng thái thay đổi.
- Giới hạn số lượng/định dạng/dung lượng ảnh.
- Nhà cung cấp bản đồ và cách xử lý vị trí.
- Chính sách thời hạn lưu trữ/xóa dữ liệu và file.
- Mục tiêu hiệu năng, chất lượng mô hình và availability.


## 9. Danh mục phân loại và phạm vi dữ liệu

Phạm vi phân loại gồm chính xác 11 danh mục cố định theo tên và thứ tự do chủ dự án cung cấp. Nguồn chuẩn về mã, mô tả và ranh giới nhãn là [CLASSIFICATION_SPECIFICATION](../01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md). Không tạo lớp thứ 12. OTHER dành cho phản ánh hợp lệ ngoài 10 nhóm; nội dung không đủ thông tin, input không hợp lệ và lỗi inference là trạng thái riêng.

Baseline Database gồm đúng 12 bảng theo [DATABASE_DESIGN](../03_DATABASE/DATABASE_DESIGN.md). Ảnh và model artifact lưu ngoài relational database; report_attachments/model_versions giữ metadata và storage reference. Audit tổng quát được ghi qua audit sink append-only ngoài 12 bảng; provider và retention còn TBD.

## 10. Ranh giới dữ liệu bắt buộc

- Người dân không bắt buộc chọn category khi gửi; AI đưa ra nhãn đề xuất, cán bộ có quyền xác nhận/chỉnh sửa.
- reports.raw_content giữ nguyên văn bản gốc.
- reports.final_category_id chỉ là nhãn cuối cùng sau xác nhận của cán bộ và có thể NULL trước review.
- predictions lưu nhãn AI, confidence, model version và preprocessing run.
- prediction_reviews lưu lịch sử append-only; không ghi đè prediction.
- Dataset sample chỉ được tạo từ nguồn có quyền tái sử dụng và qua validation.
