# REQUIREMENTS TRACEABILITY MATRIX — ST-NLP

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 0.2 |
| Cập nhật | 2026-11-28 |
| Baseline | main commit `a6f817e992e83332dec17148a9889aab324c0868`; implementation trên feature/project-foundation |
| Nguồn yêu cầu | BRD.md, SRS.md, CLASSIFICATION_SPECIFICATION.md |
| Trạng thái | RTM cập nhật theo source và Docker CI evidence; nhiều yêu cầu lớn còn PARTIAL/NOT_STARTED |

## 1. Quy ước

- Mỗi dòng ánh xạ một Requirement ID trong SRS; BRD được ánh xạ tổng hợp ở mục 3.
- API column là endpoint/route theo hợp đồng; trạng thái triển khai xem cùng Implementation Status và source code.
- Database là baseline 12 business tables; PostgreSQL/SQLAlchemy/Alembic implementation có trên feature branch.
- Test IDs là mapping tới inventory; execution evidence được ghi theo CI run/commit trong Implementation Status và TEST_CASES.
- NOT_STARTED nghĩa là chưa có code. BLOCKED nghĩa là phải có quyết định/phụ thuộc trước khi triển khai đầy đủ.
- Không đồng nhất test pass của một invariant với việc hoàn tất toàn bộ requirement lớn; dùng PARTIAL khi chỉ có coverage một phần.

## 2. Ma trận chi tiết SRS

