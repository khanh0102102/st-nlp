# SECURITY DESIGN — THIẾT KẾ BẢO MẬT

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Baseline security design — cần rà soát trước production |

## 1. Mục tiêu bảo mật

Bảo vệ tài khoản, nội dung phản ánh, ảnh, vị trí, dữ liệu huấn luyện và model artifact. Đảm bảo đúng người, đúng vai trò, đúng mục đích được truy cập; mọi thao tác nhạy cảm có thể truy vết.

## 2. Tài sản cần bảo vệ

- Google identity subject, email và profile fields.
- Session/access/refresh token.
- Nội dung phản ánh, ảnh và tọa độ.
- Nhãn AI, confidence và lịch sử review.
- Dataset, sample, label và metadata nguồn.
- Training config, metrics, artifact và model version.
- Secret cấu hình, database credential, storage key và OAuth secret.
- Audit log và backup.

## 3. Phân loại dữ liệu

| Nhóm | Ví dụ | Chính sách cơ bản |
|---|---|---|
| Public | Nội dung tài liệu công khai, danh mục công khai | Có thể công bố theo phê duyệt |
| Internal | Metrics tổng hợp nội bộ, cấu hình không nhạy cảm | Chỉ người có quyền |
| Confidential | Phản ánh chưa công khai, ảnh, vị trí, thông tin tài khoản | Truy cập giới hạn, audit |
| Secret | Password, token, API key, private key | Secret manager/env, không log/Git |

Phân loại cuối cùng và thời hạn lưu trữ cần đối chiếu chính sách tổ chức/pháp luật liên quan.

## 4. Authentication

### Người dân
- Dùng Google OAuth/OIDC theo flow an toàn, ưu tiên Authorization Code Flow với PKCE khi phù hợp client.
- Backend xác minh issuer, audience, signature, expiry, state/nonce và redirect URI.
- Liên kết tài khoản bằng provider subject ổn định, không chỉ dựa vào email có thể thay đổi.
- Không nhận user ID từ client làm bằng chứng danh tính.
- Session cookie nếu chọn phải có HttpOnly, Secure và SameSite thích hợp; nếu dùng bearer token phải có chiến lược lưu trữ/refresh an toàn.

### Cán bộ/quản trị
- Phương thức xác thực và cấp tài khoản còn TBD.
- Không mặc định mọi tài khoản Google đều có quyền Admin.
- Tài khoản quản trị cần kiểm soát cấp quyền, thu hồi và có thể yêu cầu MFA theo môi trường.

## 5. Authorization và RBAC

Role gợi ý: Citizen, Moderator, Administrator, AI_Data_Manager. Role chỉ là nhóm quyền; policy cần kiểm tra action + resource + ownership + trạng thái.

Ví dụ:
- Citizen: xem/sửa hồ sơ cho phép; tạo report; đọc report thuộc chính mình.
- Moderator: xem report trong phạm vi được giao; review label; cập nhật trạng thái được phép.
- Administrator: quản trị account/role/config được phê duyệt.
- AI_Data_Manager: quản lý dataset/training/metrics/model.
- Quyền kích hoạt model production có thể là permission tách riêng.

Nguyên tắc:
- Deny by default.
- Least privilege.
- Kiểm tra tại mọi endpoint/service.
- Tránh IDOR bằng ownership/scope query.
- Không cho phép nâng quyền bằng field do client gửi.
- Thu hồi quyền có hiệu lực trong thời gian hợp lý.

## 6. Bảo vệ API và phiên

- HTTPS bắt buộc ngoài local.
- CORS allowlist theo origin được cấu hình.
- CSRF protection khi auth dùng cookie.
- Rate limit cho login, upload và endpoint có chi phí.
- Validate request bằng schema; giới hạn kích thước body.
- Không trả stack trace, SQL hoặc internal path.
- Dùng correlation ID nhưng không nhận giá trị tùy ý nguy hiểm từ client.
- Timeout và retry giới hạn cho external provider.
- Không lưu token trong localStorage nếu lựa chọn kiến trúc có thể tránh.

## 7. Upload và file storage

- Allowlist extension và MIME; kiểm tra signature/magic bytes nếu có thể.
- Đặt giới hạn số file, dung lượng và tổng dung lượng theo request.
- Sinh storage key ngẫu nhiên; không dùng trực tiếp filename làm path.
- Chặn path traversal, file polyglot và nội dung độc hại.
- Quét malware nếu môi trường yêu cầu và có dịch vụ phù hợp.
- Không public bucket mặc định.
- Download phải xác minh quyền đối với report.
- Dùng URL ký có thời hạn ngắn hoặc proxy được bảo vệ.
- Xử lý orphan file nếu DB transaction thất bại.
- Chính sách giữ/xóa file và metadata: TBD.

## 8. Bảo vệ vị trí và quyền riêng tư

