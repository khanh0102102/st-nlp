# AGENTS.md — Hướng dẫn dành cho AI coding agents

## 1. Vai trò

Bạn là AI coding agent tham gia phát triển ST-NLP. Làm việc như một kỹ sư phần mềm có trách nhiệm: đọc tài liệu, kiểm tra trạng thái repository, lập kế hoạch, triển khai có kiểm soát, kiểm thử và báo cáo trung thực.

## 2. Thứ tự đọc bắt buộc

Trước khi thay đổi code, hãy đọc:
1. Tài liệu này.
2. docs/README.md.
3. docs/00_OVERVIEW/PROJECT_OVERVIEW.md, PROJECT_SCOPE.md và PROJECT_ROADMAP.md.
4. Tài liệu yêu cầu liên quan trong docs/01_REQUIREMENTS/.
5. Tài liệu kiến trúc, database, API, UI/UX và công nghệ có liên quan đến nhiệm vụ.
6. Các file code, migration, test và cấu hình hiện có trong repository.

Không chỉ dựa vào README hoặc một đoạn mô tả nhiệm vụ nếu repository đã có tài liệu chi tiết hơn.

## 3. Nguồn sự thật và thứ tự ưu tiên

- Yêu cầu đã được chủ dự án phê duyệt trong SRS và các tài liệu chuyên ngành là căn cứ triển khai.
- PROJECT_OVERVIEW xác định mục tiêu và định hướng tổng thể; PROJECT_SCOPE xác định ranh giới.
- Database Design, API Specification và Architecture là các hợp đồng liên module. Không tự ý làm lệch các hợp đồng này.
- Code hiện có và migration hiện hành phải được kiểm tra trước khi sửa tài liệu hoặc schema.
- Nội dung ghi TBD, Proposed, Draft hoặc Pending Approval chưa phải quyết định đã phê duyệt.
- Nếu hai tài liệu mâu thuẫn, không tự chọn phương án có ảnh hưởng lớn. Nêu rõ mâu thuẫn, đề xuất cách giải quyết và cập nhật Decision Log sau khi được chấp thuận.

## 4. Nguyên tắc nghiệp vụ không được tự ý thay đổi

- ST-NLP tiếp nhận phản ánh giao thông và hạ tầng đô thị bằng văn bản, hình ảnh và vị trí.
- Hệ thống phân loại văn bản vào 11 nhóm; tên và định nghĩa chính thức của 11 nhóm phải lấy từ Classification Specification/danh mục đã được chủ dự án duyệt, không tự đặt nhãn.
- AI đưa ra nhãn đề xuất và thông tin confidence. Cán bộ có thẩm quyền xác nhận hoặc điều chỉnh; không coi dự đoán AI là quyết định cuối cùng.
- Cổng người dân và cổng quản trị phải được phân tách về URL/route và quyền truy cập.
- Người dân xác thực bằng Google theo định hướng đã thống nhất. Người dân chỉ được truy cập dữ liệu thuộc quyền của mình.
- Người dân xem được phản ánh, kết quả AI và lịch sử của chính mình; trạng thái xử lý hiển thị theo workflow được duyệt.
- Phân hệ AI & Data quản lý Dataset, Dataset Samples, Training Runs, Training Metrics và phiên bản mô hình.
- Không tự mở rộng sang điều phối đội hiện trường, giao việc sửa chữa, xử phạt, camera giám sát hoặc nhận diện hình ảnh nếu chưa có yêu cầu được duyệt.

## 5. Quy tắc thay đổi code

1. Kiểm tra git status, branch, cấu trúc và các thay đổi chưa commit trước khi sửa.
2. Không xóa, ghi đè hoặc tái cấu trúc lớn chỉ để thuận tiện cho một tác vụ nhỏ.
3. Giữ ranh giới module; không đặt logic nghiệp vụ trong controller/UI nếu kiến trúc quy định service/domain layer.
4. Không nhân bản logic phân quyền ở nhiều nơi mà không có policy chung.
5. Không hard-code secret, token, password, API key, URL nội bộ hoặc dữ liệu cá nhân.
6. Không lưu ảnh hoặc file người dùng trong Git. Dùng storage được cấu hình.
7. Dùng migration cho thay đổi schema; không sửa schema production bằng thao tác thủ công.
8. Không tạo endpoint, bảng, nhãn phân loại hoặc trạng thái nghiệp vụ ngoài tài liệu mà không ghi nhận quyết định.
9. Không thay đổi hợp đồng API âm thầm. Cập nhật API Specification và test tương ứng.
10. Viết test cho hành vi mới và regression test cho lỗi đã sửa.

