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
- Hệ thống phân loại văn bản vào đúng 11 nhóm tại docs/01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md; đây là nguồn chuẩn về tên/thứ tự/mã. Không tự đặt, thêm, bỏ hoặc đổi category.
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
- Ranh giới nghiệp vụ chi tiết giữa các danh mục giao nhau, guideline gán nhãn và các thay đổi label schema trong tương lai.
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


## 12. CHÍNH SÁCH DOCKER-ONLY — BẮT BUỘC

Mục tiêu trải nghiệm của ST-NLP là: người phát triển clone repository, cài Docker Desktop (Windows/macOS) hoặc Docker Engine + Compose plugin (Linux), sau đó dùng Docker Compose để build và chạy toàn bộ hệ thống. Không yêu cầu cài runtime hoặc thư viện của dự án trực tiếp trên máy cá nhân.

### 12.1. Những gì được phép cài trên máy host

- Git để clone/push repository.
- Docker Desktop hoặc Docker Engine.
- Docker Compose plugin (thường đi kèm Docker Desktop).
- Trình duyệt web.
- IDE/editor là tùy chọn.

Không yêu cầu cài Python, Node.js, npm/pnpm/yarn, Java, PostgreSQL/MySQL, Redis, thư viện NLP/ML, compiler hoặc package manager của dự án trên host.

### 12.2. Quy tắc bắt buộc khi phát triển

- Mọi runtime và dependency của Frontend, Backend, Worker, NLP/ML phải được cài trong Docker image qua Dockerfile.
- Dependency phải được khai báo và pin phiên bản bằng manifest/lockfile trong repository.
- Mọi dịch vụ cần để chạy hệ thống local phải được mô tả trong docker-compose.yml (hoặc file Compose override được tài liệu hóa).
- Database, cache/queue, local object storage và worker phải chạy bằng container khi được sử dụng.
- Mọi lệnh migration, seed, lint, type-check, test, training và script quản trị phải được thực thi qua `docker compose run` hoặc `docker compose exec`, không chạy trực tiếp bằng runtime trên host.
- Có thể bind-mount source code để hot reload, nhưng không bind-mount thư mục dependency của host như node_modules, .venv hoặc site-packages vào container.
- Dùng named volumes cho dữ liệu bền vững như database và model/artifact cần giữ.
- Dùng .dockerignore để loại bỏ cache, môi trường ảo, secret, node_modules, dữ liệu upload và artifact không cần thiết khỏi build context.
- Không yêu cầu người dùng chạy pip install, npm install, yarn, pnpm install, poetry install hoặc cài thư viện dự án trực tiếp trên host.
- Không tạo hướng dẫn chạy Backend/Frontend bằng lệnh host như `python main.py`, `uvicorn ...`, `npm run dev` hoặc `npm start` như quy trình mặc định. Nếu cần dùng các lệnh này, phải chạy chúng bên trong container.
- Nếu một công cụ chỉ hỗ trợ chạy trên host, trước tiên tìm cách chạy trong container; mọi ngoại lệ phải được nêu rõ và được chủ dự án chấp thuận.

### 12.3. Trải nghiệm khởi chạy mục tiêu

Khi hệ thống hoàn thiện, trên máy mới chỉ cần:
1. Cài Git và Docker Desktop/Engine + Compose.
2. Clone repository.
3. Chạy `docker compose up --build -d`.

Mục tiêu là không cần cài thư viện/runtime/database riêng trên host. Các cấu hình bí mật từ nhà cung cấp bên ngoài (ví dụ Google OAuth hoặc dịch vụ bản đồ nếu bắt buộc) vẫn phải được cung cấp qua file .env hoặc secret mechanism; không được hard-code hay commit secret.

### 12.4. Thiết kế Compose để khởi chạy đơn giản

- Cung cấp .env.example với các giá trị local an toàn; không chứa secret thật.
- Cố gắng để các chức năng local không cần secret bên ngoài vẫn khởi động được.
- Nếu cần OAuth thật, tài liệu phải chỉ rõ credential Google cần cấu hình. Có thể cung cấp chế độ mock/development auth riêng cho local test nếu được thiết kế an toàn; tuyệt đối không cho phép chế độ này ở staging/production.
- Dùng healthcheck và depends_on condition phù hợp để service khởi động đúng thứ tự.
- Migration/seed local phải tự động hoặc có lệnh Docker Compose duy nhất được chỉ rõ; migration phải an toàn và không phá dữ liệu.
- Compose phải có named volumes cho database và dữ liệu cần giữ.
- Cung cấp lệnh xem log, dừng, chạy test và reset dữ liệu; cảnh báo rõ lệnh xóa volume.
- Không tuyên bố one-command startup hoạt động cho đến khi đã kiểm tra trên môi trường sạch.

### 12.5. Kiểm thử và Definition of Done bổ sung

Một thay đổi chỉ đạt khi:
- Build Docker image thành công.
- Các service khởi động theo Compose.
- Healthcheck đạt.
- Migration hoạt động trong container.
- Test liên quan chạy được bên trong container.
- Hướng dẫn không yêu cầu cài runtime/library dự án trên host.
- Đã thử quy trình trên môi trường sạch hoặc CI container.

Khi báo cáo, phải ghi rõ lệnh Docker đã chạy và kết quả thực tế.


## 13. Baseline danh mục và Database được cung cấp bởi chủ dự án

- Danh mục chính thức gồm đúng 11 tên và thứ tự trong docs/01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md. category_code trong tài liệu là mã kỹ thuật ổn định dùng thống nhất; không hard-code catalog khác ở module khác.
- Database baseline có đúng 12 bảng: users, incident_categories, reports, report_attachments, preprocessing_runs, model_versions, predictions, prediction_reviews, datasets, dataset_samples, training_runs, training_metrics. Nguồn schema: docs/03_DATABASE/DATABASE_DESIGN.md, ERD.md và DATA_DICTIONARY.md.
- users bao gồm CITIZEN, RECEIVER, ADMIN; permission kiểm tra server-side. Không tự tạo roles/permissions table trong baseline.
- reports.raw_content bất biến; reports.final_category_id là nhãn cán bộ xác nhận; predictions giữ nhãn AI; prediction_reviews append-only.
- Mỗi row datasets là một version bất biến khi FROZEN. Không tạo bảng dataset_versions riêng.
- Không thêm audit_logs vào schema 12 bảng. Audit tổng quát phải đi qua audit sink append-only ngoài DB; provider/retention cần được chốt trước production.
- Đây là thiết kế tài liệu; chỉ coi schema triển khai khi có SQLAlchemy models, migration, seed và test Docker thực tế.
