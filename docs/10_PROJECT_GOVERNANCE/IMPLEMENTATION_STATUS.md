# IMPLEMENTATION STATUS — ST-NLP

Ngày cập nhật: 2026-11-27

## Repository baseline

- Repository: https://github.com/khanh0102102/st-nlp
- Base branch: main
- Base commit: a6f817e992e83332dec17148a9889aab324c0868 (PR #3 merged)
- Working branch: feature/project-foundation
- Current stage: Phase 1 completed; Phase 2 Project Foundation in progress.

## Milestone status

| Giai đoạn | Trạng thái | Bằng chứng / ghi chú |
|---|---|---|
| 1. Audit và baseline | Completed (static) | Main/PR/tree và tài liệu đã được đối chiếu; 11 categories, 12-table baseline, RTM và plan hiện diện |
| 2. Project Foundation | In progress | Stack ADR, Compose, API health skeleton, frontend container scaffold và env template được thêm trong nhánh này |
| 3. Database Foundation | Not started | Chưa có models, migration hoặc seed |
| 4. Backend Core | Not started | Chưa có auth, RBAC implementation hoặc business APIs |
| 5. Citizen Portal | Not started | Frontend hiện chỉ là project foundation status page |
| 6. NLP/ML | Not started | Chưa có source code model hoặc dataset |
| 7. Admin Portal | Not started | Chưa có portal nghiệp vụ |
| 8. Dashboard/Map | Not started | Chưa có dữ liệu/API/dashboard thật |
| 9. Dataset/ML Management | Not started | Chưa có management module |
| 10. Integration | Not started | Chưa có end-to-end workflow |
| 11. Testing/QA | Not started | Chưa có full suite hoặc Docker test evidence |
| 12. Deployment/Docs | Not started | Chưa đạt clean Docker startup acceptance |

## Technical decisions recorded

- ADR-0002: stack local implementation (React/TypeScript/Vite, FastAPI/Python, PostgreSQL).
- ADR-0003: initial staff provisioning, local workflow, upload and map defaults.
- ADR-0004: confidence semantics and local audit sink boundary.
- ADR-0001: Docker-only host policy (already on main).

## Verification status

- GitHub tree and source writes are reviewed through repository APIs.
- Docker CLI is not available in the execution environment used for this repository change; Docker Compose config/build/healthchecks have NOT been executed here.
- npm package-lock and Python transitive/hash lock are pending generation and verification in Docker. Direct dependency pins are present but are not a complete lock.
- No database migration or test suite has been executed.
- No OAuth, map-provider secret, production storage, real dataset or external paid service was used.

## Required next actions

1. Generate and commit reproducible dependency lockfiles inside Docker.
2. Run docker compose config/build/up from a clean environment and fix all errors.
3. Add Alembic environment and the exact 12 SQLAlchemy models/migration/seed.
4. Add backend tests for schema, constraints and catalog.
5. Continue Backend Core and authentication with provider credentials only for a real external OAuth test.

Do not update this file to "passed" until there is command output/evidence for the relevant checks.