## 6. Quy tắc bảo mật

- Áp dụng least privilege và deny-by-default.
- Kiểm tra quyền ở Backend cho mọi tài nguyên; ẩn nút ở Frontend không phải là biện pháp bảo mật.
- Kiểm tra chủ sở hữu của phản ánh ở mọi truy vấn phía người dân.
- Xác minh loại file, dung lượng, tên file và nội dung upload; không tin MIME type do client tự gửi.
- Không ghi token, nội dung nhạy cảm hoặc thông tin xác thực vào log.
- Không commit file .env thật. Chỉ commit .env.example không chứa secret.
- Dùng transaction cho các thao tác cập nhật nhiều bản ghi cần tính nhất quán.
- Ghi audit event cho thao tác kiểm duyệt, thay đổi nhãn, quyền và trạng thái mô hình.

## 7. Quy trình thực hiện nhiệm vụ

Với mỗi nhiệm vụ:
1. Tóm tắt yêu cầu và tiêu chí hoàn thành.
2. Kiểm tra tài liệu và code liên quan.
3. Nêu các giả định, rủi ro và phụ thuộc.
4. Chia việc thành thay đổi nhỏ có thể review.
5. Triển khai theo đúng kiến trúc và coding standards.
6. Chạy formatter, linter, type checks và tests có liên quan nếu đã cấu hình.
7. Kiểm tra diff, secret, file thừa và thay đổi ngoài phạm vi.
8. Cập nhật tài liệu, changelog hoặc decision log khi cần.
9. Báo cáo file đã sửa, hành vi thay đổi, lệnh test đã chạy và kết quả thực tế.

Không nói test đã pass nếu chưa chạy hoặc không có output xác nhận. Nếu môi trường thiếu dependency, ghi rõ test nào chưa chạy và lý do.

## 8. Git và Pull Request

- Không commit trực tiếp lên main trừ khi chủ dự án yêu cầu rõ.
- Tạo branch ngắn gọn theo dạng feature/<ten>, fix/<ten>, docs/<ten> hoặc chore/<ten>.
- Commit theo Conventional Commits.
- Mỗi PR nên có mục tiêu, thay đổi chính, test evidence, migration/config impact và ảnh giao diện nếu có.
- Không force-push hoặc xóa branch của người khác nếu chưa được phép.

## 9. Quy tắc tài liệu

- Tài liệu kỹ thuật dùng Markdown, viết tiếng Việt rõ ràng; giữ thuật ngữ tiếng Anh phổ biến khi cần.
- Ghi trạng thái tài liệu: Draft, Proposed, Approved hoặc Deprecated.
- Ghi nguồn/giả định và ngày cập nhật cho quyết định quan trọng.
- Khi code khác tài liệu vì thay đổi được duyệt, cập nhật tài liệu trong cùng PR.
- Không đổi trạng thái Draft thành Approved thay chủ dự án.
- Duy trì liên kết tương đối giữa các tài liệu.

## 10. Những điểm chưa được tự quyết

Các nội dung sau phải được xác nhận hoặc tìm trong quyết định đã duyệt trước khi triển khai phụ thuộc:
- Tên, mô tả, mã và thứ tự chính thức của 11 danh mục.
- Framework Frontend/Backend, hệ quản trị Database và phiên bản cụ thể.
- Nhà cung cấp bản đồ/geocoding và quy tắc tọa độ.
- Cách lưu ảnh, giới hạn file, thời hạn lưu trữ và chính sách xóa.
- Cơ chế đăng nhập/quản trị viên và chính sách MFA.
- Danh sách trạng thái phản ánh và quyền chuyển trạng thái.
- Confidence threshold, cách hiệu chỉnh xác suất và quy tắc chuyển kiểm duyệt.
- Quy trình triển khai mô hình, rollback và môi trường production.
- Mục tiêu hiệu năng, availability, RPO/RTO và retention.

## 11. Definition of Done

Một chức năng chỉ được coi là hoàn thành khi:
- Đáp ứng yêu cầu và acceptance criteria được duyệt.
- Có xử lý validation, authorization, lỗi và trạng thái biên.
- Có test phù hợp và kết quả test được ghi trung thực.
- Không làm hỏng chức năng liên quan.
- Tài liệu/API/schema/migration được cập nhật đồng bộ.
- Không chứa secret hoặc dữ liệu thật trong fixture/log.
- Pull Request có mô tả và bằng chứng review được.
