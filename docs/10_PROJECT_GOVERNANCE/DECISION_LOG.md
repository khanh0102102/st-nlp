# DECISION LOG — ST-NLP

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.4 |
| Cập nhật | 2026-11-28 |
| Mục đích | Ghi nhận baseline, lựa chọn được ủy quyền và các mục còn mở |

## 1. Baseline đã được xác lập

| ID | Chủ đề | Quyết định/baseline | Nguồn | Trạng thái |
|---|---|---|---|---|
| DEC-001 | Local development | Docker-only; host chỉ cần Git, Docker/Compose và trình duyệt | AGENTS.md, Master Prompt | ACCEPTED |
| DEC-002 | Category catalog | Chính xác 11 danh mục và category_code theo CLASSIFICATION_SPECIFICATION.md | Chủ dự án | BASELINE ACCEPTED |
| DEC-003 | Database table set | Đúng 12 bảng; không tự thêm roles/permissions/dataset_versions/audit_logs | Chủ dự án | BASELINE ACCEPTED |
| DEC-004 | Prediction vs review | AI prediction lưu riêng; prediction_reviews append-only; reports.final_category_id là nhãn cuối cùng | SRS/Database design | BASELINE ACCEPTED |
| DEC-005 | Dataset version | Mỗi hàng datasets đại diện một version; FROZEN bất biến | Database design | BASELINE ACCEPTED |
| DEC-006 | AI scope | Text classification; ảnh chỉ là minh chứng trong baseline, không tự thêm Computer Vision | Project scope | ACCEPTED |

## 2. Quyết định triển khai được ủy quyền qua Master Prompt

Các lựa chọn dưới đây được chốt để bắt đầu local implementation theo quyền chủ dự án giao cho Agent trong Master Prompt. Chúng không tự động phê duyệt chi phí, dữ liệu thật, credentials hoặc deployment production.

| ID | Chủ đề | Quyết định | ADR | Trạng thái |
|---|---|---|---|---|
| DEC-007 | Frontend | React 19.3.1, TypeScript 5.9.3, Vite 8.4.0, Node 26, npm | ADR-0002 | ACCEPTED FOR INITIAL IMPLEMENTATION |
| DEC-008 | Backend/ORM | Python 3.14.10, FastAPI 0.165.0, SQLAlchemy 2.1.9, Alembic 1.20.1, Pydantic 2.14.4, psycopg 3.3.9 | ADR-0002 | ACCEPTED FOR INITIAL IMPLEMENTATION |
| DEC-009 | Database | PostgreSQL 18.7; đúng 12 bảng và UUID/JSONB/timezone-aware types | ADR-0002 | ACCEPTED FOR INITIAL IMPLEMENTATION |
| DEC-010 | Architecture | Modular monolith, one API + one React SPA, two separated portal route trees; add worker/queue only when needed | ADR-0002 | ACCEPTED FOR INITIAL IMPLEMENTATION |
| DEC-011 | Staff auth/local workflow | Staff provisioned locally, Argon2id password hash; six-status report workflow and controlled transitions | ADR-0003 | ACCEPTED FOR LOCAL IMPLEMENTATION |
| DEC-012 | Upload/location | Private named volume; JPEG/PNG/WebP; max 5 files/report, 10 MiB/file; WGS84/EPSG:4326; Leaflet/OSM for local demo | ADR-0003 | ACCEPTED FOR LOCAL IMPLEMENTATION |
| DEC-013 | Confidence/audit | Preserve confidence_type, no uncalibrated percentages/threshold auto-approval; local JSONL audit sink | ADR-0004 | ACCEPTED FOR INITIAL IMPLEMENTATION |
| DEC-014 | Authentication libraries | Authlib 1.9.10 for OIDC, pwdlib[argon2] 0.4.2 for Argon2id, itsdangerous 2.2.0 for signed sessions/CSRF | ADR-0003 | ACCEPTED FOR LOCAL IMPLEMENTATION |
| DEC-015 | ML runtime/training boundary | Keep API runtime free of heavy ML dependencies; install classical NLP dependencies and CPU PyTorch only in separate ML training/test image targets. Make training/test opt-in Compose profiles and share model artifact volume with API. | ADR-0005 | ACCEPTED FOR LOCAL IMPLEMENTATION |

## 3. Milestone 1 implementation decisions

| ID | Chủ đề | Quyết định | Bằng chứng | Trạng thái |
|---|---|---|---|---|
| DEC-016 | Report submission degradation | Persist report independently of ML availability; unavailable/malformed inference becomes INFERENCE_FAILED with category/confidence NULL; raw_content unchanged | reports.py, PostgreSQL/endpoint tests, CI #26 | ACCEPTED |
| DEC-017 | Review/database invariant | Append review first; transaction-local `stnlp.current_review_id` binds final_category update to exact review; PostgreSQL actor/consistency triggers and append-only protection | Alembic 0002, PostgreSQL tests, CI #26 | ACCEPTED |
| DEC-018 | Single active model | Partial unique index allows one global ACTIVE; advisory transaction lock serializes activation/rollback; retire previous model before promoting target | Model API, concurrency/rollback tests, CI #26 | ACCEPTED FOR LOCAL REGISTRY |
## 4. Trade-offs and implementation controls

| ID | Chủ đề | Quy tắc |
|---|---|---|
| PROP-001 | users.role_codes | JSON allow-list; policy tập trung; không thêm RBAC tables |
| PROP-002 | Dataset versioning | Each datasets row is one version; frozen version immutable |
| PROP-003 | Audit sink | Local JSONL is development-only; production append-only sink still open |
| PROP-004 | Confidence | Raw score/probability/calibration must retain distinct types |
| PROP-005 | ML dependencies | API runtime stays lightweight; CPU PyTorch is installed from its CPU wheel index only in ML training/test images |

## 5. Quyết định vẫn mở cho production hoặc dữ liệu thật

| ID | Nội dung còn mở | Khi nào phải chốt |
|---|---|---|
| TBD-010 | Dataset source, license/consent, PII, labeling adjudication and split policy | Before importing or training on real data |
| TBD-012 | Production audit sink, durability, retention, backup and tamper-evidence | Before production |
| TBD-013 | Quantified NFR, latency/load, availability, RPO/RTO and retention | Before QA release gate |
| TBD-014 | Production hosting, domain, TLS, secret manager, CI/CD and monitoring | Before production deployment |
| TBD-015 | Google OAuth client credentials, consent screen, approved redirect URIs and allowed origins | Before real Google sign-in test |
| TBD-016 | Production object storage, malware scan and deletion/retention policy | Before accepting real user uploads |
| TBD-017 | Production map/geocoding provider, terms, quota and location privacy | Before public map deployment |
| TBD-018 | Staff MFA and production identity/provisioning policy | Before staff access in production |
| TBD-019 | Dataset-driven calibration and confidence threshold/acceptance target | Before automation can reduce human review |

## 6. Quy tắc quản lý quyết định

- Các DEC-007..015 được chấp nhận cho initial/local implementation theo quyền triển khai được chủ dự án giao; không diễn giải thành production approval.
- Các TBD ở mục 4 không được tự động chốt bằng cách đặt giá trị mặc định rồi dùng trên production.
- Mỗi quyết định ảnh hưởng Database/API/security phải cập nhật ADR, docs chuyên ngành và RTM trong cùng PR.
- Không đánh dấu chức năng/test là hoàn thành nếu chưa có source và evidence.
