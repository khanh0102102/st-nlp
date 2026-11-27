# SRS — SOFTWARE REQUIREMENTS SPECIFICATION

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Draft — baseline yêu cầu |
| Hệ thống | ST-NLP |
| Ngôn ngữ | Tiếng Việt |

## 1. Mục đích và phạm vi

SRS mô tả hành vi mà ST-NLP phải cung cấp cho người dân, cán bộ, quản trị viên và người quản lý AI/dữ liệu. Đây là căn cứ cho thiết kế, triển khai và kiểm thử. Các yêu cầu có TBD phải được chốt trước khi tính năng phụ thuộc được nghiệm thu.

## 2. Thuật ngữ

- **Incident/Report:** phản ánh do người dân gửi.
- **Category/Label:** một trong 11 nhóm phân loại đã được phê duyệt.
- **Prediction:** kết quả mô hình AI dự đoán.
- **Confidence:** điểm/xác suất do mô hình hoặc pipeline cung cấp; không mặc định đã được calibration.
- **Review:** thao tác cán bộ xác nhận hoặc chỉnh sửa dự đoán.
- **Dataset Sample:** một mẫu dữ liệu được quản lý trong dataset.
- **Training Run:** một lần chạy huấn luyện/thí nghiệm.
- **Model Version:** phiên bản model/artifact có thể truy xuất.

## 3. Tác nhân

- Citizen: người dân đã xác thực.
- Moderator/Staff: cán bộ tiếp nhận/kiểm duyệt.
- Administrator: quản trị tài khoản, vai trò và cấu hình.
- AI/Data Manager: quản lý dataset, training và model.
- External Services: Google OAuth, map/geocoding, file/object storage và dịch vụ hạ tầng khi được cấu hình.

## 4. Giả định và phụ thuộc

- Xác thực người dân qua Google OAuth.
- Cổng Citizen và Admin có URL/route tách biệt.
- Nội dung chính là tiếng Việt.
- Có chính xác 11 danh mục được quản lý như dữ liệu chuẩn.
- Ảnh là minh chứng trong baseline, không mặc định được phân tích bằng computer vision.
- Nhà cung cấp bản đồ, storage và DB engine cần được chốt trong Technology Stack.

## 5. Quy ước ưu tiên

- **Must:** bắt buộc cho baseline.
- **Should:** cần có nếu không có ràng buộc lớn.
- **Could:** có thể bổ sung.
- **TBD:** chưa đủ thông tin để đặc tả.

## 6. Yêu cầu chức năng

### 6.1. Xác thực và phân quyền

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| FR-AUTH-01 | Hệ thống phải cho phép người dân bắt đầu đăng nhập bằng Google OAuth | Must |
| FR-AUTH-02 | Backend phải xác minh callback/token từ Google; không tin dữ liệu nhận trực tiếp từ client | Must |
| FR-AUTH-03 | Hệ thống phải tạo hoặc liên kết tài khoản người dân theo định danh nhà cung cấp an toàn | Must |
| FR-AUTH-04 | Người dùng phải có thể đăng xuất và kết thúc phiên | Must |
| FR-AUTH-05 | Hệ thống phải cung cấp cổng quản trị riêng về URL/route và kiểm tra role trước khi truy cập | Must |
| FR-AUTH-06 | Backend phải thực thi quyền trên từng API/tài nguyên; không chỉ dựa vào route guard của Frontend | Must |
| FR-AUTH-07 | Cơ chế cấp tài khoản và đăng nhập cán bộ phải được cấu hình an toàn; phương thức cụ thể TBD | Must |

### 6.2. Hồ sơ người dân

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| FR-CIT-01 | Người dân có thể xem thông tin hồ sơ của chính mình | Must |
| FR-CIT-02 | Người dân chỉ được sửa các trường hồ sơ được cho phép | Should |
| FR-CIT-03 | Hệ thống phải lưu định danh Google ổn định và tránh dùng email làm định danh duy nhất nếu provider hỗ trợ subject ID | Must |

