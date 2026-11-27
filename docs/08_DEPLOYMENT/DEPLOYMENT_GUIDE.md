# DEPLOYMENT GUIDE — HƯỚNG DẪN TRIỂN KHAI

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Template — chờ stack và service được chốt |
| Orchestration định hướng | Docker Compose cho local development |

## 1. Phạm vi

Tài liệu là khung vận hành cho local, test, staging và production. Repository hiện mới có cấu hình compose placeholder; chưa có frontend/backend service hoặc Dockerfile, vì vậy chưa thể chạy ứng dụng ST-NLP từ repository này.

## 2. Môi trường

- **Local:** phát triển và debug; dùng dữ liệu giả lập.
- **Test/CI:** tự động test, database/storage riêng.
- **Staging:** gần cấu hình production, dữ liệu đã ẩn danh.
- **Production:** dữ liệu thật, secret manager, TLS, backup và monitoring.

Không dùng cùng secret/database giữa các môi trường.

## 3. Prerequisites

Cần cài sau khi stack được chốt:
- Git.
- Docker Engine/Desktop và Docker Compose plugin.
- Runtime/package manager của Frontend/Backend.
- Database client/CLI tương ứng.
- Google OAuth test client.
- Map provider key nếu dùng.
- Quyền truy cập storage/registry theo môi trường.

Phiên bản cụ thể phải được ghi trong Technology Stack và lockfile.

## 4. Clone repository

    git clone https://github.com/khanh0102102/st-nlp.git
    cd st-nlp

Đọc AGENTS.md và docs trước khi tạo service.

## 5. Environment configuration

Tạo .env từ .env.example khi file mẫu được bổ sung. Không commit .env thật.

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

Lệnh kiểm tra sau khi compose được hoàn thiện:
    docker compose config

Khởi động:
    docker compose up --build -d

Xem log:
    docker compose logs -f

Dừng:
    docker compose down

Không chạy các lệnh trên với kỳ vọng có ứng dụng hoạt động khi chưa khai báo service. Không dùng down -v trên môi trường có dữ liệu cần giữ.

## 7. Database migration

Khi công cụ migration được chốt:
1. Kiểm tra DATABASE_URL và target environment.
2. Backup trước migration rủi ro.
3. Chạy migration upgrade.
4. Kiểm tra schema/version.
5. Chạy smoke test và API test.
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
