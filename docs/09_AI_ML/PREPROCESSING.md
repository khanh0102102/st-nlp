# PREPROCESSING — PIPELINE TIỀN XỬ LÝ VĂN BẢN TIẾNG VIỆT

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.1 |
| Trạng thái | Partially implemented; module tests passed in CI |
| Ngôn ngữ | Tiếng Việt |
| Bài toán | Single-label text classification |

## 1. Mục tiêu

Chuẩn hóa văn bản phản ánh để tạo đầu vào nhất quán cho Naive Bayes, SVM, CNN 1D và LSTM, đồng thời giữ nguyên thông tin ngữ nghĩa quan trọng. Pipeline phải có version và tái lập giữa training và inference.

## 2. Nguyên tắc

- Lưu text gốc bất biến; preprocessing tạo representation mới.
- Không xóa dấu tiếng Việt mặc định.
- Không xóa từ phủ định như không, chưa, chẳng.
- Giữ số và thông tin có ý nghĩa cho phản ánh.
- Không fit vocabulary/vectorizer trên validation/test.
- Không áp dụng stopword removal mặc định.
- Training và inference phải dùng cùng preprocessing version.
- Text rỗng/không hợp lệ phải bị từ chối hoặc gắn status riêng, không biến thành category OTHER.

## 3. Code baseline hiện có

Module: backend/app/ml/preprocessing.py.

Preprocessing version: vi-nfc-lower-underthesea-v1.

Các hàm chính:
- normalize_text(raw_text): yêu cầu input string; Unicode NFC; chuẩn hóa CRLF/CR; bỏ control characters không cần thiết; gom whitespace; lowercase; giữ dấu, số và từ phủ định.
- preprocess_text(raw_text): reject blank input; dùng underthesea.word_tokenize(..., format="text"); chuẩn hóa output thành token string.
- preprocess_many(raw_texts): áp dụng cùng logic cho batch.
- text_fingerprint(raw_text): SHA-256 trên normalized source text.
- preprocessing_metadata(): ghi tokenizer name/version và normalization policy.

Dependency underthesea==9.5.0 nằm trong ML requirements; không cài vào API runtime image.

## 4. Classical representation

NB và SVM dùng sklearn Pipeline:
1. Vietnamese preprocessing.
2. TF-IDF word n-gram (1, 2), sublinear TF.
3. MultinomialNB hoặc LinearSVC.

Preprocessor được gắn trong Pipeline để fit, predict và predict_proba/decision_function áp dụng cùng representation. Vocabulary/IDF được fit trong training pipeline và serialize cùng model artifact.

- NB score type: MODEL_PROBABILITY_UNCALIBRATED.
- SVM score type: RAW_DECISION_SCORE.

Không diễn giải hai score này thành calibrated probability.

## 5. Neural sequence representation

CNN 1D và BiLSTM tạo vocabulary chỉ từ train texts, có <PAD> và <UNK>, truncate theo max length và lưu vocabulary/label codes/max length cùng artifact. Short sequence được hỗ trợ; test hiện cover input 1, 2 và 4 token.

## 6. Stopwords và stemming

Không loại bỏ stopwords theo danh sách chung mặc định. Các từ chức năng và phủ định có thể quan trọng. Chỉ thêm stopword list/stemming sau ablation study, version hóa và dùng giống nhau ở training/inference.

## 7. Reproducibility và lưu vết

Training run cần lưu preprocessing version, tokenizer/library version, normalization settings, vocabulary/vectorizer artifact, random seed, dataset version và split information. Preprocessing ở report-level phải được ghi trong preprocessing_runs khi tích hợp inference hoàn chỉnh; reports.raw_content luôn bất biến.

## 8. Kiểm thử

CI run #14 xác minh preprocessing/classical tests trong backend suite và neural component tests trong CPU image. Tests bao gồm:
- Unicode tiếng Việt NFC/NFD equivalence.
- Whitespace/newline.
- Giữ dấu, số, từ phủ định.
- Empty/non-string input validation.
- Deterministic output và fingerprint.
- CNN/LSTM forward cho sequence ngắn.
- Artifact load/predict parity ở mức component.

Các tests chưa thay thế đánh giá chất lượng trên dataset đô thị thật.

## 9. Công việc còn lại

- Tạo DB integration tests đảm bảo preprocessing run/prediction tham chiếu đúng version.
- Đánh giá tokenization và feature alternatives bằng ablation trên dataset được cấp phép.
- Chốt policy PII, URL/phone/address normalization và retention trước khi xử lý dữ liệu thật.
- Implement authenticated inference service dùng chính xác preprocessing version của active model.