### 6.3. Tạo và quản lý phản ánh

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| FR-INC-01 | Người dân đã đăng nhập có thể tạo phản ánh mới | Must |
| FR-INC-02 | Phản ánh phải có nội dung văn bản hợp lệ theo giới hạn cấu hình | Must |
| FR-INC-03 | Người dân có thể tải lên ảnh theo định dạng, số lượng và dung lượng được cấu hình | Must |
| FR-INC-04 | Giao diện phải hiển thị preview ảnh ngay sau khi chọn file, trước khi gửi | Must |
| FR-INC-05 | Người dân có thể bỏ ảnh đã chọn hoặc thay bằng ảnh khác trước khi submit | Must |
| FR-INC-06 | Hệ thống phải kiểm tra file ở cả client và server; server là nơi quyết định cuối cùng | Must |
| FR-INC-07 | Người dân có thể chọn/chỉnh marker vị trí và xác nhận tọa độ trước khi gửi | Must |
| FR-INC-08 | Hệ thống phải lưu người tạo, thời điểm, nội dung, vị trí và tham chiếu file liên quan | Must |
| FR-INC-09 | Người dân có thể xem danh sách và chi tiết phản ánh của chính mình | Must |
| FR-INC-10 | Người dân có thể xem kết quả AI và trạng thái được phép công bố của phản ánh mình gửi | Must |
| FR-INC-11 | Người dân không được đọc/sửa phản ánh của tài khoản khác | Must |

### 6.4. NLP và dự đoán

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| FR-AI-01 | Hệ thống phải tiền xử lý văn bản trước khi đưa vào model theo pipeline có version | Must |
| FR-AI-02 | Hệ thống phải dự đoán một nhãn thuộc danh mục 11 nhóm hoặc trả trạng thái không thể dự đoán khi lỗi/đầu vào không hợp lệ | Must |
| FR-AI-03 | Kết quả cần lưu nhãn, confidence/score, thời điểm và model version | Must |
| FR-AI-04 | Kết quả AI phải được phân biệt với nhãn đã được cán bộ kiểm duyệt | Must |
| FR-AI-05 | Lỗi inference không được làm mất phản ánh đã tiếp nhận | Must |
| FR-AI-06 | Có thể cấu hình ngưỡng hỗ trợ chuyển kiểm duyệt; ngưỡng cụ thể TBD | Should |
| FR-AI-07 | Hệ thống phải hỗ trợ các mô hình Naive Bayes, SVM, CNN 1D và LSTM trong phạm vi nghiên cứu | Should |
| FR-AI-08 | Dự đoán phải ghi nhận pipeline/model version để tái lập và truy vết | Must |

### 6.5. Quản lý phản ánh và kiểm duyệt

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| FR-ADM-01 | Cán bộ có quyền có thể xem danh sách phản ánh theo bộ lọc được phép | Must |
| FR-ADM-02 | Cán bộ có thể xem nội dung, ảnh, vị trí, dự đoán và lịch sử liên quan | Must |
| FR-ADM-03 | Cán bộ có thể xác nhận nhãn AI đề xuất | Must |
| FR-ADM-04 | Cán bộ có thể chọn nhãn khác trong danh mục được duyệt | Must |
| FR-ADM-05 | Mỗi review phải lưu người thực hiện, thời điểm, nhãn trước/sau và ghi chú/lý do theo chính sách | Must |
| FR-ADM-06 | Hệ thống phải giữ lại prediction ban đầu, không ghi đè bằng nhãn review | Must |
| FR-ADM-07 | Cán bộ chỉ được chuyển trạng thái theo quyền và transition hợp lệ | Must |
| FR-ADM-08 | Hệ thống phải cung cấp lịch sử kiểm duyệt có thể tra cứu | Must |

### 6.6. Dashboard và bản đồ

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| FR-DASH-01 | Dashboard hiển thị tổng số phản ánh theo quyền truy cập | Must |
| FR-DASH-02 | Dashboard thống kê theo 11 danh mục | Must |
| FR-DASH-03 | Hỗ trợ lọc theo thời gian/trạng thái/danh mục khi có dữ liệu tương ứng | Should |
| FR-DASH-04 | Hiển thị vị trí phản ánh trên bản đồ | Must |
| FR-DASH-05 | Marker/cluster phải tuân theo bộ lọc và quyền truy cập | Must |
| FR-DASH-06 | Khi chọn marker, người dùng quản trị có quyền có thể mở chi tiết phản ánh | Should |