| Requirement ID | Yêu cầu | Module owner | Tài liệu/code scope | API dự kiến | DB tables | Test cases | Status | Blocker/gap |
|---|---|---|---|---|---|---|---|---|
| FR-AUTH-01 | Hệ thống phải cho phép người dân bắt đầu đăng nhập bằng Google OAuth | Identity & Authorization | SECURITY_DESIGN, API_SPECIFICATION | /api/v1/auth/*; admin route guards | users | TC-AUTH-001..008 | NOT_STARTED | — |
| FR-AUTH-02 | Backend phải xác minh callback/token từ Google; không tin dữ liệu nhận trực tiếp từ client | Identity & Authorization | SECURITY_DESIGN, API_SPECIFICATION | /api/v1/auth/*; admin route guards | users | TC-AUTH-001..008 | NOT_STARTED | — |
| FR-AUTH-03 | Hệ thống phải tạo hoặc liên kết tài khoản người dân theo định danh nhà cung cấp an toàn | Identity & Authorization | SECURITY_DESIGN, API_SPECIFICATION | /api/v1/auth/*; admin route guards | users | TC-AUTH-001..008 | NOT_STARTED | — |
| FR-AUTH-04 | Người dùng phải có thể đăng xuất và kết thúc phiên | Identity & Authorization | SECURITY_DESIGN, API_SPECIFICATION | /api/v1/auth/*; admin route guards | users | TC-AUTH-001..008 | NOT_STARTED | — |
| FR-AUTH-05 | Hệ thống phải cung cấp cổng quản trị riêng về URL/route và kiểm tra role trước khi truy cập | Identity & Authorization | SECURITY_DESIGN, API_SPECIFICATION | /api/v1/auth/*; admin route guards | users | TC-AUTH-001..008 | NOT_STARTED | Chốt staff authentication/provisioning; permission matrix. |
| FR-AUTH-06 | Backend phải thực thi quyền trên từng API/tài nguyên; không chỉ dựa vào route guard của Frontend | Identity & Authorization | SECURITY_DESIGN, API_SPECIFICATION | /api/v1/auth/*; admin route guards | users | TC-AUTH-001..008 | NOT_STARTED | — |
| FR-AUTH-07 | Cơ chế cấp tài khoản và đăng nhập cán bộ phải được cấu hình an toàn; phương thức cụ thể TBD | Identity & Authorization | SECURITY_DESIGN, API_SPECIFICATION | /api/v1/auth/*; admin route guards | users | TC-AUTH-001..008 | NOT_STARTED | Chốt staff authentication/provisioning; permission matrix. |
| FR-CIT-01 | Người dân có thể xem thông tin hồ sơ của chính mình | Citizen Profile | SRS, SECURITY_DESIGN, API_SPECIFICATION | GET/PATCH /api/v1/citizen/profile | users | TC-CIT-001..002 | NOT_STARTED | Bổ sung test hồ sơ Citizen; chốt field hồ sơ được phép sửa. |
| FR-CIT-02 | Người dân chỉ được sửa các trường hồ sơ được cho phép | Citizen Profile | SRS, SECURITY_DESIGN, API_SPECIFICATION | GET/PATCH /api/v1/citizen/profile | users | TC-CIT-001..002 | NOT_STARTED | Bổ sung test hồ sơ Citizen; chốt field hồ sơ được phép sửa. |
| FR-CIT-03 | Hệ thống phải lưu định danh Google ổn định và tránh dùng email làm định danh duy nhất nếu provider hỗ trợ subject ID | Citizen Profile | SRS, SECURITY_DESIGN, API_SPECIFICATION | GET/PATCH /api/v1/citizen/profile | users | TC-CIT-001..002 | NOT_STARTED | Bổ sung test hồ sơ Citizen; chốt field hồ sơ được phép sửa. |
| FR-INC-01 | Người dân đã đăng nhập có thể tạo phản ánh mới | Incident | SRS, DATABASE_DESIGN, API_SPECIFICATION, UI_UX_SPECIFICATION | POST/GET /api/v1/citizen/reports; upload API TBD | reports | PARTIAL | Endpoint và regression tests PASS; Google OAuth/Citizen Portal và user journey còn thiếu. | — |
| FR-INC-02 | Phản ánh phải có nội dung văn bản hợp lệ theo giới hạn cấu hình | Incident | SRS, DATABASE_DESIGN, API_SPECIFICATION, UI_UX_SPECIFICATION | POST/GET /api/v1/citizen/reports; upload API TBD | reports | PARTIAL | Empty/whitespace validation và raw text tests có; portal/limit contract cần QA toàn diện. | — |
| FR-INC-03 | Người dân có thể tải lên ảnh theo định dạng, số lượng và dung lượng được cấu hình | Attachment + Citizen UI | SRS, DATABASE_DESIGN, API_SPECIFICATION, UI_UX_SPECIFICATION | POST/GET /api/v1/citizen/reports; upload API TBD | report_attachments | TC-INC-004..009, TC-SEC-003 | NOT_STARTED | Chốt storage, MIME/count/size/retention. |
| FR-INC-04 | Giao diện phải hiển thị preview ảnh ngay sau khi chọn file, trước khi gửi | Attachment + Citizen UI | SRS, DATABASE_DESIGN, API_SPECIFICATION, UI_UX_SPECIFICATION | POST/GET /api/v1/citizen/reports; upload API TBD | report_attachments | TC-INC-004..009, TC-SEC-003 | NOT_STARTED | Chốt storage, MIME/count/size/retention. |
| FR-INC-05 | Người dân có thể bỏ ảnh đã chọn hoặc thay bằng ảnh khác trước khi submit | Attachment + Citizen UI | SRS, DATABASE_DESIGN, API_SPECIFICATION, UI_UX_SPECIFICATION | POST/GET /api/v1/citizen/reports; upload API TBD | report_attachments | TC-INC-004..009, TC-SEC-003 | NOT_STARTED | Chốt storage, MIME/count/size/retention. |
| FR-INC-06 | Hệ thống phải kiểm tra file ở cả client và server; server là nơi quyết định cuối cùng | Attachment + Citizen UI | SRS, DATABASE_DESIGN, API_SPECIFICATION, UI_UX_SPECIFICATION | POST/GET /api/v1/citizen/reports; upload API TBD | report_attachments | TC-INC-004..009, TC-SEC-003 | NOT_STARTED | Chốt storage, MIME/count/size/retention. |
| FR-INC-07 | Người dân có thể chọn/chỉnh marker vị trí và xác nhận tọa độ trước khi gửi | Location + Incident | SRS, DATABASE_DESIGN, API_SPECIFICATION, UI_UX_SPECIFICATION | POST/GET /api/v1/citizen/reports; upload API TBD | reports | TC-INC-010..012, TC-DB-001 | NOT_STARTED | Chốt map provider và CRS/SRID. |
| FR-INC-08 | Hệ thống phải lưu người tạo, thời điểm, nội dung, vị trí và tham chiếu file liên quan | Location + Incident | SRS, DATABASE_DESIGN, API_SPECIFICATION, UI_UX_SPECIFICATION | POST/GET /api/v1/citizen/reports; upload API TBD | reports | TC-INC-010..012, TC-DB-001 | NOT_STARTED | — |
| FR-INC-09 | Người dân có thể xem danh sách và chi tiết phản ánh của chính mình | Location + Incident | SRS, DATABASE_DESIGN, API_SPECIFICATION, UI_UX_SPECIFICATION | POST/GET /api/v1/citizen/reports; upload API TBD | reports | TC-INC-010..012, TC-DB-001 | NOT_STARTED | — |
| FR-INC-10 | Người dân có thể xem kết quả AI và trạng thái được phép công bố của phản ánh mình gửi | Location + Incident | SRS, DATABASE_DESIGN, API_SPECIFICATION, UI_UX_SPECIFICATION | POST/GET /api/v1/citizen/reports; upload API TBD | reports | TC-INC-010..012, TC-DB-001 | NOT_STARTED | — |
| FR-INC-11 | Người dân không được đọc/sửa phản ánh của tài khoản khác | Location + Incident | SRS, DATABASE_DESIGN, API_SPECIFICATION, UI_UX_SPECIFICATION | POST/GET /api/v1/citizen/reports; upload API TBD | reports | TC-INC-010..012, TC-DB-001 | NOT_STARTED | — |
| FR-AI-01 | Hệ thống phải tiền xử lý văn bản trước khi đưa vào model theo pipeline có version | NLP Preprocessing | PREPROCESSING, MODEL_DESIGN, DATABASE_DESIGN | Internal NLP pipeline; GET /citizen/reports/{id}/prediction | preprocessing_runs | PARTIAL | Preprocessing module versioned có; fallback SKIPPED đúng; tích hợp inference là M2. | — |
| FR-AI-02 | Hệ thống phải dự đoán một nhãn thuộc danh mục 11 nhóm hoặc trả trạng thái không thể dự đoán khi lỗi/đầu vào không hợp lệ | Prediction + Model Registry | PREPROCESSING, MODEL_DESIGN, DATABASE_DESIGN | Internal NLP pipeline; GET /citizen/reports/{id}/prediction | preprocessing_runs, predictions, model_versions, incident_categories | NOT_STARTED | Chưa có authenticated inference service/active model; fallback không phải inference. | — |
| FR-AI-03 | Kết quả cần lưu nhãn, confidence/score, thời điểm và model version | Prediction + Model Registry | PREPROCESSING, MODEL_DESIGN, DATABASE_DESIGN | Internal NLP pipeline; GET /citizen/reports/{id}/prediction | preprocessing_runs, predictions, model_versions, incident_categories | NOT_STARTED | Chưa chứng minh prediction thành công với model thật; không tạo confidence giả. | — |
| FR-AI-04 | Kết quả AI phải được phân biệt với nhãn đã được cán bộ kiểm duyệt | Prediction + Model Registry | PREPROCESSING, MODEL_DESIGN, DATABASE_DESIGN | Internal NLP pipeline; GET /citizen/reports/{id}/prediction | preprocessing_runs, predictions, model_versions, incident_categories | PARTIAL | Prediction và review được tách; workflow E2E với AI result còn thiếu. | — |
| FR-AI-05 | Lỗi inference không được làm mất phản ánh đã tiếp nhận | Prediction + Model Registry | PREPROCESSING, MODEL_DESIGN, DATABASE_DESIGN | Internal NLP pipeline; GET /citizen/reports/{id}/prediction | preprocessing_runs, predictions, model_versions, incident_categories | DONE | Report vẫn lưu khi service thiếu, HTTP error hoặc response sai schema; failure không label/score. | — |
| FR-AI-06 | Có thể cấu hình ngưỡng hỗ trợ chuyển kiểm duyệt; ngưỡng cụ thể TBD | Prediction + Model Registry | PREPROCESSING, MODEL_DESIGN, DATABASE_DESIGN | Internal NLP pipeline; GET /citizen/reports/{id}/prediction | preprocessing_runs, predictions, model_versions, incident_categories | TC-AI-001..009, TC-DB-003..004, TC-CAT-007..009 | NOT_STARTED | Chốt confidence semantics/threshold. |
| FR-AI-07 | Hệ thống phải hỗ trợ các mô hình Naive Bayes, SVM, CNN 1D và LSTM trong phạm vi nghiên cứu | Prediction + Model Registry | PREPROCESSING, MODEL_DESIGN, DATABASE_DESIGN | Internal NLP pipeline; GET /citizen/reports/{id}/prediction | preprocessing_runs, predictions, model_versions, incident_categories | TC-AI-001..009, TC-DB-003..004, TC-CAT-007..009 | NOT_STARTED | Cần Dataset và stack ML được duyệt. |
| FR-AI-08 | Dự đoán phải ghi nhận pipeline/model version để tái lập và truy vết | Prediction + Model Registry | PREPROCESSING, MODEL_DESIGN, DATABASE_DESIGN | Internal NLP pipeline; GET /citizen/reports/{id}/prediction | preprocessing_runs, predictions, model_versions, incident_categories | TC-AI-001..009, TC-DB-003..004, TC-CAT-007..009 | NOT_STARTED | — |
| FR-ADM-01 | Cán bộ có quyền có thể xem danh sách phản ánh theo bộ lọc được phép | Admin Incident | SRS, API_SPECIFICATION, SECURITY_DESIGN, DATABASE_DESIGN | GET /api/v1/admin/reports; POST/GET /admin/reports/{id}/reviews; PATCH status | users, reports, predictions, prediction_reviews, incident_categories | TC-ADM-001..002 | NOT_STARTED | Chốt staff auth; ghi chú review/audit sink policy. |
| FR-ADM-02 | Cán bộ có thể xem nội dung, ảnh, vị trí, dự đoán và lịch sử liên quan | Admin Incident | SRS, API_SPECIFICATION, SECURITY_DESIGN, DATABASE_DESIGN | GET /api/v1/admin/reports; POST/GET /admin/reports/{id}/reviews; PATCH status | users, reports, predictions, prediction_reviews, incident_categories | TC-ADM-001..002 | NOT_STARTED | Chốt staff auth; ghi chú review/audit sink policy. |
| FR-ADM-03 | Cán bộ có thể xác nhận nhãn AI đề xuất | Review + Incident Workflow | SRS, API_SPECIFICATION, SECURITY_DESIGN, DATABASE_DESIGN | GET /api/v1/admin/reports; POST/GET /admin/reports/{id}/reviews; PATCH status | users, reports, predictions, prediction_reviews, incident_categories | PARTIAL | API role + PostgreSQL staff trigger và transaction đã test; AI prediction E2E còn thiếu. | Chốt staff auth; ghi chú review/audit sink policy. |
| FR-ADM-04 | Cán bộ có thể chọn nhãn khác trong danh mục được duyệt | Review + Incident Workflow | SRS, API_SPECIFICATION, SECURITY_DESIGN, DATABASE_DESIGN | GET /api/v1/admin/reports; POST/GET /admin/reports/{id}/reviews; PATCH status | users, reports, predictions, prediction_reviews, incident_categories | DONE | RECEIVER/ADMIN chọn category active trong 11 nhóm; endpoint và DB consistency tests PASS. | Chốt staff auth; ghi chú review/audit sink policy. |
| FR-ADM-05 | Mỗi review phải lưu người thực hiện, thời điểm, nhãn trước/sau và ghi chú/lý do theo chính sách | Review + Incident Workflow | SRS, API_SPECIFICATION, SECURITY_DESIGN, DATABASE_DESIGN | GET /api/v1/admin/reports; POST/GET /admin/reports/{id}/reviews; PATCH status | users, reports, predictions, prediction_reviews, incident_categories | PARTIAL | Actor/time/selected category/note lưu; previous label và GET history coverage cần mở rộng. | Chốt staff auth; ghi chú review/audit sink policy. |
| FR-ADM-06 | Hệ thống phải giữ lại prediction ban đầu, không ghi đè bằng nhãn review | Review + Incident Workflow | SRS, API_SPECIFICATION, SECURITY_DESIGN, DATABASE_DESIGN | GET /api/v1/admin/reports; POST/GET /admin/reports/{id}/reviews; PATCH status | users, reports, predictions, prediction_reviews, incident_categories | PARTIAL | DB history append-only và final category riêng; successful AI prediction E2E assertion chưa có. | Chốt staff auth; ghi chú review/audit sink policy. |
| FR-ADM-07 | Cán bộ chỉ được chuyển trạng thái theo quyền và transition hợp lệ | Review + Incident Workflow | SRS, API_SPECIFICATION, SECURITY_DESIGN, DATABASE_DESIGN | GET /api/v1/admin/reports; POST/GET /admin/reports/{id}/reviews; PATCH status | users, reports, predictions, prediction_reviews, incident_categories | PARTIAL | Route/policy có; transition matrix và mọi role/state permutations chưa exhaustive. | Chốt report status state machine/transition. |
| FR-ADM-08 | Hệ thống phải cung cấp lịch sử kiểm duyệt có thể tra cứu | Review + Incident Workflow | SRS, API_SPECIFICATION, SECURITY_DESIGN, DATABASE_DESIGN | GET /api/v1/admin/reports; POST/GET /admin/reports/{id}/reviews; PATCH status | users, reports, predictions, prediction_reviews, incident_categories | PARTIAL | History append-only verified; GET history authorization/visibility E2E còn partial. | — |
| FR-DASH-01 | Dashboard hiển thị tổng số phản ánh theo quyền truy cập | Dashboard | UI_UX_SPECIFICATION, API_SPECIFICATION, DATABASE_DESIGN | GET /api/v1/admin/dashboard/*; GET /admin/map/reports | reports, incident_categories | TC-DASH-001..003 | NOT_STARTED | — |
| FR-DASH-02 | Dashboard thống kê theo 11 danh mục | Dashboard | UI_UX_SPECIFICATION, API_SPECIFICATION, DATABASE_DESIGN | GET /api/v1/admin/dashboard/*; GET /admin/map/reports | reports, incident_categories | TC-DASH-001..003 | NOT_STARTED | — |
| FR-DASH-03 | Hỗ trợ lọc theo thời gian/trạng thái/danh mục khi có dữ liệu tương ứng | Dashboard | UI_UX_SPECIFICATION, API_SPECIFICATION, DATABASE_DESIGN | GET /api/v1/admin/dashboard/*; GET /admin/map/reports | reports, incident_categories | TC-DASH-001..003 | NOT_STARTED | — |
| FR-DASH-04 | Hiển thị vị trí phản ánh trên bản đồ | Map + Location | UI_UX_SPECIFICATION, API_SPECIFICATION, DATABASE_DESIGN | GET /api/v1/admin/dashboard/*; GET /admin/map/reports | reports, incident_categories | TC-MAP-001..003 | NOT_STARTED | Chốt map provider, CRS/SRID và privacy policy. |
| FR-DASH-05 | Marker/cluster phải tuân theo bộ lọc và quyền truy cập | Map + Location | UI_UX_SPECIFICATION, API_SPECIFICATION, DATABASE_DESIGN | GET /api/v1/admin/dashboard/*; GET /admin/map/reports | reports, incident_categories | TC-MAP-001..003 | NOT_STARTED | Chốt map provider, CRS/SRID và privacy policy. |
| FR-DASH-06 | Khi chọn marker, người dùng quản trị có quyền có thể mở chi tiết phản ánh | Map + Location | UI_UX_SPECIFICATION, API_SPECIFICATION, DATABASE_DESIGN | GET /api/v1/admin/dashboard/*; GET /admin/map/reports | reports, incident_categories | TC-MAP-001..003 | NOT_STARTED | Chốt map provider, CRS/SRID và privacy policy. |
| FR-DATA-01 | Người có quyền có thể tạo, xem, cập nhật và lưu trữ Dataset | Dataset | DATASET_SPECIFICATION, DATABASE_DESIGN, API_SPECIFICATION | /api/v1/admin/datasets/*; /dataset-samples/* | datasets, dataset_samples, incident_categories, reports, prediction_reviews | TC-DATA-001..002, TC-DB-008..009 | NOT_STARTED | — |
| FR-DATA-02 | Dataset Sample phải thuộc Dataset hoặc version được xác định | Dataset | DATASET_SPECIFICATION, DATABASE_DESIGN, API_SPECIFICATION | /api/v1/admin/datasets/*; /dataset-samples/* | datasets, dataset_samples, incident_categories, reports, prediction_reviews | TC-DATA-001..002, TC-DB-008..009 | NOT_STARTED | — |
| FR-DATA-03 | Có thể thêm/import, sửa nhãn, loại bỏ hoặc đánh dấu sample theo quyền | Dataset Sample + Validation | DATASET_SPECIFICATION, DATABASE_DESIGN, API_SPECIFICATION | /api/v1/admin/datasets/*; /dataset-samples/* | datasets, dataset_samples, incident_categories, reports, prediction_reviews | TC-DATA-003..006, TC-DB-008..009 | NOT_STARTED | Chốt nguồn dữ liệu, privacy/provenance policy và permission. |
| FR-DATA-04 | Hệ thống phải validate schema, nhãn, dữ liệu rỗng và trùng lặp theo quy tắc | Dataset Sample + Validation | DATASET_SPECIFICATION, DATABASE_DESIGN, API_SPECIFICATION | /api/v1/admin/datasets/*; /dataset-samples/* | datasets, dataset_samples, incident_categories, reports, prediction_reviews | TC-DATA-003..006, TC-DB-008..009 | NOT_STARTED | Chốt nguồn dữ liệu, privacy/provenance policy và permission. |
| FR-DATA-05 | Hệ thống cần lưu nguồn gốc và trạng thái kiểm duyệt của dữ liệu | Dataset Sample + Validation | DATASET_SPECIFICATION, DATABASE_DESIGN, API_SPECIFICATION | /api/v1/admin/datasets/*; /dataset-samples/* | datasets, dataset_samples, incident_categories, reports, prediction_reviews | TC-DATA-003..006, TC-DB-008..009 | NOT_STARTED | Chốt nguồn dữ liệu, privacy/provenance policy và permission. |
| FR-DATA-06 | Chia train/validation/test phải tránh rò rỉ dữ liệu giữa các tập | Dataset Sample + Validation | DATASET_SPECIFICATION, DATABASE_DESIGN, API_SPECIFICATION | /api/v1/admin/datasets/*; /dataset-samples/* | datasets, dataset_samples, incident_categories, reports, prediction_reviews | TC-DATA-003..006, TC-DB-008..009 | NOT_STARTED | Chốt nguồn dữ liệu, privacy/provenance policy và permission. |
| FR-ML-01 | Người có quyền có thể tạo Training Run với dataset version và cấu hình rõ ràng | Training | MODEL_DESIGN, DATASET_SPECIFICATION, DATABASE_DESIGN | POST/GET /api/v1/admin/training-runs; /models/* | datasets, training_runs, training_metrics, model_versions, incident_categories | TC-TRAIN-001,003, TC-DB-010 | NOT_STARTED | Cần Dataset hợp lệ và runtime ML. |
| FR-ML-02 | Training Run phải có trạng thái và thời điểm bắt đầu/kết thúc | Training | MODEL_DESIGN, DATASET_SPECIFICATION, DATABASE_DESIGN | POST/GET /api/v1/admin/training-runs; /models/* | datasets, training_runs, training_metrics, model_versions, incident_categories | TC-TRAIN-001,003, TC-DB-010 | NOT_STARTED | Cần Dataset hợp lệ và runtime ML. |
| FR-ML-03 | Lưu metrics tổng thể và theo lớp khi khả dụng | Evaluation/Metrics | MODEL_DESIGN, DATASET_SPECIFICATION, DATABASE_DESIGN | POST/GET /api/v1/admin/training-runs; /models/* | datasets, training_runs, training_metrics, model_versions, incident_categories | TC-TRAIN-002..004, TC-DB-011 | NOT_STARTED | Cần Dataset hợp lệ và runtime ML. |
| FR-ML-04 | Lưu tham chiếu artifact, code/config và model version | Evaluation/Metrics | MODEL_DESIGN, DATASET_SPECIFICATION, DATABASE_DESIGN | POST/GET /api/v1/admin/training-runs; /models/* | datasets, training_runs, training_metrics, model_versions, incident_categories | TC-TRAIN-002..004, TC-DB-011 | NOT_STARTED | Cần Dataset hợp lệ và runtime ML. |
| FR-ML-05 | Có thể so sánh các training run | Evaluation/Metrics | MODEL_DESIGN, DATASET_SPECIFICATION, DATABASE_DESIGN | POST/GET /api/v1/admin/training-runs; /models/* | datasets, training_runs, training_metrics, model_versions, incident_categories | TC-TRAIN-002..004, TC-DB-011 | NOT_STARTED | Cần Dataset hợp lệ và runtime ML. |
| FR-ML-06 | Model Version phải có trạng thái rõ ràng; chỉ model được phê duyệt mới được kích hoạt | Model Registry | MODEL_DESIGN, DATASET_SPECIFICATION, DATABASE_DESIGN | POST/GET /api/v1/admin/training-runs; /models/* | datasets, training_runs, training_metrics, model_versions, incident_categories | DONE | Approved gate, partial unique ACTIVE index và concurrent activation/advisory lock verified. | Chốt approval/activation policy, artifact storage/deployment target. |
| FR-ML-07 | Hỗ trợ rollback về model version trước nếu triển khai lỗi hoặc chất lượng suy giảm | Model Registry | MODEL_DESIGN, DATASET_SPECIFICATION, DATABASE_DESIGN | POST/GET /api/v1/admin/training-runs; /models/* | datasets, training_runs, training_metrics, model_versions, incident_categories | DONE | Rollback reactivates prior approved version, retires current, preserves approval metadata and emits audit. | Chốt approval/activation policy, artifact storage/deployment target. |
| FR-AUD-01 | Lưu audit cho đăng nhập quan trọng, review, thay nhãn, thay trạng thái, thay quyền và kích hoạt model | Audit + Security | SECURITY_DESIGN, DATABASE_DESIGN, Decision Log | Audit sink adapter/read API TBD | users, reports, prediction_reviews, model_versions; sink ngoài 12 bảng | TC-AUD-001..005, TC-SEC-004 | BLOCKED | Chọn audit sink bền vững, read permission, delivery/retry, retention và tamper detection. |
| FR-AUD-02 | Audit ghi actor, action, resource, timestamp và kết quả; tránh lưu secret/dữ liệu nhạy cảm không cần thiết | Audit + Security | SECURITY_DESIGN, DATABASE_DESIGN, Decision Log | Audit sink adapter/read API TBD | users, reports, prediction_reviews, model_versions; sink ngoài 12 bảng | TC-AUD-001..005, TC-SEC-004 | BLOCKED | Chọn audit sink bền vững, read permission, delivery/retry, retention và tamper detection. |
| FR-AUD-03 | Quyền xem audit phải được giới hạn | Audit + Security | SECURITY_DESIGN, DATABASE_DESIGN, Decision Log | Audit sink adapter/read API TBD | users, reports, prediction_reviews, model_versions; sink ngoài 12 bảng | TC-AUD-001..005, TC-SEC-004 | BLOCKED | Chọn audit sink bền vững, read permission, delivery/retry, retention và tamper detection. |
| FR-CAT-01 | Hệ thống phải duy trì chính xác 11 danh mục theo CLASSIFICATION_SPECIFICATION, có category_code ổn định và thứ tự hiển thị 1–11 | Classification Catalog | CLASSIFICATION_SPECIFICATION, DATABASE_DESIGN, API_SPECIFICATION | GET /api/v1/categories; review/dataset category fields | incident_categories và mọi FK category | DONE | PostgreSQL seed xác minh chính xác 11 categories trong run #26. | Cần DB engine để seed/migration/API code; ranh giới lớp giao nhau cần guideline. |
| FR-CAT-02 | API, Database, Dashboard, Dataset và NLP/ML phải dùng chung category_code/label_schema_version; không dùng tên hiển thị làm khóa | Classification Catalog | CLASSIFICATION_SPECIFICATION, DATABASE_DESIGN, API_SPECIFICATION | GET /api/v1/categories; review/dataset category fields | incident_categories và mọi FK category | TC-CAT-001..009, TC-DB-012 | NOT_STARTED | Cần DB engine để seed/migration/API code; ranh giới lớp giao nhau cần guideline. |
| FR-CAT-03 | Citizen không bắt buộc chọn danh mục khi tạo phản ánh; hệ thống thực hiện phân loại văn bản bằng AI | Classification Catalog | CLASSIFICATION_SPECIFICATION, DATABASE_DESIGN, API_SPECIFICATION | GET /api/v1/categories; review/dataset category fields | incident_categories và mọi FK category | TC-CAT-001..009, TC-DB-012 | NOT_STARTED | Cần DB engine để seed/migration/API code; ranh giới lớp giao nhau cần guideline. |
| FR-CAT-04 | Prediction thành công phải trả một category thuộc catalog; input không hợp lệ, thiếu thông tin và inference failure phải có trạng thái riêng, không tự động gán OTHER | Classification Catalog | CLASSIFICATION_SPECIFICATION, DATABASE_DESIGN, API_SPECIFICATION | GET /api/v1/categories; review/dataset category fields | incident_categories và mọi FK category | TC-CAT-001..009, TC-DB-012 | NOT_STARTED | Cần DB engine để seed/migration/API code; ranh giới lớp giao nhau cần guideline. |
| FR-CAT-05 | Cán bộ có quyền được xác nhận nhãn AI hoặc chọn một trong 11 danh mục; mọi lần review được lưu lịch sử và không ghi đè prediction | Classification Catalog | CLASSIFICATION_SPECIFICATION, DATABASE_DESIGN, API_SPECIFICATION | GET /api/v1/categories; review/dataset category fields | incident_categories và mọi FK category | TC-CAT-001..009, TC-DB-012 | NOT_STARTED | Cần DB engine để seed/migration/API code; ranh giới lớp giao nhau cần guideline. |
| FR-CAT-06 | Dashboard phải thống kê và hiển thị đủ 11 danh mục, kể cả danh mục có số lượng bằng 0 | Classification Catalog | CLASSIFICATION_SPECIFICATION, DATABASE_DESIGN, API_SPECIFICATION | GET /api/v1/categories; review/dataset category fields | incident_categories và mọi FK category | TC-CAT-001..009, TC-DB-012 | NOT_STARTED | Cần DB engine để seed/migration/API code; ranh giới lớp giao nhau cần guideline. |
| NFR-SEC-01 |  | Security | SECURITY_DESIGN, AGENTS.md | Tất cả API bảo vệ; upload | users, reports, report_attachments và các bảng có dữ liệu bảo vệ | TC-AUTH-005..007, TC-INC-007..009, TC-SEC-001..005 | NOT_STARTED | Cần stack/auth/storage policy để triển khai. |
| NFR-SEC-02 |  | Security | SECURITY_DESIGN, AGENTS.md | Tất cả API bảo vệ; upload | users, reports, report_attachments và các bảng có dữ liệu bảo vệ | TC-AUTH-005..007, TC-INC-007..009, TC-SEC-001..005 | NOT_STARTED | Cần stack/auth/storage policy để triển khai. |
| NFR-SEC-03 |  | Security | SECURITY_DESIGN, AGENTS.md | Tất cả API bảo vệ; upload | users, reports, report_attachments và các bảng có dữ liệu bảo vệ | TC-AUTH-005..007, TC-INC-007..009, TC-SEC-001..005 | NOT_STARTED | Cần stack/auth/storage policy để triển khai. |
| NFR-SEC-04 |  | Security | SECURITY_DESIGN, AGENTS.md | Tất cả API bảo vệ; upload | users, reports, report_attachments và các bảng có dữ liệu bảo vệ | TC-AUTH-005..007, TC-INC-007..009, TC-SEC-001..005 | NOT_STARTED | Cần stack/auth/storage policy để triển khai. |
| NFR-REL-01 |  | Reliability / Incident + Prediction | SYSTEM_DESIGN, BUSINESS_PROCESS | Create report + inference | reports, preprocessing_runs, predictions | TC-AI-005..006, TC-REL-001, TC-DB-004 | NOT_STARTED | Cần source code/worker strategy. |
| NFR-DATA-01 |  | Database Integrity | DATABASE_DESIGN, DATA_DICTIONARY | Tất cả write APIs | Cả 12 bảng | PARTIAL | PostgreSQL/schema đã triển khai; M1 critical invariants verified, chưa exhaustive test mọi write path. | Cần DB engine/type mapping và migrations. |
| NFR-AUD-01 |  | Traceability | DATABASE_DESIGN, MODEL_DESIGN | Prediction/review/model endpoints | predictions, prediction_reviews, model_versions | TC-DB-003..007 | NOT_STARTED | Cần models/API và invariant tests. |
| NFR-PERF-01 |  | Performance | SRS, TEST_PLAN, SYSTEM_DESIGN | List, dashboard, map, inference | reports, incident_categories, coordinate indexes | TC-PERF-001 | BLOCKED | Chưa có workload/latency target được duyệt. |
| NFR-PERF-02 |  | Performance | SRS, TEST_PLAN, SYSTEM_DESIGN | List, dashboard, map, inference | reports, incident_categories, coordinate indexes | TC-PERF-001 | BLOCKED | Chưa có workload/latency target được duyệt. |
| NFR-USE-01 |  | Frontend UX | UI_UX_SPECIFICATION, FOLDER_STRUCTURE | Portal screens | N/A | Responsive/accessibility E2E (bổ sung) | NOT_STARTED | Cần framework và UI acceptance details. |
| NFR-USE-02 |  | Frontend UX | UI_UX_SPECIFICATION, FOLDER_STRUCTURE | Portal screens | N/A | Responsive/accessibility E2E (bổ sung) | NOT_STARTED | Cần framework và UI acceptance details. |
| NFR-MNT-01 |  | Engineering Quality | CODING_STANDARDS, AGENTS.md | API schema/type validation | ORM models | Lint/type/unit tests (bổ sung) | BLOCKED | Chờ stack/framework/tooling. |
| NFR-PORT-01 |  | DevOps/Configuration | DEPLOYMENT_GUIDE, TECHNOLOGY_STACK | N/A | N/A | TC-DEP-001, TC-SEC-004 | NOT_STARTED | Cần stack/env config schema. |
| NFR-BACKUP-01 |  | Backup & Recovery | DEPLOYMENT_GUIDE, SECURITY_DESIGN | Operational | DB + file storage | Backup/restore test (bổ sung) | BLOCKED | Chốt RPO/RTO, retention, DB/storage provider. |
| NFR-OBS-01 |  | Observability | SYSTEM_DESIGN, SECURITY_DESIGN | health/readiness/metrics TBD | Logs/metrics external | Health/log redaction tests (bổ sung) | NOT_STARTED | Cần chọn runtime/observability stack. |

## 3. Ánh xạ yêu cầu nghiệp vụ BRD

| BRD ID | Phạm vi | SRS liên quan | Module chính | Status |
|---|---|---|---|---|
| BR-01 | Kênh gửi phản ánh | FR-INC-01..02, FR-AUTH-01..03 | Citizen + Identity | NOT_STARTED |
| BR-02 | Nội dung, người gửi, thời gian, vị trí | FR-INC-02, FR-INC-07..08 | Incident + Location | NOT_STARTED |
| BR-03 | Ảnh minh chứng | FR-INC-03..06 | Attachment | BLOCKED: storage policy |
| BR-04 | NLP phân loại 11 nhóm | FR-AI-01..08, FR-CAT-01..04 | NLP + Classification | BLOCKED: code/data |
| BR-05 | Prediction là đề xuất có confidence/model | FR-AI-02..05, FR-AI-08 | Prediction | NOT_STARTED |
| BR-06 | Cán bộ xác nhận/chỉnh nhãn | FR-ADM-03..06, FR-CAT-05 | Review | BLOCKED: staff auth |
| BR-07 | Lịch sử kiểm duyệt | FR-ADM-05..08, FR-AUD-01..03 | Review + Audit | BLOCKED: audit sink |
| BR-08 | Người dân chỉ xem dữ liệu của mình | FR-INC-09..11, FR-AUTH-06 | Authorization | NOT_STARTED |
| BR-09 | Dashboard và bản đồ | FR-DASH-01..06 | Dashboard + Map | BLOCKED: map provider |
| BR-10 | Dataset/Samples | FR-DATA-01..06 | Dataset | BLOCKED: source/privacy |
| BR-11 | Training Runs/Metrics | FR-ML-01..05, FR-AI-07 | Training + Metrics | BLOCKED: dataset |
| BR-12 | Model Version lifecycle | FR-ML-04..07 | Model Registry | BLOCKED: artifact/deploy policy |
| BR-13 | Dữ liệu review làm training source | FR-DATA-05, FR-ML-01 | Dataset provenance | BLOCKED: source/privacy approval |
| BR-14 | Audit thao tác nhạy cảm | FR-AUD-01..03 | Audit + Security | BLOCKED: audit sink |

## 4. Coverage và lỗ hổng test

### Test IDs hiện có
- Authentication/authorization: TC-AUTH-001..008.
- Citizen report/upload/location: TC-INC-001..012.
- NLP/prediction: TC-AI-001..009.
- Admin/review: TC-ADM-001..002, TC-REV-001..007.
- Dashboard/map: TC-DASH-001..003, TC-MAP-001..003.
- Dataset/training/model: TC-DATA-001..006, TC-TRAIN-001..004, TC-MODEL-001..003.
- Security/performance/reliability/deployment: TC-SEC-001..005, TC-PERF-001, TC-REL-001, TC-DEP-001.
- Category/database: TC-CAT-001..009, TC-DB-001..013.

### Test đã bổ sung trong nhánh audit này
- TC-CIT-001..002: xem/cập nhật hồ sơ Citizen và field allow-list.
- TC-AUD-001..005: audit login, review, report status, role change, model activation/rollback và chặn đọc audit trái quyền.

### Test vẫn cần bổ sung khi có quyết định/implementation
- TC-AI-010: confidence semantics/threshold, chỉ tạo sau khi threshold policy được duyệt.
- Backup/restore, accessibility/responsive, healthcheck/observability, API contract và clean Docker environment tests.

## 5. Quy tắc cập nhật ma trận

1. Mỗi FR/NFR phải có module owner và ít nhất một test case.
2. Khi API được triển khai, thay endpoint dự kiến bằng method/path và link OpenAPI operation.
3. Khi Database migration có thật, đối chiếu table/column/constraint thực tế.
4. Sau mỗi module PR, cập nhật source files, commit/PR, test result và blocker.
5. Không đổi trạng thái sang IMPLEMENTED/TESTED/VERIFIED chỉ vì đã viết code hoặc có test file.
6. Một requirement chỉ TESTED khi test đã thực thi thành công; VERIFIED khi acceptance criteria được review và có evidence.

## 6. Baseline execution status

- SRS requirement rows được ánh xạ: 80.
- BRD requirements mapped: 14.
- Application modules implemented: 0.
- Automated tests executed: 0.
- VERIFIED requirements: 0.


## Milestone 1 execution evidence

- Code commit tested: `e89f9287ac07e83094eda0aa3f7cc65b9ec15963`.
- GitHub Actions [run #26](https://github.com/khanh0102102/st-nlp/actions/runs/46146303002): SUCCESS.
- Docker backend/PostgreSQL: 61 passed, 1 skipped; CPU neural: 8 passed.
- Fresh/upgrade/downgrade/re-upgrade migrations, seed 11 categories, exact 12 business tables, model rollback, trainer CLI, startup and health checks: PASS.
- Evidence scope is M1 critical report/review/database/model-registry invariants, not all SRS requirements.
