# Hệ thống đánh giá đóng góp GitHub bằng Python và AI

Đề tài: **Xây dựng hệ thống phân tích và đánh giá mức độ đóng góp của thành viên trong dự án GitHub sử dụng Python và AI**.

Ứng dụng dùng Python, PyQt6 và GitHub API để phân tích contributor trong một repository. Phiên bản hiện tại không chỉ chấm theo số commit hoặc số dòng code, mà bổ sung rule-based AI để đánh giá chất lượng commit, tác động vào source code và phát hiện commit kém chất lượng.

## Chức năng chính

- Nhập repository bằng GitHub URL hoặc Owner/Repository.
- Lấy commit từ GitHub API, bao gồm additions, deletions, file thay đổi và patch/diff khi GitHub cung cấp.
- Gom dữ liệu theo contributor, có chuẩn hoá identity bằng GitHub login hoặc email/name để tránh tách một người thành nhiều contributor khi GitHub cung cấp đủ thông tin.
- Bỏ qua bot và commit tự động như `actions-user`, `github-actions[bot]`, `dependabot[bot]`, `auto update report`, `automatic report`, `generated report`.
- Tính điểm nội bộ 0-100 nhưng hiển thị điểm đánh giá chính theo thang /10 để dễ đọc hơn.
- Ước tính thời gian code từ khoảng cách giữa các commit, số ngày hoạt động và số phiên làm việc.
- Phát hiện commit đáng nghi như `test`, `update`, `abc`, `ok`, `nộp`, `final`, `backup`, `tmp`, `demo`.
- Chấm chất lượng code theo loại file thay đổi: source code, tài liệu/báo cáo, file tự động sinh hoặc file môi trường local.
- Sinh nhận xét AI rule-based bằng tiếng Việt.
- Hiển thị dashboard 1 trang với bảng contributor, bảng commit cần xem lại và nhiều biểu đồ đánh giá.
- Xuất báo cáo Markdown, CSV và PDF.
- Bỏ phần lịch sử phân tích trên giao diện để tập trung vào đánh giá chất lượng đóng góp.

## Công nghệ sử dụng

- Python 3.11+
- PyQt6
- requests
- python-dotenv
- matplotlib
- reportlab
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
```

Ghi chú:

- `GITHUB_TOKEN` không bắt buộc với repo public.
- Nếu không có token, GitHub giới hạn request thấp hơn.
- Không hardcode token hoặc AI API key trong code.
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
- Thẻ tổng quan: tổng commit, contributor, additions, deletions, tổng giờ code ước tính, số phiên làm việc, điểm chất lượng trung bình, số commit cần xem lại.
- Bảng contributor: số commit, additions, deletions, files, giờ code ước tính, số ngày hoạt động, điểm chất lượng /10, điểm thời gian /10, điểm cuối /10, điểm trừ, mức đánh giá, số commit cần xem lại và nhận xét ngắn.
- Bảng `Commit kém chất lượng / Commit cần xem lại`: contributor, SHA, message, lý do bị đánh dấu và mức độ nghi ngờ.
- Biểu đồ: tỷ lệ điểm cuối, điểm chất lượng, số commit cần xem lại, so sánh dòng thêm/xoá, điểm trừ, giờ code ước tính và số ngày hoạt động.
- Khung nhận xét AI rule-based.

## Tiêu chí đánh giá chất lượng

Trước khi tính điểm, hệ thống chuẩn hoá contributor theo thứ tự ưu tiên:

- GitHub login nếu commit có liên kết với tài khoản GitHub hợp lệ.
- Email hoặc tên author nếu không có login.
- Alias mapping chỉ dùng để gộp đúng danh tính khi cùng một người có nhiều tên/email khác nhau; alias không được dùng để cộng điểm riêng.

Các commit từ bot hoặc commit sinh báo cáo tự động bị loại khỏi điểm chính. Kết quả vẫn ghi lại:

- `ignored_bot_commit_count`: số commit bot đã loại.
- `ignored_auto_commit_count`: số commit tự động đã loại.
- `ignored_commits`: danh sách commit bot/tự động đã loại, gồm sha ngắn, contributor, message và lý do loại.

Bot bị loại gồm `actions-user`, `github-actions[bot]`, `dependabot[bot]`. Commit tự động bị loại nếu message chứa `auto update report`, `automatic report` hoặc `generated report`.

Hệ thống bổ sung các chỉ số:

- `commit_message_score`: chất lượng commit message.
- `meaningful_change_score`: mức độ có ý nghĩa của thay đổi.
- `code_impact_score`: tác động vào file source code chính.
- `quality_score`: điểm chất lượng tổng hợp nội bộ 0-100.
- `quality_score_display`: điểm chất lượng hiển thị theo thang /10.
- `estimated_coding_hours`: thời gian code ước tính từ lịch sử commit.
- `active_days`: số ngày có commit được tính điểm.
- `coding_sessions`: số phiên làm việc, gom theo khoảng cách commit tối đa 2 giờ.
- `estimated_time_score`: điểm thời gian nội bộ 0-100, dùng log scale và có giới hạn.
- `consistency_score`: điểm độ đều đóng góp theo ngày hoạt động và phiên làm việc.
- `integration_score`: điểm ghi nhận vai trò tích hợp hợp lệ, không gắn với tên contributor.
- `suspicious_commit_count`: số commit cần xem lại.
- `suspicious_commit_ratio`: tỷ lệ commit cần xem lại.
- `penalty_score`: điểm phạt nội bộ do commit kém chất lượng.
- `penalty_score_display`: điểm trừ hiển thị theo thang 0-10, chuẩn hóa từ penalty nội bộ tối đa 30 điểm.

Rule chính:

- Commit message rõ ràng, mô tả công việc cụ thể thì điểm cao.
- Message quá chung như `test`, `update`, `abc`, `ok`, `nộp`, `final`, `tmp`, `demo` bị trừ điểm.
- Chữ `fix` không bị coi là xấu tuyệt đối. Ví dụ `Fix GitHub token handling` vẫn là message tốt vì có ngữ cảnh rõ.
- Commit sửa `.py`, `.ui`, `requirements.txt` được xem là có tác động kỹ thuật cao hơn.
- Commit chỉ sửa `README.md`, `report.md`, `reports/` được xem là thiên về tài liệu/báo cáo.
- Commit sửa `.idea/`, `__pycache__/`, `.env`, database SQLite hoặc file môi trường local bị trừ điểm.

## Công thức điểm mới

```text
raw_score =
    0.10 * commit_score
  + 0.15 * code_volume_score
  + 0.15 * file_impact_score
  + 0.25 * quality_score
  + 0.15 * consistency_score
  + 0.10 * estimated_time_score
  + 0.10 * integration_score

