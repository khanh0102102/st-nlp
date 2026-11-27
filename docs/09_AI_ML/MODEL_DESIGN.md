# MODEL DESIGN — THIẾT KẾ MÔ HÌNH AI/ML

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Proposed research baseline |
| Bài toán | Phân loại văn bản tiếng Việt thành 11 nhóm |

## 1. Mục tiêu

Thiết kế pipeline có thể huấn luyện, đánh giá, đăng ký, triển khai và truy vết nhiều mô hình. Mục tiêu không chỉ là có prediction mà còn đo chất lượng theo từng lớp và đảm bảo confidence được diễn giải đúng.

## 2. Input/Output

**Input:** văn bản phản ánh đã qua validation và preprocessing version xác định.

**Output tối thiểu:**
- predicted_category_code.
- raw_score hoặc probability vector theo semantics model.
- confidence_value kèm confidence_type.
- model_version.
- preprocessing_version.
- prediction_timestamp.
- inference_status.

Không được gọi raw decision function là calibrated probability. Nếu UI hiển thị phần trăm, cần hiệu chỉnh và kiểm tra calibration trước.

## 3. Nhóm mô hình nghiên cứu

### 3.1. Multinomial Naive Bayes
- Baseline nhanh cho TF-IDF/count features.
- Dễ huấn luyện và làm mốc so sánh.
- Cần đánh giá khi lớp/feature phụ thuộc mạnh.
- Lưu vectorizer và label mapping cùng classifier.

### 3.2. Support Vector Machine
- Thử Linear SVM với TF-IDF.
- Theo dõi class imbalance và class_weight.
- Decision score không mặc định là xác suất.
- Nếu cần probability/confidence, dùng calibration trên validation phù hợp và đánh giá calibration.

### 3.3. CNN 1D
- Input sequence/token embedding.
- Dùng convolution/pooling để học n-gram pattern.
- Cần kiểm soát vocabulary, padding, max length và overfitting.
- Lưu seed, architecture config và tokenizer.

### 3.4. LSTM
- Học thông tin trình tự token.
- Kiểm soát sequence length, hidden size, dropout và training cost.
- Theo dõi overfitting và thời gian inference.
- So sánh công bằng trên cùng split và preprocessing.

## 4. Baseline và thực nghiệm

1. Thiết lập baseline đơn giản (majority class hoặc dummy classifier) để xác định mốc.
2. Huấn luyện NB/SVM với TF-IDF.
3. Thử CNN 1D và LSTM nếu dữ liệu/nguồn lực phù hợp.
4. Giữ cố định train/validation/test split khi so sánh.
5. Tune hyperparameters trên validation/cross-validation.
6. Chỉ đánh giá cuối cùng một lần trên held-out test.
7. Lưu toàn bộ config và kết quả để tái lập.

## 5. Metrics

Bắt buộc xem xét:
- Accuracy.
- Precision, Recall, F1-score theo từng lớp.
- Macro-F1 để phản ánh các lớp hiếm.
- Weighted-F1 để bổ sung góc nhìn theo support.
- Confusion Matrix.
- Support/count từng lớp.

Nếu model xuất probability và cần dùng confidence:
- Calibration curve/reliability diagram.
- Brier score hoặc log loss khi phù hợp.
- Expected calibration error nếu phương pháp được định nghĩa rõ.

Không dùng accuracy đơn lẻ làm tiêu chí chọn model khi dữ liệu mất cân bằng.

## 6. Xử lý mất cân bằng lớp

Đầu tiên phải báo cáo phân bố. Có thể đánh giá class weights, resampling hoặc data augmentation có kiểm soát. Mọi kỹ thuật chỉ áp dụng trên train data; không resample validation/test. Không tạo sample tổng hợp khiến nhãn sai hoặc rò rỉ.

## 7. Model artifact và registry

