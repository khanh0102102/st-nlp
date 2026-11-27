# GIT WORKFLOW — QUY TRÌNH LÀM VIỆC VỚI GIT

| Thuộc tính | Giá trị |
|---|---|
| Phiên bản | 1.0 |
| Trạng thái | Proposed baseline |
| Repository | https://github.com/khanh0102102/st-nlp |

## 1. Nhánh chính

- main: nhánh ổn định, chứa thay đổi đã review.
- feature/<name>: chức năng mới.
- fix/<name>: sửa lỗi.
- docs/<name>: cập nhật tài liệu.
- chore/<name>: cấu hình, tooling, dependency hoặc công việc bảo trì.
- hotfix/<name>: sửa lỗi khẩn cấp trên bản phát hành.

Không làm việc trực tiếp trên main trừ khi chủ dự án yêu cầu rõ.

## 2. Quy trình chuẩn

1. Đồng bộ main.
2. Tạo branch từ main.
3. Đọc AGENTS.md và tài liệu module.
4. Tạo thay đổi nhỏ theo task.
5. Chạy formatter/linter/type check/test liên quan.
6. Kiểm tra git diff và git status.
7. Commit với message đúng convention.
8. Push branch.
9. Tạo Pull Request.
10. Review code, docs, test và migration.
11. Merge sau khi checks/review đạt.
12. Xóa branch sau merge nếu không cần giữ.

## 3. Conventional Commits

Định dạng:
    <type>(<scope>): <imperative summary>

Type thường dùng:
- feat: chức năng mới.
- fix: sửa lỗi.
- docs: tài liệu.
- refactor: tái cấu trúc không đổi hành vi.
- test: test.
- chore: tooling/configuration.
- build: build/dependency.
- ci: pipeline.

Ví dụ:
    docs(requirements): add initial ST-NLP SRS
    feat(citizen): add report submission flow
    fix(review): prevent unauthorized label update
    test(api): cover report ownership checks

## 4. Pull Request checklist

- [ ] Mục tiêu và phạm vi rõ.
- [ ] Liên kết issue/task.
- [ ] Đọc và tuân thủ AGENTS.md.
- [ ] Không thay đổi ngoài phạm vi.
- [ ] Test đã chạy và ghi kết quả.
- [ ] API/database/docs đồng bộ.
- [ ] Có migration và hướng rollback nếu schema đổi.
- [ ] Không có secret/dữ liệu cá nhân.
- [ ] Có screenshot/video nếu UI thay đổi.
- [ ] Có lưu ý cấu hình/deployment.

## 5. Quy tắc branch protection đề xuất

Khi repository và CI đã sẵn sàng:
- Bắt buộc Pull Request để merge main.
- Yêu cầu CI xanh.
- Ít nhất một review nếu có cộng tác viên.
- Chặn force push và xóa main.
- Yêu cầu resolve review thread.
- Có thể dùng CODEOWNERS cho tài liệu/schema nhạy cảm.

Cài đặt cụ thể phụ thuộc GitHub plan và nhu cầu cộng tác.

## 6. Conflict và migration

- Không force push để giải quyết conflict tùy tiện.
- Rebase/merge main vào feature branch theo workflow đã thống nhất.
- Nếu hai PR cùng thay schema, người phụ trách DB phải phối hợp thứ tự migration.
- Không sửa migration đã apply ở môi trường chia sẻ; tạo migration mới.

## 7. Release và tag

- Dùng tag version theo SemVer khi sản phẩm có release.
- Ghi release note: tính năng, breaking change, migration, security fix và known issues.
- Gắn model version với application release khi inference compatibility phụ thuộc.
- Không coi commit merge là release production nếu chưa deploy/verify.
