# Mục lục tài liệu ST-NLP

**Dự án:** Smart Traffic & Urban Incident Classifier  
**Ngôn ngữ:** Tiếng Việt  
**Trạng thái bộ tài liệu:** Bản khởi tạo – cần rà soát và phê duyệt theo từng tài liệu.

## Cách đọc

Đọc theo thứ tự từ tổng quan đến chi tiết. Tài liệu đánh dấu **TBD** hoặc **Proposed** là nội dung cần xác minh/chốt, không phải quyết định đã duyệt.

## 00 — Tổng quan dự án

- [PROJECT_OVERVIEW](00_OVERVIEW/PROJECT_OVERVIEW.md) — mục tiêu, đối tượng, phân hệ và kết quả dự kiến.
- [PROJECT_SCOPE](00_OVERVIEW/PROJECT_SCOPE.md) — phạm vi trong/ngoài dự án, ràng buộc và tiêu chí thành công.
- [PROJECT_ROADMAP](00_OVERVIEW/PROJECT_ROADMAP.md) — các giai đoạn và cổng nghiệm thu.

## 01 — Yêu cầu

- [BRD](01_REQUIREMENTS/BRD.md) — nhu cầu nghiệp vụ và giá trị kỳ vọng.
- [SRS](01_REQUIREMENTS/SRS.md) — yêu cầu chức năng, phi chức năng và tiêu chí nghiệm thu.
- [CLASSIFICATION_SPECIFICATION](01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md) — nguồn chuẩn của 11 danh mục, mã và quy tắc gán nhãn.
- [USE_CASE](01_REQUIREMENTS/USE_CASE.md) — tác nhân và đặc tả ca sử dụng.
- [BUSINESS_PROCESS](01_REQUIREMENTS/BUSINESS_PROCESS.md) — quy trình nghiệp vụ đầu-cuối.

## 02 — Kiến trúc

- [SYSTEM_ARCHITECTURE](02_ARCHITECTURE/SYSTEM_ARCHITECTURE.md) — kiến trúc tổng thể và nguyên tắc phân lớp.
- [SYSTEM_DESIGN](02_ARCHITECTURE/SYSTEM_DESIGN.md) — thiết kế thành phần và luồng tương tác.
- [MODULE_DESIGN](02_ARCHITECTURE/MODULE_DESIGN.md) — trách nhiệm, đầu vào/đầu ra và phụ thuộc của module.
- [SECURITY_DESIGN](02_ARCHITECTURE/SECURITY_DESIGN.md) — xác thực, phân quyền, bảo vệ dữ liệu và audit.

## 03 — Cơ sở dữ liệu

- [DATABASE_DESIGN](03_DATABASE/DATABASE_DESIGN.md) — nguyên tắc, miền dữ liệu và ràng buộc.
- [ERD](03_DATABASE/ERD.md) — mô hình quan hệ khái niệm.
- [DATA_DICTIONARY](03_DATABASE/DATA_DICTIONARY.md) — từ điển dữ liệu và quy tắc mô tả cột.

**Database baseline:** đúng 12 bảng theo đề xuất của chủ dự án; xem DATABASE_DESIGN, ERD và DATA_DICTIONARY. Đây là thiết kế đề xuất, chưa phải migration đã chạy.

## 04 — API

- [API_SPECIFICATION](04_API/API_SPECIFICATION.md) — quy ước và danh mục endpoint dự kiến.

## 05 — UI/UX

- [UI_UX_SPECIFICATION](05_UI_UX/UI_UX_SPECIFICATION.md) — sitemap, màn hình, trạng thái và hành vi giao diện.

## 06 — Phát triển

- [TECHNOLOGY_STACK](06_DEVELOPMENT/TECHNOLOGY_STACK.md) — công nghệ đã biết, đề xuất và điểm còn TBD.
- [FOLDER_STRUCTURE](06_DEVELOPMENT/FOLDER_STRUCTURE.md) — cấu trúc mã nguồn mục tiêu.
- [CODING_STANDARDS](06_DEVELOPMENT/CODING_STANDARDS.md) — quy tắc code và review.
- [GIT_WORKFLOW](06_DEVELOPMENT/GIT_WORKFLOW.md) — branch, commit, PR và release.

## 07 — Kiểm thử

- [TEST_PLAN](07_TESTING/TEST_PLAN.md) — chiến lược, cấp độ và cổng kiểm thử.
- [TEST_CASES](07_TESTING/TEST_CASES.md) — danh sách test case ban đầu.

## 08 — Triển khai

- [DEPLOYMENT_GUIDE](08_DEPLOYMENT/DEPLOYMENT_GUIDE.md) — cấu hình môi trường, Docker, triển khai và vận hành.

## 09 — AI/ML

- [DATASET_SPECIFICATION](09_AI_ML/DATASET_SPECIFICATION.md) — cấu trúc dữ liệu, nhãn và quản lý phiên bản dataset.
- [PREPROCESSING](09_AI_ML/PREPROCESSING.md) — pipeline tiền xử lý tiếng Việt.
- [MODEL_DESIGN](09_AI_ML/MODEL_DESIGN.md) — baseline, mô hình, đánh giá, serving và quản lý phiên bản.

## Quy ước trạng thái

- **Draft:** bản nháp đang được rà soát.
- **Proposed:** phương án đề xuất, cần phê duyệt.
- **Approved:** chủ dự án đã chấp thuận.
- **TBD:** chưa có quyết định hoặc dữ liệu đủ tin cậy.
- **Deprecated:** không còn áp dụng; cần chỉ ra tài liệu thay thế.

## Quy tắc cập nhật

Mỗi thay đổi ảnh hưởng đến nghiệp vụ, API, dữ liệu, bảo mật hoặc triển khai phải cập nhật tài liệu liên quan. Không coi tài liệu là đã được phê duyệt chỉ vì file đã tồn tại trong GitHub.