Mỗi Model Version cần:
- model_family và version.
- artifact URI/storage key và checksum.
- source training_run_id.
- dataset version.
- preprocessing version.
- label schema version.
- hyperparameters/architecture config.
- metrics summary và evaluation report.
- created/approved/activated by/time.
- status và deployment target.

Không commit checkpoint lớn vào Git. Dùng artifact storage được cấu hình.

## 8. Inference flow

1. Validate text.
2. Load active model version đã được phê duyệt.
3. Nạp preprocessing artifact đúng version.
4. Tạo feature/sequence.
5. Gọi model.predict/predict_proba/decision_function theo contract.
6. Chuẩn hóa output sang label code và score semantics.
7. Validate label thuộc 11 classes.
8. Ghi prediction cùng model/preprocess version.
9. Trả kết quả an toàn cho ứng dụng.

Nếu model không sẵn sàng, trả trạng thái lỗi; không dùng nhãn mặc định để giả lập dự đoán.

## 9. Human-in-the-loop

- Prediction ban đầu được giữ bất biến.
- Cán bộ xác nhận hoặc sửa nhãn.
- Review được lưu riêng với actor/time/reason.
- Dữ liệu review chỉ trở thành training sample sau validation và approval.
- Đo acceptance rate, correction rate và phân tích nhầm lẫn theo category.

## 10. Model promotion

Điều kiện đề xuất trước activation:
- Evaluation trên dataset version cố định.
- Đạt ngưỡng metrics đã được duyệt.
- Không suy giảm nghiêm trọng ở lớp quan trọng.
- Confidence/calibration được đánh giá nếu sử dụng.
- Model artifact/checksum hợp lệ.
- Inference smoke test thành công.
- Có rollback về version trước.

Ngưỡng số học và người phê duyệt: TBD.

## 11. Monitoring

Theo dõi:
- inference latency/error rate.
- phân phối category và score.
- tỷ lệ low-confidence/needs-review.
- tỷ lệ cán bộ sửa nhãn.
- data drift và performance drift khi có ground truth.
- model version đang active.

Không tự động retrain/promote chỉ dựa vào drift alert.

## 12. Rủi ro và giới hạn

- Dataset nhỏ/mất cân bằng.
- Label inconsistency.
- Ngôn ngữ địa phương, viết tắt, lỗi chính tả.
- Distribution shift theo thời gian/khu vực.
- Confidence không calibration.
- Bias giữa các loại phản ánh.
- Model artifact không tương thích preprocessing.

Báo cáo phải trình bày hạn chế và trường hợp model không nên được tin cậy.


## 13. Label schema và Database mapping

Mô hình phải phân loại vào chính xác 11 category_code trong [CLASSIFICATION_SPECIFICATION](../01_REQUIREMENTS/CLASSIFICATION_SPECIFICATION.md). Label encoder/decoder phải lưu label_schema_version và mapping đầy đủ; không phụ thuộc thứ tự ngẫu nhiên của database query hoặc tên hiển thị.

Mỗi model_versions record phải lưu model_family, algorithm_name, version_label, text_representation, preprocessing_version, label_schema_version, source training_run_id, artifact_uri/checksum, hyperparameters và metrics summary. Một prediction phải tham chiếu report_id, preprocessing_run_id, model_version_id và predicted_category_id. Prediction failed/insufficient-information không được gán OTHER mặc định.

Training_metrics phải lưu metric_name/value, data_split, averaging và category_id cho kết quả theo lớp; tối thiểu báo cáo Accuracy, Precision, Recall, Macro F1 và Weighted F1. Không tạo metric giả hoặc điền metrics nếu không có evaluation output thật. Dataset/model của các lần chạy phải dùng cùng label schema để so sánh công bằng.

## 14. Ý nghĩa class OTHER

OTHER là class thứ 11 trong tập supervised classification, không phải catch-all cho lỗi input. Input rỗng/không hợp lệ, văn bản thiếu thông tin và inference error phải được biểu diễn bằng status riêng; prediction category có thể NULL khi inference không thành công hoặc không thể xác định.
