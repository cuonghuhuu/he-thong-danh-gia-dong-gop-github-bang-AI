def xac_dinh_muc_dong_gop(score):
    """Phan loai muc dong gop theo thang diem 0-100."""
    if score >= 80:
        return "Đóng góp rất tích cực"
    if score >= 60:
        return "Đóng góp tốt"
    if score >= 40:
        return "Đóng góp trung bình"
    return "Đóng góp thấp"


def xac_dinh_loai_dong_gop(item):
    """
    Phan loai contributor theo kieu dong gop.
    Cac nguong duoc giu don gian de phu hop bai thuc hanh sinh vien.
    """
    commit_count = item.get("commit_count", 0)
    total_additions = item.get("total_additions", item.get("additions", 0))
    total_deletions = item.get("total_deletions", item.get("deletions", 0))
    total_changes = item.get("total_changes", 0)
    files_changed = item.get("changed_files_count", item.get("files_changed", 0))

    if commit_count <= 1 and total_changes < 50:
        return "Hoạt động thấp"

    if total_additions >= max(50, total_deletions * 1.6):
        return "Thiên về phát triển tính năng"

    if total_deletions >= max(30, total_additions * 1.2) or files_changed >= 10:
        return "Thiên về refactor/sửa lỗi"

    if total_changes > 0:
        chenhlech = abs(total_additions - total_deletions) / total_changes
        if chenhlech <= 0.35:
            return "Đóng góp cân bằng"

    return "Đóng góp cân bằng"


def _tao_diem_manh(item):
    commit_count = item.get("commit_count", 0)
    total_changes = item.get("total_changes", 0)
    files_changed = item.get("changed_files_count", item.get("files_changed", 0))
    balance_score = item.get("balance_score", 0)

    if commit_count >= 5 and total_changes >= 300:
        return "có tần suất commit tốt và khối lượng thay đổi lớn"
    if files_changed >= 8:
        return "tham gia trên nhiều file, phạm vi ảnh hưởng khá rộng"
    if balance_score >= 70:
        return "giữ được sự cân bằng giữa thêm mới và chỉnh sửa/xóa code"
    if total_changes > 0:
        return "có đóng góp cụ thể trong tập commit đã phân tích"
    return "chưa có điểm mạnh rõ ràng trong dữ liệu hiện tại"


def _tao_han_che(item):
    commit_count = item.get("commit_count", 0)
    total_changes = item.get("total_changes", 0)
    files_changed = item.get("changed_files_count", item.get("files_changed", 0))
    balance_score = item.get("balance_score", 0)

    if total_changes <= 0:
        return "chưa có thay đổi code đáng kể"
    if commit_count <= 1:
        return "số commit còn ít nên chưa phản ánh đầy đủ mức độ tham gia"
    if files_changed <= 1:
        return "phạm vi thay đổi còn hẹp, chủ yếu tập trung ở ít file"
    if balance_score < 30:
        return "tỷ lệ additions/deletions còn lệch, cần xem thêm chất lượng thay đổi"
    return "chưa thấy hạn chế lớn từ các chỉ số định lượng"


def _tao_goi_y(item):
    contribution_level = item.get("contribution_level", "")
    contribution_type = item.get("contribution_type", "")

    if contribution_level == "Đóng góp thấp":
        return "nên nhận thêm task nhỏ, sửa lỗi đơn giản hoặc bổ sung tài liệu để tăng tần suất đóng góp"
    if contribution_type == "Thiên về phát triển tính năng":
        return "nên bổ sung test, review và refactor nhẹ để cân bằng giữa thêm mới và ổn định code"
    if contribution_type == "Thiên về refactor/sửa lỗi":
        return "nên ghi rõ mục tiêu refactor/sửa lỗi trong commit message để nhóm dễ theo dõi"
    return "nên duy trì nhịp đóng góp hiện tại và chú ý chất lượng commit message, test, review"


def tao_noi_dung_nhan_xet(item):
    """Tao nhan xet rule-based ngan gon cho tung contributor."""
    final_score = item.get("final_score", item.get("score", 0))
    contribution_level = item.get("contribution_level") or xac_dinh_muc_dong_gop(final_score)
    contribution_type = item.get("contribution_type") or xac_dinh_loai_dong_gop(item)

    return (
        f"Mức độ tham gia: {contribution_level}. "
        f"Điểm mạnh: {_tao_diem_manh(item)}. "
        f"Hạn chế: {_tao_han_che(item)}. "
        f"Gợi ý cải thiện: {_tao_goi_y({**item, 'contribution_level': contribution_level, 'contribution_type': contribution_type})}."
    )


