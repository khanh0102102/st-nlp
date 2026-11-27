# REQUIREMENTS TRACEABILITY MATRIX — ST-NLP

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.1 |
| Ngày lập | 2026-11-27 |
| Trạng thái | Initial mapping — implementation chưa bắt đầu |
| Nguồn yêu cầu chính | docs/01_REQUIREMENTS/SRS.md |

## 1. Quy ước

- **Requirement IDs** là các mã trong SRS.
- **Module** là vùng chức năng chịu trách nhiệm chính.
- **API** tham chiếu nhóm endpoint dự kiến trong API Specification; chưa phải endpoint đã triển khai.
- **Data domain** là miền dữ liệu logic; chưa khẳng định tên bảng vật lý.
- **Test IDs** tham chiếu Test Cases; chưa có kết quả thực thi.
- **Status**: NOT_STARTED cho các chức năng vì chưa có source code.

## 2. Ma trận truy vết

| Requirement IDs | Mô tả phạm vi | Module | API dự kiến | Data domain logic | Test cases | Trạng thái |
|---|---|---|---|---|---|---|
| FR-AUTH-01..04 | Citizen Google OAuth, identity, logout | Identity & Auth | /auth/* | User/Identity, Session | TC-AUTH-001..004, 008 | NOT_STARTED |
| FR-AUTH-05..07 | Admin portal entry, staff authentication, backend authz | Identity & Authorization | /auth/*, Admin APIs | User/Role/Permission | TC-AUTH-005, 007 | NOT_STARTED |
| FR-CIT-01..03 | Citizen profile, Google identity mapping | Citizen Profile | /citizen/profile | User/Identity | TC-AUTH-001..004 | NOT_STARTED |
| FR-INC-01..02 | Tạo report và validate description | Incident | POST /citizen/reports | Incident | TC-INC-001..003 | NOT_STARTED |
| FR-INC-03..06 | Upload, preview, remove/replace và validate ảnh | Attachment + Citizen UI | Attachment/upload endpoints TBD | Attachment/Storage | TC-INC-004..009 | NOT_STARTED |
| FR-INC-07..08 | Chọn vị trí và lưu report/location | Location + Incident | POST /citizen/reports | Incident/Location | TC-INC-010 | NOT_STARTED |
| FR-INC-09..11 | Citizen list/detail/result ownership | Citizen Portal + Incident | GET /citizen/reports/* | Incident/Prediction/Review | TC-INC-012, TC-AUTH-006 | NOT_STARTED |
| FR-AI-01..08 | Preprocessing, prediction, score, version, failure handling | NLP Pipeline + Prediction | Internal inference contract; prediction read API | Prediction/Category/Model Version | TC-AI-001..009 | NOT_STARTED |
| FR-ADM-01..02 | Admin report list/detail/filter | Admin Portal + Incident | GET /admin/reports* | Incident/Attachment/Location | TC-ADM-001..002 | NOT_STARTED |
| FR-ADM-03..06 | Confirm/correct label, preserve original prediction, review history | Review | POST/GET /admin/reports/{id}/reviews | Prediction/Review/Category/Audit | TC-REV-001..006 | NOT_STARTED |
| FR-ADM-07..08 | Valid report state transition and review history | Workflow + Review | PATCH status, GET reviews | Incident/Review/Audit | TC-REV-006..007 | BLOCKED by BLOCK-06 |
| FR-DASH-01..03 | Aggregate dashboard and category/time/status filters | Dashboard | GET /admin/dashboard/* | Incident/Category/Review | TC-DASH-001..003 | NOT_STARTED |
| FR-DASH-04..06 | Map markers/clusters, privacy and detail navigation | Map + Location | GET /admin/map/reports | Incident/Location | TC-MAP-001..003 | BLOCKED by BLOCK-09 for provider integration |
| FR-DATA-01..02 | Dataset and dataset version/sample relationship | Dataset | /admin/datasets* | Dataset/Dataset Version/Dataset Sample | TC-DATA-001..002 | BLOCKED by BLOCK-01, BLOCK-10 |
| FR-DATA-03..05 | Sample editing, validation, provenance and labeling status | Dataset Sample + Validation | /admin/dataset-samples*, validate endpoint | Dataset Sample/Category/Provenance | TC-DATA-003..004 | BLOCKED by BLOCK-01, BLOCK-10 |
| FR-DATA-06 | Train/validation/test split and leakage prevention | Dataset Validation | Dataset validate/version endpoints | Dataset Version/Sample/Split | TC-DATA-005..006 | NOT_STARTED |
| FR-ML-01..02 | Create Training Run and lifecycle state | Training | POST/GET /admin/training-runs | Dataset Version/Training Run | TC-TRAIN-001, 003 | NOT_STARTED |
| FR-ML-03..05 | Metrics, artifacts and run comparison | Evaluation/Metrics | GET /training-runs/{id}/metrics | Training Run/Training Metric | TC-TRAIN-002, 004 | BLOCKED by BLOCK-10 for real evaluation |
| FR-ML-06..07 | Model registration, approval, activation and rollback | Model Registry | /admin/models* | Model Version/Training Run/Audit | TC-MODEL-001..003 | NOT_STARTED |
| FR-AUD-01..03 | Audit security/business actions and restrict access | Audit + Security | Internal/audit read API TBD | Audit Event/User | TC-SEC-004 and review/admin tests | NOT_STARTED |
| NFR-SEC-01..04 | Authz, secret, upload and privacy protections | Security | All protected APIs | Identity/Incident/Attachment | TC-AUTH, TC-INC, TC-SEC | NOT_STARTED |
| NFR-REL-01 | AI failure must not lose saved report | Incident + Prediction | Report/prediction APIs | Incident/Prediction | TC-AI-005..006, TC-REL-001 | NOT_STARTED |
| NFR-DATA-01, NFR-AUD-01 | Data integrity and traceability | Database + Audit | All write APIs | All relevant domains | DB/integration tests to add | NOT_STARTED |
| NFR-PERF-01..02 | API/dashboard/map performance and pagination | API + Dashboard + Map | List/dashboard/map APIs | Incident/Location | TC-PERF-001 | BLOCKED by BLOCK-12 |
| NFR-USE-01..02 | Vietnamese UX, responsive and UI states | Frontend Shared UI | N/A | N/A | E2E/accessibility tests to add | NOT_STARTED |
| NFR-MNT-01, NFR-PORT-01 | Maintainability and configurable deployments | All modules + DevOps | N/A | N/A | CI/container tests to add | NOT_STARTED |
| NFR-BACKUP-01 | Backup/restore and recovery | DevOps + Database | Operational | DB/Storage | Restore test to add | BLOCKED by BLOCK-12 |
| NFR-OBS-01 | Structured logs, correlation ID, health/metrics | Platform/Observability | Health/metrics endpoints TBD | Logs/metrics | Health/observability tests to add | NOT_STARTED |

## 3. Quy tắc quản lý coverage

1. Mọi FR/NFR phải có ít nhất một module owner.
2. Mỗi FR cần ít nhất một test case; nếu chưa có, tạo test ID mới trong TEST_CASES.md.
3. Khi API được chốt, thay endpoint group bằng method + path cụ thể.
4. Khi physical schema được duyệt, thay data domain bằng table/column thật.
5. Khi implementation bắt đầu, cập nhật status và liên kết PR/commit.
6. Không đổi status thành TESTED/VERIFIED nếu thiếu test evidence.
7. Requirement thay đổi phải được ghi version và impact analysis.

## 4. Các trạng thái

- NOT_STARTED: chưa có code triển khai.
- IN_PROGRESS: đang thực hiện.
- BLOCKED: không thể triển khai đầy đủ vì thiếu quyết định/phụ thuộc.
- IMPLEMENTED: code đã được viết, chưa đồng nghĩa test pass.
- TESTED: test liên quan đã chạy và đạt.
- VERIFIED: đã review acceptance criteria và có bằng chứng nghiệm thu.

## 5. Coverage baseline

Tại thời điểm lập ma trận:
- Requirements được định danh trong SRS: đã ánh xạ ở mức module/API/data/test group.
- Source implementation: chưa có.
- Test execution evidence: chưa có.
- Verified requirements: 0.
