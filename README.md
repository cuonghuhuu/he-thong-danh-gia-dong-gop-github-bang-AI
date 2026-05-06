# 🚀 GitHub Contributor Analyzer


## 📌 Giới thiệu
Công cụ Python dùng để phân tích mức độ đóng góp của các contributor trong GitHub repository.

Hệ thống:
- 📊 Tính toán chỉ số đóng góp  
- 🧠 Đánh giá mức độ ảnh hưởng  
- 🤖 Sinh nhận xét tự động (rule-based)  
- 📄 Xuất báo cáo Markdown  

---

## ⚙️ Chức năng chính

- Lấy dữ liệu commit từ GitHub API  
- Tính các metrics:
  - commit_count  
  - total_additions  
  - total_deletions  
  - changed_files_count  
  - total_changes  
- Tính điểm đóng góp (score)  
- Phân loại contributor:
  - feature-focused  
  - refactor-focused  
  - balanced  
- Sinh AI summary  
- Tạo file `report.md`  

---

## 📊 Công thức tính điểm

```python
score = log(commit_count) * 0.4 
      + log(total_changes) * 0.4 
      + log(changed_files_count) * 0.2

Ứng dụng desktop PyQt6 phân tích mức độ đóng góp của contributor trên GitHub repository bằng metrics và nhận xét AI rule-based.

## Chạy chương trình

```bash
pip install -r requirements.txt
python app.py
```

Trong PyCharm, mở file `app.py` ở thư mục gốc rồi bấm Run.

## Test nhanh

- Owner: `octocat`
- Repository: `Hello-World`
- Số commit: `5`

Sau khi bấm `Phân tích`, kiểm tra các tab Dashboard, Bảng contributor, Biểu đồ, Nhận xét AI và Lịch sử.

## Công thức điểm

```text
final_score = 0.35 * commit_score
            + 0.35 * code_score
            + 0.20 * file_score
            + 0.10 * balance_score
```

Các điểm thành phần dùng log + Min-Max để tránh contributor có quá nhiều dòng code làm lệch kết quả.

## Xuất báo cáo

Báo cáo Markdown, CSV và PDF được tạo trong thư mục `reports/`, tên file có timestamp để không bị ghi đè.