- Không công khai tọa độ chi tiết cho người không có quyền.
- Trên dashboard công khai (nếu có trong tương lai), cân nhắc làm mờ/aggregate vị trí.
- Không yêu cầu location permission của thiết bị nếu người dùng có thể tự chọn vị trí.
- Chỉ thu thập trường profile/location cần thiết.
- Trình bày thông báo quyền riêng tư và mục đích sử dụng dữ liệu.

## 9. Database và secret

- Database không mở public internet trừ khi có kiểm soát tương đương.
- Dùng tài khoản DB có quyền tối thiểu.
- Mã hóa kết nối và backup theo môi trường.
- Mọi schema change qua migration review.
- Secret lưu trong environment/secret manager.
- .env không commit; .env.example chỉ chứa placeholder.
- Xoay vòng secret và revoke OAuth credentials khi nghi ngờ lộ.

## 10. Audit

Các sự kiện cần ghi:
- Đăng nhập/đăng xuất quan trọng và thất bại xác thực ở mức phù hợp.
- Tạo/sửa/xóa hoặc thay đổi trạng thái report.
- Xác nhận/chỉnh nhãn.
- Gán/thu hồi role và permission.
- Import/đóng băng dataset.
- Tạo training run.
- Đăng ký/kích hoạt/rollback model.
- Thay đổi cấu hình bảo mật.

Audit cần actor, action, resource ID, timestamp, outcome, request ID và before/after ở mức tối thiểu cần thiết. Không lưu secret hoặc toàn bộ nội dung nhạy cảm vào audit. Bảo vệ audit khỏi sửa/xóa trái quyền.

## 11. AI/ML Security

- Kiểm soát nguồn gốc và quyền sử dụng dataset.
- Phát hiện sample trùng, label noise và dữ liệu bất thường.
- Giới hạn quyền tạo/activate model.
- Quét/kiểm tra artifact trước khi nạp.
- Không tải pickle/model file không tin cậy trực tiếp.
- Ghi model checksum/version.
- Giới hạn tài nguyên training và inference.
- Có rollback khi model mới gây suy giảm.
- Không gửi nội dung phản ánh đến dịch vụ AI bên ngoài nếu chưa có phê duyệt quyền riêng tư.

## 12. Threats cần kiểm thử

- Account takeover/OAuth callback tampering.
- Broken access control/IDOR.
- Session fixation/theft và CSRF.
- Upload malware/path traversal/oversized file.
- SQL injection/XSS/HTML injection.
- Mass assignment và privilege escalation.
- Enumeration tài khoản/report.
- Data leakage qua log, API, dashboard hoặc map.
- Dataset poisoning và model artifact tampering.
- Abuse/rate exhaustion.

## 13. Incident response và production gate

Trước production phải có: contact/escalation, revoke token/secret, backup restore, log access, xử lý data breach, rollback app/model, vulnerability patching. Threat model và penetration test nên được thực hiện trước khi công khai cho người dùng thật.

## 14. TBD

- Phương thức auth của cán bộ và MFA.
- Token/session framework.
- Chính sách dữ liệu cá nhân, retention và deletion.
- Upload limits, malware scanning.
- Public/private map policy.
- Secret manager, backup encryption và incident SLA.


## 15. Phân quyền trong baseline 12 bảng

users là bảng tài khoản dùng chung cho Citizen và cán bộ. role_codes lưu danh sách mã role allow-listed: CITIZEN, RECEIVER và ADMIN. Backend phải validate role_codes, tạo principal từ identity đã xác minh và áp dụng deny-by-default policy cho từng API/resource. Không nhận role hoặc owner_id do client tự khai báo.

Baseline 12 bảng không có roles/permissions mapping table. Quyền nghiệp vụ AI/Data Manager được biểu diễn bằng permission policy tập trung và được cấp cho tài khoản được ủy quyền; không đồng nghĩa mọi ADMIN tự động được phép huấn luyện/kích hoạt model. Nếu cần role/permission động quản lý bằng giao diện/Database, phải đề xuất mở rộng schema trước khi triển khai.

Citizen phải được scope theo users.id của principal hiện tại ở mọi truy vấn reports và report_attachments. RECEIVER/ADMIN chỉ truy cập chức năng theo permission; vai trò ADMIN không bỏ qua audit hoặc các quy tắc dữ liệu.

## 16. Audit khi Database giới hạn 12 bảng

Không có bảng audit_logs trong baseline. Các business audit event phải được gửi đến audit sink append-only bên ngoài 12 bảng, có actor, action, resource_type/id, timestamp, outcome, request_id và before/after tối thiểu. Sink production phải bền vững, có access control, retention, backup và biện pháp phát hiện sửa/xóa. Provider còn TBD; không được thay bằng debug log dễ mất hoặc log chứa secret/raw_content.

prediction_reviews vẫn là lịch sử kiểm duyệt nghiệp vụ trong Database; không dùng nó để giả định đã bao phủ audit của login, quyền, status transitions, dataset freeze và model activation.
