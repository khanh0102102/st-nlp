# ST-NLP — Smart Traffic & Urban Incident Classifier

ST-NLP là hệ thống hỗ trợ tiếp nhận phản ánh giao thông và hạ tầng đô thị. NLP được thiết kế để phân loại nội dung văn bản vào đúng 11 danh mục; kết quả AI chỉ là đề xuất, cán bộ có thẩm quyền mới xác nhận nhãn cuối cùng.

## Trạng thái repository

- Branch đang chứa implementation đã kiểm thử: feature/project-foundation.
- main chưa được cập nhật các commit triển khai này; không dùng lệnh clone mặc định nếu cần lấy phiên bản đang phát triển.
- CI run #17 đã xác minh Docker build, PostgreSQL migration/seed, 37 backend tests, 8 neural tests trong CPU image, DB-backed NB/SVM training integration, trainer CLI smoke test và health checks.
- Đây là local development foundation, chưa phải release hoàn chỉnh hoặc production-ready.

## Local development (Docker-only)

Prerequisites trên máy host: Git, Docker Desktop (Windows/macOS) hoặc Docker Engine + Docker Compose plugin (Linux), và trình duyệt. Không cần cài Python, Node.js, npm, pip, PostgreSQL hoặc thư viện NLP/ML trên host.

Lấy đúng branch đã triển khai:

    git clone --branch feature/project-foundation --single-branch https://github.com/khanh0102102/st-nlp.git
    cd st-nlp
    docker compose up --build -d

Mở http://localhost:8080.

Các cấu hình local mặc định đủ để chạy stack cơ bản. Sao chép .env.example thành .env khi muốn tùy chỉnh biến môi trường hoặc cấu hình Google OAuth. Đăng nhập Google thật cần OAuth client credentials và redirect URI hợp lệ; CI không kiểm thử tài khoản Google thật.

Lệnh quản trị:

    docker compose ps
    docker compose logs -f
    docker compose logs -f api
    docker compose down

Cảnh báo: docker compose down -v xóa named volumes, bao gồm PostgreSQL, uploads, model artifacts và audit local. Chỉ dùng khi chủ động muốn xóa dữ liệu.

## Docker profiles

- Mặc định: PostgreSQL, FastAPI và frontend/Nginx.
- Profile test: backend/API tests và CPU neural tests.
- Profile training: image CLI huấn luyện riêng; không cài dependency ML nặng vào API runtime.

Huấn luyện yêu cầu dataset đã đóng băng, đủ TRAIN/VALIDATION/TEST và TRAIN có đủ 11 danh mục. CI đã chạy NB/SVM training integration trên dataset tổng hợp trong PostgreSQL và xác minh TrainingRun, 120 TrainingMetric rows, ModelVersion, checksum và artifact reload; chưa chứng minh chất lượng mô hình trên dataset thật. Xem Deployment Guide.

## Phạm vi hiện tại và giới hạn

- Database implementation giữ đúng 12 bảng nghiệp vụ và seed đúng 11 danh mục.
- Backend có nền tảng auth, reports, review, dashboard, dataset và model-registry APIs; các luồng nghiệp vụ vẫn đang được hoàn thiện.
- NLP/ML core đã có Vietnamese preprocessing, metrics, TF-IDF + Naive Bayes/Linear SVM, CNN 1D và BiLSTM components.
- Chưa có inference service được xác thực để nạp active model và xử lý prediction end-to-end. Khi chưa có model, hệ thống không tự tạo nhãn AI giả.
- Frontend hiện là trang foundation/status; Citizen Portal, Admin Portal, bản đồ và dashboard vận hành hoàn chỉnh chưa được triển khai.

## Cấu trúc repository

- docs/: yêu cầu, nghiệp vụ, kiến trúc, database, API, UI/UX, phát triển, kiểm thử, triển khai, AI/ML và governance.
- backend/: FastAPI, SQLAlchemy, Alembic, APIs và NLP/ML modules.
- frontend/: React/Vite SPA được phục vụ qua Nginx.
- docker-compose.yml: local application, test và training profiles.

## Tài liệu bắt đầu

- AGENTS.md — quy tắc coding agent.
- docs/README.md — mục lục.
- Repository Audit, Requirements Traceability Matrix, Implementation Plan, Decision Log và Implementation Status trong docs/10_PROJECT_GOVERNANCE/.

## API foundation hiện có

- Catalog: GET /api/v1/categories.
- Citizen profile/reports: /api/v1/citizen/profile, /api/v1/citizen/reports.
- Attachments: /api/v1/attachments và report-scoped download routes.
- Staff review/history/status transitions: /api/v1/admin/reports.
- Dashboard/map: /api/v1/admin/dashboard/*, /api/v1/admin/map/reports.
- Auth: /api/v1/auth/staff/login, Google OIDC start/callback, session, CSRF và logout.
- Dataset/model registry foundations: /api/v1/admin/datasets, /api/v1/admin/models.

Xem API Specification. Các endpoint tồn tại trong code chưa đồng nghĩa toàn bộ workflow và frontend đã được nghiệm thu. External Google OAuth chưa được thử bằng credentials thật; inference chưa hoàn chỉnh, nên không tạo prediction category/confidence giả.
