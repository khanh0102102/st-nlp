# MODEL DESIGN — THIẾT KẾ MÔ HÌNH AI/ML

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.1 |
| Trạng thái | Partial implementation; real-data evaluation pending |
| Bài toán | Phân loại văn bản tiếng Việt thành đúng 11 nhóm |

## 1. Mục tiêu

Thiết kế pipeline có thể huấn luyện, đánh giá, đăng ký, triển khai và truy vết nhiều mô hình. Prediction AI chỉ là đề xuất; cán bộ có quyền mới xác nhận nhãn cuối cùng.

## 2. Label contract và output

Input là raw report text đã qua validation. Output khi inference được triển khai phải có predicted category code, score kèm confidence type, model version, preprocessing version, timestamp và inference status.

Không gọi raw decision function là calibrated probability. Nếu UI hiển thị phần trăm cần calibration và đánh giá calibration trước.

Label codes lấy từ classification specification và schema version. Không phụ thuộc thứ tự ngẫu nhiên từ database query.

## 3. Model components hiện có

### 3.1. Multinomial Naive Bayes

- Code: backend/app/ml/classical.py.
- TF-IDF word n-gram (1, 2) và MultinomialNB(alpha=1.0).
- Có artifact save/load.
- Score type: MODEL_PROBABILITY_UNCALIBRATED.

### 3.2. Linear SVM

- Dùng LinearSVC(C=1.0, class_weight="balanced").
- Score type: RAW_DECISION_SCORE; không phải probability.
- Có artifact save/load.

### 3.3. CNN 1D

- Code: backend/app/ml/neural.py.
- Token vocabulary có PAD/UNK, embedding, Conv1D kernels 2/3/4 và max pooling.
- Đã kiểm thử forward với chuỗi ngắn trong CPU image.

### 3.4. BiLSTM

- Embedding + bidirectional LSTM + packed sequence + classification head.
- Model artifact có state dict, vocabulary và label codes.

Neural CPU dependencies nằm trong backend/requirements-neural.txt; không cài vào API runtime.

## 4. Evaluation metrics

backend/app/ml/metrics.py triển khai:
- Accuracy.
- Precision/Recall/F1 macro và weighted.
- Per-class precision/recall/F1/support.
- Confusion matrix theo label order cố định.
- Chuyển kết quả sang metric rows tương thích training_metrics.

Macro-F1 quan trọng với lớp hiếm; không dùng accuracy đơn lẻ để chọn model.

Calibration curve, Brier score, log loss và ECE chưa được triển khai/đánh giá trong baseline này.

## 5. Training boundary

Training CLI: backend/app/ml/cli.py. Lệnh CLI --help được smoke-test trong Docker CI.

- Classical dependencies và underthesea nằm ở ML image.
- PyTorch CPU wheel được cài trong training/test image riêng.
- ml-trainer bật qua Compose profile training.
- API runtime không cài PyTorch.
- Artifacts lưu vào named volume model_artifacts_data; model registry lưu URI/checksum/metrics metadata.

Training orchestration có kiểm tra dataset FROZEN, đủ ba split, đủ 11 classes trong TRAIN và không để fingerprint giống nhau rơi vào nhiều split. Tuy nhiên, một lần training với dataset thật/approved chưa được xác minh end-to-end.

## 6. Inference flow mục tiêu và giới hạn hiện tại

Inference service phải:
1. Load model APPROVED/ACTIVE.
2. Verify artifact checksum và label/preprocessing schema.
3. Preprocess report bằng đúng version.
4. Predict với đúng score semantics.
5. Validate category thuộc 11 codes.
6. Append prediction history.
7. Không set final category; final label chỉ do authorized review.

Giới hạn hiện tại: authenticated inference service chưa được hoàn thiện. Khi không có active model, không được bịa category/confidence hoặc dùng OTHER mặc định.

## 7. Human-in-the-loop

- Prediction ban đầu được giữ lịch sử riêng.
- Cán bộ xác nhận hoặc sửa nhãn.
- Review lưu actor/time/reason theo append-only.
- reports.final_category_id chỉ đổi qua authorized review.
- Reviewed examples chỉ được đưa vào dataset sau validation và approval.

## 8. Promotion

Trước activation cần evaluation trên dataset version cố định, metrics theo lớp, artifact/checksum verification, confidence calibration nếu có sử dụng, smoke test và rollback. Numeric thresholds và production approval vẫn TBD.

## 9. Giới hạn/rủi ro

- Chưa có real labeled dataset được chủ dự án phê duyệt.
- Imbalance, label inconsistency, local spelling/slang và distribution shift chưa được đo.
- NB probability chưa calibration.
- SVM decision score không phải probability.
- Component tests không chứng minh model quality.
- Không tự động retrain/promote từ drift alert.

## 10. Work tiếp theo

1. DB integration test full training orchestration trên synthetic CI data (chỉ xác minh mechanics, không dùng để báo cáo chất lượng mô hình).
2. Chạy train execution và artifact registration trên frozen approved dataset.
3. Implement authenticated inference API/service.
4. Thực hiện evaluation và calibration trên real/approved dataset.
5. Hoàn thiện model approval/activation/rollback tests.
