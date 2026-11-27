# DEPLOYMENT GUIDE — HƯỚNG DẪN TRIỂN KHAI

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.1 |
| Trạng thái | Local Docker foundation — CI verified; production deployment chưa sẵn sàng |
| Orchestration | Docker Compose |

## 1. Phạm vi và trạng thái đã xác minh

Repository có Docker Compose stack gồm PostgreSQL 18.7, FastAPI, React/Vite build được phục vụ bởi Nginx. CI run #17 trên code commit 58b6acf5890c416b9d55812afdacf6739d74c560 đã xác minh:

- docker compose config --quiet và build các image app/test.
- Alembic migration trên PostgreSQL mới.
- Seed/verify chính xác 11 danh mục.
- 37 backend tests passed, 1 test skip trong API runtime image.
- 8 CNN/LSTM neural component tests passed trong CPU ML test image.
- DB-backed NB/SVM training integration trên dataset tổng hợp: TrainingRun SUCCEEDED, 120 TrainingMetric rows, ModelVersion, SHA-256 artifact và artifact reload đều được kiểm tra.
- ML trainer CLI --help chạy thành công.
- Khởi động stack và kiểm tra frontend/API liveness/readiness.

CI không chứng minh Google OAuth với tài khoản thật, frontend portal đầy đủ, model quality trên dataset thật hoặc production readiness. DB-backed training test chỉ xác minh mechanics bằng synthetic CI samples.

## 2. Branch hiện tại

Code triển khai đang nằm trên feature/project-foundation. Nhánh main chưa nhận các commit này. Cho đến khi pull request được xem xét và merge theo quyết định của chủ dự án, clone branch triển khai bằng:

    git clone --branch feature/project-foundation --single-branch https://github.com/khanh0102102/st-nlp.git
    cd st-nlp

Không dùng clone mặc định nếu cần đúng implementation hiện tại.

## 3. Công cụ trên máy host

Cần có Git, Docker Desktop trên Windows/macOS hoặc Docker Engine và Compose plugin trên Linux, cùng trình duyệt web.

Không cần cài Python, Node.js, npm, pip, PostgreSQL, thư viện NLP/ML hoặc compiler của dự án trên host. Dependencies được cài khi build image.

Google OAuth credentials và các secret tích hợp thật phải được cấu hình qua .env/secret manager; không commit secret.

## 4. Khởi động local

.env.example đã có trong repository. Các mặc định local đủ cho stack cơ bản. Sao chép file khi cần cấu hình riêng.

PowerShell:

    Copy-Item .env.example .env

Bash:

    cp .env.example .env

Khởi động:

    docker compose up --build -d
    docker compose ps

Mở http://localhost:8080.

Xem log:

    docker compose logs -f
    docker compose logs -f api

Dừng stack và giữ dữ liệu:

    docker compose down

Cảnh báo: docker compose down -v xóa named volumes gồm database, uploads, model artifacts và audit local. Không chạy lệnh này khi cần giữ dữ liệu.

## 5. Compose services và profiles

- Default stack: db, api, web.
- api-test ở profile test: chạy Alembic, seed và backend pytest.
- ml-test ở profile test: chạy CNN/LSTM component tests trong image có CPU PyTorch.
- ml-trainer ở profile training: CLI huấn luyện riêng. API runtime không cài thư viện ML nặng.

CI chạy test profiles riêng biệt rồi mới khởi động stack bình thường. Không bật trainer như service nền khi không huấn luyện.

## 6. Migration và seed

Khi database healthcheck đạt, API entrypoint chạy Alembic upgrade head, seed 11 danh mục rồi khởi động Uvicorn.

CI đã xác minh migration trên database mới và seed idempotent đúng 11 danh mục. Schema baseline vẫn đúng 12 bảng nghiệp vụ; không thêm bảng nếu chưa được chủ dự án chấp thuận.

Với staging/production, migration cần release procedure, backup, approval và kiểm soát chạy một lần; không xem cơ chế local entrypoint là production migration strategy đã được nghiệm thu.

## 7. Kiểm thử trong Docker

Chạy backend tests và migration/seed:

    docker compose --profile test run --build --rm api-test

