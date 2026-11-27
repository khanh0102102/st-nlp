# ADR-0003: Local Authentication, Workflow, Storage và Map baseline

- Trạng thái: Accepted for initial local implementation by delegated Master Prompt
- Ngày quyết định: 2026-11-27
- Phạm vi: Development/local demo; không tự động áp dụng policy production

## Bối cảnh

Các yêu cầu nghiệp vụ đã quy định Citizen Google sign-in, staff permission, upload ảnh, vị trí, review và audit; các chi tiết triển khai còn TBD. Master Prompt mới giao quyền chọn phương án triển khai ban đầu, nhưng cấm tự dùng secret/dịch vụ có phí hoặc triển khai production.

## Quyết định

### Authentication và staff provisioning

- Citizen: Google OpenID Connect Authorization Code Flow, state/nonce validation và PKCE; provider subject là định danh ổn định.
- Staff local: tài khoản được provision bằng lệnh quản trị nội bộ; không có public staff registration. Password phải hash bằng Argon2id; không cấp quyền staff dựa trên email Google.
- Session browser dùng cookie ký phía server: HttpOnly, SameSite=Lax, Secure ngoài localhost; session ngắn hạn và user/role được tải lại từ DB khi xử lý request.
- Với cookie authentication, mọi mutation phải có CSRF protection và kiểm tra Origin. Logout phải xóa cookie; account disable/role change phải có hiệu lực qua kiểm tra DB.
- MFA và phương thức staff identity cho môi trường production cần được đánh giá trước khi public.

### Role và permission

- Giữ role codes baseline trong users.role_codes: CITIZEN, RECEIVER, ADMIN.
- Không tạo bảng roles/permissions và không thêm role thứ tư trong baseline.
- Permission được tập trung trong policy module và deny-by-default. AI/Data Management chỉ được mở cho principal được policy cấp quyền; local bản đầu ADMIN-only, không đồng nghĩa mọi thao tác production tự động cấp cho mọi admin.
- Không nhận owner_id, reviewer_id hoặc role từ client làm bằng chứng quyền.

### Report workflow

Các trạng thái local v1:
- SUBMITTED
- UNDER_REVIEW
- IN_PROGRESS
- RESOLVED
- REJECTED
- CLOSED

Transition:
- SUBMITTED -> UNDER_REVIEW hoặc REJECTED.
- UNDER_REVIEW -> IN_PROGRESS hoặc REJECTED.
- IN_PROGRESS -> RESOLVED hoặc REJECTED.
- RESOLVED -> IN_PROGRESS (reopen chỉ ADMIN) hoặc CLOSED.
- REJECTED -> CLOSED.
- CLOSED là terminal.

RECEIVER và ADMIN được chuyển trạng thái theo transition policy; chỉ ADMIN được reopen RESOLVED. Citizen chỉ đọc timeline công khai, không tự chuyển trạng thái. Mỗi transition phát audit event. Không tạo bảng status history thứ 13; audit sink giữ event tổng quát. Cập nhật state phải có concurrency check.

### Upload và local storage

- Local chỉ nhận ảnh JPEG, PNG và WebP; tối đa 5 file trên một report; tối đa 10 MiB mỗi file.
- Backend kiểm tra extension, magic bytes/MIME đã xác minh, kích thước, file name/path và checksum; sinh storage key ngẫu nhiên.
- Files nằm trong private named volume, không public write và không commit Git.
- Download phải kiểm tra quyền sở hữu/quyền staff. Binary file ngoài Database; report_attachments giữ metadata/storage key.
- Malware scanning, retention, deletion SLA và production object-storage provider chưa được quyết định; không coi local volume là giải pháp production/backup.

### Location và map

- Tọa độ dùng WGS84, EPSG:4326; latitude/longitude cùng null hoặc cùng có giá trị, kiểm tra miền hợp lệ.
- Local/demo dùng Leaflet với OpenStreetMap standard tile layer và attribution. Không bulk-download, không tự host tile, không xem public OSM tile service là SLA/production provider.
- Production map/tiles/geocoding provider, quota, terms và privacy policy phải được rà soát trước triển khai public.

### UI baseline

Chưa có brand guideline; dùng design tokens trung tính, typography dễ đọc tiếng Việt, responsive và accessibility semantics. Không coi màu/logo hiện tại là thương hiệu đã được chủ dự án phê duyệt.

## Hệ quả

- Có thể xây local authentication/storage/map adapters mà không cần dịch vụ trả phí hoặc secret thật.
- Production credentials, MFA, data retention, malware scan, object storage và map service vẫn là các cổng phát hành riêng.
- Không thay đổi giới hạn 12 bảng hoặc 11 danh mục.


## Implementation notes

- Google OIDC routes are implemented with Authlib 1.9.10 using OIDC discovery, Authorization Code flow, PKCE S256 and Authlib state validation through a short-lived Starlette session cookie.
- Local staff passwords use Argon2id through pwdlib[argon2] 0.4.2; local CLI requires at least 12 characters and stores only the password hash.
- Application session is signed, HttpOnly, SameSite=Lax and has an eight-hour max age. Account status and roles are loaded from PostgreSQL for each authenticated request.
- Authenticated mutation requests require a signed user-bound CSRF token, matching CSRF cookie/header and origin allow-list check.
- Citizen report API, staff review/status API and private attachment upload/download routes are implemented in the local baseline. API has no UI portal yet.
- Google sign-in is inactive until GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET and GOOGLE_REDIRECT_URI are configured. Staff login is available using the local CLI-provisioned account.
- Login rate limiting, staff MFA and production identity policy remain release blockers; this local auth code is not a production security certification.
