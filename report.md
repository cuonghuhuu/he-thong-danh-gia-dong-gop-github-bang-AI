# Báo cáo đánh giá đóng góp GitHub bằng AI

## Tổng quan

- Repository: cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI
- Thời gian phân tích: 2026-05-30 14:31:10
- Số commit đã phân tích: 23
- Tổng contributor: 4
- Tổng additions: 8771
- Tổng deletions: 2777
- Điểm chất lượng trung bình: 81.75
- Số commit cần xem lại: 8
- Số commit bot đã loại: 7
- Số commit tự động đã loại: 7
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

## Bảng tổng hợp contributor

| STT | Contributor | Commit | Additions | Deletions | Files | Quality score | Penalty | Suspicious commits | Final score | Mức đánh giá | Nhận xét AI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | cuonghuhuu | 17 | 7857 | 2407 | 22 | 75.10 | 8.47 | 7 | 85.30 | Đóng góp chất lượng cao | Mức độ tham gia: tham gia tích cực với 17 commit, điểm tổng hợp 85.3/100 và khối lượng thay đổi 10264 dòng.<br>Chất lượng đóng góp: quality_score 75.1/100 ở mức khá; đóng góp có giá trị nhưng vẫn còn điểm có thể cải thiện; có 7 commit cần xem lại nên cần viết commit message rõ hơn và tránh các message quá chung chung.<br>Điểm mạnh: đóng góp có chất lượng tốt, quality_score cao; thiên về code chính, có tác động trực tiếp đến logic/source code; đóng góp nhiều cho tài liệu/báo cáo, giúp dự án dễ theo dõi hơn; thay đổi có ý nghĩa, không chỉ là chỉnh sửa nhỏ.<br>Điểm hạn chế: có nhiều commit cần xem lại, đặc biệt về độ rõ của commit message; có thay đổi file môi trường hoặc file tự động sinh.<br>Commit cần xem lại: f048e2c - "Merge branch 'main' into feature/update-project" (commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo); 8ce2d92 - "Update project features and report" (commit có sửa file môi trường hoặc file tự động sinh; commit có sửa file rác/môi trường local); db7bcbc - "HoanThanh" (commit message quá ngắn; commit chủ yếu sửa tài liệu/báo cáo); còn 4 commit khác.<br>Gợi ý cải thiện: viết commit message cụ thể hơn, nêu rõ phần đã sửa và lý do sửa; hạn chế các message kiểu test/update/nộp/final nếu không mô tả rõ thay đổi. |
| 2 | ngocanh1798 | 2 | 663 | 261 | 2 | 86.40 | 0.00 | 0 | 72.80 | Đóng góp tốt | Mức độ tham gia: mức độ tham gia còn thấp hoặc chưa có commit được tính điểm.<br>Chất lượng đóng góp: quality_score 86.4/100 cho thấy đóng góp có chất lượng cao, message và nội dung thay đổi nhìn chung rõ ràng.<br>Điểm mạnh: đóng góp có chất lượng tốt, quality_score cao; thiên về code chính, có tác động trực tiếp đến logic/source code; commit message tương đối rõ ràng; thay đổi có ý nghĩa, không chỉ là chỉnh sửa nhỏ.<br>Điểm hạn chế: chưa thấy hạn chế lớn từ các rule hiện tại.<br>Commit cần xem lại: không có commit đáng nghi nổi bật.<br>Gợi ý cải thiện: duy trì đóng góp vào code chính và bổ sung test/comment vừa đủ khi thay đổi logic quan trọng. |
| 3 | dinhphuongbinh | 3 | 160 | 74 | 4 | 76.60 | 6.00 | 1 | 58.50 | Đóng góp trung bình | Mức độ tham gia: tham gia ở mức khá với 3 commit; cần xem thêm chất lượng và mức tác động của từng commit.<br>Chất lượng đóng góp: quality_score 76.6/100 ở mức khá; đóng góp có giá trị nhưng vẫn còn điểm có thể cải thiện; có 1 commit cần xem lại.<br>Điểm mạnh: đóng góp có chất lượng tốt, quality_score cao; thiên về code chính, có tác động trực tiếp đến logic/source code; commit message tương đối rõ ràng; thay đổi có ý nghĩa, không chỉ là chỉnh sửa nhỏ.<br>Điểm hạn chế: có commit cần xem lại.<br>Commit cần xem lại: ef5f5ab - "Normalize contributors and ignore bot commits" (thay đổi quá nhỏ).<br>Gợi ý cải thiện: xem lại các commit bị đánh dấu và bổ sung commit message rõ mục đích hơn. |
| 4 | ngoclinh205 | 1 | 91 | 35 | 3 | 88.90 | 0.00 | 0 | 58.09 | Đóng góp trung bình | Mức độ tham gia: tham gia còn ít vì mới có 1 commit trong phạm vi phân tích; kết luận nên được xem cùng nội dung commit.<br>Chất lượng đóng góp: quality_score 88.9/100 cho thấy đóng góp có chất lượng cao, message và nội dung thay đổi nhìn chung rõ ràng.<br>Điểm mạnh: đóng góp có chất lượng tốt, quality_score cao; commit message tương đối rõ ràng; thay đổi có ý nghĩa, không chỉ là chỉnh sửa nhỏ.<br>Điểm hạn chế: chưa thấy hạn chế lớn từ các rule hiện tại.<br>Commit cần xem lại: không có commit đáng nghi nổi bật.<br>Gợi ý cải thiện: duy trì chất lượng hiện tại, tiếp tục viết commit message rõ và chia commit theo từng mục đích. |

