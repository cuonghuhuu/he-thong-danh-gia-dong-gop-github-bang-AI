# Hệ thống đánh giá đóng góp GitHub bằng AI

## 1. Giới thiệu

Đây là ứng dụng Python dùng để phân tích commit trong một GitHub repository và đánh giá mức độ đóng góp của từng thành viên trong nhóm.

Hệ thống không chỉ dựa vào số commit hoặc số dòng code, mà còn đánh giá theo nhiều tiêu chí như chất lượng commit, mức độ ảnh hưởng của file, độ đều đóng góp, thời gian code ước tính và commit cần xem lại.

Ứng dụng có giao diện PyQt6, biểu đồ trực quan, nhận xét AI rule-based và hỗ trợ xuất báo cáo Markdown, CSV, PDF.

## 2. Đề tài

**Xây dựng hệ thống phân tích và đánh giá mức độ đóng góp của thành viên trong dự án GitHub sử dụng Python và AI**

## 3. Thành viên nhóm

| Thành viên | Vai trò |
|---|---|
| Cường | Trưởng nhóm, thuật toán, tích hợp hệ thống |
| Bình | GitHub API, chuẩn hóa contributor, lọc bot |
| Ngọc Linh | Giao diện, dashboard, biểu đồ |
| Ngọc Anh | Nhận xét AI, báo cáo, tài liệu |

## 4. Chức năng chính

- Nhập GitHub URL hoặc owner/repository.
- Lấy dữ liệu commit từ GitHub API.
- Chuẩn hóa contributor, tránh tách sai cùng một người.
- Lọc bot và commit tự động.
- Chấm điểm đóng góp theo thang 1-10.
- Đánh giá chất lượng commit và chất lượng thay đổi code.
- Ước tính thời gian code từ lịch sử commit.
- Phát hiện commit cần xem lại.
- Hiển thị dashboard, bảng thành viên và biểu đồ.
- Tạo nhận xét AI rule-based bằng tiếng Việt.
- Xuất báo cáo Markdown, CSV, PDF.
- Build thành file `.exe` chạy trên Windows.

## 5. Công nghệ sử dụng

- Python
- PyQt6
- GitHub REST API
- Matplotlib
- ReportLab
- python-dotenv
- PyInstaller

## 6. Cấu trúc project

```text
project/
├── app.py                  # File chạy chính
├── requirements.txt        # Danh sách thư viện
├── build_exe.bat           # Script build file exe
├── README.md               # Tài liệu project
│
├── core/                   # Logic phân tích và AI rule-based
│   ├── analyzer.py
│   └── ai_summary.py
│
├── services/               # Kết nối GitHub API
│   └── github_client.py
│
├── ui/                     # Giao diện và biểu đồ
│   ├── main_window.py
│   ├── main_window.ui
│   └── chart_widget.py
│
├── exporters/              # Xuất báo cáo
│   └── report_generator.py
│
├── utils/                  # Hàm tiện ích
│   └── path_utils.py
│
├── assets/                 # Icon ứng dụng
│   └── app_icon.ico
│
└── reports/                # Báo cáo xuất ra
## 7. Luồng xử lý

Luồng hoạt động chính của hệ thống:

1. Người dùng nhập GitHub URL hoặc `owner/repository`.
2. Ứng dụng gọi GitHub API để lấy dữ liệu commit.
3. Hệ thống chuẩn hóa contributor để tránh tách sai cùng một người.
4. Bot và commit tự động được lọc khỏi kết quả đánh giá chính.
5. Các commit được phân tích theo nhiều tiêu chí.
6. Hệ thống tính điểm đóng góp theo thang **1-10**.
7. AI rule-based tạo nhận xét tự động bằng tiếng Việt.
8. Kết quả được hiển thị qua dashboard, bảng thành viên, biểu đồ và báo cáo.

---

## 8. Thuật toán đánh giá

Hệ thống đánh giá contributor theo nhiều tiêu chí khác nhau, không chỉ dựa vào số commit hoặc số dòng code.

| Tiêu chí | Ý nghĩa |
|---|---|
| `commit_score` | Điểm dựa trên số commit |
| `code_volume_score` | Điểm dựa trên số dòng thêm/xóa |
| `file_impact_score` | Điểm theo mức độ quan trọng của file được sửa |
| `quality_score` | Điểm chất lượng commit và thay đổi code |
| `consistency_score` | Điểm độ đều đóng góp theo thời gian |
| `estimated_time_score` | Điểm thời gian code ước tính |
| `integration_score` | Điểm vai trò tích hợp hệ thống |
| `penalty_score` | Điểm trừ cho commit kém chất lượng |

Công thức tổng quát:

```text
final_score =
  commit_score
+ code_volume_score
+ file_impact_score
+ quality_score
+ consistency_score
+ estimated_time_score
+ integration_score
- penalty_score
## 9. Commit cần xem lại

Một commit có thể bị đánh dấu là **cần xem lại** nếu có dấu hiệu chưa rõ ràng hoặc chưa phản ánh đúng đóng góp kỹ thuật.

Các trường hợp thường bị đánh dấu:

- Commit message quá ngắn hoặc quá chung chung.
- Commit chỉ ghi các từ như `test`, `update`, `fix`, `demo`, `final`, `tmp`.
- Commit chỉ sửa file tự động sinh, file local hoặc file môi trường.
- Commit chỉ sửa báo cáo/tài liệu với thay đổi quá nhỏ.
- Commit có số dòng thay đổi rất ít và không thể hiện rõ ý nghĩa.
- Commit do bot hoặc công cụ tự động tạo ra.

Ví dụ commit cần xem lại:

```text
update
test
final
auto update report
fix
