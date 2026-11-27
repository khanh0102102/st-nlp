# IMPLEMENTATION PLAN — ST-NLP

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.2 |
| Cập nhật | 2026-11-27 |
| Trạng thái | Proposed plan, bám Master Instruction và PROJECT_ROADMAP |
| Baseline | main commit 39a937cb7474f6a8e09f2915140b7ba89c4708ac |

## 1. Nguyên tắc triển khai

- Triển khai theo dependency, không theo thứ tự tạo giao diện.
- Database/API/security contract phải ổn định trước khi module phụ thuộc tích hợp.
- Mọi runtime, dependency, migration, test và training chạy trong Docker.
- Không tự quyết định nội dung TBD về stack, workflow, credential, retention hoặc bảo mật.
- Có thể tiếp tục các tài liệu/governance/scaffold độc lập khi một phần code bị chặn.
- Mỗi giai đoạn phải có output, acceptance criteria, test evidence và Pull Request.
- Không đánh dấu VERIFIED nếu chưa có bằng chứng chạy thực tế.

## 2. Mapping theo Master Instruction

### Phase 0 — Repository Audit & Requirement Baseline
**Trạng thái:** IN_PROGRESS ở nhánh audit; audit cũ được cập nhật theo main mới.

Công việc:
- Xác minh Git tree, main, PR và thay đổi chưa merge.
- Đọc toàn bộ AGENTS/README/docs.
- Lập Repository Audit, RTM, Decision Log, Implementation Plan.
- Xác nhận 11 danh mục và 12 bảng baseline.
- Liệt kê dependencies, TBD, risk và phần có thể làm độc lập.

Acceptance:
- Audit phản ánh đúng commit/main hiện tại.
- Mọi FR/NFR trong SRS được ánh xạ tới module, API, bảng, test và status.
- Không coi Proposed/TBD là Approved.
- Không chạy/ghi nhận test khi chưa có source.

### Phase 1 — Project Foundation
**Phụ thuộc:** quyết định stack tối thiểu cho Docker service.

Công việc:
- Chốt Frontend framework/language/package manager.
- Chốt Backend framework/Python runtime.
- Chốt Database engine/version/migration tool.
- Chốt auth/session baseline, cấu hình local và provider adapter.
- Thêm Dockerfiles, .dockerignore, .env.example, Compose services, healthchecks, named volumes, networks.
- Thêm lint/test commands và CI container workflows.
- Tạo cấu trúc source theo Folder Structure đã duyệt.

Acceptance:
- Compose config hợp lệ.
- Image build thành công, healthcheck đạt.
- Máy host không cần cài runtime/dependency dự án.
- Clean clone/build/start được chứng minh.

### Phase 2 — Database Foundation
**Phụ thuộc:** Phase 1 và SQL schema decision.

Công việc:
- Tạo đúng 12 SQLAlchemy models theo DATABASE_DESIGN/ERD/Data Dictionary.
- Tạo PK/FK/check/unique/index và cross-table validations.
- Migration và seed idempotent đúng 11 categories.
- Tạo fixtures/factories không chứa dữ liệu cá nhân.
- Kiểm tra migration DB rỗng và đường nâng cấp.

Acceptance:
- Có đúng 12 bảng business baseline, không sinh bảng thứ 13 trái phép.
- Seed có đủ 11 category code/name/sort order.
- DB integrity, upgrade/downgrade hoặc rollback guidance được kiểm thử trong container.

### Phase 3 — Backend Core
**Phụ thuộc:** Phase 2 và API/auth contract.

Công việc:
- App config, health/readiness, error envelope, request ID.
- Google OAuth Citizen.
- Staff authentication/provisioning theo quyết định.
- Authorization/policy/owner scope.
- SQLAlchemy repositories/application services.
- Upload/storage adapter và audit sink abstraction.
- API versioning, OpenAPI và API tests.

Acceptance:
- Protected endpoint enforce permission tại Backend.
- Citizen không đọc tài nguyên người khác.
- Không lộ secret/PII qua log.
- Migration, API tests và healthcheck chạy trong Docker.

### Phase 4 — Citizen Portal
**Phụ thuộc:** Backend Core, file storage policy, map/CRS adapter.

Công việc:
- Citizen login/profile.
- Report create form và validation.
- Image preview/remove/replace/upload.
- Location picker và tọa độ xác nhận.
- Report list/detail/history.
- AI result/status presentation theo quyền.

Acceptance:
- Preview hoạt động trước submit.
- Upload server-side validation.
- User A không thể xem report User B.
- E2E submit/list/detail chạy với test data.

### Phase 5 — NLP & Machine Learning
**Phụ thuộc:** Phase 2, label schema, dataset hợp lệ và preprocessing contract.

Công việc:
- Versioned Vietnamese text preprocessing (Unicode NFC, tokenizer, stopword config).
- Naive Bayes/SVM baseline.
- CNN 1D/LSTM theo điều kiện dataset và tài nguyên.
- Evaluation metrics/confidence semantics.
- Prediction persistence, model version, failure/retry handling.

Acceptance:
- Prediction chỉ trả 11 category code hoặc status không thể dự đoán.
- Training/inference dùng đúng preprocessing và label schema version.
- Không làm mất report khi inference lỗi.
- Metrics thật chỉ được báo cáo khi dùng Dataset hợp lệ và test set độc lập.

### Phase 6 — Admin Portal
**Phụ thuộc:** Backend Core, Prediction, Review và workflow status approved.

