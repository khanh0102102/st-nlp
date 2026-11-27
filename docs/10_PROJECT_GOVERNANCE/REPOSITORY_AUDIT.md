# REPOSITORY AUDIT — ST-NLP

| Thuộc tính | Giá trị |
|---|---|
| Ngày kiểm tra | 2026-11-27 |
| Repository | https://github.com/khanh0102102/st-nlp |
| Nhánh/commit được kiểm tra | main / 39a937cb7474f6a8e09f2915140b7ba89c4708ac |
| Pull Request tài liệu | PR #2 — đã merge vào main |
| Trạng thái | Static repository audit — chưa có source implementation |

## 1. Kết luận điều hành

Repository hiện ở trạng thái **đã có bộ tài liệu nền tảng và baseline nghiệp vụ/dữ liệu, nhưng chưa có ứng dụng để chạy**.

Tại commit được kiểm tra:
- Có 36 file được Git theo dõi, trong đó 28 file tài liệu trong `docs/`; các file còn lại gồm tài liệu gốc/cấu hình và placeholder.
- Các thư mục `backend/`, `frontend/`, `database/`, `tests/` chỉ có `.gitkeep`.
- `docker-compose.yml` khai báo `services: {}`; không có service hoạt động.
- Chưa có Dockerfile, dependency manifest/lockfile, mã nguồn backend/frontend, SQLAlchemy model, migration, seed, test source hoặc GitHub Actions workflow.
- `.gitignore` đã có; `.dockerignore` và `.env.example` chưa có trên main tại thời điểm audit.
- Chưa có Dataset thực tế hoặc model artifact để huấn luyện/đánh giá.

PR #2 đã đưa tài liệu 11 danh mục và baseline 12 bảng vào main. Vì vậy, các hạng mục từng thiếu trong audit trước đã được cập nhật ở **mức đặc tả**, nhưng chưa được triển khai thành code/migration.

**Kết luận:** Repository sẵn sàng cho giai đoạn Project Foundation sau khi chốt stack kỹ thuật tối thiểu. Chưa thể triển khai an toàn các service phụ thuộc framework, DB engine, authentication, storage/map provider và workflow còn TBD. Các tài liệu/quản trị project, Docker build-context exclusions và traceability tracking có thể hoàn thiện ngay.

## 2. Phạm vi và phương pháp kiểm tra

Đã kiểm tra:
- Repository metadata, default branch, commit SHA, lịch sử Pull Request và Git tree đệ quy.
- `AGENTS.md`, `README.md`, `docs/README.md`.
- Toàn bộ tài liệu thuộc 00_OVERVIEW đến 09_AI_ML, gồm requirements, classification, architecture, database, API, UI/UX, technology stack, coding/Git, testing, deployment và NLP/ML.
- Nội dung `docker-compose.yml`, `.gitignore` và các thư mục source.
- PR #2 (đã merge) và nhánh `chore/repository-audit`/PR #1 (đã đóng, chưa merge) để tránh bỏ sót thay đổi chưa đưa vào main.

Đây là static repository audit qua GitHub. Không có local clone/runtime để thực thi build/test. Vì Compose chưa khai báo service và source chưa tồn tại, không có cơ sở để chạy test ứng dụng.

## 3. Kết quả kiểm tra hiện trạng

| Hạng mục | Trạng thái | Bằng chứng |
|---|---|---|
| Repository và quyền truy cập | PASS | Repository public; default branch main; có quyền đọc/ghi |
| PR tài liệu #2 | MERGED | Đã merge taxonomy 11 danh mục và baseline Database 12 bảng |
| AGENTS/README/docs index | PRESENT | Có quy tắc Docker-only, coding, security và tài liệu |
| Overview/Scope/Roadmap/BRD/SRS | PRESENT | Có phạm vi và yêu cầu nghiệp vụ |
| Classification catalog | SPECIFIED | Có đúng 11 tên và category_code trong CLASSIFICATION_SPECIFICATION |
| Database schema | PROPOSED | Có đúng 12 bảng, quan hệ và Data Dictionary; chưa có SQLAlchemy models/migration |
| Architecture/Security | PROPOSED | Có kiến trúc modular monolith đề xuất, ranh giới module và bảo mật |
| API | PROPOSED | Có endpoint/contract dự kiến; chưa có OpenAPI được sinh từ source |
| UI/UX | WIREFRAME-LEVEL | Có sitemap/mô tả màn hình; chưa có UI source, wireframe/prototype hoặc design tokens được duyệt |
| Technology Stack | PARTIAL / TBD | Python, SQLAlchemy, Docker Compose, Google OAuth và model families đã được định hướng; nhiều framework/provider/version chưa chốt |
| Backend source | NOT_STARTED | Chỉ có backend/.gitkeep |
| Frontend source | NOT_STARTED | Chỉ có frontend/.gitkeep |
| Database migrations/seeds | NOT_STARTED | Chỉ có database/.gitkeep |
| Test source | NOT_STARTED | Chỉ có tests/.gitkeep; TEST_CASES.md mới là danh sách expected cases |
| Dockerfiles | MISSING | Chưa có Dockerfile |
| Docker Compose | BLOCKED | services rỗng |
| .dockerignore | MISSING ON MAIN | Sẽ bổ sung trên nhánh audit hiện tại |
| .env.example | MISSING | Chờ config schema/secret names được chốt |
| Dependency manifests/lockfiles | MISSING | Chưa có package manifest/lockfile |
| CI workflows | MISSING | Chưa có .github/workflows |
| Dataset thật | NOT_PROVIDED | Chưa có file dữ liệu/quyền sử dụng/labeling guideline đã xác nhận |
| Model artifact/metrics | NOT_STARTED | Chưa có model artifact hoặc kết quả đánh giá thực tế |

