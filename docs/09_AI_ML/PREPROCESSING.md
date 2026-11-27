# PREPROCESSING — PIPELINE TIỀN XỬ LÝ VĂN BẢN TIẾNG VIỆT

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Proposed pipeline |
| Ngôn ngữ | Tiếng Việt |
| Bài toán | Single-label text classification, cần xác nhận trong SRS |

## 1. Mục tiêu

Chuẩn hóa văn bản phản ánh để tạo đầu vào nhất quán cho Naive Bayes, SVM, CNN 1D và LSTM, đồng thời giữ nguyên thông tin ngữ nghĩa quan trọng. Pipeline phải có version và tái lập được giữa training và inference.

## 2. Nguyên tắc quan trọng

- Lưu text gốc bất biến; preprocessing tạo representation mới.
- Cùng một phiên bản preprocessing phải được dùng nhất quán khi train và infer.
- Không xóa dấu tiếng Việt mặc định; dấu có thể phân biệt từ.
- Không xóa từ phủ định như không, chưa, chẳng vì có thể đảo nghĩa.
- Không loại bỏ số, đơn vị, thời gian hoặc ký hiệu có ý nghĩa nếu chưa đánh giá.
- Không fit vocab/vectorizer trên validation/test.
- Tránh leakage từ dữ liệu tương lai hoặc bản sao gần giống.
- Mỗi thay đổi preprocessing phải được đánh giá bằng experiment.

## 3. Pipeline đề xuất

1. Validate input: kiểu, encoding, length và null.
2. Unicode normalization: thống nhất Unicode representation, ưu tiên NFC nếu phù hợp.
3. Chuẩn hóa newline, tab và khoảng trắng thừa.
4. Xử lý HTML/markup nếu nguồn dữ liệu có, theo nguyên tắc không làm mất nghĩa.
5. Chuẩn hóa URL/mention/phone/identifier thành placeholder khi policy cho phép.
6. Xử lý emoji/ký tự đặc biệt theo kết quả thí nghiệm; không xóa tự động mọi ký tự.
7. Tokenization tiếng Việt theo thư viện được chọn.
8. Tạo representation theo model family.
9. Kiểm tra output rỗng/quá dài và gắn preprocessing version.

## 4. Nhánh đặc trưng cho mô hình truyền thống

### Naive Bayes và SVM
- Dùng word/character n-gram TF-IDF làm baseline có thể so sánh.
- Fit vectorizer chỉ trên train set.
- Lưu vocabulary, IDF và config cùng artifact.
- Thử word-level, character-level hoặc kết hợp bằng experiment.
- Cân nhắc class_weight/sample_weight cho SVM nếu imbalance.

### CNN 1D và LSTM
- Tokenize và map token thành sequence.
- Vocabulary/embedding chỉ fit trên train hoặc dùng embedding được kiểm soát.
- Quy định padding/truncation length từ thống kê train.
- Unknown token phải có mapping ổn định.
- Lưu tokenizer/vocabulary, max sequence length và embedding config cùng model.
- Không dùng preprocessing khác ở inference.

## 5. Stopwords và stemming

Không loại bỏ stopwords theo danh sách chung một cách mặc định. Các từ chức năng và phủ định có thể quan trọng với phân loại phản ánh. Chỉ áp dụng sau ablation study và lưu version danh sách. Stemming/lemmatization tiếng Việt không được giả định có lợi; cần thử nghiệm.

## 6. Dữ liệu thiếu chuẩn

- Text rỗng: từ chối dự đoán hoặc gắn trạng thái không đủ dữ liệu.
- Text chỉ có URL/ký hiệu: áp dụng policy đầu vào.
- Văn bản trộn ngôn ngữ: giữ nguyên hoặc xử lý theo policy, không dịch tự động.
- Text cực dài: giới hạn/segment theo quy định.
- Text có PII: xử lý theo privacy policy, không log raw.
- Nội dung độc hại/không phù hợp: xử lý như dữ liệu người dùng, không thực thi.

## 7. Reproducibility

Mỗi training run lưu:
- preprocessing_version.
- normalization settings.
- tokenizer/library/version.
- vectorizer/vocabulary artifact.
- stopword list version nếu dùng.
- max sequence length/padding strategy.
- random seed.
- dataset version và split IDs.

## 8. Kiểm thử preprocessing

- Unicode tiếng Việt có dấu.
- Hai dạng Unicode tương đương.
- Khoảng trắng/newline.
- Dấu câu, số, đơn vị, biển số/địa chỉ giả lập.
- Từ phủ định.
- Text rỗng và cực dài.
- Emoji/URL/HTML.
- Tính deterministic trên cùng input/version.
- Training/inference parity.

## 9. Đánh giá

Dùng ablation study để so sánh raw normalization, word n-gram, char n-gram, tokenization và stopword policy. Đánh giá trên validation; chỉ báo cáo cuối trên test set độc lập. Không chọn pipeline chỉ dựa trên accuracy.


## 10. Lưu vết trong Database

Mỗi lần pipeline chạy cho một report tạo một preprocessing_runs record gồm report_id, preprocessing_version, tokenizer/library version, normalization_config, stopword_config, processing_status, processing_time_ms và error_code nếu thất bại. processed_text có thể lưu trực tiếp hoặc ở artifact storage theo privacy/retention policy. predictions phải tham chiếu preprocessing_run_id chính xác đã dùng. reports.raw_content luôn bất biến.

Pipeline baseline cần hỗ trợ Unicode NFC, chuẩn hóa whitespace, tokenization tiếng Việt và cấu hình stopword theo version. **Không mặc định xóa toàn bộ stopwords**: giữ từ phủ định như không/chưa/chẳng và các từ có ý nghĩa phân loại. Chỉ áp dụng danh sách stopwords đã được đánh giá bằng ablation study; training và inference phải dùng đúng cùng version/cấu hình. Không fit vocabulary/vectorizer bằng validation/test.

`+String.raw`