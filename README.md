# Hệ thống đánh giá đóng góp GitHub bằng Python và AI

Đề tài bài kết thúc học phần: **Xây dựng hệ thống phân tích và đánh giá mức độ đóng góp của thành viên trong dự án GitHub sử dụng Python và AI**.

Ứng dụng dùng Python để lấy dữ liệu commit từ GitHub API, tổng hợp chỉ số theo từng contributor, tính điểm đóng góp, sinh nhận xét AI rule-based bằng tiếng Việt, hiển thị kết quả trên giao diện PyQt6 và xuất báo cáo.

## Mục tiêu

- Nhập thông tin GitHub repository bằng URL đầy đủ hoặc bằng Owner/Repository.
- Lấy danh sách commit và chi tiết commit từ GitHub API.
- Thống kê số commit, additions, deletions, số file thay đổi và tổng thay đổi theo contributor.
- Tính điểm đóng góp trên thang 0-100.
- Phân loại mức đóng góp và loại đóng góp.
- Hiển thị bảng, biểu đồ, nhận xét AI rule-based và lịch sử phân tích.
- Xuất báo cáo Markdown, CSV và PDF.

## Chức năng chính

- Phân tích repository public hoặc private nếu có token hợp lệ.
- Hỗ trợ nhập `https://github.com/owner/repo`, `owner/repo`, hoặc nhập riêng Owner và Repository.
- Xử lý contributor không có GitHub login bằng cách fallback sang tên author trong commit.
- Hiển thị dashboard tổng quan, bảng contributor, biểu đồ và nhận xét.
- Lưu lịch sử phân tích vào SQLite local.
- Xuất báo cáo vào thư mục `reports/`.
- Có chế độ CLI để chạy nhanh hoặc dùng trong GitHub Actions.

## Công nghệ sử dụng

- Python 3.11+
- PyQt6
- requests
- python-dotenv
- matplotlib
- reportlab
- SQLite
- GitHub REST API

## Cấu trúc thư mục

```text
.
├── app.py                  # Điểm chạy chính: GUI hoặc CLI
├── github_client.py         # Gọi GitHub API, xử lý token, lỗi HTTP, parse URL repo
├── analyzer.py              # Gom commit, tính metrics, tính điểm, tạo kết quả phân tích
├── ai_summary.py            # AI rule-based: phân loại và nhận xét tiếng Việt
├── main_window.py           # Logic giao diện PyQt6
├── main_window.ui           # Layout giao diện PyQt6
├── chart_widget.py          # Vẽ biểu đồ bằng matplotlib
├── db_manager.py            # Lưu và đọc lịch sử phân tích bằng SQLite
├── report_generator.py      # Xuất Markdown, CSV, PDF
├── requirements.txt         # Danh sách thư viện cần cài
├── report.md                # Báo cáo mẫu hoặc báo cáo sinh bởi CLI
└── reports/                 # Báo cáo xuất từ giao diện
```

## Cài đặt

```bash
pip install -r requirements.txt
```

Trong PyCharm, mở project, chọn Python interpreter phù hợp rồi cài dependencies từ `requirements.txt`.

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

- `GITHUB_TOKEN` không bắt buộc với repository public, nhưng nên dùng để tăng giới hạn GitHub API.
- Không hardcode token hoặc API key trong source code.
- Không commit file `.env`, database SQLite local, `.venv`, `__pycache__` hoặc báo cáo sinh tự động trong `reports/`.

## Chạy chương trình

Chạy giao diện desktop:

```bash
python app.py
```

Chạy CLI:

```bash
python app.py --cli
```

Ví dụ test:

- GitHub URL: `https://github.com/cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI`
- Owner: `cuonghuhuu`
- Repository: `he-thong-danh-gia-dong-gop-github-bang-AI`
- Số commit: `30`

## Thuật toán chấm điểm

Mỗi contributor được tính các chỉ số:

- `commit_count`: số commit
- `total_additions`: tổng số dòng thêm
- `total_deletions`: tổng số dòng xóa
- `changed_files_count`: số file khác nhau đã thay đổi
- `total_changes`: `total_additions + total_deletions`

Điểm thành phần được chuẩn hóa về thang 0-100 bằng `log1p(value)` theo giá trị lớn nhất trong tập contributor. Cách này giảm ảnh hưởng của contributor có thay đổi quá lớn.

```text
final_score = 0.35 * commit_score
            + 0.35 * code_score
            + 0.20 * file_score
            + 0.10 * balance_score
```

Trong đó:

- `commit_score`: dựa trên số commit.
- `code_score`: dựa trên tổng additions + deletions.
- `file_score`: dựa trên số file thay đổi.
- `balance_score`: đánh giá mức cân bằng giữa additions và deletions.

Mức đóng góp:

- `>= 80`: Đóng góp rất tích cực
- `60 - 79`: Đóng góp tốt
- `40 - 59`: Đóng góp trung bình
- `< 40`: Đóng góp thấp

## AI rule-based

Project chưa yêu cầu bắt buộc dùng API AI thật, nên phần nhận xét đang dùng rule-based AI. Hệ thống tự tạo nhận xét tiếng Việt gồm:

- Mức độ tham gia.
- Điểm mạnh.
- Hạn chế.
- Gợi ý cải thiện.

Nếu cần phát triển tiếp, có thể kết nối OpenAI API hoặc mô hình AI khác qua biến môi trường `AI_API_KEY`.

## Xử lý lỗi

Ứng dụng có xử lý các trường hợp thường gặp:

- Token GitHub sai hoặc hết hạn.
- Repository không tồn tại hoặc không có quyền truy cập.
- GitHub API bị rate limit.
- Repository không có commit.
- Dữ liệu commit thiếu `author`, `stats` hoặc danh sách file.
- Owner/Repository để trống hoặc URL repository không hợp lệ.

## Hướng phát triển

- Thêm phân tích pull request, issue, review và comment.
- Tính thêm chất lượng commit message và mức độ test.
- So sánh đóng góp theo thời gian.
- Kết nối AI API thật để tạo nhận xét tự nhiên hơn.
- Đóng gói thành file cài đặt desktop.
