# ST-NLP
## Smart Traffic & Urban Incident Classifier

ST-NLP là hệ thống tiếp nhận, quản lý và hỗ trợ phân loại phản ánh về giao thông và hạ tầng đô thị bằng NLP và Machine Learning.

Repository này là nguồn quản lý tập trung cho tài liệu, mã nguồn, kiểm thử và cấu hình triển khai của dự án. Hiện repository đang ở giai đoạn khởi tạo tài liệu; chưa có bản phát hành phần mềm chạy được.

## Quy tắc chạy dự án: Docker-only

ST-NLP được định hướng để người dùng chỉ cần Git và Docker Desktop/Engine + Docker Compose trên máy cá nhân. Không yêu cầu cài Python, Node.js, database server hoặc thư viện dự án trực tiếp trên host. Mọi dependency, migration, test và worker chạy trong container.

Khi triển khai hoàn chỉnh, quy trình mục tiêu là:

```bash
git clone https://github.com/khanh0102102/st-nlp.git
cd st-nlp
docker compose up --build -d
```

**Lưu ý:** docker-compose.yml hiện vẫn là scaffold chưa có service, nên lệnh trên chưa khởi chạy được ứng dụng ở trạng thái hiện tại. Các credential bên ngoài như Google OAuth có thể cần cấu hình riêng; không commit secret vào Git.

## Bắt đầu từ đâu?

1. Đọc [AGENTS.md](AGENTS.md) để hiểu quy tắc làm việc dành cho AI coding agents.
2. Đọc [Project Overview](docs/00_OVERVIEW/PROJECT_OVERVIEW.md).
3. Đọc [Project Scope](docs/00_OVERVIEW/PROJECT_SCOPE.md) và [Project Roadmap](docs/00_OVERVIEW/PROJECT_ROADMAP.md).
4. Đọc SRS, kiến trúc, thiết kế dữ liệu và API trước khi triển khai module liên quan.
5. Kiểm tra trạng thái quyết định trong tài liệu. Nội dung ghi TBD hoặc Proposed chưa phải quyết định đã được phê duyệt.

## Các cổng chức năng

- **Citizen Portal:** người dân đăng nhập, gửi phản ánh kèm nội dung, ảnh và vị trí; xem kết quả AI và lịch sử của mình.
- **Admin Portal:** cán bộ tiếp nhận, xem dashboard/bản đồ và kiểm duyệt kết quả phân loại.
- **AI & Data Management:** quản lý dataset, mẫu dữ liệu, lần huấn luyện, metrics và phiên bản mô hình.

AI chỉ đưa ra kết quả đề xuất. Cán bộ có thẩm quyền là người xác nhận hoặc điều chỉnh nhãn.

## Tài liệu

Xem [Mục lục tài liệu](docs/README.md). Tài liệu được viết bằng tiếng Việt; tên file và một số thuật ngữ kỹ thuật dùng tiếng Anh để thống nhất trong repository.

## Cấu trúc repository

- `docs/`: yêu cầu, nghiệp vụ, kiến trúc, database, API, UI/UX, phát triển, kiểm thử, triển khai và AI/ML.
- `frontend/`: ứng dụng giao diện.
- `backend/`: API và logic nghiệp vụ.
- `database/`: migration, seed và tài nguyên database.
- `tests/`: kiểm thử tích hợp và end-to-end ở cấp repository.
- `AGENTS.md`: quy tắc dành cho AI agents.

## Trạng thái hiện tại

- Tài liệu nền tảng: bản nháp khởi tạo, cần được chủ dự án rà soát/phê duyệt.
- Mã nguồn: chưa được đưa vào repository.
- Technology stack chi tiết: một số lựa chọn còn TBD.
- Database/API/11 nhãn phân loại: cần chốt đặc tả chi tiết trước khi coi là hợp đồng triển khai.

Không chạy lệnh triển khai ứng dụng cho đến khi các service và dependency được khai báo trong cấu hình tương ứng.
