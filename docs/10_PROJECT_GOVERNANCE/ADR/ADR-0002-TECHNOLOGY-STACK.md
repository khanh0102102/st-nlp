# ADR-0002: Technology Stack cho local implementation

- Trạng thái: Accepted for initial implementation by delegated Master Prompt
- Ngày quyết định: 2026-11-27
- Phạm vi: Local/dev and academic demonstration baseline; production deployment remains separate
- Căn cứ: Chủ dự án giao AI Agent chủ động lựa chọn các mục TBD và ghi ADR, đồng thời yêu cầu Docker-only.

## Bối cảnh

Repository đã có nghiệp vụ, API, Database và UI/UX baseline nhưng chưa có framework, runtime, DB engine, migration hoặc dependency manifests. Cần chọn stack vừa hỗ trợ ứng dụng NLP tiếng Việt, vừa giữ modular monolith dễ chạy trong Docker.

## Quyết định

| Lớp | Công nghệ / phiên bản baseline |
|---|---|
| Frontend runtime | Node.js 26 Active LTS |
| Frontend framework | React 19.3.1 |
| Frontend language | TypeScript 5.9.3 |
| Frontend build | Vite 8.4.0 |
| Frontend package manager | npm; package-lock phải được sinh và commit từ Docker trước khi coi build reproducible |
| Backend runtime | Python 3.14.10 |
| Backend framework | FastAPI 0.165.0 + Uvicorn 0.54.0 |
| Validation/config | Pydantic 2.14.4, pydantic-settings 2.16.3 |
| ORM / migrations | SQLAlchemy 2.1.9, Alembic 1.20.1 |
| PostgreSQL driver | psycopg 3.3.9 |
| Database | PostgreSQL 18.7 |
| NLP tokenization | underthesea 9.5.0 |
| Classical ML | scikit-learn 1.9.1 |
| Deep learning | PyTorch 2.15.0, CPU-only image for local baseline |
| Backend quality | pytest 9.2.0, httpx 0.29.0, Ruff 0.17.6 |
| Web serving | Nginx stable-alpine3.24 |
| Orchestration | Docker Compose |

Các package version là direct dependency baseline. Build gate tiếp theo phải tạo npm lockfile và Python transitive/hash lock trong container, sau đó build và kiểm thử thực tế. Không được gọi stack là validated trước gate này.

## Kiến trúc triển khai

- Modular monolith: một FastAPI API, một React SPA, một PostgreSQL.
- Hai portal phân tách ở route/layout: /citizen và /admin; Backend kiểm tra quyền cho tất cả API.
- Frontend static build phục vụ bởi Nginx; Nginx reverse-proxy /api và /health đến Backend.
- Không thêm Redis hoặc training worker ngay từ foundation; chỉ thêm khi có queue/background workload đã được xác định. Khi training dài được triển khai, tạo worker container riêng nhưng dùng chung module/domain contracts.
- SQLAlchemy sync + psycopg 3 được chọn cho foundation để giảm độ phức tạp concurrency ban đầu; request handler không chạy training dài trực tiếp.
- PostgreSQL native UUID, JSONB và timestamp with time zone; không thêm PostGIS ở foundation. Tọa độ lưu WGS84/EPSG:4326; query bản đồ ban đầu dùng tọa độ/bounding box.
- Database không publish port ra host trong Compose mặc định.

## Lý do lựa chọn

- FastAPI, SQLAlchemy và Python phù hợp định hướng Python/NLP đã có trong tài liệu; React/TypeScript đáp ứng web responsive và tách portal bằng route.
- PostgreSQL hỗ trợ quan hệ, JSONB, UUID, transaction và integrity rules của schema.
- Node 26 là dòng Active LTS tại thời điểm quyết định; Vite 8 yêu cầu runtime Node hiện đại.
- Python 3.14 được chọn thay vì dòng 3.15 mới hơn để giảm rủi ro chọn runtime mới nhất ngay từ đầu, trong khi các package ML được chọn có metadata hỗ trợ Python 3.14.
- Modular monolith giảm overhead so với microservices, phù hợp quy mô đồ án và vẫn giữ ranh giới module để tách worker sau.
- CPU-only PyTorch là baseline local; không phụ thuộc GPU/NVIDIA runtime trên máy người dùng.

## Hệ quả / điều kiện

- Phải pin và lock transitive dependency trước release.
- Cần kiểm tra tương thích thực tế trong Docker; version numbers alone are not a test result.
- PyTorch image sẽ lớn; chỉ cài ở ML worker/image khi module ML cần, không cài vào API image ban đầu.
- Database schema implementation phải tuân thủ đúng 12 bảng hiện hành.
- Production hosting, TLS, secret manager, autoscaling, backups và availability chưa được quyết định bởi ADR này.

## Nguồn tham khảo kiểm tra ngày 2026-11-27

- Node.js releases: https://nodejs.org/en/about/previous-releases
- React package releases: https://www.npmjs.com/package/react
- Vite guide: https://vite.dev/guide/
- Python downloads: https://www.python.org/downloads/
- FastAPI releases: https://github.com/fastapi/fastapi/releases
- SQLAlchemy releases: https://pypi.org/project/SQLAlchemy/
- PostgreSQL releases: https://www.postgresql.org/support/versioning/
- Pydantic: https://pypi.org/project/pydantic/
- Alembic: https://pypi.org/project/alembic/
- psycopg: https://pypi.org/project/psycopg/
- underthesea: https://pypi.org/project/underthesea/
- scikit-learn: https://pypi.org/project/scikit-learn/
- PyTorch: https://pypi.org/project/torch/