## Commit cần xem lại

### cuonghuhuu

| SHA ngắn | Message | Lý do bị đánh dấu |
| --- | --- | --- |
| `f048e2c` | Merge branch 'main' into feature/update-project | commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo |
| `8ce2d92` | Update project features and report | commit có sửa file môi trường hoặc file tự động sinh; commit có sửa file rác/môi trường local |
| `db7bcbc` | HoanThanh | commit message quá ngắn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo |
| `b647486` | fix missing requests dependency | thay đổi quá nhỏ |
| `d2ec877` | them Ai summary vao report | commit có sửa file môi trường hoặc file tự động sinh; commit có sửa file rác/môi trường local |
| `c31183c` | update report | commit message quá ngắn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo |
| `16c6a4b` | Merge branch 'main' of https://github.com/cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI | commit message hơi dài, nên viết gọn hơn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo |

### dinhphuongbinh

| SHA ngắn | Message | Lý do bị đánh dấu |
| --- | --- | --- |
| `ef5f5ab` | Normalize contributors and ignore bot commits | thay đổi quá nhỏ |

## Commit bot/tự động đã loại

| SHA ngắn | Contributor | Message | Lý do loại |
| --- | --- | --- | --- |
| `9267342` | actions-user | Auto update report | bot; auto_commit |
| `41a6ed6` | actions-user | Auto update report | bot; auto_commit |
| `807c38b` | actions-user | Auto update report | bot; auto_commit |
| `57ed69c` | actions-user | Auto update report | bot; auto_commit |
| `cc12cf6` | actions-user | Auto update report | bot; auto_commit |
| `f7c6f2c` | actions-user | Auto update report | bot; auto_commit |
| `80c9e8e` | actions-user | Auto update report | bot; auto_commit |

## Nhận xét AI tổng quan

Nhận xét tổng quan:
Repository cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI có 4 contributor trong 23 commit đã phân tích. Điểm chất lượng trung bình là 81.75, số commit cần xem lại là 8. Hệ thống đã chuẩn hóa contributor theo GitHub login, alias, author name/email để tránh tách sai cùng một người. Hệ thống đã loại bỏ commit bot/tự động để kết quả đánh giá công bằng hơn.

Contributor nổi bật:
Contributor có điểm cao nhất là cuonghuhuu với final_score 85.30, quality_score 75.10, penalty_score 8.47.

Gợi ý cải thiện:
Nên rà soát các commit bị đánh dấu, đặc biệt là commit message quá ngắn, commit chỉ sửa báo cáo hoặc commit có file môi trường/local. Contributor có nhiều commit cần xem lại nên viết message rõ phần thay đổi và lý do thay đổi.
