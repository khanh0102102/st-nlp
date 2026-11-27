# IMPLEMENTATION PLAN — ST-NLP

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.1 |
| Ngày lập | 2026-11-27 |
| Trạng thái | Proposed plan dựa trên Repository Audit |
| Branch audit | chore/repository-audit |

## 1. Chiến lược

Triển khai theo dependency và contract; ưu tiên nền tảng có thể tái sử dụng, sau đó hoàn thiện các luồng nghiệp vụ từ người dân đến AI và cán bộ. Không triển khai song song những module chưa có schema/API/permission thống nhất.

Tất cả bước phát triển, migration, lint, test và training phải chạy trong container theo AGENTS.md.

## 2. Work packages

### WP-00 — Chốt đầu vào và quyết định nền tảng

**Cần hoàn tất trước các module phụ thuộc**
- Xác nhận 11 category codes, tên và labeling guideline.
- Xác nhận physical DB schema/12 bảng hiện hành nếu đây là baseline được chủ dự án giữ.
- Chọn Frontend framework/language/package manager.
- Chọn Backend framework/Python runtime.
- Chọn PostgreSQL/DB engine và migration tool.
- Chọn cách xác thực/cấp tài khoản cán bộ.
- Chọn storage và map provider hoặc phê duyệt adapter contract.
- Chốt workflow trạng thái và permission matrix.

**Đầu ra:** ADR được duyệt, tài liệu cập nhật, API/Data contracts đủ triển khai.

### WP-01 — Docker & Repository Foundation

**Phụ thuộc:** WP-00 tối thiểu cho stack.

- Thêm .dockerignore và .env.example.
- Tạo Dockerfile Frontend/Backend/Worker theo stack.
- Tạo Compose services cho portal/API/database và service phụ trợ đã chọn.
- Pin image tags và dependency lockfiles.
- Healthchecks, named volumes, networks và config.
- Chuẩn hóa entrypoint, graceful shutdown và startup ordering.
- Tạo containerized lint/test commands.
- Xác nhận clean clone/build startup.

**Acceptance:** chỉ cần host Git + Docker; Compose config hợp lệ; containers healthy; không cần cài runtime/dependency lên host.

### WP-02 — Database Foundation

**Phụ thuộc:** physical schema được duyệt, WP-00 và WP-01.

- SQLAlchemy models và relationships.
- Constraints, indexes và ownership fields.
- Alembic migrations hoặc migration tool đã duyệt.
- Seed category/roles theo dữ liệu chính thức.
- Test DB rỗng, migration upgrade và integrity.
- Không tạo bảng dựa trên logical concept khi chưa duyệt schema.

**Acceptance:** DB mới có thể dựng hoàn toàn từ migrations/seed trong container; constraints và test đạt.

### WP-03 — Backend Core & Security

**Phụ thuộc:** WP-02, auth policy, API contracts.

- App config, API versioning, health/readiness.
- Google OAuth Citizen.
- Staff auth/provisioning theo quyết định được duyệt.
- RBAC, owner-scope policy.
- Validation, error envelope, logging, audit.
- Repository/service/use-case boundaries.
- API contract/OpenAPI và tests.

**Acceptance:** protected APIs enforce permission; ownership/IDOR tests đạt; API schemas được sinh/kiểm chứng.

### WP-04 — Citizen Portal

**Phụ thuộc:** WP-03, file storage contract, map provider/adapter.

- Citizen auth and profile.
- Create report.
- Image preview/remove/replace/upload.
- Location picker.
- Report list/detail/history.
- Prediction result and allowed status display.

**Acceptance:** user A không thể truy cập dữ liệu user B; preview trước submit; upload được server validate; E2E submit/list/detail đạt.

### WP-05 — NLP Inference Baseline

**Phụ thuộc:** WP-00 label schema/dataset; WP-02 model/prediction schema; preprocessing contract.

- Versioned Vietnamese preprocessing.
- Naive Bayes/SVM baseline trước.
- CNN 1D/LSTM theo experiment.
- Training/inference contract.
- Prediction persistence, confidence semantics, model version.
- Failure handling không ảnh hưởng report đã lưu.

**Acceptance:** output đúng label mapping; model/pipeline version truy vết; evaluation chỉ dùng dataset hợp lệ; không giả lập metrics thật.

### WP-06 — Admin Review & Workflow

**Phụ thuộc:** WP-03, WP-02, label catalog và state machine.

- Admin route/layout/authz.
- Report list/detail/filter.
- Prediction display.
- Confirm/correct review.
- Review history/audit.
- Valid status transitions.

**Acceptance:** prediction gốc không bị ghi đè; review actor/time/before-after được lưu; permission và concurrency tests đạt.

### WP-07 — Dashboard & Map

**Phụ thuộc:** report/review/category/location schema và provider.

- KPI summary.
- Category/status/time aggregates.
- Shared filters.
- Map marker/cluster and detail navigation.
- Privacy-safe map payload and pagination/performance.

**Acceptance:** số liệu đối chiếu dữ liệu nguồn; list/chart/map filter nhất quán; map không lộ PII trái quyền.

### WP-08 — AI & Data Management

**Phụ thuộc:** category schema, dataset source and policy, WP-02/03.

- Dataset/sample CRUD/import.
- Validation, provenance, version freeze.
- Leakage/duplicate checks.
- Training Run orchestration.
- Metrics/artifact tracking.
- Model Registry, approval, activate/rollback.

**Acceptance:** training run gắn immutable dataset version/config/artifact/metrics; chỉ model được phép mới active.

### WP-09 — Integration, QA & Deployment

**Phụ thuộc:** các module chính.

- Unit/API/integration/E2E/security/performance tests.
- End-to-end workflows.
- Docker clean-environment test.
- Backup/restore, logs/monitoring.
- README, deployment/user/admin documentation.
- Release candidate and known-issues report.

**Acceptance:** các requirement Must có test evidence; các ngưỡng NFR đã được duyệt; Compose run và smoke test thành công trên môi trường sạch.

## 3. Có thể làm song song

Sau khi contract được chốt:
- UI wireframes và Backend API skeleton có thể song song.
- Dataset tooling và model experiments có thể song song nếu label schema/version đã cố định.
- Citizen UI và Admin UI có thể song song khi API contracts và shared auth rules ổn định.
- Dashboard frontend/backend có thể song song khi metric definitions và filter semantics được chốt.

Không song song hóa hai nhóm cùng sửa schema/API mà chưa có owner/coordination.

## 4. Thứ tự ưu tiên đề xuất

1. WP-00 — Chốt đầu vào tối thiểu.
2. WP-01 — Docker/Project Foundation.
3. WP-02 — Database.
4. WP-03 — Backend Core/Security.
5. WP-04 — Citizen Portal.
6. WP-05 — NLP Inference baseline.
7. WP-06 — Review workflow.
8. WP-07 — Dashboard/Map.
9. WP-08 — AI/Data Management.
10. WP-09 — Integration/QA/Deployment.

## 5. Quy tắc theo dõi

Mỗi work package cần:
- Owner/agent.
- Requirement IDs.
- Dependencies.
- Acceptance criteria.
- Branch/PR.
- Files/modules changed.
- Docker commands executed.
- Test results and evidence.
- Documentation updated.
- Remaining blockers.

Không có thời gian hoàn thành được ấn định trong plan này; tiến độ phải được cập nhật dựa trên kết quả thực tế.