## 4. Baseline đã được xác định trong tài liệu

### 4.1. Phân hệ

1. Citizen Portal: Google sign-in, gửi phản ánh bằng văn bản/ảnh/vị trí, xem dữ liệu của chính mình.
2. Admin Portal: route/URL tách biệt, quản lý phản ánh, kiểm duyệt AI, dashboard và map.
3. AI & Data Management: dataset, samples, training runs, metrics và model versions.

AI chỉ đề xuất nhãn; cán bộ có thẩm quyền xác nhận hoặc điều chỉnh.

### 4.2. Danh mục

Có chính xác 11 danh mục trong `docs/01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md`. Tên và thứ tự theo cung cấp của chủ dự án; category_code là mapping kỹ thuật được ghi trong tài liệu. Những ranh giới dễ giao nhau (nhóm 1/4, 5/10, 6/7/8) vẫn cần guideline gán nhãn và ví dụ được xác nhận bằng dữ liệu thực tế.

### 4.3. Database

Baseline thiết kế yêu cầu đúng 12 bảng:
`users`, `incident_categories`, `reports`, `report_attachments`, `preprocessing_runs`, `model_versions`, `predictions`, `prediction_reviews`, `datasets`, `dataset_samples`, `training_runs`, `training_metrics`.

Các quy tắc lõi đã ghi:
- `reports.raw_content` bất biến.
- `reports.final_category_id` lưu nhãn cán bộ xác nhận, ban đầu có thể NULL.
- `predictions` giữ nhãn AI và tham chiếu preprocessing/model.
- `prediction_reviews` append-only, không ghi đè prediction.
- Mỗi hàng `datasets` đại diện một phiên bản; FROZEN phải bất biến.
- Audit tổng quát nằm ngoài 12 bảng qua audit sink append-only; provider/durability/retention còn TBD.

Đây là **schema proposal**, chưa phải Database đã tạo. DB engine, SQL type mapping và migrations vẫn chưa có.

### 4.4. Docker-only

Đây là yêu cầu đã được chủ dự án nêu rõ trong AGENTS.md và TECHNOLOGY_STACK.md. Host chỉ cần Git, Docker Desktop/Engine + Compose và trình duyệt. Mục tiêu cuối là clone và chạy `docker compose up --build -d`; không được coi đây là khả năng hiện tại khi Compose chưa có service.

## 5. Blockers và quyết định còn cần chốt

| ID | Vấn đề | Trạng thái sau PR #2 | Ảnh hưởng / đầu ra cần thiết |
|---|---|---|---|
| BLK-01 | Ranh giới/guideline gán nhãn | PARTIAL | Danh sách 11 lớp và code đã có; cần quy tắc adjudication/positive-negative examples cho lớp giao nhau |
| BLK-02 | Physical DB engine/type mapping | PARTIAL | 12 bảng/quan hệ/cột logic đã đặc tả; cần chọn engine/version, PK type, SQL types, indexes, JSON/geospatial mapping trước migration |
| BLK-03 | Frontend framework/language | OPEN | Chọn framework, TypeScript/JavaScript, package manager và build strategy |
| BLK-04 | Backend framework/runtime | OPEN | Xác nhận framework Python và Python runtime version |
| BLK-05 | Database/migration tool | OPEN | Chọn DB engine/version; SQLAlchemy đã định hướng, Alembic là đề xuất chưa duyệt |
| BLK-06 | Staff authentication/provisioning | OPEN | Cách tạo tài khoản, đăng nhập, MFA, reset/disable và cấp quyền cán bộ |
| BLK-07 | RBAC/AI Data Manager permission | PARTIAL | Bảng users có role_codes; cần chốt allow-list/permissions và quản lý các quyền AI/Data Manager mà không thêm bảng tùy tiện |
| BLK-08 | Report status/state machine | OPEN | Danh sách trạng thái, transition, actor, điều kiện và timeline hiển thị |
| BLK-09 | File storage/upload | OPEN | Provider, private access, file count/MIME/size limit, malware scanning, retention/deletion |
| BLK-10 | Map/geocoding/CRS | OPEN | Provider, key/quota, coordinate CRS/SRID, reverse geocoding và privacy policy |
| BLK-11 | Dataset thật và quyền sử dụng | OPEN | Nguồn, format, license/consent, privacy, labeling và split; thiếu dữ liệu thì không thể có ML metrics thật |
| BLK-12 | Confidence semantics/threshold | OPEN | Phân biệt raw score/probability/calibrated probability; chốt threshold nếu dùng để cảnh báo |
| BLK-13 | Audit sink | OPEN | Chọn sink bền vững, append-only, access control, retention/backup/tamper detection; làm rõ retry/delivery guarantee mà không âm thầm thêm bảng thứ 13 |
| BLK-14 | NFR số học/retention | OPEN | Latency/load/availability, backup RPO/RTO, retention/xóa dữ liệu |
| BLK-15 | API contract | PARTIAL | Endpoint list hiện Proposed; cần request/response schemas, error codes, auth/permissions và OpenAPI contract |
| BLK-16 | UI/UX design approval | PARTIAL | Sitemap có; cần wireframe/design tokens/accessibility target và trạng thái hiển thị |
| BLK-17 | Docker runtime | NOT_STARTED | Dockerfiles, Compose services, healthchecks, migrations/seeds, volumes, clean-environment test |
| BLK-18 | CI/security supply chain | NOT_STARTED | GitHub Actions, lint/test/build/security/dependency/license checks và artifact versioning |

