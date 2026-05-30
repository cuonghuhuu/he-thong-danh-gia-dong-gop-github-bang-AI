# Xây dựng hệ thống phân tích và đánh giá mức độ đóng góp của thành viên trong dự án GitHub sử dụng Python và AI

## 1. Giới Thiệu

Đây là ứng dụng desktop dùng Python, PyQt6 và GitHub REST API để phân tích mức độ đóng góp của các thành viên trong một repository GitHub. Hệ thống lấy dữ liệu commit, chuẩn hóa contributor, đánh giá chất lượng đóng góp, phát hiện commit cần xem lại và hiển thị kết quả trên dashboard trực quan.

Ứng dụng sử dụng **rule-based AI** để tạo nhận xét tiếng Việt. Phiên bản hiện tại chưa bắt buộc dùng AI API thật, nhờ đó có thể chạy ổn định trong môi trường học tập, demo và nộp bài.

## 2. Mục Tiêu

- Hỗ trợ nhóm đánh giá đóng góp của từng thành viên trong dự án GitHub.
- Không chỉ dựa vào số commit hoặc số dòng code.
- Kết hợp chất lượng commit, chất lượng code, loại file sửa, độ đều đóng góp và điểm trừ.
- Có nhận xét AI rule-based dễ hiểu bằng tiếng Việt.
- Có dashboard trực quan gồm bảng, biểu đồ và danh sách commit cần xem lại.
- Xuất báo cáo Markdown, CSV và PDF.
- Có thể đóng gói thành file `.exe` để người dùng Windows chạy mà không cần mở PyCharm.

## 3. Chức Năng Chính

- Nhập GitHub URL hoặc nhập riêng Owner/Repository.
- Lấy commit từ GitHub API.
- Chuẩn hóa contributor theo GitHub login, email hoặc tên author.
- Lọc bot và commit tự động khỏi điểm chính.
- Chấm điểm đóng góp theo thang hiển thị **1-10**.
- Tính `quality_score`, `final_score`, `penalty_score`.
- Ước tính thời gian code từ lịch sử commit.
- Phát hiện commit kém chất lượng hoặc commit cần xem lại.
- Hiển thị bảng contributor và bảng commit cần xem lại.
- Hiển thị nhiều biểu đồ: điểm cuối, điểm chất lượng, commit cần xem lại, dòng thêm/xóa, điểm trừ, giờ code ước tính, số ngày hoạt động.
- Xuất báo cáo Markdown/CSV/PDF vào thư mục `reports/`.

## 4. Công Nghệ Sử Dụng

- Python
- PyQt6
- GitHub REST API
- requests
- python-dotenv
- Matplotlib
- ReportLab
- SQLite nếu dùng lại phần lưu trữ cũ
- PyInstaller
- Rule-based AI

## 5. Cấu Trúc Thư Mục

```text
.
├── app.py                 # Entry point chính, chạy GUI hoặc CLI
├── github_client.py       # Gọi GitHub API, chuẩn hóa commit/contributor
├── analyzer.py            # Thuật toán phân tích và chấm điểm đóng góp
├── ai_summary.py          # Sinh nhận xét rule-based AI bằng tiếng Việt
├── main_window.py         # Logic giao diện PyQt6
├── main_window.ui         # Layout giao diện Qt Designer
├── chart_widget.py        # Biểu đồ Matplotlib trong dashboard
├── report_generator.py    # Xuất báo cáo Markdown/CSV/PDF
├── requirements.txt       # Danh sách thư viện cần cài
├── build_exe.bat          # Script build file exe trên Windows
├── .env.example           # Mẫu cấu hình môi trường
└── README.md              # Tài liệu hướng dẫn
```

Các thư mục/file runtime như `.env`, `.venv`, `.git`, `__pycache__`, `.idea`, `build/`, `dist/`, database local và `reports/` không nên đưa vào bản nộp source hoặc bản build.

## 6. Thuật Toán Đánh Giá

Hệ thống giữ điểm nội bộ theo thang 0-100 để dễ tính toán, sau đó hiển thị điểm chính theo thang 1-10:

```text
display_score = round(score_100 / 10, 1)
```

Công thức tổng hợp:

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

Ý nghĩa các thành phần:

