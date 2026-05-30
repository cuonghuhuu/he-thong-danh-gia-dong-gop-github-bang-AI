# Báo cáo đánh giá đóng góp contributor trên GitHub

## Tổng quan

- Repository: cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI
- Thời gian phân tích: 2026-05-30 09:50:36
- Số commit đã phân tích: 23
- Tổng contributor: 3
- Tổng additions: 7674
- Tổng deletions: 2257
- Điểm chất lượng trung bình: 79.12
- Số commit cần xem lại: 10
- Số commit bot đã loại: 6
- Số commit tự động đã loại: 6
- Contributor điểm cao nhất: cuonghuhuu

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
| 1 | cuonghuhuu | 19 | 7423 | 2148 | 22 | 71.85 | 10.11 | 9 | 47.4% | 82.86 | Đóng góp tốt | Quality 71.9, có 9 commit cần xem lại. |
| 2 | dinhphuongbinh | 3 | 160 | 74 | 4 | 76.60 | 6.00 | 1 | 33.3% | 58.16 | Đóng góp trung bình | Quality 76.6, có 1 commit cần xem lại. |
| 3 | ngoclinh205 | 1 | 91 | 35 | 3 | 88.90 | 0.00 | 0 | 0.0% | 57.92 | Đóng góp trung bình | Quality 88.9, đóng góp tốt vào code chính. |

## Commit cần xem lại

### cuonghuhuu

- `f048e2c` - Merge branch 'main' into feature/update-project: commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo
- `8ce2d92` - Update project features and report: commit có sửa file môi trường hoặc file tự động sinh; commit có sửa file rác/môi trường local
- `db7bcbc` - HoanThanh: commit message quá ngắn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo
- `b647486` - fix missing requests dependency: thay đổi quá nhỏ
- `d2ec877` - them Ai summary vao report: commit có sửa file môi trường hoặc file tự động sinh; commit có sửa file rác/môi trường local
- `c31183c` - update report: commit message quá ngắn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo
- `16c6a4b` - Merge branch 'main' of https://github.com/cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI: commit message hơi dài, nên viết gọn hơn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo
- `d7b445d` - Update README.md: commit message quá ngắn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo
- `7252f66` - Initial commit: commit message quá ngắn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo

### dinhphuongbinh

- `ef5f5ab` - Normalize contributors and ignore bot commits: thay đổi quá nhỏ

## Commit bot/tự động đã loại

- `41a6ed6` - actions-user: Auto update report (bot, auto_commit)
- `807c38b` - actions-user: Auto update report (bot, auto_commit)
- `57ed69c` - actions-user: Auto update report (bot, auto_commit)
- `cc12cf6` - actions-user: Auto update report (bot, auto_commit)
- `f7c6f2c` - actions-user: Auto update report (bot, auto_commit)
- `80c9e8e` - actions-user: Auto update report (bot, auto_commit)

## Nhận xét AI rule-based

Nhận xét tổng quan:
Repository cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI có 3 contributor trong 23 commit đã phân tích. Điểm chất lượng trung bình là 79.12, số commit cần xem lại là 10. Hệ thống đã chuẩn hóa contributor theo GitHub login, alias, author name/email để tránh tách sai cùng một người. Hệ thống đã loại bỏ commit bot/tự động để kết quả đánh giá công bằng hơn.

Contributor nổi bật:
Contributor có điểm cao nhất là cuonghuhuu với final score 82.86, quality score 71.85, penalty 10.11.

Gợi ý cải thiện:
Nên rà soát các commit bị đánh dấu, đặc biệt commit message quá ngắn, commit chỉ sửa báo cáo hoặc commit có file môi trường/local.
