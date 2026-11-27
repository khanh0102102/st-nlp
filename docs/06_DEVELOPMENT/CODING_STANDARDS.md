# CODING STANDARDS — QUY CHUẨN LẬP TRÌNH

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Proposed baseline |

## 1. Nguyên tắc chung

- Code dễ đọc, dễ kiểm tra và nhất quán.
- Ưu tiên giải pháp đơn giản, không over-engineering.
- Tách presentation, application, domain và infrastructure theo mức phù hợp.
- Không lặp lại nghiệp vụ hoặc permission logic.
- Tên biến/hàm phải thể hiện ý nghĩa.
- Không để TODO quan trọng mà không tạo issue/backlog.

## 2. Python

- Tuân theo PEP 8.
- Dùng type hints cho public function, service interface và schema quan trọng.
- Dùng formatter/linter/type checker sau khi chọn công cụ; lựa chọn cụ thể TBD.
- Không dùng mutable default argument.
- Exception phải cụ thể; không bắt mọi exception rồi bỏ qua.
- Dùng context manager cho resource.
- Không print debug trong code production; dùng logger.
- Tránh circular import.
- Tách cấu hình khỏi business logic.
- Dùng timezone-aware datetime và UTC.
- Không đưa ORM entity trực tiếp vào response API.

## 3. SQLAlchemy và Database

- Model phải mô tả đúng schema và constraints.
- Query phải có scope quyền/owner từ repository hoặc service.
- Dùng parameterized query/ORM; không nối chuỗi SQL từ input.
- Nêu rõ lazy/eager loading để tránh N+1.
- Không giữ session/transaction quá lâu.
- Migration là nguồn thay đổi schema có thể review.
- Dùng transaction cho thao tác nhiều bản ghi liên quan.
- Không xóa prediction/history/audit bằng thao tác cascade nếu không có policy.
- Tránh lưu JSON cho dữ liệu cần filter/join thường xuyên.

## 4. Frontend

- Component nhỏ, có trách nhiệm rõ.
- Business rule quan trọng không chỉ nằm ở UI.
- API request đi qua client/service tập trung.
- Không nhúng secret vào bundle.
- Validate UI để hỗ trợ người dùng; Backend validate lại.
- Có loading, empty, error, success và disabled state.
- Không render nội dung người dùng như HTML không sanitize.
- Quản lý object URL preview và giải phóng khi không dùng.
- Hỗ trợ keyboard, focus và label.
- Không dùng trạng thái màu duy nhất để truyền đạt ý nghĩa.

## 5. API

- Resource path dùng danh từ và nhất quán.
- Endpoint có auth/permission được mô tả.
- Request/response schema rõ ràng.
- Error code ổn định.
- Phân trang, filter và sort có giới hạn.
- Không trả field nội bộ không cần thiết.
- Thay đổi breaking phải version/migration.
- Dùng idempotency/concurrency control với thao tác phù hợp.

## 6. AI/ML

- Tách preprocessing fit/transform đúng; không fit vectorizer trên test.
- Ghi version dữ liệu, preprocessing, label mapping và model.
- Dùng random seed khi cần tái lập.
- Báo cáo metric per-class và macro average.
- Confidence cần định nghĩa; không đổi raw decision score thành probability tùy tiện.
- Không dùng test set để tune hyperparameters.
- Lưu cấu hình và nguồn dữ liệu của training run.
- Không nạp model artifact không tin cậy.
- Inference phải validate input và có error state.
- Không để inference failure làm mất dữ liệu phản ánh.

## 7. Naming

- Python: snake_case cho module/function/variable; PascalCase cho class.
- TypeScript/JavaScript: camelCase cho variable/function, PascalCase cho component/type.
- Constant dùng UPPER_SNAKE_CASE nếu convention ngôn ngữ phù hợp.
- Database: snake_case.
- API: lowercase path, resource plural/singular thống nhất.
- Boolean đặt tên is_/has_/can_.
- ID dùng tên rõ resource, tránh id chung khi nhiều resource cùng payload.

## 8. Logging và lỗi

- Log có level và context.
- Không log password, token, secret, raw image, hoặc nội dung phản ánh đầy đủ nếu không cần.
- Có correlation ID.
- Thông báo cho người dùng phải an toàn; log kỹ thuật ghi đủ để điều tra nhưng đã làm sạch.

## 9. Comments và documentation

- Comment giải thích lý do, invariant hoặc rủi ro; không diễn giải lại code.
- Public API/service có docstring khi cần.
- README module giải thích cách dùng và phụ thuộc.
- Cập nhật tài liệu khi thay đổi contract.

## 10. Test và review

- Test độc lập, deterministic, không phụ thuộc dịch vụ thật nếu không cần.
- Dùng fixture/factory; tránh dữ liệu cá nhân.
- Kiểm tra positive, negative, boundary và permission.
- PR nhỏ, có mô tả, test evidence và migration note.
- Không merge khi CI fail trừ ngoại lệ được ghi nhận và chấp thuận.
