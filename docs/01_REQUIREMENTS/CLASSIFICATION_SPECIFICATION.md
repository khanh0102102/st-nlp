# CLASSIFICATION SPECIFICATION — ĐẶC TẢ DANH MỤC PHÂN LOẠI

| Thuộc tính | Giá trị |
|---|---|
| Hệ thống | Smart Traffic & Urban Incident Classifier (ST-NLP) |
| Phiên bản label schema | 1.0 |
| Trạng thái | Proposed baseline — tên và thứ tự do chủ dự án cung cấp; mã kỹ thuật được đề xuất |
| Bài toán | Single-label Vietnamese text classification |
| Số lượng lớp | Chính xác 11 |

## 1. Mục đích và nguồn sự thật

Tài liệu này là nguồn chuẩn duy nhất cho tên hiển thị, thứ tự và mã kỹ thuật của 11 danh mục ST-NLP. Tên tiếng Việt và thứ tự được lấy nguyên văn từ danh sách do chủ dự án cung cấp ngày 27/11/2026. Mã category_code tiếng Anh là mã kỹ thuật đề xuất để sử dụng thống nhất trong Database, API, Dataset và model label mapping.

Các tài liệu khác phải tham chiếu tài liệu này, không tự định nghĩa một danh sách hoặc cách viết khác. Không tạo thêm danh mục thứ 12. Thay đổi tên, thứ tự, mã hoặc ranh giới nghiệp vụ phải được chủ dự án phê duyệt, tăng label schema version và có kế hoạch tương thích dữ liệu/model.

## 2. Danh mục chính thức theo thứ tự

| STT | category_code | Tên hiển thị chính thức |
|---:|---|---|
| 1 | ROAD_BRIDGE_INFRA_DAMAGE | Đường/Cầu/Hạ tầng hư hỏng |
| 2 | POWER_LIGHTING | Điện lực/Chiếu sáng |
| 3 | DRAINAGE_SEWER | Cống/Hố ga/Thoát nước |
| 4 | SIDEWALK_ROADWAY | Vỉa hè/Lòng đường |
| 5 | TREES_OBSTRUCTIONS | Cây xanh/Vật cản |
| 6 | TRAFFIC_SIGNS | Biển báo |
| 7 | TRAFFIC_ORGANIZATION | Tổ chức giao thông |
| 8 | TRAFFIC_LIGHTS | Đèn tín hiệu |
| 9 | WASTE_ENVIRONMENT | Rác thải/Vệ sinh môi trường |
| 10 | OBSTRUCTIVE_PARKING | Đỗ xe cản trở |
| 11 | OTHER | Khác |

**Quy tắc mã:** category_code là định danh máy ổn định, duy nhất, không dấu, viết hoa và dùng dấu gạch dưới. Không dùng tên tiếng Việt làm khóa ngoại. Không tái sử dụng mã của danh mục đã ngừng hiệu lực.

## 3. Ý nghĩa phạm vi nhãn

Tên bên trên là tên chính thức. Nội dung dưới đây là hướng dẫn phân loại ban đầu để xây dựng Dataset và kiểm thử; ví dụ không tạo thêm danh mục và không thay thế hướng dẫn nghiệp vụ chi tiết.

| Mã | Phạm vi nhận diện ban đầu |
|---|---|
| ROAD_BRIDGE_INFRA_DAMAGE | Hư hỏng vật lý của đường, cầu và hạ tầng giao thông/đô thị có tính kết cấu hoặc mặt công trình, ví dụ nứt, sụt lún, ổ gà, hư hỏng kết cấu cầu. |
| POWER_LIGHTING | Sự cố điện lực và hệ thống chiếu sáng công cộng, ví dụ mất điện, dây điện nguy hiểm, đèn chiếu sáng đường phố không hoạt động. |
| DRAINAGE_SEWER | Sự cố cống, hố ga và thoát nước, ví dụ tắc cống, ngập do thoát nước, nắp hố ga hỏng hoặc mất. |
| SIDEWALK_ROADWAY | Vấn đề liên quan không gian/vận hành vỉa hè và lòng đường, bao gồm tình trạng sử dụng, mặt bằng hoặc lấn chiếm khi không thuộc nhóm chuyên biệt hơn. |
| TREES_OBSTRUCTIONS | Cây xanh, cành cây hoặc vật cản trên không gian công cộng gây cản trở/nguy hiểm, không phân loại vật cản là xe đỗ vào nhóm này. |
| TRAFFIC_SIGNS | Biển báo giao thông bị hư hỏng, mất, che khuất hoặc có nội dung/vị trí bất cập. |
| TRAFFIC_ORGANIZATION | Bất cập trong tổ chức, phân luồng, phân làn, hướng lưu thông hoặc bố trí giao thông không thuộc sự cố riêng của biển báo/đèn tín hiệu. |
| TRAFFIC_LIGHTS | Sự cố đèn tín hiệu giao thông, ví dụ mất tín hiệu, sai chu kỳ, đèn không sáng hoặc hiển thị bất thường. |
| WASTE_ENVIRONMENT | Rác thải, vệ sinh công cộng và ô nhiễm môi trường tại khu vực đô thị. |
| OBSTRUCTIVE_PARKING | Phương tiện dừng/đỗ gây cản trở giao thông, lối đi bộ, lối ra vào hoặc tiếp cận công trình. |
| OTHER | Phản ánh hợp lệ, có nội dung có thể hiểu được nhưng không thuộc 10 nhóm còn lại. |

