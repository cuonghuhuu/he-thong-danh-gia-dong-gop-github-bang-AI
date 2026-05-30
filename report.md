# Báo cáo đánh giá đóng góp contributor trên GitHub

## Tổng quan

- Repository: cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI
- Thời gian phân tích: 2026-05-30 02:24:24
- Số commit đã phân tích: 19
- Tổng contributor: 2
- Tổng additions: 7354
- Tổng deletions: 2109
- Điểm chất lượng trung bình: 80.03
- Số commit cần xem lại: 9
- Số commit bot đã loại: 5
- Số commit tự động đã loại: 5
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
| 1 | cuonghuhuu | 18 | 7263 | 2074 | 22 | 71.16 | 10.67 | 9 | 50.0% | 82.12 | Đóng góp tốt | Quality 71.2, có 9 commit cần xem lại. |
| 2 | ngoclinh205 | 1 | 91 | 35 | 3 | 88.90 | 0.00 | 0 | 0.0% | 58.00 | Đóng góp trung bình | Quality 88.9, đóng góp tốt vào code chính. |

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

## Commit bot/tự động đã loại

- `807c38b` - actions-user: Auto update report (bot, auto_commit)
- `57ed69c` - actions-user: Auto update report (bot, auto_commit)
- `cc12cf6` - actions-user: Auto update report (bot, auto_commit)
- `f7c6f2c` - actions-user: Auto update report (bot, auto_commit)
- `80c9e8e` - actions-user: Auto update report (bot, auto_commit)

## Nhận xét AI rule-based

Nhận xét tổng quan:
Repository cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI có 2 contributor trong 19 commit đã phân tích. Điểm chất lượng trung bình là 80.03, số commit cần xem lại là 9. Hệ thống đã loại bỏ commit tự động/bot để kết quả đánh giá công bằng hơn.

Contributor nổi bật:
Contributor có điểm cao nhất là cuonghuhuu với final score 82.12, quality score 71.16, penalty 10.67.

Gợi ý cải thiện:
Nên rà soát các commit bị đánh dấu, đặc biệt commit message quá ngắn, commit chỉ sửa báo cáo hoặc commit có file môi trường/local.
