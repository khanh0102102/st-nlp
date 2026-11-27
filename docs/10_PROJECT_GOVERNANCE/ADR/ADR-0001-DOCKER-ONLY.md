# ADR-0001: Docker-only cho môi trường máy cá nhân

- **Trạng thái:** Accepted
- **Ngày:** 2026-11-27
- **Người quyết định:** Chủ dự án ST-NLP
- **Bối cảnh:** Người phát triển muốn clone repository và chạy dự án mà không phải cài runtime, thư viện hoặc Database trực tiếp lên máy cá nhân.

## Quyết định

ST-NLP sử dụng Docker/Docker Compose làm cách chuẩn và bắt buộc để phát triển, kiểm thử và chạy local.

Máy host chỉ cần Git, Docker Desktop hoặc Docker Engine + Compose plugin và trình duyệt. IDE/editor là tùy chọn.

Mọi runtime, dependency, database, worker, NLP/ML, migration, seed, lint, test và training phải chạy trong container.

Mục tiêu khởi chạy sau khi sản phẩm hoàn thiện:

```bash
git clone https://github.com/khanh0102102/st-nlp.git
cd st-nlp
docker compose up --build -d
```

## Hệ quả tích cực

- Môi trường phát triển nhất quán giữa máy cá nhân và CI.
- Không cần cài Python/Node/database/package manager trên host.
- Dễ tái tạo môi trường và onboarding.
- Các lệnh quản trị/test được chuẩn hóa trong container.

## Hệ quả và đánh đổi

- Cần Docker Engine và dung lượng lưu images/volumes.
- Build lần đầu cần tải base images và dependencies.
- Cần thiết kế cache, bind mount, healthcheck, volume và startup ordering.
- Một số provider bên ngoài vẫn cần credential; Docker không loại bỏ yêu cầu cấu hình secret.
- Muốn đạt one-command phải có migration/seed orchestration và kiểm thử trên môi trường sạch.

## Điều kiện nghiệm thu

- Clone repository trên máy sạch có Git + Docker.
- `docker compose up --build -d` build và khởi chạy các service.
- Healthchecks đạt.
- Không yêu cầu cài runtime/dependency trên host.
- Test/migration chạy trong container.
- Tài liệu mô tả đúng lệnh và credential cần thiết.

## Implementation status

Quyết định đã được chấp thuận; implementation chưa hoàn thành. docker-compose.yml hiện chưa khai báo service, chưa có Dockerfiles hoặc clean-environment test.
