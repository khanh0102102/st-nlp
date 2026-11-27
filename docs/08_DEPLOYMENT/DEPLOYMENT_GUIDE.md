# DEPLOYMENT GUIDE — HƯỚNG DẪN TRIỂN KHAI

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Template — chờ stack và service được chốt |
| Orchestration | Docker Compose — bắt buộc cho local development và là baseline container deployment |

## 1. Phạm vi

Tài liệu là khung vận hành cho local, test, staging và production.

**Yêu cầu của chủ dự án:** máy cá nhân không cài runtime hoặc dependency riêng của ST-NLP. Toàn bộ Frontend, Backend, Database, Worker, NLP/ML và công cụ kiểm thử phải được chạy trong Docker container.

**Trạng thái repository hiện tại:** docker-compose.yml mới là placeholder với services rỗng; chưa có Dockerfile hoặc service thực tế. Vì vậy lệnh khởi chạy mục tiêu bên dưới chưa chạy được cho đến khi AI triển khai đầy đủ Dockerfiles, Compose services, cấu hình và healthchecks.

## 2. Môi trường

- **Local:** phát triển và debug; dùng dữ liệu giả lập.
- **Test/CI:** tự động test, database/storage riêng.
- **Staging:** gần cấu hình production, dữ liệu đã ẩn danh.
- **Production:** dữ liệu thật, secret manager, TLS, backup và monitoring.

Không dùng cùng secret/database giữa các môi trường.

## 3. Prerequisites

### Công cụ duy nhất cần có trên máy host

- Git để clone repository.
- Docker Desktop (Windows/macOS) hoặc Docker Engine + Docker Compose plugin (Linux).
- Trình duyệt web.
- IDE/editor là tùy chọn.

**Không cài trên host:** Python, Node.js, npm/pnpm/yarn, PostgreSQL/MySQL, Redis, thư viện NLP/ML, compiler hoặc package manager của dự án.

Docker Desktop/Engine là yêu cầu hệ thống; Docker sẽ tải base images và build dependency vào image/container. Điều đó không đồng nghĩa với việc cài thư viện dự án vào Windows/macOS/Linux host.

Credential của Google OAuth hoặc map provider, nếu cần cho chức năng tích hợp thật, phải được cung cấp riêng qua .env/secret. Credential không phải thư viện và không được commit.

## 4. Clone repository

    git clone https://github.com/khanh0102102/st-nlp.git
    cd st-nlp

Đọc AGENTS.md và docs trước khi tạo service.

## 5. Environment configuration

Khi .env.example được bổ sung, copy thành .env nếu môi trường cần cấu hình riêng. Giá trị local mặc định nên được thiết kế để các container cơ bản có thể khởi động mà không cần secret bên ngoài. Không commit .env thật.

Google OAuth thật và một số map provider có thể cần credential. Khi thiếu credential, ứng dụng phải báo cấu hình chưa đầy đủ hoặc cung cấp chế độ local development được cô lập rõ ràng; tuyệt đối không vô hiệu hóa bảo mật trong staging/production.

Nhóm biến dự kiến:
- APP_ENV, APP_SECRET_KEY, APP_BASE_URL.
- DATABASE_URL.
- GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REDIRECT_URI.
- SESSION/JWT configuration theo auth strategy.
- STORAGE endpoint/bucket/credentials.
- MAP provider key.
- MODEL_REGISTRY/ARTIFACT_STORAGE.
- LOG_LEVEL, CORS_ALLOWED_ORIGINS.

Tên biến cuối cùng phải thống nhất với code/config schema; không tự tạo nhiều tên tương tự.

## 6. Docker Compose

File docker-compose.yml hiện chỉ là placeholder tên dự án và services rỗng để giữ vị trí cấu hình. Chưa có service chạy được. Sau khi chốt stack, bổ sung:
- frontend service hoặc hai frontend service.
- backend API.
- worker nếu có.
- database.
- cache/queue nếu cần.
- local object storage nếu cần.

### Khởi động mục tiêu sau khi clone

    git clone https://github.com/khanh0102102/st-nlp.git
    cd st-nlp
    docker compose up --build -d

Mục tiêu nghiệm thu là lệnh cuối cùng tự build image, khởi động các service, chờ Database healthy, chạy migration/seed an toàn và đưa ứng dụng lên trạng thái sẵn sàng. Người dùng không phải chạy pip install, npm install hoặc cài database trên host.

### Lệnh quản trị

Kiểm tra cấu hình:

    docker compose config

Xem trạng thái:

    docker compose ps

Xem log:

    docker compose logs -f

Dừng service nhưng giữ dữ liệu named volume:

    docker compose down

Chạy test trong container (thay <service> và <test-command> theo Compose thực tế):

    docker compose run --rm <service> <test-command>

