# TECHNOLOGY STACK — CÔNG NGHỆ SỬ DỤNG

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Partially known / Pending confirmation |

## 1. Nguyên tắc lựa chọn

Chọn công nghệ dựa trên yêu cầu, khả năng triển khai, kinh nghiệm đội ngũ, độ ổn định và mức độ bảo trì. Không thêm framework/library chỉ vì phổ biến. Phiên bản phải được pin trong dependency lock/config khi bắt đầu triển khai.

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

Nên tách:
- local development.
- automated test/CI.
- staging.
- production.

Mỗi môi trường dùng cấu hình và secret riêng. Không copy database production xuống local nếu chưa ẩn danh/được phép.

## 6. Nguyên tắc dependency

- Pin phiên bản trực tiếp/gián tiếp bằng lockfile.
- Kiểm tra license và lỗ hổng bảo mật.
- Loại bỏ dependency không sử dụng.
- Tránh phụ thuộc vào API deprecated.
- Có quy trình nâng phiên bản và chạy regression tests.
- Ghi lý do khi thêm dependency lớn.

## 7. Cổng phê duyệt stack

Trước khi triển khai feature đầu tiên, cần chốt Frontend, Backend, DB, migration, auth/session, storage, map và test framework. Sau khi duyệt, cập nhật tài liệu này thành trạng thái Approved và pin phiên bản.
