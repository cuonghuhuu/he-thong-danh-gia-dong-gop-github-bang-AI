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