### 6.7. Dataset và dữ liệu huấn luyện

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| FR-DATA-01 | Người có quyền có thể tạo, xem, cập nhật và lưu trữ Dataset | Must |
| FR-DATA-02 | Dataset Sample phải thuộc Dataset hoặc version được xác định | Must |
| FR-DATA-03 | Có thể thêm/import, sửa nhãn, loại bỏ hoặc đánh dấu sample theo quyền | Must |
| FR-DATA-04 | Hệ thống phải validate schema, nhãn, dữ liệu rỗng và trùng lặp theo quy tắc | Must |
| FR-DATA-05 | Hệ thống cần lưu nguồn gốc và trạng thái kiểm duyệt của dữ liệu | Should |
| FR-DATA-06 | Chia train/validation/test phải tránh rò rỉ dữ liệu giữa các tập | Must |

### 6.8. Training và model lifecycle

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| FR-ML-01 | Người có quyền có thể tạo Training Run với dataset version và cấu hình rõ ràng | Must |
| FR-ML-02 | Training Run phải có trạng thái và thời điểm bắt đầu/kết thúc | Must |
| FR-ML-03 | Lưu metrics tổng thể và theo lớp khi khả dụng | Must |
| FR-ML-04 | Lưu tham chiếu artifact, code/config và model version | Should |
| FR-ML-05 | Có thể so sánh các training run | Should |
| FR-ML-06 | Model Version phải có trạng thái rõ ràng; chỉ model được phê duyệt mới được kích hoạt | Must |
| FR-ML-07 | Hỗ trợ rollback về model version trước nếu triển khai lỗi hoặc chất lượng suy giảm | Should |

### 6.9. Audit và quản trị

| ID | Yêu cầu | Ưu tiên |
|---|---|---|
| FR-AUD-01 | Lưu audit cho đăng nhập quan trọng, review, thay nhãn, thay trạng thái, thay quyền và kích hoạt model | Must |
| FR-AUD-02 | Audit ghi actor, action, resource, timestamp và kết quả; tránh lưu secret/dữ liệu nhạy cảm không cần thiết | Must |
| FR-AUD-03 | Quyền xem audit phải được giới hạn | Must |

## 7. Yêu cầu phi chức năng

| ID | Nhóm | Yêu cầu |
|---|---|---|
| NFR-SEC-01 | Bảo mật | Bắt buộc xác thực và authorization phía Backend cho tài nguyên bảo vệ |
| NFR-SEC-02 | Bảo mật | Secret chỉ được truyền qua secret/environment management, không commit |
| NFR-SEC-03 | Bảo mật | Upload phải kiểm tra định dạng, dung lượng và quyền truy cập |
| NFR-SEC-04 | Riêng tư | Người dân chỉ được xem dữ liệu của mình; dữ liệu quản trị theo RBAC |
| NFR-REL-01 | Tin cậy | Lỗi AI không được làm mất dữ liệu phản ánh đã lưu |
| NFR-DATA-01 | Toàn vẹn | Dùng foreign key, unique/check constraints và transaction phù hợp |
| NFR-AUD-01 | Truy vết | Prediction, review và model version phải liên kết được |
| NFR-PERF-01 | Hiệu năng | Thời gian phản hồi API/UI phải được đo và có ngưỡng chấp nhận được duyệt; mục tiêu số TBD |
| NFR-PERF-02 | Hiệu năng | Dashboard và bản đồ phải có phân trang/lọc hoặc cơ chế tải phù hợp với quy mô dữ liệu |
| NFR-USE-01 | Dễ dùng | UI hỗ trợ tiếng Việt, trạng thái loading/empty/error/success rõ ràng |
| NFR-USE-02 | Responsive | Các cổng web phải hoạt động trên desktop và màn hình di động phổ biến |
| NFR-MNT-01 | Bảo trì | Code phân module, có type hints/schema validation và test phù hợp |
| NFR-PORT-01 | Triển khai | Cấu hình theo môi trường; không hard-code domain/secret |
| NFR-BACKUP-01 | Khôi phục | Có kế hoạch backup/restore DB và file; RPO/RTO TBD |
| NFR-OBS-01 | Quan sát | Có log có cấu trúc, correlation/request ID và health check; không log secret |

## 8. Quy tắc dữ liệu và workflow

Danh mục 11 nhãn phải có mã ổn định, tên hiển thị, mô tả, trạng thái hiệu lực và quy tắc quản lý version. Không dùng tên hiển thị làm khóa liên kết.