Chạy neural component tests trong CPU PyTorch image:

    docker compose --profile test run --build --rm --no-deps ml-test

Kiểm tra cấu hình:

    docker compose config --quiet

Các lệnh trên không yêu cầu cài thư viện lên host. CI run #17 là bằng chứng được xác minh cho snapshot code nêu tại mục 1.

## 8. Huấn luyện mô hình trong Docker

Trainer là CLI one-shot, không phải inference service. Xem CLI:

    docker compose --profile training run --build --rm --no-deps ml-trainer --help

Cú pháp đã được smoke-test qua CLI --help và NB/SVM orchestration đã được tích hợp với PostgreSQL bằng synthetic CI data; các lệnh train bên dưới vẫn chưa được xác minh trên frozen dataset thật/được duyệt:

    docker compose --profile training run --rm --no-deps ml-trainer train --dataset-id <DATASET_UUID> --model-family NB --created-by <ADMIN_USER_UUID>
    docker compose --profile training run --rm --no-deps ml-trainer train --dataset-id <DATASET_UUID> --model-family SVM --created-by <ADMIN_USER_UUID>
    docker compose --profile training run --rm --no-deps ml-trainer train --dataset-id <DATASET_UUID> --model-family CNN_1D --created-by <ADMIN_USER_UUID>
    docker compose --profile training run --rm --no-deps ml-trainer train --dataset-id <DATASET_UUID> --model-family LSTM --created-by <ADMIN_USER_UUID>

Điều kiện theo code hiện tại:

- Dataset phải có trạng thái FROZEN.
- Phải có sample đã gán nhãn trong đủ TRAIN, VALIDATION và TEST.
- TRAIN phải có đủ 11 danh mục.
- Text trùng không được rò rỉ giữa các split.
- --seed đặt random seed; --epochs áp dụng cho CNN_1D/LSTM.

Artifacts ghi vào named volume model_artifacts_data, được chia sẻ với API. Không xóa volume nếu cần giữ artifacts.

Score NB là MODEL_PROBABILITY_UNCALIBRATED; score SVM là RAW_DECISION_SCORE. Không hiển thị chúng như calibrated probability hoặc tự động duyệt phản ánh.

## 9. Model deployment boundary

Đã có training CLI, preprocessing, metrics, NB/SVM, CNN/LSTM components và artifact metadata. Chưa có authenticated inference service hoàn chỉnh để tải model ACTIVE/APPROVED, xác minh checksum, chạy prediction và append lịch sử. Khi không có active model, API không được tạo category mặc định hoặc confidence giả.

## 10. Google OAuth và secrets

- Google OAuth thật cần client ID/secret, authorized origins và redirect URI chính xác.
- Dùng HTTPS ở staging/production; không dùng wildcard redirect URI.
- Không commit .env hoặc credentials.
- CI hiện không xác minh luồng Google account thật.

## 11. Production checklist

- [ ] Domain và TLS.
- [ ] Secret manager và rotation.
- [ ] Google OAuth thật đã được xác minh.
- [ ] DB private network, least-privilege account.
- [ ] Backup/restore test và RPO/RTO.
- [ ] File storage private, malware scanning và retention.
- [ ] CORS/rate limit/security headers.
- [ ] Staff MFA và provisioning policy.
- [ ] Audit sink bền vững, monitoring/alerting.
- [ ] Inference service có auth, timeout và model rollback.
- [ ] Model được đánh giá/duyệt trên dataset có nguồn gốc hợp lệ.
- [ ] Citizen/Admin portals và E2E workflows hoàn chỉnh.
- [ ] Privacy notice/retention policy.
- [ ] Release note và vận hành.

## 12. Rollback

- App: deploy lại image/version trước.
- Model: chỉ chuyển về version đã duyệt và đã lưu checksum.
- Database: ưu tiên forward-fix; restore backup chỉ khi có kế hoạch mất dữ liệu rõ ràng.
- Files: bảo toàn storage version/backup.
- Mọi rollback cần ghi audit.

## 13. TBD

Hosting platform, domain, TLS provider, production storage, map/geocoding provider, secret manager, monitoring, retention, backup frequency, RPO/RTO và deployment approval vẫn mở. CI local foundation không phải production certification.
