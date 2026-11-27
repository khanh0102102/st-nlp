# Mục lục tài liệu ST-NLP

**Dự án:** Smart Traffic & Urban Incident Classifier  
**Ngôn ngữ:** Tiếng Việt  
**Trạng thái:** Tài liệu yêu cầu và governance được quản lý theo trạng thái trong từng file.

## 00 — Tổng quan dự án

- PROJECT_OVERVIEW (00_OVERVIEW/PROJECT_OVERVIEW.md)
- PROJECT_SCOPE (00_OVERVIEW/PROJECT_SCOPE.md)
- PROJECT_ROADMAP (00_OVERVIEW/PROJECT_ROADMAP.md)

## 01 — Yêu cầu

- BRD, SRS, CLASSIFICATION_SPECIFICATION, USE_CASE, BUSINESS_PROCESS (01_REQUIREMENTS/).
- CLASSIFICATION_SPECIFICATION là nguồn chuẩn của 11 danh mục.

## 02 — Kiến trúc

- SYSTEM_ARCHITECTURE, SYSTEM_DESIGN, MODULE_DESIGN, SECURITY_DESIGN (02_ARCHITECTURE/).

## 03 — Cơ sở dữ liệu

- DATABASE_DESIGN, ERD, DATA_DICTIONARY (03_DATABASE/).
- Baseline implementation đã được migration/models/seed kiểm thử: đúng 12 bảng nghiệp vụ.

## 04 — API

- API_SPECIFICATION (04_API/API_SPECIFICATION.md).

## 05 — UI/UX

- UI_UX_SPECIFICATION (05_UI_UX/UI_UX_SPECIFICATION.md).

## 06 — Phát triển

- TECHNOLOGY_STACK, FOLDER_STRUCTURE, CODING_STANDARDS, GIT_WORKFLOW (06_DEVELOPMENT/).

## 07 — Kiểm thử

- TEST_PLAN, TEST_CASES (07_TESTING/).

## 08 — Triển khai

- DEPLOYMENT_GUIDE (08_DEPLOYMENT/DEPLOYMENT_GUIDE.md).

## 09 — AI/ML

- DATASET_SPECIFICATION (09_AI_ML/DATASET_SPECIFICATION.md).
- PREPROCESSING (09_AI_ML/PREPROCESSING.md).
- MODEL_DESIGN (09_AI_ML/MODEL_DESIGN.md).

## 10 — Governance và implementation tracking

- REPOSITORY_AUDIT, REQUIREMENTS_TRACEABILITY_MATRIX, IMPLEMENTATION_PLAN.
- DECISION_LOG, IMPLEMENTATION_STATUS.
- ADR-0001 Docker-only.
- ADR-0002 Technology Stack.
- ADR-0003 Local Integration Baseline.
- ADR-0004 AI Confidence and Audit.
- ADR-0005 ML Training Runtime Boundary.

Tài liệu đánh dấu TBD/Proposed không tự trở thành quyết định đã được phê duyệt. Mọi thay đổi ảnh hưởng nghiệp vụ, API, Database, bảo mật hoặc triển khai phải cập nhật tài liệu chuyên ngành và Requirements Traceability Matrix trong cùng Pull Request.