Chạy lệnh trong container đang chạy:

    docker compose exec <service> <command>

**Cảnh báo:** `docker compose down -v` xóa named volumes và có thể xóa Database/dữ liệu; chỉ dùng khi chủ động reset dữ liệu local.

Không tuyên bố lệnh one-command hoạt động cho đến khi đã build/test trên môi trường sạch.

## 7. Database migration

Migration tool và migration command phải chạy bên trong container; không yêu cầu người dùng cài DB client hoặc migration CLI trên host.

Local Compose nên có quy trình migration tự động an toàn (ví dụ one-shot migration service phụ thuộc Database healthcheck, Backend chờ migration hoàn tất). Seed phải idempotent. Không chạy migration đồng thời ở nhiều replica.

Với staging/production:
1. Kiểm tra DATABASE_URL và target environment qua secret/config.
2. Backup trước migration rủi ro.
3. Chạy migration bằng release/migration container.
4. Kiểm tra schema/version.
5. Chạy smoke test.
6. Ghi migration version vào release record.

Không chỉnh schema production thủ công.

## 8. Static assets và upload

- Frontend build không được chứa secret.
- Upload storage cần private access.
- Signed URL có expiry ngắn nếu dùng.
- Giới hạn upload theo policy.
- Backup metadata và file có kế hoạch nhất quán.

## 9. Google OAuth deployment

- Đăng ký origin và redirect URI chính xác theo từng môi trường.
- Dùng HTTPS trên staging/production.
- Không dùng wildcard redirect URI.
- Secret OAuth chỉ nằm trong secret manager/env.
- Kiểm tra state/nonce, logout và callback sau deployment.

## 10. Model deployment

- Artifact có checksum và version.
- Model phải tương thích preprocessing/label mapping.
- Chỉ kích hoạt model đã đánh giá và duyệt.
- Có health check inference và timeout.
- Giữ model version trước để rollback.
- Không tự động promote model chỉ dựa trên training accuracy.

## 11. Production checklist

- [ ] Domain và TLS.
- [ ] OAuth origins/callback chính xác.
- [ ] Secret manager.
- [ ] DB private network, least-privilege account.
- [ ] Migrations đã kiểm tra.
- [ ] File storage private và backup.
- [ ] CORS/rate limit/headers.
- [ ] Admin account/role review.
- [ ] Audit/logging/monitoring.
- [ ] Backup/restore test.
- [ ] Model artifact verified và rollback plan.
- [ ] Smoke test các luồng trọng yếu.
- [ ] Privacy notice/retention policy.
- [ ] Release note và người trực vận hành.

## 12. Rollback

Rollback phải xét cả application, database và model:
- App: deploy lại image/version trước.
- Model: chuyển active reference về model version đã lưu.
- Database: ưu tiên forward-fix; chỉ restore backup khi có kế hoạch rõ vì có thể mất dữ liệu mới.
- File: bảo toàn storage version/backup.
- Mọi rollback cần ghi audit và thông báo người phụ trách.

## 13. TBD

Hosting platform, domain, TLS provider, DB engine, storage, map provider, CI/CD, secret manager, monitoring, backup frequency, RPO/RTO và deployment approval.

## Huấn luyện mô hình trong Docker

API runtime không cài các thư viện ML nặng. Image huấn luyện riêng được bật bằng profile `training` và dùng chung PostgreSQL cùng named volume `model_artifacts_data` với API.

Khởi động stack trước để API thực hiện migration và seed:

```bash
docker compose up --build -d
```

Build image huấn luyện và xem CLI:

```bash
docker compose --profile training build ml-trainer
docker compose --profile training run --rm ml-trainer --help
```

Huấn luyện NB hoặc SVM trên một dataset đã ở trạng thái FROZEN:

```bash
docker compose --profile training run --rm ml-trainer train --dataset-id <DATASET_UUID> --model-family NB --created-by <ADMIN_USER_UUID>
docker compose --profile training run --rm ml-trainer train --dataset-id <DATASET_UUID> --model-family SVM --created-by <ADMIN_USER_UUID>
```

Có thể dùng `--seed` và `--epochs` để cấu hình lần chạy; `--epochs` chỉ áp dụng cho CNN_1D/LSTM. Các model artifacts được lưu trong named volume dùng chung với API. Không xóa volume nếu cần giữ model artifacts hoặc dữ liệu PostgreSQL.

Lưu ý: training yêu cầu dataset FROZEN có đủ ba split TRAIN/VALIDATION/TEST, và TRAIN phải có đủ 11 category. Score của SVM là `RAW_DECISION_SCORE`; xác suất Naive Bayes là `MODEL_PROBABILITY_UNCALIBRATED`. Cả hai chưa được coi là calibrated probability.
