# IMPLEMENTATION STATUS — ST-NLP

Ngày cập nhật: 2026-11-27

## Repository baseline

- Repository: https://github.com/khanh0102102/st-nlp
- Base branch: `main`
- Working branch: `feature/project-foundation`
- Current verified source commit before this status update: `a56f6acd2fa2c5f729313f76873c57f7571f37a2`
- Main is not modified and no PR has been merged.

## Verified foundation

| Hạng mục | Trạng thái | Bằng chứng / giới hạn |
|---|---|---|
| Docker Compose configuration | Passed in CI | `docker compose config --quiet` passed |
| Docker image build | Passed in CI | API runtime, API test and frontend images built successfully |
| Database migration | Passed in CI | Alembic created the schema on a fresh PostgreSQL service |
| Category seed | Passed in CI | Seed verified exactly 11 categories |
| Database contract | Passed in CI | Test asserts exactly the 12 approved business tables |
| Backend automated tests | Passed in CI | 17 passed, 2 warnings |
| Application startup | Passed in CI | API and web stack started successfully |
| Health checks | Passed in CI | Frontend `/health`, API `/health/live`, API `/health/ready` passed |

Evidence: GitHub Actions run [46031434183](https://github.com/khanh0102102/st-nlp/actions/runs/46031434183), commit `a56f6acd2fa2c5f729313f76873c57f7571f37a2`, conclusion `success`.

## Implementation status by subsystem

| Subsystem | Status | Notes |
|---|---|---|
| Project foundation | Implemented; CI verified | Compose includes PostgreSQL, FastAPI and React/Vite served by Nginx. ML service is intentionally not in Compose until a real inference service exists. |
| Database foundation | Implemented; CI verified | 12 SQLAlchemy business models, initial Alembic migration, PostgreSQL integrity triggers and 11-category seed. |
| Backend core | Partial | Settings, DB session, signed cookie session, CSRF checks, role dependencies, local staff login, Google OIDC flow and local audit sink exist. External Google OAuth has not been tested with real credentials. |
| Citizen API | Partial | Report submission/read routes and attachment storage foundation exist. Complete citizen profile and end-user workflow have not been verified. |
| Admin API | Partial | Report review/history, dashboard, dataset registry and model registry routes exist. Authorization and full workflow coverage still need broader tests. |
| Dataset management | API foundation present | CRUD/sample validation/versioning routes exist. No real labeled dataset has been supplied or trained. |
| Model registry | API foundation present | Register/approve/activate/rollback operations exist. A real trained model artifact and model evaluation evidence are not available. |
| NLP/ML | Incomplete | `neural.py` and `training.py` are partial scaffolding. Required `classical.py`, `metrics.py`, and `preprocessing.py` modules are missing; their dependencies are not in the backend runtime requirements. There is no standalone authenticated inference service or active model. |
| Frontend | Foundation only | Current React page is a project status/health page. Citizen portal, admin portal, map and operational dashboard UI are not implemented. |
| Integration / end-to-end | Not complete | No complete citizen-to-review-to-dataset-to-training-to-inference workflow has been demonstrated. |
| Production readiness | Not ready | OAuth credentials, secret management, production storage, observability, deployment and security review remain outstanding. |

## Important architecture boundaries

- Exactly 12 business tables are approved; do not add a 13th business table without explicit approval.
- The 11 category codes and their ordering are the approved catalog.
- `reports.raw_content` is immutable.
- Predictions and reviews are append-only.
- `reports.final_category_id` is set only through an authorized human review.
- Frozen datasets and their samples are immutable.
- Training requires a FROZEN dataset.
- No placeholder prediction, fabricated confidence, or default OTHER label is allowed.
- Evidence images are not treated as image-classification input by default.

## Recent fixes on feature/project-foundation

1. `5b3ae936407d5bf3f1067e8f1c1cc207596d114b`
   - Removed the Compose ML service that referenced a nonexistent `ml/Dockerfile`.
   - ML service invocation is opt-in via a non-empty `ML_SERVICE_URL`.
   - With no configured ML service, reports retain an explicit unavailable inference record; no fake prediction is generated.
2. `a56f6acd2fa2c5f729313f76873c57f7571f37a2`
   - Changed the test invocation to `python -m pytest` so the application package is importable in the test container.

## Next implementation work

1. Complete and test missing Vietnamese preprocessing, metrics and classical NB/SVM modules.
2. Decide and implement a separate training/inference container boundary with compatible pinned ML dependencies.
3. Implement a real authenticated inference API that loads only approved/active model artifacts and appends prediction history.
4. Add database-backed API tests for report submission, attachment ownership, review authorization, dataset freeze and model lifecycle.
5. Build citizen and admin frontend routes and connect them to the implemented APIs.
6. Add integration tests for the complete workflow and verify Google OAuth using real configured credentials.
7. Generate reproducible dependency lockfiles and review deployment/security configuration.

## Verification policy

- CI evidence above applies only to the code at commit `a56f6acd2fa2c5f729313f76873c57f7571f37a2`.
- Passing foundation CI does not mean all project requirements are implemented.
- Do not mark an item complete without source review and relevant test evidence.
- Do not merge this branch into `main` automatically.
