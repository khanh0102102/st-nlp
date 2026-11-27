# FOLDER STRUCTURE — CẤU TRÚC THƯ MỤC

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Proposed skeleton |

## 1. Cấu trúc repository cấp cao

    st-nlp/
    ├── AGENTS.md
    ├── README.md
    ├── .gitignore
    ├── docker-compose.yml
    ├── docs/
    │   ├── 00_OVERVIEW/
    │   ├── 01_REQUIREMENTS/
    │   ├── 02_ARCHITECTURE/
    │   ├── 03_DATABASE/
    │   ├── 04_API/
    │   ├── 05_UI_UX/
    │   ├── 06_DEVELOPMENT/
    │   ├── 07_TESTING/
    │   ├── 08_DEPLOYMENT/
    │   └── 09_AI_ML/
    ├── frontend/
    ├── backend/
    ├── database/
    └── tests/

## 2. Frontend structure đề xuất

Cấu trúc chi tiết phụ thuộc framework được chốt. Hướng tổ chức theo feature:

    frontend/
      src/
        app/
        shared/
          components/
          hooks/
          api/
          utils/
          styles/
        features/
          auth/
          citizen/
            profile/
            reports/
          admin/
            dashboard/
            reports/
            reviews/
            map/
            users/
          ai_management/
            datasets/
            samples/
            training_runs/
            metrics/
            models/
        assets/
      public/
      tests/

Tách portal bằng route/layout/guard rõ ràng. Nếu build thành hai ứng dụng, cấu trúc có thể tách thành citizen-app và admin-app nhưng dùng shared package có kiểm soát.

## 3. Backend structure đề xuất

Cấu trúc không phụ thuộc framework cụ thể:

    backend/
      app/
        api/
          v1/
        core/
          config/
          security/
          logging/
        domain/
          identity/
          incidents/
          classification/
          prediction/
          review/
          datasets/
          training/
          models/
        application/
          use_cases/
          services/
        infrastructure/
          database/
          repositories/
          storage/
          providers/
          workers/
        schemas/
        ml/
          preprocessing/
          features/
          models/
          evaluation/
        main.py
      migrations/
      scripts/
      tests/

Có thể tinh chỉnh theo kiến trúc framework; không bắt buộc tạo tất cả thư mục rỗng ngay.

## 4. Database structure

    database/
      migrations/
      seeds/
      diagrams/
      scripts/

Migration do công cụ được chọn quản lý; không sửa trực tiếp DB mà không có migration.

## 5. Test structure

    tests/
      unit/
      api/
      integration/
      e2e/
      fixtures/
      factories/

Backend/Frontend vẫn có thể có test gần source. Thư mục root dành cho kiểm thử tích hợp xuyên thành phần và E2E.

## 6. Tài liệu và cấu hình

- docs: tài liệu theo nhóm đã thống nhất.
- AGENTS.md: quy tắc coding agent.
- README.md: hướng dẫn vào dự án.
- .env.example: placeholder cấu hình, không chứa secret.
- docker-compose.yml: orchestration local sau khi service được xác định.
- .gitignore: loại bỏ venv, node_modules, cache, artifact và secret.

## 7. Quy tắc mở rộng

- Một feature mới phải có nơi đặt rõ ràng.
- Không đặt code nghiệp vụ vào thư mục utils chung.
- Không tạo nhiều bản sao schema/API.
- Không lưu dataset lớn, image upload, model checkpoint hoặc DB dump trong Git; dùng storage/artifact repository.
- Thư mục mới cần có README nếu mục đích không hiển nhiên.


## 8. Docker files và nguyên tắc không cài dependency trên host

Khi triển khai thật, cấu trúc cần bổ sung tối thiểu:

    st-nlp/
      docker-compose.yml
      .dockerignore
      .env.example
      frontend/
        Dockerfile
        package.json
        package-lock.json hoặc lockfile tương ứng
      backend/
        Dockerfile
        pyproject.toml/requirements file và lockfile
      docker/
        nginx/                 # nếu dùng reverse proxy
        scripts/               # entrypoint/healthcheck scripts
      database/
        migrations/
        seeds/

Các Dockerfile và manifest thực tế phụ thuộc stack được duyệt. Database/cache/queue/storage service dùng image trong Compose, không cài trực tiếp trên host.

Không tạo hoặc yêu cầu host có `.venv/`, `node_modules/`, Python, Node.js hay package manager dự án. Nếu dùng bind mount cho hot reload, dependency phải nằm trong container hoặc named volume riêng, không lấy dependency từ host.

Các lệnh dự kiến:
- Build/start: `docker compose up --build -d`
- Logs: `docker compose logs -f`
- Run test: `docker compose run --rm <service> <test-command>`
- Execute trong container: `docker compose exec <service> <command>`
- Stop: `docker compose down`

Tên service và câu lệnh cụ thể chỉ được ghi sau khi Compose thực tế được triển khai và kiểm thử.