def tao_nhan_xet_don_gian(danh_sach_xep_hang):
    """
    Tao muc dong gop, loai dong gop va nhan xet cho tung contributor.
    Ham tra ve danh sach moi de tranh sua truc tiep dau vao.
    """
    ket_qua = []

    for item in danh_sach_xep_hang:
        thong_tin_moi = item.copy()
        final_score = thong_tin_moi.get("final_score", thong_tin_moi.get("score", 0))
        contribution_level = xac_dinh_muc_dong_gop(final_score)
        contribution_type = xac_dinh_loai_dong_gop(thong_tin_moi)

        thong_tin_moi["contribution_level"] = contribution_level
        thong_tin_moi["contribution_type"] = contribution_type
        thong_tin_moi["ai_summary"] = tao_noi_dung_nhan_xet(thong_tin_moi)
        ket_qua.append(thong_tin_moi)

    return ket_qua


def tao_tong_ket_repo(danh_sach_xep_hang):
    """Tao nhan xet tong quan toan repository."""
    if not danh_sach_xep_hang:
        return "Không có dữ liệu để đánh giá."

    top = danh_sach_xep_hang[0]
    tong_contributor = len(danh_sach_xep_hang)

    if tong_contributor == 1:
        return "Repository hiện tại chủ yếu do một contributor phụ trách."

    tong_diem = sum(item.get("final_score", item.get("score", 0)) for item in danh_sach_xep_hang)
    diem_top = top.get("final_score", top.get("score", 0))
    ti_le_top = diem_top / tong_diem if tong_diem > 0 else 0

    if ti_le_top >= 0.5:
        return "Đóng góp đang tập trung mạnh vào contributor có điểm cao nhất."

    if ti_le_top >= 0.35:
        return "Đóng góp có chênh lệch nhất định nhưng vẫn có nhiều contributor tham gia."

    return "Đóng góp trong repository được phân bổ tương đối cân bằng."


def tao_nhan_xet_ai_rule_based(ket_qua_phan_tich):
    """Nhan xet AI gia lap bang rule-based, chua can API AI that."""
    contributors = ket_qua_phan_tich.get("contributors", [])
    overview = ket_qua_phan_tich.get("overview", {})

    if not contributors:
        return "Chưa có dữ liệu contributor để tạo nhận xét."

    top = contributors[0]
    tong_diem = overview.get("total_score", 0)
    diem_top = top.get("final_score", top.get("score", 0))
    ti_le_top = diem_top / tong_diem if tong_diem > 0 else 0

    tong_quan = (
        f"Repository {overview.get('repo_full_name', '')} có "
        f"{overview.get('contributor_count', 0)} contributor trong "
        f"{overview.get('analyzed_commit_count', 0)} commit đã phân tích. "
        f"Tổng additions là {overview.get('total_additions', 0)}, "
        f"tổng deletions là {overview.get('total_deletions', 0)}."
    )

    noi_bat = (
        f"Contributor nổi bật nhất là {top.get('contributor', 'Không xác định')} "
        f"với {top.get('commit_count', 0)} commit, "
        f"{top.get('total_changes', 0)} total changes, "
        f"{top.get('files_changed', 0)} files changed và điểm {diem_top:.2f}. "
        f"Mức đánh giá: {top.get('contribution_level', xac_dinh_muc_dong_gop(diem_top))}."
    )

    if ti_le_top >= 0.5:
        muc_chenh_lech = "Mức chênh lệch cao: một contributor đang chiếm tỷ trọng điểm lớn."
        goi_y = (
            "Nên chia task theo module nhỏ hơn, tăng review chéo và giao thêm issue vừa sức "
            "cho các contributor còn lại để giảm phụ thuộc."
        )
    elif ti_le_top >= 0.35:
        muc_chenh_lech = (
            "Mức chênh lệch trung bình: nhóm có contributor nổi bật "
            "nhưng vẫn có sự tham gia từ các thành viên khác."
        )
        goi_y = (
            "Nên duy trì contributor chính ở vai trò review/hướng dẫn, đồng thời phân công thêm "
            "task sửa lỗi, test và tài liệu cho các thành viên còn lại."
        )
    else:
        muc_chenh_lech = "Mức chênh lệch thấp: đóng góp của nhóm khá cân bằng."
        goi_y = (
            "Có thể tiếp tục cách phân công hiện tại, nhưng nên theo dõi thêm chất lượng commit "
            "và mức độ review để đánh giá đầy đủ hơn."
        )

    return "\n\n".join(
        [
            "Nhận xét tổng quan về nhóm:\n" + tong_quan,
            "Contributor nổi bật:\n" + noi_bat,
            "Mức độ chênh lệch đóng góp:\n" + muc_chenh_lech,
            "Gợi ý cải thiện phân chia công việc:\n" + goi_y,
        ]
    )