- `commit_score`: đánh giá số commit bằng log scale để hạn chế spam commit.
- `code_volume_score`: đánh giá số dòng thêm/xóa, có giới hạn để tránh sửa nhiều dòng rác được điểm quá cao.
- `file_impact_score`: đánh giá mức độ ảnh hưởng của file sửa; core code cao hơn UI/config, tài liệu và file generated/local.
- `quality_score`: đánh giá chất lượng commit message, mức độ thay đổi có ý nghĩa và tác động vào code.
- `consistency_score`: đánh giá độ đều đóng góp theo ngày hoạt động và phiên làm việc.
- `estimated_time_score`: điểm từ thời gian code ước tính, chỉ chiếm một phần nhỏ vì đây là chỉ số tham khảo.
- `integration_score`: ghi nhận commit tích hợp hợp lệ như merge, resolve conflict, tích hợp dashboard/report/analyzer.
- `penalty_score`: điểm trừ do commit message kém, commit quá nhỏ, file local/environment, report tự sinh hoặc tỷ lệ commit cần xem lại cao.

Mức đánh giá theo điểm `/10`:

- `>= 8.5`: Đóng góp chất lượng cao
- `7.0 - 8.4`: Đóng góp tốt
- `5.0 - 6.9`: Đóng góp trung bình
- `3.0 - 4.9`: Đóng góp thấp
- `< 3.0`: Cần cải thiện

## 7. Ước Tính Thời Gian Code

GitHub không lưu chính xác thời gian lập trình, vì vậy hệ thống chỉ ước tính từ thời gian commit:

- Sắp xếp commit của từng contributor theo `commit_date`.
- Commit cách nhau tối đa 2 giờ được gom vào cùng một phiên làm việc.
- Commit đầu tiên của mỗi phiên được tính mặc định 30 phút.
- Khoảng cách giữa hai commit trong cùng phiên được cộng vào thời gian, nhưng mỗi khoảng tối đa 120 phút.
- Mỗi phiên làm việc tối đa 6 giờ để tránh tính nhầm qua đêm.

Chỉ số này dùng để tham khảo, không được xem là thời gian làm việc tuyệt đối.

## 8. AI Nhận Xét

Module `ai_summary.py` tạo nhận xét rule-based bằng tiếng Việt, gồm:

- Mức độ tham gia.
- Chất lượng đóng góp.
- Thời gian code ước tính.
- Điểm mạnh.
- Điểm hạn chế.
- Commit cần xem lại.
- Gợi ý cải thiện.

Ví dụ nhận xét:

```text
Thành viên đạt 8.4/10. Hệ thống ước tính có khoảng 4.5 giờ hoạt động code qua 3 phiên làm việc. Điểm mạnh là có nhiều thay đổi ở file code chính và commit tương đối đều. Tuy nhiên vẫn có 2 commit cần xem lại do message còn chung chung. Nên viết commit message cụ thể hơn và tránh commit chỉ sửa file tự động.
```
## 8. Hướng Dẫn Build File `.exe`

Cài thư viện:

```bash
pip install -r requirements.txt
```

Hoặc nếu muốn cài PyInstaller riêng:

```bash
pip install pyinstaller
```

Build nhanh bằng script:

```bash
build_exe.bat
```

Lệnh thủ công tương đương:

```bash
pyinstaller --noconfirm --clean --windowed --name "GitHub Contribution AI" --add-data "main_window.ui;." --hidden-import "matplotlib.backends.backend_qtagg" app.py
```

Sau khi build, file exe nằm tại:

```text
dist/GitHub Contribution AI/GitHub Contribution AI.exe
```

Trong project này, `main_window.ui` được load qua hàm `resource_path()` để chạy đúng cả khi chạy source và khi đóng gói bằng PyInstaller. Thư mục `reports/` được tự tạo khi ứng dụng chạy nếu chưa tồn tại.

## 9. Hướng Phát Triển

- Tích hợp AI API thật để sinh nhận xét tự nhiên hơn.
- Phân tích Pull Request, Issue, Review và Comment.
- Đánh giá chất lượng test case.
- So sánh đóng góp theo từng giai đoạn.
- Xuất báo cáo PDF đẹp hơn với biểu đồ nhúng trực tiếp.
- Tối ưu thuật toán phát hiện commit kém chất lượng.
