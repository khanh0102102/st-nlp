# DECISION LOG — ST-NLP

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.1 |
| Cập nhật | 2026-11-27 |
| Mục đích | Ghi lại quyết định đã được chủ dự án cung cấp/chấp thuận và các mục còn mở |

## 1. Quyết định/baseline đã được xác lập

| ID | Chủ đề | Quyết định/baseline | Nguồn | Trạng thái |
|---|---|---|---|---|
| DEC-001 | Local development | Docker-only; host chỉ cần Git, Docker/Compose và trình duyệt; runtime/dependency chạy trong container | AGENTS.md, TECHNOLOGY_STACK.md, Master Instruction | ACCEPTED |
| DEC-002 | Category catalog | Chính xác 11 danh mục và category_code theo CLASSIFICATION_SPECIFICATION.md | Chủ dự án cung cấp danh sách 11 nhóm và chấp nhận mapping code trong Master Instruction | BASELINE ACCEPTED |
| DEC-003 | Database table set | Baseline gồm đúng 12 bảng trong DATABASE_DESIGN.md; không tự thêm roles/permissions/dataset_versions/audit_logs | Chủ dự án cung cấp 12 bảng và Master Instruction | BASELINE ACCEPTED |
| DEC-004 | Prediction vs review | Prediction AI được lưu riêng; prediction_reviews là lịch sử kiểm duyệt; reports.final_category_id là nhãn cuối cùng do cán bộ xác nhận | SRS, DATABASE_DESIGN, Master Instruction | BASELINE ACCEPTED |
| DEC-005 | Dataset version | Mỗi hàng datasets đại diện một version; version FROZEN bất biến | DATABASE_DESIGN, Master Instruction | BASELINE ACCEPTED |
| DEC-006 | AI scope | Text classification; ảnh là minh chứng trong baseline, không tự thêm Computer Vision | PROJECT_SCOPE, PROJECT_OVERVIEW | ACCEPTED |

**Phạm vi của trạng thái ACCEPTED:** xác nhận baseline nghiệp vụ/giới hạn nêu trên, không đồng nghĩa physical SQL implementation hoặc mọi cột kỹ thuật đã được nghiệm thu.

## 2. Quyết định thiết kế đang là Proposed/đánh đổi cần review

| ID | Chủ đề | Nội dung đang mô tả | Cần review |
|---|---|---|---|
| PROP-001 | users.role_codes | Lưu role codes dạng JSON trong users để giữ giới hạn 12 bảng | Kiểm tra validation allow-list, truy vấn permission, cấp/thu hồi quyền và audit; không tự thêm RBAC tables |
| PROP-002 | Dataset versioning | Mỗi row datasets là một version, parent_dataset_id lưu lineage | Kiểm tra copy samples/versioning và freeze enforcement |
| PROP-003 | Audit sink | Audit tổng quát ngoài 12 bảng qua sink append-only | Chọn nơi lưu bền vững, delivery/retry, access, retention và tamper detection |
| PROP-004 | Confidence | predictions lưu confidence_value + confidence_type | Chọn semantics/calibration và chính sách hiển thị trước khi dùng threshold |

## 3. Các quyết định còn mở (TBD)

| ID | Chủ đề | Nội dung cần quyết định | Ảnh hưởng |
|---|---|---|---|
| TBD-001 | Frontend stack | Framework, language, package manager, build/runtime version | Frontend, Docker, CI |
| TBD-002 | Backend stack | Framework Python, Python runtime/version, ASGI server, dependency manager | API, Docker, ML |
| TBD-003 | Database | DB engine/version, UUID type, JSON/geospatial support, SQL type mapping | Models, migrations, indexes |
| TBD-004 | Migration | Alembic hay công cụ khác; strategy upgrade/downgrade | Database Foundation |
| TBD-005 | Staff authentication | Provisioning, login method, MFA, password/reset/disable | Admin Portal, Authorization |
| TBD-006 | Permission policy | Role/permission matrix cho RECEIVER, ADMIN và AI/Data Manager | Security, AI Management |
| TBD-007 | Report workflow | Status codes, state transitions, actors and visibility | Incident, Admin, Citizen |
| TBD-008 | File storage | Local/dev and production provider, bucket/private access, file limits, scan, retention | Attachment, Docker, Backup |
| TBD-009 | Map/location | Provider, CRS/SRID, geocoding, quotas, privacy and address policy | Citizen, Admin, Dashboard |
| TBD-010 | Dataset | Dataset source, file format, license/consent, PII handling, labeling guideline, split ratio | Training, evaluation |
| TBD-011 | AI confidence | Raw score/probability/calibrated probability, review threshold and no-prediction states | Prediction, Citizen/Admin UI |
| TBD-012 | Audit | Production sink, access/read API, retention, backup, delivery guarantee | Security, Compliance |
| TBD-013 | Non-functional targets | Latency, load, availability, RPO/RTO, retention period | QA and Deployment |
| TBD-014 | Production hosting | Hosting platform, domain, TLS, secret manager, CI/CD, monitoring | Deployment |

## 4. Quy tắc quản lý quyết định

- Không thay đổi trạng thái TBD/Proposed thành Accepted nếu không có quyết định từ chủ dự án.
- Mỗi quyết định mới phải ghi người quyết định, ngày, bối cảnh, lựa chọn, hệ quả và tài liệu/code bị ảnh hưởng.
- Khi quyết định làm thay đổi API/Database/security, cập nhật tài liệu liên quan và RTM cùng Pull Request.
- Không coi việc một phương án xuất hiện trong bảng “đề xuất” là bằng chứng chủ dự án đã duyệt.
