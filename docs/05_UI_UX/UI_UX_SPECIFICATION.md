# UI/UX SPECIFICATION — ĐẶC TẢ GIAO DIỆN

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Wireframe-level specification |
| Nền tảng | Web responsive |

## 1. Mục tiêu trải nghiệm

- Người dân gửi phản ánh nhanh, biết rõ thông tin nào bắt buộc và xem preview ảnh trước khi gửi.
- Cán bộ dễ tìm phản ánh, hiểu ngữ cảnh văn bản/ảnh/vị trí và kiểm duyệt AI.
- Người quản lý AI nhìn được chất lượng dữ liệu và model lifecycle.
- Hai cổng có nhận diện, route, navigation và quyền khác nhau.

## 2. Sitemap đề xuất

### Citizen Portal

    /citizen/login
    /citizen/
    /citizen/reports
    /citizen/reports/new
    /citizen/reports/{id}
    /citizen/profile

### Admin Portal

    /admin/login
    /admin/dashboard
    /admin/reports
    /admin/reports/{id}
    /admin/map
    /admin/reviews
    /admin/datasets
    /admin/datasets/{id}
    /admin/training-runs
    /admin/training-runs/{id}
    /admin/models
    /admin/users
    /admin/settings

Route trên là đề xuất ban đầu; có thể tách thành subdomain riêng. Dù chọn cách nào, Backend vẫn phải kiểm tra role/permission.

## 3. Citizen Portal — màn hình

### 3.1. Đăng nhập
- Logo/tên ST-NLP.
- Giải thích ngắn mục đích hệ thống.
- Nút đăng nhập Google.
- Thông báo lỗi OAuth thân thiện.
- Không hiển thị chức năng quản trị.

### 3.2. Trang chủ
- CTA tạo phản ánh.
- Tóm tắt số phản ánh của người dùng nếu có giá trị.
- Danh sách gần đây.
- Trạng thái phản ánh rõ ràng.
- Hướng dẫn nội dung phản ánh hữu ích.

### 3.3. Form tạo phản ánh
Các vùng:
1. Nội dung mô tả.
2. Chọn ảnh.
3. Preview ảnh.
4. Chọn vị trí.
5. Tóm tắt và xác nhận trước khi gửi.

Hành vi:
- Preview xuất hiện ngay sau khi file được chọn.
- Mỗi ảnh có nút xóa/thay thế.
- Hiển thị tiến độ upload và lỗi theo từng file.
- Không mất nội dung khi có lỗi validation nếu có thể.
- Nút gửi có trạng thái loading và chống double submit.
- Hiển thị lỗi dưới đúng trường.
- Vị trí phải cho người dùng xác nhận marker/tọa độ.
- Giới hạn ký tự/file hiển thị trước khi submit.

### 3.4. Lịch sử phản ánh
- Danh sách có mã, thời gian, tóm tắt, trạng thái và category nếu được phép.
- Có phân trang.
- Có empty state khi chưa gửi phản ánh.
- Người dùng chỉ thấy dữ liệu của mình.

### 3.5. Chi tiết phản ánh
- Nội dung đã gửi.
- Ảnh minh chứng.
- Vị trí.
- Kết quả AI: nhãn đề xuất và confidence được giải thích rõ.
- Nhãn đã kiểm duyệt nếu được hiển thị.
- Trạng thái và timeline.
- Không hiển thị ghi chú nội bộ/audit nhạy cảm của cán bộ.

## 4. Admin Portal — màn hình

### 4.1. Dashboard
- KPI tổng quan.
- Biểu đồ theo 11 category.
- Bộ lọc thời gian/trạng thái.
- Biểu đồ chỉ dùng dữ liệu có quyền.
- Không gán ý nghĩa cho số liệu khi filter chưa được áp dụng đồng bộ.

### 4.2. Danh sách phản ánh
- Search theo mã/nội dung nếu quyền cho phép.
- Filter theo category, status, time range.
- Sort và pagination.
- Phân biệt AI label và reviewed label.
- Hiển thị confidence có tooltip/giải thích.

### 4.3. Chi tiết/kiểm duyệt
- Khu vực nội dung, ảnh và map.
- Prediction card: nhãn, score/confidence, model version, thời điểm.
- Control xác nhận hoặc chọn nhãn thay thế.
- Ghi chú/lý do.
- Hiển thị trạng thái review và lịch sử.
- Xác nhận thao tác có ảnh hưởng dữ liệu.
- Khi dữ liệu bị thay đổi bởi cán bộ khác, hiển thị conflict và yêu cầu tải lại.

### 4.4. Bản đồ
- Marker/cluster.
- Filter đồng bộ với dashboard.
- Popup tối thiểu; mở chi tiết khi được phép.
- Loading/error/empty state.
- Không để lộ địa chỉ/PII qua popup không cần thiết.

### 4.5. Quản lý AI và dữ liệu
- Dataset list/detail, version và validation.
- Sample table có filter, pagination và label.
- Training run list/detail với status, duration và metrics.
- Model versions với source run, metrics, status và action theo permission.
- Confirmation trước activate/rollback.
- Cảnh báo khi model chưa đủ điều kiện.

## 5. Design system đề xuất

- Typography dễ đọc, hỗ trợ tiếng Việt đầy đủ.
- Spacing và layout nhất quán.
- Màu trạng thái có ý nghĩa, không chỉ dựa vào màu; kèm text/icon.
- Button có hierarchy primary/secondary/danger.
- Form có label, hint, required marker và error message.
- Bảng có header, sorting indicator và pagination.
- Dialog xác nhận cho thao tác phá hủy hoặc activate model.
- Accessibility: focus-visible, keyboard navigation, contrast và label cho control.

Màu sắc, font, logo, brand guideline: TBD; không tự sử dụng style mặc định như quyết định thương hiệu.

## 6. Responsive và accessibility

- Desktop là môi trường ưu tiên cho Admin Portal.
- Citizen Portal phải usable trên mobile.
- Bản đồ và bảng cần layout thay thế trên màn hình nhỏ.
- Không dùng color-only status.
- Input có label và focus order hợp lý.
- Hỗ trợ phóng to trình duyệt.

## 7. Trạng thái UI bắt buộc

Mọi trang dữ liệu phải có:
- Loading/skeleton.
- Empty state.
- Error state với retry khi phù hợp.
- Success/confirmation.
- Access denied.
- Not found.
- Conflict/stale data.
- Validation errors.

## 8. Nội dung hiển thị AI

Phải ghi rõ đây là kết quả máy đề xuất, không phải kết luận. Confidence cần có giải thích về ý nghĩa và giới hạn. Không hiển thị phần trăm nếu output là raw margin/decision score chưa hiệu chỉnh xác suất.

## 9. Nội dung cần thiết kế chi tiết sau

- Wireframe từng màn hình.
- Design tokens, logo và brand colors.
- Quy tắc hiển thị 11 categories.
- Status labels và timeline.
- Bản đồ/provider.
- Mobile breakpoint và accessibility target.
