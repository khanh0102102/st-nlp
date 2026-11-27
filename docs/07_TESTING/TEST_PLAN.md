# TEST PLAN — KẾ HOẠCH KIỂM THỬ

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Draft |
| Phạm vi | Citizen, Admin, API, Database, NLP/ML và deployment |

## 1. Mục tiêu

Xác minh chức năng đúng yêu cầu, bảo vệ dữ liệu, giữ tính toàn vẹn giữa Frontend/Backend/Database/AI và giảm hồi quy. Test phải dựa trên SRS/acceptance criteria đã duyệt.

## 2. Phạm vi kiểm thử

### In scope
- Google OAuth flow và session.
- RBAC, resource ownership và portal separation.
- Tạo phản ánh, upload ảnh, preview, vị trí và history.
- NLP preprocessing, prediction, confidence semantics và model version.
- Admin list/detail/review/status.
- Dashboard và map filtering.
- Dataset/sample validation, training run, metrics và model version.
- Database constraints/migrations.
- Deployment config, health check, backup/restore theo môi trường.

### Out of scope hiện tại
- Penetration test thuê ngoài hoặc certification chính thức nếu chưa được lập kế hoạch.
- Load test theo số người dùng thật khi chưa có workload target.
- Kiểm thử integrations chưa được lựa chọn/cấu hình.

## 3. Cấp độ kiểm thử

| Level | Mục tiêu | Ví dụ |
|---|---|---|
| Unit | Kiểm tra logic nhỏ | validator, permission policy, preprocessing |
| API | Kiểm tra endpoint/contract | status code, schema, auth |
| Integration | Kiểm tra nhiều module | report + DB + storage, prediction + model |
| E2E | Kiểm tra luồng người dùng | login → submit → prediction → review |
| ML Evaluation | Đo chất lượng model | Macro-F1, per-class recall, calibration |
| Security | Tìm lỗi quyền và input | IDOR, upload, OAuth, injection |
| Performance | Đo latency/throughput | API, dashboard, map, inference |
| UAT | Xác nhận phù hợp nghiệp vụ | cán bộ/người dùng thử |

## 4. Môi trường và dữ liệu test

- Unit/API: test DB riêng, storage fake/local, external provider mock.
- Integration: service dependency được container hóa hoặc test double.
- E2E: staging/test environment, tài khoản giả lập.
- ML: dataset snapshot/version cố định, không dùng test data để fit/tune.
- Không dùng dữ liệu cá nhân thật nếu chưa được ẩn danh và cho phép.
- Seed test phải deterministic và idempotent.

## 5. Chiến lược test theo phân hệ

### Citizen
- OAuth success/failure.
- Tạo report hợp lệ/không hợp lệ.
- Preview, xóa/thay file, file type/size.
- Tọa độ hợp lệ/ngoài miền.
- History/detail chỉ thuộc owner.
- Retry/double submit.

### Admin
- Role không đủ quyền bị từ chối.
- List/filter/pagination.
- Review confirm/correct.
- Concurrency conflict.
- Audit history.
- Dashboard aggregate và map permission.

### AI
- Input rỗng/siêu ngắn/ký tự Unicode.
- Preprocessing tái lập.
- Label mapping 11 lớp.
- Model load failure/inference timeout.
- Score range/semantics.
- Model version traceability.
- Train/test leakage và duplicate.

### Data Management
- Dataset CRUD/validation/freeze.
- Sample label không hợp lệ.
- Split integrity.
- Training state transitions.
- Metric schema.
- Artifact reference và model activation/rollback.

## 6. Exit criteria

- Tất cả test Must đã được thực thi.
- Không còn lỗi Critical/High chưa được xử lý hoặc chấp thuận có ghi nhận.
- Không có lỗi authorization/ownership nghiêm trọng.
- Migration test thành công trên database sạch và đường nâng cấp được hỗ trợ.
- ML evaluation có report trên test set độc lập.
- Hiệu năng đạt target được chủ dự án phê duyệt.
- UAT được đại diện nghiệp vụ ký xác nhận.

## 7. Báo cáo test

Mỗi test run cần ghi:
- commit/branch và phiên bản build.
- môi trường, phiên bản runtime/dependencies.
- test suite và số passed/failed/skipped.
- lỗi, mức độ nghiêm trọng và link issue.
- log/screenshot/số liệu phù hợp đã che dữ liệu nhạy cảm.
- kết luận: pass, pass with known issues hoặc fail.

## 8. Automation

Khi code được thêm, CI nên chạy format/lint/type check/unit/API tests; integration/E2E có thể chạy theo job riêng. Không giả định pipeline đã tồn tại trong repository hiện tại.


## 9. Test bổ sung cho catalog và Database baseline

- Seed catalog phải tạo đúng 11 category, đúng category_code/name/sort_order; chạy lại seed không tạo duplicate.
- API và UI hiển thị đủ 11 category theo đúng thứ tự; Dashboard giữ nhóm count = 0.
- API từ chối category_code không tồn tại; label mapping của model chỉ chấp nhận 11 mã hợp lệ.
- OTHER không được dùng thay cho INSUFFICIENT_INFORMATION, INVALID_INPUT, UNLABELED, NEEDS_REVIEW hoặc INFERENCE_FAILED.
- reports.raw_content không đổi qua preprocessing; reports.final_category_id NULL trước review và được cập nhật cùng transaction khi review thành công.
- predictions phải tham chiếu cùng report với preprocessing_run; prediction failure không làm mất report.
- prediction_reviews append-only; kiểm thử hai lần review, concurrency conflict và không ghi đè prediction.
- Dataset version FROZEN không thể thay đổi; dataset_samples chỉ gán category hoặc labeling_status hợp lệ.
- training_metrics kiểm thử metric tổng thể/per-class, split, averaging và category FK.
- Kiểm tra migration tạo đúng 12 bảng; không tự sinh bảng roles/permissions/dataset_versions/audit_logs trong baseline.
- Audit event được phát ra audit sink theo adapter contract; test retry/failure không làm mất thao tác nghiệp vụ đã commit.

Test phải chạy trong Docker container theo Docker-only policy. Không ghi VERIFIED khi chưa có kết quả thực thi.