Workflow trạng thái phản ánh và tên trạng thái cuối cùng: TBD. Trước khi triển khai cần xác định:
- Trạng thái tạo mới/đã gửi.
- Trạng thái chờ tiếp nhận/đang xem xét.
- Trạng thái đã phân loại/đã xác nhận.
- Trạng thái hoàn tất/không xử lý hoặc các trạng thái khác nếu nghiệp vụ yêu cầu.
- Actor được phép chuyển từng trạng thái và điều kiện chuyển.

Không triển khai các trạng thái gợi ý ở trên như enum cố định trước khi duyệt.

## 9. Tiêu chí nghiệm thu

Mỗi FR phải được ánh xạ ít nhất một test case. Nghiệm thu tổng thể yêu cầu:
- Các luồng Must hoàn thành.
- Kiểm thử quyền sở hữu và RBAC đạt.
- Migration tạo được schema trên database mới.
- Prediction và review được phân biệt, có lịch sử.
- Các số liệu Dashboard đối chiếu được với dữ liệu nguồn.
- Training run có dataset/model/config/metrics truy vết.
- Không còn lỗi nghiêm trọng chưa được chấp nhận.
- Các ngưỡng hiệu năng và ML được điền trước khi nghiệm thu chính thức.

## 10. Ngoài phạm vi

Tuân theo [PROJECT_SCOPE](../00_OVERVIEW/PROJECT_SCOPE.md). Bất kỳ chức năng mới nào ngoài scope phải qua quy trình change request.


## 11. Baseline danh mục và quy tắc lưu nhãn

Nguồn chuẩn của 11 danh mục là [CLASSIFICATION_SPECIFICATION](CLASSIFICATION_SPECIFICATION.md). Hệ thống phải có đúng 11 category theo thứ tự, tên và category_code tại tài liệu này; Dashboard hiển thị đủ 11 nhóm kể cả nhóm không có phản ánh.

Yêu cầu phân loại:
- Bài toán baseline là single-label; mỗi prediction/sample đã gán nhãn có một category chính trong catalog.
- Người dân không bắt buộc tự chọn danh mục khi gửi phản ánh; AI đưa ra nhãn đề xuất.
- Cán bộ có quyền xác nhận nhãn AI hoặc chọn một trong 11 danh mục khác.
- OTHER là lớp hợp lệ cho phản ánh hợp lệ ngoài 10 nhóm còn lại. INSUFFICIENT_INFORMATION, INVALID_INPUT, UNLABELED, NEEDS_REVIEW và INFERENCE_FAILED là trạng thái, không phải danh mục.
- Category code phải ổn định và được dùng thống nhất trong Database, API, Dataset, model label mapping và metrics. Không dùng tên hiển thị làm khóa.

## 12. Baseline Database 12 bảng

Physical design baseline đúng 12 bảng được mô tả trong DATABASE_DESIGN.md và DATA_DICTIONARY.md: users, incident_categories, reports, report_attachments, preprocessing_runs, model_versions, predictions, prediction_reviews, datasets, dataset_samples, training_runs và training_metrics.

Quy tắc dữ liệu bắt buộc:
- users quản lý cả CITIZEN, RECEIVER và ADMIN; role_codes được kiểm tra bằng allow-list/policy phía Backend. Phương thức đăng nhập cán bộ còn TBD.
- reports.raw_content giữ nguyên văn bản người dân gửi; reports.final_category_id nullable cho đến khi cán bộ xác nhận.
- report_attachments lưu metadata/storage key; binary lưu ngoài Database.
- preprocessing_runs lưu từng lần xử lý và version/config; không thay đổi raw_content.
- predictions tham chiếu report, preprocessing_run, model_version và category dự đoán; lỗi inference không làm rollback report.
- prediction_reviews append-only; thao tác review tạo review record và cập nhật reports.final_category_id trong cùng transaction, không ghi đè predictions.
- Mỗi hàng datasets là một version Dataset. Version đã FROZEN là bất biến.
- dataset_samples liên kết Dataset version, category và provenance; category_id NULL chỉ khi labeling_status cho phép chưa gán nhãn.
- training_runs tham chiếu Dataset version cụ thể; training_metrics lưu split, averaging và category khi là metric theo lớp.
- Audit tổng quát nằm ở audit sink append-only ngoài 12 bảng. Không tự thêm bảng thứ 13; provider/retention production cần được chốt.

Database Engine, kiểu dữ liệu SQL cụ thể, tập report status, auth cán bộ, storage và audit sink vẫn TBD; không coi gợi ý kỹ thuật trong Data Dictionary là quyết định stack đã duyệt.
