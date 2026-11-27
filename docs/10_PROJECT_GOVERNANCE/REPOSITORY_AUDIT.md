# REPOSITORY AUDIT — ST-NLP

| Thuộc tính | Giá trị |
|---|---|
| Ngày audit | 2026-11-27 |
| Repository | https://github.com/khanh0102102/st-nlp |
| Nhánh được kiểm tra | main |
| Commit được kiểm tra | 4e1640f98821f6a55336a483f16b2f442dc7f01b |
| Trạng thái | Audit baseline — cần chủ dự án rà soát các quyết định TBD |

## 1. Tóm tắt điều hành

Repository hiện là **repository khởi tạo tài liệu**, chưa phải source code của một ứng dụng có thể chạy.

- Đã có 26 tài liệu chuyên môn trong `docs/`, cùng `AGENTS.md`, `README.md`, `docs/README.md` và các file cấu hình/placeholder.
- Tổng số file Git được kiểm tra: 35.
- Có các thư mục `frontend/`, `backend/`, `database/`, `tests/`, nhưng hiện chỉ có `.gitkeep`.
- `docker-compose.yml` có `services: {}`, chưa có service.
- Chưa có Dockerfile, dependency manifest/lockfile, source code, database migration, seed, automated test hoặc CI workflow.
- Vì vậy, chưa thể build image, khởi động ứng dụng, chạy migration hoặc thực thi test ST-NLP.

**Kết luận:** có thể bắt đầu Project Foundation sau khi chốt các quyết định stack tối thiểu; chưa thể tuyên bố bất kỳ phân hệ phần mềm nào đã được triển khai.

## 2. Phạm vi kiểm tra

Đã kiểm tra:
- Metadata repository và nhánh mặc định.
- Danh sách file trên `main`.
- `AGENTS.md`, `README.md`, `docs/README.md`.
- Toàn bộ 26 tài liệu thuộc 10 nhóm tài liệu chuyên môn.
- `docker-compose.yml` và các thư mục source placeholder.

Audit này là static repository review. Chưa có build/test runtime vì repository chưa có ứng dụng và Docker service.

## 3. Kết quả kiểm tra repository

| Hạng mục | Trạng thái | Bằng chứng/nhận xét |
|---|---|---|
| GitHub repository | PASS | Truy cập được, public, default branch `main` |
| AGENTS.md | PASS | Có quy tắc coding, bảo mật, Git và Docker-only |
| Tài liệu tổng quan/yêu cầu | PASS | Có Overview, Scope, Roadmap, BRD, SRS, Use Case, Business Process |
| Tài liệu kiến trúc | PASS | Có Architecture, System Design, Module Design, Security Design |
| Tài liệu Database | PARTIAL | Có logical design, conceptual ERD và logical dictionary; chưa có physical schema |
| API Specification | PARTIAL | Có endpoint dự kiến; chưa có OpenAPI schema được sinh/kiểm chứng từ code |
| UI/UX Specification | PARTIAL | Có sitemap và mô tả màn hình; chưa có wireframe/prototype/design tokens được duyệt |
| Technology Stack | BLOCKED | Frontend, framework Backend, DB engine và nhiều provider còn TBD |
| Source Frontend | NOT STARTED | Chỉ có `.gitkeep` |
| Source Backend | NOT STARTED | Chỉ có `.gitkeep` |
| Database migrations/seeds | NOT STARTED | Chưa có migration hoặc seed |
| Dockerfiles | MISSING | Chưa có Dockerfile |
| Docker Compose | BLOCKED | `services: {}`, chưa thể chạy ứng dụng |
| .dockerignore | MISSING AT AUDIT | Cần bổ sung trước khi build images |
| .env.example | MISSING AT AUDIT | Cần bổ sung cùng config schema |
| Dependency manifests/lockfiles | MISSING | Chưa có package manifest hoặc lockfile |
| Automated tests | NOT STARTED | Chưa có test source/config |
| CI workflow | MISSING | Chưa có `.github/workflows/` |
| Dataset thực tế | NOT PROVIDED | Chưa có dataset/label guideline chính thức |
| Model artifacts | NOT STARTED | Chưa có artifact/model version |

