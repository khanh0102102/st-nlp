# IMPLEMENTATION STATUS — ST-NLP

Ngày cập nhật: 2026-11-27

## Repository baseline

- Repository: https://github.com/khanh0102102/st-nlp
- Base branch: main
- Base commit: a6f817e992e83332dec17148a9889aab324c0868 (PR #3 merged)
- Working branch: feature/project-foundation
- Current stage: Phases 1–3 implemented at source level; Phase 4 Backend Core and Phase 5 report API foundation in progress. Docker validation pending.

## Milestone status

| Giai đoạn | Trạng thái | Bằng chứng / ghi chú |
|---|---|---|
| 1. Audit và baseline | Completed (static) | Main/PR/tree và tài liệu đã được đối chiếu; 11 categories, 12-table baseline, RTM và plan hiện diện |
| 2. Project Foundation | Implemented; not runtime-verified | Docker Compose, PostgreSQL/API/web services, FastAPI health, React/Vite/Nginx scaffold, env template and direct dependency pins |
| 3. Database Foundation | Implemented; not runtime-verified | Exactly 12 SQLAlchemy models, Alembic initial schema, 11-category seed and PostgreSQL integrity/immutability triggers |
| 4. Backend Core | In progress | Local staff login, Argon2id, signed sessions/CSRF, Google OIDC adapter, role policy dependencies and staff provisioning CLI; broader security hardening pending |
| 5. Citizen Portal | Not started | Frontend hiện chỉ là project foundation status page |
| 6. NLP/ML | Not started | Chưa có source code model hoặc dataset |
| 7. Admin Portal | API foundation in progress | Admin report list/detail, prediction/review history, label review transaction and workflow transition APIs; frontend portal not implemented |
| 8. Dashboard/Map | API foundation in progress | PostgreSQL-driven summary/category aggregates and report-coordinate API; visual dashboard/map UI not implemented |
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
- Docker CLI is not available in the execution environment used for this repository change; Docker Compose config/build/healthchecks, PostgreSQL migration and API tests have NOT been executed here.
- npm package-lock and Python transitive/hash lock are pending generation and verification in Docker. Direct dependency pins are present but are not a complete lock.
- No database migration or test suite has been executed. Static source inspection only; GitHub Actions workflow was added to run Docker Compose build, migration, seed and tests on PR.
- No OAuth, map-provider secret, production storage, real dataset or external paid service was used.

## Required next actions

1. Generate and commit reproducible dependency lockfiles inside Docker.
2. Run docker compose config/build/up from a clean environment and fix all errors.
3. Add Alembic environment and the exact 12 SQLAlchemy models/migration/seed.
4. Add backend tests for schema, constraints and catalog.
5. Continue Backend Core and authentication with provider credentials only for a real external OAuth test.

Do not update this file to "passed" until there is command output/evidence for the relevant checks.