Công việc:
- Staff login/permission route.
- Report list/search/filter/detail.
- Prediction/confidence display.
- Confirm/correct review.
- Review history, notes và audit.
- Report state transition.

Acceptance:
- Prediction gốc không bị ghi đè.
- Review actor/time/previous/selected labels lưu đúng.
- Concurrency/permission tests đạt.

### Phase 7 — Dashboard & Map
**Phụ thuộc:** report/review/category/location schema và map provider.

Công việc:
- KPI/summary.
- Aggregates theo 11 categories/status/time.
- Shared filter semantics.
- Marker/cluster/detail navigation.
- Pagination, query optimization và privacy-safe map payload.

Acceptance:
- Dashboard đủ 11 nhóm, kể cả count 0.
- Tổng số liệu khớp dữ liệu nguồn.
- Chart/list/map filters nhất quán.
- Không rò rỉ PII/địa chỉ trái quyền.

### Phase 8 — AI & Data Management
**Phụ thuộc:** Dataset source/policy, Database, authorization và ML services.

Công việc:
- Dataset CRUD/versioning.
- Dataset sample import/edit/label/validation.
- Provenance, duplicate/leakage checks, freeze.
- Training run worker/orchestration.
- Metrics/artifact tracking.
- Model registry, compare, approve, activate/rollback.

Acceptance:
- Training run tham chiếu đúng dataset version/config/code version.
- Dataset FROZEN bất biến.
- Model artifact có checksum và preprocessing/label version.
- Model chưa được duyệt không thể active.

### Phase 9 — System Integration
**Phụ thuộc:** các module chính.

Công việc:
- Kết nối Citizen → Report → Preprocess → Prediction → Review.
- Nối Dataset → Training → Metrics → Model Version → Inference.
- Kiểm tra authorization xuyên portal/API.
- Kiểm tra transaction, retry, storage cleanup và audit delivery.

Acceptance:
- Luồng nghiệp vụ xuyên module chạy trên Docker compose test environment.
- Không còn contract drift giữa Frontend/Backend/DB/ML.

### Phase 10 — Testing & Quality Assurance
**Phụ thuộc:** integration baseline.

Công việc:
- Unit/API/integration/E2E/ML evaluation/security/performance tests.
- Regression tests.
- Accessibility/responsive test.
- Migration test, data integrity, backup/restore.
- Clean-environment Docker test.
- Triage và sửa lỗi.

Acceptance:
- Tất cả Must requirements có test evidence.
- Không có Critical/High unresolved.
- NFR target do chủ dự án duyệt được đo và đạt.
- Không ghi VERIFIED khi thiếu evidence.

### Phase 11 — Deployment & Documentation
**Phụ thuộc:** QA exit criteria và deployment decisions.

Công việc:
- Finalize Docker Compose, env/secrets, healthchecks, volumes, reverse proxy/TLS nếu dùng.
- Deployment guide, user/admin guide, backup/restore, monitoring.
- Release notes, known issues, rollback plan.
- Staging smoke test; production chỉ khi được chủ dự án cho phép.

Acceptance:
- Clone + Docker Compose startup trên môi trường sạch.
- Không yêu cầu cài runtime/library dự án trên host.
- Documentation và source thống nhất.
- Chưa deploy production nếu chưa có yêu cầu/phê duyệt riêng.

## 3. Blockers đầu vào ưu tiên

| ID | Cần chốt | Blocked phases |
|---|---|---|
| B-01 | Frontend framework/language/package manager | 1, 4, 6, 7, 8 |
| B-02 | Backend framework/Python runtime/version | 1–11 |
| B-03 | DB engine/version, SQL types, migration tool | 1–3 |
| B-04 | Staff authentication, MFA, account provisioning | 3, 6, 8 |
| B-05 | Report status state machine and transition policy | 3, 6, 7 |
| B-06 | File storage, upload limits, retention/deletion | 1, 3, 4 |
| B-07 | Map/geocoding provider, CRS/SRID, location privacy | 1, 4, 7 |
| B-08 | Dataset file/source, license, privacy and labeling approval | 5, 8, 10 |
| B-09 | Confidence semantics/threshold and model acceptance criteria | 5, 6, 10 |
| B-10 | Audit sink provider, durability, retention and access policy | 3, 6, 8, 10, 11 |
| B-11 | Performance/load, availability, RPO/RTO and retention targets | 10, 11 |

Không yêu cầu giải quyết mọi blocker cùng lúc. Ưu tiên B-01..B-07 để hoàn thiện foundation; B-08..B-11 có thể chốt theo dependency trước module liên quan.

## 4. Công việc độc lập có thể làm ngay

- Repository audit, RTM, decision log, backlog.
- .dockerignore và repository hygiene không phụ thuộc framework.
- Test inventory coverage và missing test IDs.
- ADR cho quyết định đã được chủ dự án chấp thuận.
- Dọn các tài liệu có nội dung TBD đã được thay thế.
- Không tạo Dockerfile/Compose service, SQL migration hoặc dependency lock trước khi stack được duyệt.

## 5. Theo dõi tiến độ và bằng chứng

Mỗi work package phải cập nhật:
- Requirement IDs.
- Owner/agent.
- Dependencies/blocker.
- Files/module thay đổi.
- API và Database liên quan.
- Branch/commit/PR.
- Docker commands đã chạy.
- Test cases và kết quả thực tế.
- Link evidence/CI run.
- Còn thiếu gì.

Trạng thái toàn dự án chỉ phản ánh kết quả đã quan sát; không ước lượng completion theo số file hoặc số dòng code.
