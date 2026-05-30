# Báo cáo đánh giá đóng góp GitHub bằng AI

## Tổng quan

- Repository: cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI
- Thời gian phân tích: 2026-05-30 15:13:55
- Số commit đã phân tích: 22
- Tổng contributor: 4
- Tổng additions: 9477
- Tổng deletions: 3260
- Điểm chất lượng trung bình: 8.3/10
- Số commit cần xem lại: 5
- Số commit bot đã loại: 8
- Số commit tự động đã loại: 8
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

Điểm chất lượng và điểm cuối hiển thị theo thang /10. Điểm trừ hiển thị theo thang 0-10, chuẩn hóa từ penalty nội bộ tối đa 30 điểm.

## Bảng tổng hợp contributor

| STT | Thành viên | Số commit | Dòng thêm | Dòng xoá | File đã sửa | Điểm chất lượng /10 | Điểm trừ /10 | Commit cần xem lại | Điểm cuối /10 | Mức đánh giá | Nhận xét AI |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | cuonghuhuu | 16 | 8563 | 2890 | 18 | 8.1 | 1.5 | 4 | 9.1 | Đóng góp chất lượng cao | Mức độ tham gia: tham gia tích cực với 16 commit, điểm tổng hợp 9.1/10 và khối lượng thay đổi 11453 dòng.<br>Chất lượng đóng góp: đạt 8.1/10 về chất lượng, cho thấy đóng góp có chất lượng cao, message và nội dung thay đổi nhìn chung rõ ràng; có 4 commit cần xem lại nên cần viết commit message rõ hơn và tránh các message quá chung chung.<br>Điểm mạnh: đóng góp có chất lượng tốt, đạt 8.1/10; thiên về code chính, có tác động trực tiếp đến logic/source code; đóng góp nhiều cho tài liệu/báo cáo, giúp dự án dễ theo dõi hơn; thay đổi có ý nghĩa, không chỉ là chỉnh sửa nhỏ.<br>Điểm hạn chế: có nhiều commit cần xem lại, đặc biệt về độ rõ của commit message; có thay đổi file môi trường hoặc file tự động sinh.<br>Commit cần xem lại: b9ef5f1 - "Merge pull request #5 from cuonghuhuu/feature/cuong-score-dashboard-upgrade" (commit message hơi dài, nên viết gọn hơn); f048e2c - "Merge branch 'main' into feature/update-project" (commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo); 8ce2d92 - "Update project features and report" (commit có sửa file môi trường hoặc file tự động sinh; commit có sửa file rác/môi trường local); còn 1 commit khác.<br>Gợi ý cải thiện: viết commit message cụ thể hơn, nêu rõ phần đã sửa và lý do sửa; hạn chế các message kiểu test/update/nộp/final nếu không mô tả rõ thay đổi. |
| 2 | ngocanh1798 | 2 | 663 | 261 | 2 | 8.6 | 0.0 | 0 | 7.3 | Đóng góp tốt | Mức độ tham gia: mức độ tham gia còn thấp hoặc chưa có commit được tính điểm.<br>Chất lượng đóng góp: đạt 8.6/10 về chất lượng, cho thấy đóng góp có chất lượng cao, message và nội dung thay đổi nhìn chung rõ ràng.<br>Điểm mạnh: đóng góp có chất lượng tốt, đạt 8.6/10; thiên về code chính, có tác động trực tiếp đến logic/source code; commit message tương đối rõ ràng; thay đổi có ý nghĩa, không chỉ là chỉnh sửa nhỏ.<br>Điểm hạn chế: chưa thấy hạn chế lớn từ các rule hiện tại.<br>Commit cần xem lại: không có commit đáng nghi nổi bật.<br>Gợi ý cải thiện: duy trì đóng góp vào code chính và bổ sung test/comment vừa đủ khi thay đổi logic quan trọng. |
| 3 | dinhphuongbinh | 3 | 160 | 74 | 4 | 7.7 | 2.0 | 1 | 5.9 | Đóng góp trung bình | Mức độ tham gia: tham gia ở mức khá với 3 commit; cần xem thêm chất lượng và mức tác động của từng commit.<br>Chất lượng đóng góp: đạt 7.7/10 về chất lượng, ở mức khá; đóng góp có giá trị nhưng vẫn còn điểm có thể cải thiện; có 1 commit cần xem lại.<br>Điểm mạnh: đóng góp có chất lượng tốt, đạt 7.7/10; thiên về code chính, có tác động trực tiếp đến logic/source code; commit message tương đối rõ ràng; thay đổi có ý nghĩa, không chỉ là chỉnh sửa nhỏ.<br>Điểm hạn chế: có commit cần xem lại.<br>Commit cần xem lại: ef5f5ab - "Normalize contributors and ignore bot commits" (thay đổi quá nhỏ).<br>Gợi ý cải thiện: xem lại các commit bị đánh dấu và bổ sung commit message rõ mục đích hơn. |
| 4 | ngoclinh205 | 1 | 91 | 35 | 3 | 8.9 | 0.0 | 0 | 5.8 | Đóng góp trung bình | Mức độ tham gia: tham gia còn ít vì mới có 1 commit trong phạm vi phân tích; kết luận nên được xem cùng nội dung commit.<br>Chất lượng đóng góp: đạt 8.9/10 về chất lượng, cho thấy đóng góp có chất lượng cao, message và nội dung thay đổi nhìn chung rõ ràng.<br>Điểm mạnh: đóng góp có chất lượng tốt, đạt 8.9/10; commit message tương đối rõ ràng; thay đổi có ý nghĩa, không chỉ là chỉnh sửa nhỏ.<br>Điểm hạn chế: chưa thấy hạn chế lớn từ các rule hiện tại.<br>Commit cần xem lại: không có commit đáng nghi nổi bật.<br>Gợi ý cải thiện: duy trì chất lượng hiện tại, tiếp tục viết commit message rõ và chia commit theo từng mục đích. |

