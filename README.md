# Hệ thống đánh giá đóng góp GitHub bằng AI

Ứng dụng desktop Python dùng **PyQt6**, **GitHub API**, **Matplotlib**, **ReportLab** và **PyInstaller** để phân tích mức độ đóng góp của thành viên trong một repository GitHub.

Hệ thống lấy commit từ GitHub, chuẩn hóa contributor, chấm điểm theo nhiều tiêu chí, phát hiện commit cần xem lại, tạo nhận xét AI rule-based bằng tiếng Việt và xuất báo cáo Markdown/CSV/PDF.

## Chức năng chính

- Nhập GitHub URL hoặc Owner/Repository.
- Lấy và chuẩn hóa dữ liệu commit qua GitHub REST API.
- Gom contributor theo GitHub login, author name và email.
- Loại commit bot khỏi điểm chính.
- Chấm điểm đóng góp theo commit, khối lượng thay đổi, loại file, chất lượng commit, độ đều, thời gian code ước tính, vai trò tích hợp và điểm trừ.
- Hiển thị dashboard PyQt6 gồm bảng contributor, biểu đồ và bảng commit cần xem lại.
- Sinh nhận xét AI rule-based, không bắt buộc dùng AI API thật.
- Xuất báo cáo Markdown, CSV, PDF vào `reports/`.
- Build được file `.exe` bằng PyInstaller.

## Cấu trúc project

```text
.
|-- app.py
|-- requirements.txt
|-- build_exe.bat
|-- README.md
|-- .gitignore
|-- assets/
|   |-- app_icon.ico
|   `-- app_icon.png
|-- core/
|   |-- analyzer.py
|   `-- ai_summary.py
|-- services/
|   `-- github_client.py
|-- ui/
|   |-- main_window.py
|   |-- main_window.ui
|   `-- chart_widget.py
|-- exporters/
|   `-- report_generator.py
|-- storage/
|   `-- db_manager.py
`-- utils/
    |-- path_utils.py
    `-- constants.py
```

Vai trò chính:

- `app.py`: entry point, chạy GUI hoặc CLI.
- `core/`: phân tích commit, tính điểm và tạo nhận xét AI rule-based.
- `services/`: gọi GitHub API và chuẩn hóa dữ liệu thô.
- `ui/`: giao diện PyQt6, file `.ui` và biểu đồ Matplotlib.
- `exporters/`: xuất Markdown, CSV, PDF.
- `storage/`: module lưu lịch sử dự phòng.
- `utils/`: helper đường dẫn và hằng số dùng chung.

## Cài đặt

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Tạo `.env` từ `.env.example` nếu muốn cấu hình sẵn:

```env
GITHUB_TOKEN=
GITHUB_REPO_URL=
REPO_OWNER=
REPO_NAME=
SO_LUONG_COMMIT=30
AI_API_KEY=
```

`GITHUB_TOKEN` không bắt buộc với repository public, nhưng nên dùng để tăng giới hạn gọi API. Không hardcode token hoặc API key trong source code.

## Chạy ứng dụng

Chạy GUI:

```bash
python app.py
```

Chạy CLI để tạo `report.md`:

```bash
python app.py --cli
```

Khi xuất báo cáo từ GUI, thư mục `reports/` sẽ được tự tạo nếu chưa tồn tại.

## Build exe

```bat
build_exe.bat
```

File exe sau khi build:

```text
dist/GitHub Contribution AI/GitHub Contribution AI.exe
```

`build_exe.bat` đóng gói `ui/main_window.ui` và `assets/`, không đóng gói `.env`. Đường dẫn tài nguyên dùng `utils.path_utils.resource_path()` nên chạy được cả khi chạy source và khi chạy exe.

## Công thức điểm

Điểm nội bộ dùng thang 0-100, điểm hiển thị dùng thang `/10`.

```text
raw_score =
    0.10 * commit_score
  + 0.15 * code_volume_score
  + 0.15 * file_impact_score
  + 0.25 * quality_score
  + 0.15 * consistency_score
  + 0.10 * estimated_time_score
  + 0.10 * integration_score

final_score_100 = clamp(raw_score - penalty_score, 0, 100)
display_score_10 = round(final_score_100 / 10, 1)
```

`penalty_score` trừ điểm cho commit quá nhỏ, message chung chung, file local/generated hoặc tỷ lệ commit cần xem lại cao.

## Báo cáo và bảo mật

- Báo cáo xuất ra `reports/` hoặc `report.md` khi chạy CLI.
- `.env`, `.venv/`, `build/`, `dist/`, `reports/`, database local và report tự sinh không đưa vào Git.
- `.env.example` chỉ là file mẫu, không chứa secret.