Ranh giới giữa nhóm 1 và 4, nhóm 5 và 10, nhóm 6–7–8 có thể giao nhau trong một số phản ánh. Khi có nhiều vấn đề, dùng vấn đề chính được nêu rõ nhất theo guideline; nếu không xác định đáng tin cậy, đưa vào hàng đợi kiểm duyệt thay vì tự tạo nhãn đa lớp. Các ví dụ/rule ranh giới cần được bổ sung bằng dữ liệu thực tế và phê duyệt nghiệp vụ trước khi làm ground truth chính thức.

## 4. Khác không đồng nghĩa với không đủ thông tin

- **OTHER** là một trong 11 lớp hợp lệ của bài toán phân loại: phản ánh hợp lệ nhưng nằm ngoài 10 nhóm còn lại.
- **UNLABELED / NEEDS_REVIEW** là trạng thái dữ liệu chưa có nhãn đáng tin cậy; không phải category.
- **INSUFFICIENT_INFORMATION** là trạng thái xử lý khi văn bản quá mơ hồ/thiếu thông tin để phân loại; không phải category.
- **INVALID_INPUT** là trạng thái đầu vào không hợp lệ, ví dụ rỗng hoặc chỉ chứa ký tự không có ý nghĩa.
- **INFERENCE_FAILED** là trạng thái kỹ thuật khi pipeline/model lỗi; không phải category.

Không ép các trạng thái trên thành OTHER. Trong Database, category_id có thể NULL khi prediction thất bại hoặc sample chưa được gán nhãn; trạng thái tương ứng phải được lưu riêng.

## 5. Quy tắc nghiệp vụ và AI

1. Bài toán baseline là single-label: mỗi prediction/sample đã gán nhãn có tối đa một category chính.
2. Người dân không bắt buộc tự chọn category khi gửi phản ánh; hệ thống đề xuất nhãn bằng AI.
3. Cán bộ có quyền xác nhận nhãn AI hoặc chọn một nhãn khác trong đúng 11 danh mục.
4. Nhãn AI và nhãn cuối cùng của cán bộ phải lưu riêng; không ghi đè prediction.
5. Dataset chỉ sử dụng nhãn đã được gán/kiểm duyệt theo labeling policy; mọi sample cần trạng thái và nguồn gốc.
6. Cùng category_code và cùng label schema version phải được dùng xuyên suốt API, training, inference và metrics.
7. Model output phải được validate để chỉ nhận một trong 11 category_code; output ngoài tập hợp phải được coi là lỗi mapping.

## 6. Seed và quản lý catalog

- Khởi tạo đúng 11 bản ghi bằng seed idempotent trong migration/seed container.
- Có unique constraint trên category_code và sort_order.
- Các category code và tên hiển thị là catalog cố định; không cung cấp CRUD tạo/xóa category tùy ý cho người dùng quản trị.
- Không xóa category đang được reports, predictions, reviews, dataset_samples hoặc metrics tham chiếu.
- is_active (nếu được dùng) chỉ phục vụ quản trị chuyển đổi theo change approval; baseline phải có đủ 11 danh mục active.
- Đổi tên hiển thị không làm thay đổi category_code. Đổi mã hoặc thay đổi định nghĩa lớp phải version label schema và đánh giá tác động lên Dataset/model.

## 7. Contract dùng chung

- Database: incident_categories.category_code là unique stable key.
- API: request/response trao đổi category_code và category object có id, code, name, sort_order.
- Frontend: hiển thị tên tiếng Việt theo sort_order; không hard-code danh sách ở nhiều component nếu API catalog sẵn có.
- NLP/ML: model label encoder/decoder map đúng 11 category_code theo label schema version.
- Dashboard: luôn hiển thị đủ 11 nhóm, kể cả nhóm có count bằng 0.
- Dataset: category_id là FK đến incident_categories; không dùng text label tự do làm khóa.

## 8. Test acceptance

- Seed tạo chính xác 11 category, không trùng code hoặc sort_order.
- Tên và thứ tự hiển thị đúng bảng ở mục 2.
- category_code không bị thay đổi khi đổi tên hiển thị.
- API từ chối code không tồn tại hoặc category không hợp lệ.
- Prediction/model mapping chỉ phát ra 11 code hợp lệ.
- OTHER chỉ dùng cho phản ánh hợp lệ ngoài 10 nhóm; thiếu thông tin/lỗi inference có trạng thái riêng.
- Dashboard trả đủ 11 nhóm.
- Dataset import từ chối nhãn tự do không thuộc catalog và xử lý trạng thái chưa gán nhãn riêng.