## Thống kê hỗ trợ biểu đồ

- Điểm cuối cao nhất: cuonghuhuu (9.1/10).
- Điểm chất lượng cao nhất: ngoclinh205 (8.9/10).
- Commit cần xem lại nhiều nhất: cuonghuhuu (4 commit).
- Tổng dòng thêm/xoá: +9477 / -3260.
- Điểm trừ trong báo cáo là mức 0-10 chuẩn hóa từ penalty nội bộ tối đa 30 điểm.


## Commit cần xem lại

| Contributor | SHA | Message | Lý do bị đánh dấu | Mức độ nghi ngờ |
| --- | --- | --- | --- | --- |
| cuonghuhuu | `b9ef5f1` | Merge pull request #5 from cuonghuhuu/feature/cuong-score-dashboard-upgrade | commit message hơi dài, nên viết gọn hơn | Thấp (0.0/10) |
| cuonghuhuu | `f048e2c` | Merge branch 'main' into feature/update-project | commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo | Trung bình (1.6/10) |
| cuonghuhuu | `8ce2d92` | Update project features and report | commit có sửa file môi trường hoặc file tự động sinh; commit có sửa file rác/môi trường local | Trung bình (3.2/10) |
| cuonghuhuu | `db7bcbc` | HoanThanh | commit message quá ngắn; commit chủ yếu sửa tài liệu/báo cáo; commit thiên về tài liệu/báo cáo | Cao (4.8/10) |
| dinhphuongbinh | `ef5f5ab` | Normalize contributors and ignore bot commits | thay đổi quá nhỏ | Thấp (2.4/10) |

## Commit bot/tự động đã loại

| SHA ngắn | Contributor | Message | Lý do loại |
| --- | --- | --- | --- |
| `cbddaa1` | actions-user | Auto update report | bot; auto_commit |
| `9267342` | actions-user | Auto update report | bot; auto_commit |
| `41a6ed6` | actions-user | Auto update report | bot; auto_commit |
| `807c38b` | actions-user | Auto update report | bot; auto_commit |
| `57ed69c` | actions-user | Auto update report | bot; auto_commit |
| `cc12cf6` | actions-user | Auto update report | bot; auto_commit |
| `f7c6f2c` | actions-user | Auto update report | bot; auto_commit |
| `80c9e8e` | actions-user | Auto update report | bot; auto_commit |

## Nhận xét AI tổng quan

Nhận xét tổng quan:
Repository cuonghuhuu/he-thong-danh-gia-dong-gop-github-bang-AI có 4 contributor trong 22 commit đã phân tích. Điểm chất lượng trung bình là 8.3/10, số commit cần xem lại là 5. Hệ thống đã chuẩn hóa contributor theo GitHub login và author name/email để tránh tách sai cùng một người. Hệ thống đã loại bỏ commit bot/tự động để kết quả đánh giá công bằng hơn.

Contributor nổi bật:
Contributor có điểm cao nhất là cuonghuhuu với điểm cuối 9.1/10, điểm chất lượng 8.1/10, điểm trừ 1.5/10.

Gợi ý cải thiện:
Nên rà soát các commit bị đánh dấu, đặc biệt là commit message quá ngắn, commit chỉ sửa báo cáo hoặc commit có file môi trường/local. Contributor có nhiều commit cần xem lại nên viết message rõ phần thay đổi và lý do thay đổi.