Các blocker trên không đồng nghĩa phải chờ mọi quyết định mới được viết bất kỳ dòng code nào. Tuy nhiên không triển khai phần phụ thuộc vào một lựa chọn chưa duyệt, và phải tiếp tục các phần độc lập như governance, Docker exclusions, test traceability và scaffold không gắn framework.

## 6. Rủi ro thiết kế cần theo dõi

1. **Role storage:** `users.role_codes` dạng JSON giúp giữ đúng 12 bảng nhưng không có FK role/permission. Backend phải validate allow-list và dùng policy tập trung; nếu cần role/permission động, phải đánh giá lại giới hạn schema.
2. **Audit sink:** không có audit_logs trong 12 bảng. Sink ngoài Database phải thực sự bền vững; debug log/container stdout đơn thuần không đủ cho audit có thể truy vết.
3. **Prediction integrity:** phải đảm bảo report_id của prediction, preprocessing_run và review khớp nhau; các invariant cross-table cần kiểm tra ở application/test và constraint phù hợp.
4. **Dataset immutability:** FROZEN cần được bảo vệ ở service/database permission; chỉ dựa vào nút UI read-only là không đủ.
5. **File/database consistency:** upload storage và DB transaction không atomic; cần compensating cleanup/orphan detection.
6. **No real dataset:** không huấn luyện hoặc hiển thị metrics thật khi chưa có nguồn dữ liệu hợp lệ.
7. **Docker one-command:** cần migration/seed orchestration, healthcheck, named volumes và clean environment test; Compose “Up” chưa đồng nghĩa ứng dụng sẵn sàng.

## 7. Công việc có thể làm ngay và công việc bị chặn

### Có thể thực hiện ngay
- Quản lý audit, RTM, decision log và implementation backlog.
- Bổ sung `.dockerignore` với quy tắc chung, không quyết định stack.
- Chuẩn hóa naming, code ownership và PR/test evidence templates.
- Xây test inventory coverage, mapping FR/NFR tới module/API/bảng/test.
- Chuẩn bị khung CI chỉ sau khi lựa chọn runner/container command được xác định; chưa cần khai báo package-specific commands.

### Chưa nên triển khai trước khi chốt dependency
- Dockerfiles/Compose services thật (cần stack/framework/runtime/database).
- SQLAlchemy physical models/migrations (cần DB engine/type mapping và quyết định schema chi tiết).
- Login cán bộ và permission management đầy đủ (cần staff auth/RBAC policy).
- Upload/map thật (cần provider, credential, limits và privacy).
- Model training/metrics production-like (cần Dataset và labeling policy).
- Workflow transitions (cần report status state machine).

## 8. Hướng triển khai tiếp theo

Thứ tự cụ thể nằm trong `IMPLEMENTATION_PLAN.md`. Ưu tiên:
1. Chốt stack và quyết định đầu vào tối thiểu.
2. Docker/Project Foundation.
3. Database Foundation.
4. Backend Core/Security.
5. Citizen Portal.
6. NLP inference baseline.
7. Admin review/workflow.
8. Dashboard/Map.
9. AI & Data Management.
10. Integration/QA/Deployment.

Không đánh dấu module VERIFIED cho tới khi có code, migration, Docker build và test evidence.

## 9. Kết luận

Repository hiện **đủ tài liệu để bắt đầu Project Foundation có kiểm soát**, nhưng chưa có ứng dụng chạy được. Các tài liệu mới sau PR #2 đã xác định 11 danh mục và 12 bảng ở mức baseline; các quyết định kỹ thuật còn TBD cần được giải quyết trước khi tạo artifact khó thay đổi.

Audit không xác nhận bất kỳ chức năng ứng dụng, Database migration, Docker image hoặc test suite nào đã chạy thành công.