final_score = raw_score - penalty_score
```

Ý nghĩa:

- `commit_score`: số commit, dùng log để hạn chế spam commit.
- `code_volume_score`: additions + deletions, có giới hạn để tránh sửa nhiều dòng rác được điểm quá cao.
- `file_impact_score`: core code > UI/config > tài liệu > file generated/local.
- `quality_score`: chất lượng message, ý nghĩa thay đổi và tác động code.
- `consistency_score`: mức độ đóng góp đều theo ngày hoạt động và phiên làm việc.
- `estimated_time_score`: điểm thời gian code ước tính, dùng log scale và cap để tránh tính quá mức.
- `integration_score`: ghi nhận merge, resolve conflict, tích hợp dashboard/report/analyzer hoặc cấu trúc dự án nếu commit có nội dung thật.
- `penalty_score`: điểm trừ do commit đáng nghi hoặc file không nên tính cao.

Điểm cuối nội bộ được chuẩn hóa trong khoảng 0-100. Giao diện và báo cáo hiển thị `final_score_display = round(final_score / 10, 1)` theo thang /10.

## Ước tính thời gian code

GitHub không lưu chính xác thời gian lập trình, nên hệ thống chỉ ước tính từ `commit_date`:

- Commit của từng contributor được sắp xếp theo thời gian tăng dần.
- Các commit cách nhau tối đa 2 giờ được gom vào cùng một phiên làm việc.
- Commit đầu tiên của mỗi phiên được tính mặc định 30 phút.
- Khoảng cách giữa 2 commit trong cùng phiên được cộng vào thời gian, nhưng mỗi khoảng tối đa 120 phút.
- Mỗi phiên làm việc tối đa 6 giờ để tránh tính nhầm qua đêm.
- Một commit đơn lẻ tương đương khoảng 0.5 giờ hoạt động.

Đây là chỉ số tham khảo, không phải thời gian làm việc tuyệt đối. Vì vậy `estimated_time_score` chỉ chiếm 10% công thức điểm.

## Cách đọc điểm

- `quality_score`: tập trung vào chất lượng commit/code, gồm commit message, file code chính, mức độ thay đổi có ý nghĩa và commit cần xem lại.
- `final_score`: điểm tổng hợp sau khi xét số commit, dòng code, loại file, chất lượng, độ đều đóng góp, thời gian ước tính, tích hợp và điểm trừ.
- Một contributor có thể có `final_score` cao hơn `quality_score` nếu có nhiều đóng góp đều, tác động file tốt và thời gian code ước tính hợp lý, nhưng vẫn có một số commit cần xem lại.

## Mức đánh giá contributor

- `>= 8.5`: Đóng góp chất lượng cao
- `7.0 - 8.4`: Đóng góp tốt
- `5.0 - 6.9`: Đóng góp trung bình
- `3.0 - 4.9`: Đóng góp thấp
- `< 3.0`: Cần cải thiện

Nhãn phụ có thể gồm:

- Contributor chất lượng
- Contributor tích cực nhưng cần cải thiện chất lượng
- Contributor ít đóng góp
- Contributor có nhiều commit kém chất lượng
- Contributor thiên về tài liệu/báo cáo
- Contributor thiên về code chính

## Báo cáo

Báo cáo Markdown/CSV/PDF có:

- Bảng contributor.
- Điểm chất lượng /10, điểm trừ /10, điểm cuối /10, `suspicious_commit_count`, `suspicious_commit_ratio`.
- Mức đánh giá và nhận xét AI.
- Bảng commit cần xem lại kèm SHA, message, lý do bị đánh dấu và mức độ nghi ngờ.
- Thống kê hỗ trợ biểu đồ: điểm cuối, điểm chất lượng, commit cần xem lại, dòng thêm/xoá và điểm trừ.
- Mục `Commit bot/tự động đã loại` để kiểm tra lại các commit không được đưa vào điểm chính.

## Hướng phát triển

- Kết nối AI API thật qua `AI_API_KEY`.
- Phân tích thêm pull request, issue, review và comment.
- Tính chất lượng test và mức độ review code.
- So sánh đóng góp theo từng giai đoạn thời gian.
