# Hệ thống đánh giá đóng góp GitHub bằng Python và AI

Đề tài: **Xây dựng hệ thống phân tích và đánh giá mức độ đóng góp của thành viên trong dự án GitHub sử dụng Python và AI**.

Ứng dụng dùng Python, PyQt6 và GitHub API để phân tích contributor trong một repository. Phiên bản hiện tại không chỉ chấm theo số commit hoặc số dòng code, mà bổ sung rule-based AI để đánh giá chất lượng commit, tác động vào source code và phát hiện commit kém chất lượng.

## Chức năng chính

- Nhập repository bằng GitHub URL hoặc Owner/Repository.
- Lấy commit từ GitHub API, bao gồm additions, deletions, file thay đổi và patch/diff khi GitHub cung cấp.
- Gom dữ liệu theo contributor, có chuẩn hoá identity bằng GitHub login, email/name và alias để tránh tách một người thành nhiều contributor.
- Bỏ qua bot và commit tự động như `actions-user`, `github-actions[bot]`, `dependabot[bot]`, `auto update report`, `automatic report`, `generated report`.
- Tính điểm đóng góp 0-100 dựa trên số lượng và chất lượng.
- Ghi nhận vai trò tích hợp hệ thống qua merge commit hợp lệ, commit code lõi và commit tài liệu có ý nghĩa.
- Không ưu tiên cá nhân nào theo tên; điểm dựa trên dữ liệu commit thực tế.
- Phát hiện commit đáng nghi như `test`, `update`, `abc`, `ok`, `nộp`, `final`, `backup`, `tmp`, `demo`.
- Chấm chất lượng code theo loại file thay đổi: source code, tài liệu/báo cáo, file tự động sinh hoặc file môi trường local.
- Sinh nhận xét AI rule-based bằng tiếng Việt.
- Hiển thị dashboard 1 trang với bảng contributor và biểu đồ.
- Xuất báo cáo Markdown, CSV và PDF.
- Lưu lịch sử phân tích vào SQLite local.

## Công nghệ sử dụng

- Python 3.11+
- PyQt6
- requests
- python-dotenv
- matplotlib
- reportlab
- SQLite
- GitHub REST API

## Cấu trúc project

```text
.
├── app.py
├── github_client.py
├── analyzer.py
├── ai_summary.py
├── main_window.py
├── main_window.ui
├── chart_widget.py
├── db_manager.py
├── report_generator.py
├── requirements.txt
├── README.md
├── report.md
└── reports/
```

## Cài đặt

```bash
pip install -r requirements.txt
```

## Cấu hình `.env`

Tạo file `.env` từ `.env.example` nếu muốn cấu hình sẵn:

```env
GITHUB_TOKEN=
GITHUB_REPO_URL=https://github.com/owner/repo
REPO_OWNER=owner
REPO_NAME=repo
SO_LUONG_COMMIT=30
AI_API_KEY=
CONTRIBUTOR_ALIASES=
```

Ghi chú:

- `GITHUB_TOKEN` không bắt buộc với repo public.
- Nếu không có token, GitHub giới hạn request thấp hơn.
- Không hardcode token hoặc AI API key trong code.
- `CONTRIBUTOR_ALIASES` là tùy chọn, dùng định dạng `ten_phu=ten_chuan;email=ten_chuan` nếu cần gộp identity. Mặc định hệ thống không hardcode alias cá nhân nào.
- Không commit file `.env`, `.venv`, database SQLite local hoặc báo cáo sinh tự động.

## Chạy chương trình

Chạy giao diện:

```bash
python app.py
```

Chạy CLI:

```bash
python app.py --cli
```

Ví dụ test:

- GitHub URL: `https://github.com/cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI`
- Số commit: `30`

## Dashboard

Giao diện chính gồm:

- Vùng nhập GitHub URL, Owner, Repository, Token và số commit.
- Nút phân tích và các nút xuất báo cáo Markdown/CSV/PDF.
- Thẻ tổng quan: tổng commit, contributor, additions, deletions, điểm chất lượng trung bình, số commit cần xem lại.
- Bảng contributor: commit, additions, deletions, files, quality score, penalty, final score, mức đánh giá, nhận xét ngắn.
- Báo cáo xuất ra có thêm integration commits, core code commits, documentation commits và nhận xét vai trò contributor.
- Biểu đồ: tỷ lệ final score, quality score và số commit cần xem lại.
- Khung nhận xét AI rule-based.

## Tiêu chí đánh giá chất lượng

Trước khi tính điểm, hệ thống chuẩn hoá contributor theo thứ tự ưu tiên:

- GitHub login nếu commit có liên kết với tài khoản GitHub hợp lệ.
- Email hoặc tên author nếu không có login.
- Alias cấu hình qua `CONTRIBUTOR_ALIASES` nếu cần gộp nhiều identity của cùng một người; mặc định không có alias cá nhân hardcode.

Các commit từ bot hoặc commit sinh báo cáo tự động bị loại khỏi điểm chính. Kết quả vẫn ghi lại:

- `ignored_bot_commit_count`: số commit bot đã loại.
- `ignored_auto_commit_count`: số commit tự động đã loại.

Hệ thống bổ sung các chỉ số:

- `commit_message_score`: chất lượng commit message.
- `meaningful_change_score`: mức độ có ý nghĩa của thay đổi.
- `code_impact_score`: tác động vào file source code chính.
- `quality_score`: điểm chất lượng tổng hợp.
- `integration_commit_count`: số commit tích hợp hợp lệ như merge pull request hoặc merge branch có dấu hiệu tích hợp thật.
- `core_code_commit_count`: số commit có thay đổi vào code lõi/source code.
- `documentation_commit_count`: số commit có đóng góp tài liệu, README hoặc báo cáo.
- `review_or_merge_activity_score`: điểm hoạt động tích hợp/merge khi dữ liệu commit đủ để ghi nhận.
- `suspicious_commit_count`: số commit cần xem lại.
- `suspicious_commit_ratio`: tỷ lệ commit cần xem lại.
- `penalty_score`: điểm phạt do commit kém chất lượng.

Vai trò trưởng nhóm/tích hợp chỉ được ghi nhận khi contributor có hoạt động thật như merge pull request, merge branch, sửa lỗi hệ thống, cập nhật README hoặc báo cáo có nội dung. Không có rule nào cộng điểm theo tên contributor.

Rule chính:

- Commit message rõ ràng, mô tả công việc cụ thể thì điểm cao.
- Message quá chung như `test`, `update`, `abc`, `ok`, `nộp`, `final`, `tmp`, `demo` bị trừ điểm.
- Chữ `fix` không bị coi là xấu tuyệt đối. Ví dụ `Fix GitHub token handling` vẫn là message tốt vì có ngữ cảnh rõ.
- `Initial commit` không bị xem là xấu tuyệt đối; hệ thống vẫn xét file thay đổi và mức độ có ý nghĩa.
- `Merge pull request` hoặc `Merge branch` được ghi nhận là commit tích hợp nếu không chỉ sửa file môi trường/local.
- Commit sửa `.py`, `.ui`, `requirements.txt` được xem là có tác động kỹ thuật cao hơn.
- Commit chỉ sửa `README.md`, `report.md`, `reports/` được xem là đóng góp tài liệu hợp lệ nếu có nhiều nội dung hướng dẫn, thuật toán, cấu hình, test hoặc báo cáo có ý nghĩa.
- Commit sửa `.idea/`, `__pycache__/`, `.env`, database SQLite hoặc file môi trường local bị trừ điểm.

## Công thức điểm mới

```text
final_score =
    0.18 * commit_score
  + 0.18 * code_volume_score
  + 0.18 * file_impact_score
  + 0.24 * quality_score
  + 0.12 * consistency_score
  + 0.10 * review_or_merge_activity_score
  - penalty_score
```

Ý nghĩa:

- `commit_score`: số commit, dùng log để hạn chế spam commit.
- `code_volume_score`: additions + deletions, có giới hạn để tránh sửa nhiều dòng rác được điểm quá cao.
- `file_impact_score`: file source code có trọng số cao hơn file tài liệu/báo cáo.
- `quality_score`: chất lượng message, ý nghĩa thay đổi và tác động code.
- `consistency_score`: mức độ đóng góp đều, không chỉ một commit lớn.
- `review_or_merge_activity_score`: ghi nhận hoạt động tích hợp/merge hợp lệ, áp dụng cho mọi contributor theo dữ liệu commit.
- `penalty_score`: điểm trừ do commit đáng nghi hoặc file không nên tính cao.

Điểm cuối được chuẩn hóa trong khoảng 0-100.

## Mức đánh giá contributor

- `>= 85`: Đóng góp chất lượng cao
- `70 - 84`: Đóng góp tốt
- `50 - 69`: Đóng góp trung bình
- `30 - 49`: Đóng góp thấp
- `< 30`: Cần cải thiện

Nhãn phụ có thể gồm:

- Contributor chất lượng
- Contributor tích cực nhưng cần cải thiện chất lượng
- Contributor ít đóng góp
- Contributor có nhiều commit kém chất lượng
- Contributor có vai trò tích hợp hệ thống
- Contributor thiên về tài liệu/báo cáo
- Contributor thiên về code chính

## Báo cáo

Báo cáo Markdown/CSV/PDF có:

- Bảng contributor.
- `integration_commit_count`, `core_code_commit_count`, `documentation_commit_count`.
- `quality_score`, `penalty_score`, `suspicious_commit_count`, `suspicious_commit_ratio`.
- Nhận xét vai trò contributor, bao gồm vai trò tích hợp hệ thống nếu có dữ liệu phù hợp.
- Mức đánh giá và nhận xét AI.
- Danh sách commit đáng nghi kèm lý do.

## Hướng phát triển

- Kết nối AI API thật qua `AI_API_KEY`.
- Phân tích thêm pull request, issue, review và comment.
- Tính chất lượng test và mức độ review code.
- So sánh đóng góp theo từng giai đoạn thời gian.