## 4. Điểm đã rõ và có thể coi là baseline nghiệp vụ

1. ST-NLP nhận phản ánh giao thông và hạ tầng đô thị bằng văn bản, ảnh và vị trí.
2. Có ba phân hệ: Citizen Portal, Admin Portal, AI & Data Management.
3. Người dân đăng nhập Google theo định hướng đã thống nhất.
4. Citizen Portal và Admin Portal phải tách biệt về route/URL và quyền truy cập.
5. AI đề xuất nhãn và confidence; cán bộ có quyền xác nhận hoặc điều chỉnh.
6. Prediction gốc và kết quả review phải được lưu riêng để truy vết.
7. AI quản lý Dataset, Dataset Samples, Training Runs, Training Metrics và Model Versions.
8. Local development phải theo chính sách Docker-only: không yêu cầu cài runtime/dependency dự án trên host.
9. Mục tiêu vận hành cuối cùng là clone repository rồi chạy `docker compose up --build -d`, sau khi Compose thực sự được triển khai và xác minh.

## 5. Các điểm chặn và quyết định cần chốt

| ID | Vấn đề | Tác động | Việc cần chốt |
|---|---|---|---|
| BLOCK-01 | Chưa có 11 nhãn chính thức | Ảnh hưởng category seed, UI, training label mapping, API, DB và evaluation | Chủ dự án cung cấp mã, tên, định nghĩa, tiêu chí bao gồm/loại trừ và ví dụ của đủ 11 nhóm |
| BLOCK-02 | Physical Database Schema chưa được xác nhận | Không thể tạo SQLAlchemy models/migrations cuối cùng an toàn | Đối chiếu thiết kế 12 bảng đã làm trước đây (nếu là baseline hiện hành), chốt tên bảng/cột/PK/FK/constraints |
| BLOCK-03 | Frontend stack TBD | Ảnh hưởng build, routing, UI, Dockerfile | Chọn framework/language và package manager |
| BLOCK-04 | Backend framework/version TBD | Ảnh hưởng API, auth, validation và Docker image | Xác nhận framework Python và runtime version |
| BLOCK-05 | Database engine/version TBD | Ảnh hưởng ORM, migration, geospatial và Compose | Chọn engine/version; PostgreSQL là phương án đề xuất cần duyệt |
| BLOCK-06 | Workflow trạng thái phản ánh chưa chốt | Ảnh hưởng quyền chuyển trạng thái, timeline và thông báo | Chốt state machine, transition, actor và điều kiện |
| BLOCK-07 | Auth cán bộ chưa chốt | Có nguy cơ cấp quyền quản trị sai | Chốt cách tạo tài khoản, login, MFA và thu hồi quyền |
| BLOCK-08 | File storage/limit/retention TBD | Ảnh hưởng upload, bảo mật, backup và chi phí | Chốt loại storage, MIME/size/count limit, retention và deletion |
| BLOCK-09 | Map/geocoding provider TBD | Ảnh hưởng UI, API key, quota và tọa độ | Chọn provider, CRS/SRID, geocoding và policy hiển thị vị trí |
| BLOCK-10 | Dataset/nguồn dữ liệu chưa được cung cấp | Không thể báo cáo chất lượng model thật | Cung cấp dataset được phép sử dụng, nguồn gốc và labeling guideline |
| BLOCK-11 | Confidence semantics và ngưỡng chưa chốt | Có thể hiển thị sai confidence hoặc tự động hóa quá mức | Chốt raw score/probability/calibration và ngưỡng review nếu cần |
| BLOCK-12 | NFR mục tiêu số học TBD | Chưa có căn cứ nghiệm thu hiệu năng/availability | Chốt latency, tải, backup, RPO/RTO và retention |
| BLOCK-13 | API contract mới ở mức đề xuất | Frontend/Backend có thể lệch contract | Chốt request/response/error schemas và OpenAPI |
| BLOCK-14 | Local one-command Docker chưa thể chứng minh | Không thể xác nhận mục tiêu clone-and-run | Cần Dockerfiles, Compose services, healthchecks, migration/seed và clean-environment test |

