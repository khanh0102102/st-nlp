# TECHNOLOGY STACK — CÔNG NGHỆ SỬ DỤNG

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Partially known / Pending confirmation |

## 1. Nguyên tắc lựa chọn

Chọn công nghệ dựa trên yêu cầu, khả năng triển khai, độ ổn định và mức độ bảo trì. Không thêm framework/library chỉ vì phổ biến. Phiên bản phải được pin trong dependency lock/config khi bắt đầu triển khai.

## 1.1. Quyết định vận hành: Docker-only trên máy cá nhân

**Yêu cầu đã thống nhất với chủ dự án:** ST-NLP phải được phát triển và chạy theo mô hình Docker-first/Docker-only. Người dùng không phải cài runtime hoặc thư viện của dự án trực tiếp trên máy cá nhân.

Máy host chỉ cần:
- Git.
- Docker Desktop trên Windows/macOS hoặc Docker Engine trên Linux.
- Docker Compose plugin.
- Trình duyệt; IDE/editor là tùy chọn.

Không yêu cầu cài Python, Node.js, npm/pnpm/yarn, database server/client, Redis, thư viện NLP/ML hoặc package manager dự án trên host.

Toàn bộ runtime, dependency và service phải được đóng gói/chạy trong container. Dockerfile cài dependency dựa trên manifest/lockfile; Docker Compose điều phối các service. Các lệnh lint, test, migration, seed, training và quản trị phải chạy qua `docker compose run/exec`.

**Trải nghiệm cuối cùng mong muốn:** sau khi clone repository, người dùng chạy `docker compose up --build -d` để build và khởi động hệ thống. Điều này là tiêu chí thiết kế và nghiệm thu, chưa phải trạng thái hiện tại vì Compose đang là placeholder.

Các credential của dịch vụ bên ngoài như Google OAuth hoặc map provider không phải thư viện cần cài trên host; nếu chức năng yêu cầu, chúng được cấu hình an toàn qua .env/secret và không commit vào Git.

## 2. Những định hướng đã xuất hiện trong quá trình phát triển

| Thành phần | Định hướng hiện có | Trạng thái |
|---|---|---|
| Backend language | Python | Đã có trong hướng triển khai trước |
| ORM | SQLAlchemy | Đã được dùng/định hướng trong thiết kế Database |
| Container | Docker Compose | Đã được dùng trong workflow phát triển trước |
| Citizen identity | Google OAuth | Yêu cầu nghiệp vụ đã thống nhất |
| NLP/ML | Naive Bayes, SVM, CNN 1D, LSTM | Nhóm mô hình nghiên cứu đã xác định |

Các mục trên cần đối chiếu với dependency/code được đưa vào repository. Chưa có cơ sở để tuyên bố phiên bản cụ thể đang được pin ở đây.

## 3. Thành phần chưa chốt

| Thành phần | Lựa chọn cần quyết định | Ghi chú |
|---|---|---|
| Frontend framework | TBD | React/Vue/Angular hoặc lựa chọn khác |
| Frontend language | TBD | TypeScript được khuyến nghị nếu phù hợp |
| Backend framework | TBD | FastAPI/Flask/Django hoặc framework đang dùng |
| Python runtime | TBD | Kiểm tra phiên bản môi trường dự án |
| Database engine | TBD | PostgreSQL được cân nhắc nếu cần geospatial/JSON và quan hệ mạnh |
| Migration | TBD | Alembic thường phù hợp với SQLAlchemy |
| Cache/Queue | TBD | Chỉ thêm khi có tác vụ async/scale |
| File storage | TBD | Local dev + object storage private ở production |
| Map provider | TBD | Cần xác minh giá, quota, geocoding và terms |
| Authentication/session | TBD | Google OIDC; session/cookie/token cần chốt |
| ML tracking/registry | TBD | Có thể bắt đầu bằng metadata DB và artifact storage |
| CI/CD | TBD | GitHub Actions là một lựa chọn |
| Hosting | TBD | Cần quyết định môi trường và ngân sách |

Không tự cài một stack hoàn chỉnh dựa trên các gợi ý trong bảng. Chủ dự án cần duyệt stack trước khi tạo cấu trúc phụ thuộc không dễ thay đổi.

## 4. NLP/ML stack

Các nhóm thư viện dự kiến cần cân nhắc:
- Xử lý dữ liệu: pandas/NumPy hoặc công cụ tương đương.
- Baseline NLP: scikit-learn cho vectorizer, Naive Bayes, SVM và calibration.
- Deep learning: PyTorch hoặc TensorFlow/Keras cho CNN 1D/LSTM.
- Tokenization tiếng Việt: chọn thư viện phù hợp dữ liệu và mô hình.
- Evaluation: scikit-learn metrics và công cụ trực quan hóa.

Thư viện và phiên bản chỉ được chốt sau khi có thử nghiệm tương thích và file lock.

## 5. Môi trường

Tất cả môi trường phải ưu tiên container hóa:
- local development: Docker Compose.
- automated test/CI: Docker image/container; không cài dependency dự án trực tiếp trên runner host ngoài Docker engine.
- staging: container image đã build và kiểm tra.
- production: container image có version/tag bất biến, secret và dữ liệu tách biệt.

Mỗi môi trường dùng cấu hình và secret riêng. Không copy database production xuống local nếu chưa ẩn danh/được phép. Không tạo hướng dẫn yêu cầu cài runtime/library dự án trên host.

## 6. Nguyên tắc dependency

- Pin phiên bản trực tiếp/gián tiếp bằng lockfile.
- Kiểm tra license và lỗ hổng bảo mật.
- Loại bỏ dependency không sử dụng.
- Tránh phụ thuộc vào API deprecated.
- Có quy trình nâng phiên bản và chạy regression tests.
- Ghi lý do khi thêm dependency lớn.

## 6.1. Quy tắc đóng gói dependency

- Backend: Dockerfile cài Python runtime và package từ requirements/pyproject lock trong image.
- Frontend: Dockerfile cài Node runtime và package từ lockfile trong image.
- Database/cache/queue/storage: dùng container image chính thức/phù hợp, pin tag phiên bản; không cài service lên host.
- NLP/ML: dependency và model runtime nằm trong image/worker image; artifact lớn lưu trong volume hoặc artifact storage, không commit Git.
- Tối ưu multi-stage build và layer cache nhưng không hy sinh khả năng tái lập.
- Dùng .dockerignore và không đưa .env, .venv, node_modules hoặc dataset riêng tư vào build context.

## 7. Cổng phê duyệt stack

Trước khi triển khai feature đầu tiên, cần chốt Frontend, Backend, DB, migration, auth/session, storage, map và test framework. Sau khi duyệt, cập nhật tài liệu này thành trạng thái Approved và pin phiên bản.
