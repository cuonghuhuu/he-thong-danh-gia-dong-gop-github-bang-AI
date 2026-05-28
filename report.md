# Báo cáo đánh giá đóng góp contributor trên GitHub

## Tổng quan

- Repository: cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI
- Thời gian phân tích: 2026-05-28 23:26:46
- Số commit đã phân tích: 16
- Tổng contributor: 3
- Tổng additions: 2858
- Tổng deletions: 463
- Điểm chất lượng trung bình: 50.99
- Số commit cần xem lại: 12
- Contributor điểm cao nhất: Le Van Cuong

## Công thức điểm

```text
final_score = 0.20 * commit_score
            + 0.20 * code_volume_score
            + 0.20 * file_impact_score
            + 0.25 * quality_score
            + 0.15 * consistency_score
            - penalty_score
```

## Bảng contributor

| STT | Contributor | Commit | Additions | Deletions | Files | Quality score | Penalty | Suspicious commits | Suspicious ratio | Final score | Mức đánh giá | Nhận xét |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Le Van Cuong | 9 | 2559 | 433 | 22 | 69.28 | 12.00 | 5 | 55.6% | 75.49 | Đóng góp tốt | Quality 69.3, có 5 commit cần xem lại. |
| 2 | cuonghuhuu | 3 | 255 | 10 | 2 | 46.60 | 24.00 | 3 | 100.0% | 36.78 | Đóng góp thấp | Quality 46.6, có 3 commit cần xem lại. |
| 3 | actions-user | 4 | 44 | 20 | 1 | 37.10 | 28.50 | 4 | 100.0% | 22.01 | Cần cải thiện | Quality 37.1, có 4 commit cần xem lại. |

## Commit cần xem lại

### Le Van Cuong

- `8ce2d92` - Update project features and report: commit có sửa file môi trường hoặc file tự động sinh; commit có sửa file rác/môi trường local
- `b647486` - fix missing requests dependency: thay đổi quá nhỏ; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo
- `d2ec877` - them Ai summary vao report: commit có sửa file môi trường hoặc file tự động sinh; commit có sửa file rác/môi trường local
- `c31183c` - update report: commit message quá ngắn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo
- `16c6a4b` - Merge branch 'main' of https://github.com/cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI: commit message hơi dài, nên viết gọn hơn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo

### cuonghuhuu

- `db7bcbc` - HoanThanh: commit message quá ngắn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo
- `d7b445d` - Update README.md: commit message quá ngắn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo
- `7252f66` - Initial commit: commit message quá ngắn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo

### actions-user

- `57ed69c` - Auto update report: commit tự động cập nhật báo cáo; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo
- `cc12cf6` - Auto update report: commit tự động cập nhật báo cáo; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo
- `f7c6f2c` - Auto update report: commit tự động cập nhật báo cáo; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo
- `80c9e8e` - Auto update report: commit tự động cập nhật báo cáo; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo

## Nhận xét AI rule-based

Nhận xét tổng quan:
Repository cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI có 3 contributor trong 16 commit đã phân tích. Điểm chất lượng trung bình là 50.99, số commit cần xem lại là 12.

Contributor nổi bật:
Contributor có điểm cao nhất là Le Van Cuong với final score 75.49, quality score 69.28, penalty 12.00.

Gợi ý cải thiện:
Nên rà soát các commit bị đánh dấu, đặc biệt commit message quá ngắn, commit chỉ sửa báo cáo hoặc commit có file môi trường/local.