## 6. Các điểm cần làm rõ trong tài liệu

- `DATABASE_DESIGN.md` có nhắc thiết kế làm việc hướng tới 12 bảng, nhưng ERD hiện là conceptual. Không được tự giả định 12 logical concepts chính là 12 bảng vật lý.
- `API_SPECIFICATION.md` ghi nhiều endpoint là dự kiến; cần chốt contract trước khi Frontend và Backend triển khai song song.
- `PROJECT_ROADMAP.md` và Master Instruction mô tả cùng các workstream theo cách nhóm khác nhau. Dùng dependency và deliverable làm chuẩn, không lệ thuộc số thứ tự giai đoạn.
- Citizen có thể xem kết quả AI/trạng thái của mình; cần chốt mức chi tiết được hiển thị, đặc biệt confidence và nhãn đã được cán bộ sửa.
- `SYSTEM_ARCHITECTURE.md` đề xuất modular monolith; đây là hướng kiến trúc, chưa phải quyết định công nghệ cuối cùng.
- Docker-only có nghĩa runtime/dependency dự án nằm trong container; credential Google/Map và các secret dịch vụ bên ngoài vẫn cần cấu hình riêng khi dùng.

## 7. Rủi ro ưu tiên

1. **Sai dữ liệu/nhãn:** tự định nghĩa category có thể làm sai toàn bộ dataset, model, dashboard và schema.
2. **Sai quyền truy cập:** nếu không chốt RBAC và ownership sớm có nguy cơ IDOR/privilege escalation.
3. **Schema thay đổi muộn:** physical DB chưa chốt có thể gây migration và API rework.
4. **One-command Docker không thực chất:** nếu thiếu healthcheck, migration, secret defaults và persistence thì lệnh Compose có thể chạy nhưng app chưa sẵn sàng.
5. **Metrics không đáng tin:** thiếu dataset độc lập, split và calibration policy sẽ làm kết quả đánh giá không thể nghiệm thu.

## 8. Đề xuất việc tiếp theo

**Work package A — Chốt tối thiểu để khởi tạo code**
- Chọn Frontend framework/language.
- Chọn Backend framework/Python runtime.
- Chọn Database engine/version/migration.
- Xác nhận physical schema hiện hành.
- Xác định login/admin provisioning tối thiểu.
- Chốt provider hoặc adapter contract cho map/storage.

**Work package B — Chốt nghiệp vụ trước khi các module phụ thuộc triển khai**
- Danh mục 11 nhóm.
- Report state machine và transition.
- Role-permission matrix.
- Upload policy và data retention.
- Quy tắc hiển thị AI result cho Citizen.
- Confidence semantics và evaluation target.

**Work package C — Xây nền tảng Docker**
- .dockerignore, .env.example.
- Dockerfiles và lockfiles.
- Compose services, healthchecks, volumes.
- Migration/seed orchestration.
- Containerized lint/test commands.
- Clean-clone/clean-volume smoke test.

## 9. Kết luận audit

Repository hiện sẵn sàng về mặt **khung tài liệu ban đầu**, nhưng chưa sẵn sàng để xây dựng toàn bộ sản phẩm mà không có một số quyết định đầu vào.

Có thể bắt đầu công việc độc lập như project skeleton, Docker conventions, CI scaffolding và ADR. Không nên tự tạo category, physical schema, workflow hoặc policy bảo mật khi chưa có quyết định hợp lệ.

Audit không xác nhận bất kỳ chức năng ứng dụng nào đã được triển khai hoặc kiểm thử.
