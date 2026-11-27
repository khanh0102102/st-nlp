# ST-NLP — Smart Traffic & Urban Incident Classifier

ST-NLP là hệ thống hỗ trợ tiếp nhận phản ánh giao thông và hạ tầng đô thị. NLP phân loại nội dung văn bản vào đúng 11 danh mục; kết quả AI là đề xuất để cán bộ có thẩm quyền xác nhận hoặc chỉnh sửa.

## Repository baseline

- 11 danh mục theo docs/01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md.
- Database baseline chính xác 12 bảng theo docs/03_DATABASE/.
- Kiến trúc triển khai: modular monolith, React/TypeScript, FastAPI/Python và PostgreSQL.
- Phát triển/chạy local theo Docker-only; không yêu cầu runtime hoặc thư viện dự án trên host.

## Local development

Prerequisites: Git, Docker Desktop (Windows/macOS) hoặc Docker Engine + Compose plugin (Linux), và trình duyệt.

1. Clone repository.
2. Sao chép .env.example thành .env nếu cần thay đổi port hoặc thông số local.
3. Chạy:

    docker compose up --build -d

4. Mở http://localhost:8080.

Lệnh quản trị:

    docker compose ps
    docker compose logs -f
    docker compose logs -f api
    docker compose down

Cảnh báo: docker compose down -v xóa named volumes, bao gồm dữ liệu PostgreSQL, upload, model artifacts và audit local. Chỉ chạy khi chủ động muốn xóa dữ liệu local.

**Trạng thái:** Foundation hiện ở feature branch; Docker build/start chưa được xác minh. README mô tả cấu hình dự kiến, không phải bằng chứng các service đã chạy thành công.

## Cấu trúc repository

- docs/: yêu cầu, nghiệp vụ, kiến trúc, database, API, UI/UX, phát triển, kiểm thử, triển khai, AI/ML và governance.
- frontend/: React SPA và giao diện hai cổng.
- backend/: FastAPI, business modules, NLP/ML adapters.
- database/: migration, seed và sơ đồ.
- tests/: kiểm thử tích hợp/end-to-end ở cấp repository.

## Tài liệu bắt đầu

- AGENTS.md — quy tắc coding agent.
- docs/README.md — mục lục.
- docs/10_PROJECT_GOVERNANCE/REPOSITORY_AUDIT.md — audit repository.
- docs/10_PROJECT_GOVERNANCE/REQUIREMENTS_TRACEABILITY_MATRIX.md — truy vết yêu cầu.
- docs/10_PROJECT_GOVERNANCE/IMPLEMENTATION_PLAN.md — 12 giai đoạn.
- docs/10_PROJECT_GOVERNANCE/DECISION_LOG.md — quyết định kỹ thuật.
- docs/10_PROJECT_GOVERNANCE/IMPLEMENTATION_STATUS.md — tiến độ triển khai có bằng chứng.
