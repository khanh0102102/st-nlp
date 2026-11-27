# TECHNOLOGY STACK — CÔNG NGHỆ SỬ DỤNG

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.1 |
| Trạng thái | Approved for initial implementation by delegated Master Prompt; production choices remain separate |
| Cập nhật | 2026-11-27 |

## 1. Nguyên tắc lựa chọn

Chọn công nghệ theo yêu cầu NLP tiếng Việt, khả năng bảo trì, tương thích runtime và Docker-only. Các version dưới đây là direct dependency baseline đã pin trong manifest hoặc Dockerfile. Đây chưa phải bằng chứng build thành công; transitive lock và container verification là build gate bắt buộc.

## 1.1. Quyết định vận hành: Docker-only

Máy host chỉ cần Git, Docker Desktop/Engine + Compose và trình duyệt. IDE/editor là tùy chọn. Không cài Python, Node.js, npm, PostgreSQL, Redis hoặc package dự án trên Windows host.

Mọi runtime, dependency, Database, migration, seed, lint, test, training và script quản trị chạy trong container. Mục tiêu sau khi hoàn thiện:

    git clone https://github.com/khanh0102102/st-nlp.git
    cd st-nlp
    docker compose up --build -d

Credential thật của Google OAuth hoặc nhà cung cấp ngoài phải cấu hình qua secret/environment; không commit vào Git. Lệnh khởi động trong README là mục tiêu hiện tại, chưa được xác minh bằng Docker ở branch này.

## 2. Stack local đã chốt cho implementation

| Thành phần | Công nghệ | Phiên bản baseline |
|---|---|---|
| Frontend runtime | Node.js Active LTS line | 26 |
| Frontend | React | 19.3.1 |
| Language | TypeScript | 5.9.3 |
| Frontend build | Vite | 8.4.0 |
| Package manager | npm | đi kèm Node 26; package-lock pending |
| Backend runtime | Python | 3.14.10 |
| Backend API | FastAPI | 0.165.0 |
| ASGI server | Uvicorn | 0.54.0 |
| Validation/config | Pydantic / pydantic-settings | 2.14.4 / 2.16.3 |
| ORM | SQLAlchemy | 2.1.9 |
| Migration | Alembic | 1.20.1 |
| PostgreSQL driver | psycopg | 3.3.9 |
| Database | PostgreSQL | 18.7 |
| Vietnamese tokenization | underthesea | 9.5.0 (ML image, not API image) |
| Classical ML | scikit-learn | 1.9.1 (ML image) |
| Deep learning | PyTorch CPU | 2.15.0 (separate ML image when needed) |
| Backend test/client | pytest / httpx | 9.2.0 / 0.29.0 |
| Python lint | Ruff | 0.17.6 |
| Web server | Nginx stable Alpine line | stable-alpine3.24 |
| Orchestration | Docker Compose | version bundled with Docker Desktop/Compose plugin |

### Dependency policy

- requirements.txt pins direct backend runtime dependencies.
- requirements-dev.txt adds test/lint dependencies.
- frontend/package.json pins direct frontend dependencies.
- npm package-lock.json and a Python transitive/hash lock are still required. They must be generated and committed from Docker before the stack can be considered reproducible.
- PyTorch and underthesea are intentionally not installed into the API image; they belong to the dedicated NLP/ML image/worker to keep the web API image smaller.
- CPU-only PyTorch is chosen for local compatibility; no GPU/NVIDIA runtime is required on the host.
- Base image patch digests and complete dependency locks must be captured in the release hardening step.

## 3. Kiến trúc triển khai

- Modular monolith: one FastAPI Backend API, one React SPA and one PostgreSQL Database.
- Citizen Portal and Admin Portal are separated by route/layout and server-side authorization. They are not allowed to rely on frontend route hiding as security.
- Nginx serves the built SPA and reverse-proxies /api and /health to Backend.
- SQLAlchemy synchronous engine + psycopg 3 for the initial API foundation. Long-running training will not execute inside request handlers.
- PostgreSQL native UUID, JSONB and timezone-aware timestamps. WGS84/EPSG:4326 coordinates are stored as latitude/longitude; PostGIS is not introduced in foundation.
- No Redis or worker service until a concrete async queue/training job requires it. A separate worker container can be added later without changing the 12-table relational baseline.
- Database port is not published to host by default.

## 4. Các quyết định triển khai khác

Các quyết định local về staff account provisioning, workflow, storage, map, confidence và audit được ghi trong:
- ADR-0003-LOCAL-INTEGRATION-BASELINE.md
- ADR-0004-AI-CONFIDENCE-AND-AUDIT.md

Tóm tắt:
- Citizen Google OIDC; staff local accounts provisioned separately; never auto-grant staff role based on a Google email.
- Report workflow local v1: SUBMITTED, UNDER_REVIEW, IN_PROGRESS, RESOLVED, REJECTED, CLOSED.
- Local image upload: JPEG/PNG/WebP, at most 5 files/report and 10 MiB/file; private named volume.
- Location coordinate reference: WGS84/EPSG:4326; local demo map uses Leaflet + OSM attribution.
- Every initial prediction requires human review; do not turn raw scores into percentages.
- Local audit events use separate JSONL named volume; production audit sink remains open.

## 5. Những quyết định chưa được áp dụng cho production

- Staff identity provider, MFA and production account provisioning.
- Google OAuth credentials and allowed origins.
- Production object storage, malware scanning, file retention and deletion.
- Production map/tile/geocoding provider, terms, quota and privacy.
- Durable audit sink, retention, backup and tamper-evidence.
- Dataset source, license, consent and privacy approval.
- Confidence calibration and model acceptance thresholds.
- Hosting, domain, TLS, secrets manager, CI/CD, backup RPO/RTO and quantified NFR targets.

Không dùng credential/paid services hoặc triển khai production khi chưa có phê duyệt riêng.

## 6. Nguồn lựa chọn và kiểm tra version

Version metadata was checked on 2026-11-27 using official project release pages and package indexes:
- Node.js: https://nodejs.org/en/about/previous-releases
- React: https://www.npmjs.com/package/react
- Vite: https://vite.dev/guide/
- Python: https://www.python.org/downloads/
- FastAPI: https://github.com/fastapi/fastapi/releases
- SQLAlchemy: https://pypi.org/project/SQLAlchemy/
- PostgreSQL: https://www.postgresql.org/support/versioning/
- PyTorch: https://pypi.org/project/torch/
- underthesea: https://pypi.org/project/underthesea/
- scikit-learn: https://pypi.org/project/scikit-learn/

Version selection is not equivalent to compatibility testing. The Docker clean-build and test evidence remains pending.
