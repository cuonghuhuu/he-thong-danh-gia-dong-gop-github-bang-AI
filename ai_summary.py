def tao_nhan_xet_don_gian(danh_sach_xep_hang):
    """
    Tạo nhận xét đơn giản cho từng contributor dựa trên metrics đã tính
    """
    for item in danh_sach_xep_hang:
        commit_count = item.get("commit_count", 0)
        total_additions = item.get("total_additions", 0)
        total_deletions = item.get("total_deletions", 0)
        total_changes = item.get("total_changes", 0)
        changed_files_count = item.get("changed_files_count", 0)

        # Phân loại kiểu đóng góp
        if total_additions > total_deletions * 2:
            loai_dong_gop = "feature-focused"
        elif total_deletions > total_additions:
            loai_dong_gop = "refactor-focused"
        else:
            loai_dong_gop = "balanced"

        # Nhận xét tổng quát
        if commit_count >= 5 and total_changes >= 100:
            nhan_xet = "Dong gop rat tich cuc, khoi luong thay doi cao."
        elif changed_files_count >= 5:
            nhan_xet = "Pham vi anh huong rong, tham gia tren nhieu file."
        elif total_changes > 0:
            nhan_xet = "Co dong gop on dinh trong repository."
        else:
            nhan_xet = "Muc dong gop hien tai con han che."

        item["contribution_type"] = loai_dong_gop
        item["ai_summary"] = nhan_xet

    return danh_sach_xep_hang


def tao_tong_ket_repo(danh_sach_xep_hang):
    """
    Tạo nhận xét tổng quan toàn repo
    """
    if not danh_sach_xep_hang:
        return "Khong co du lieu."

    top = danh_sach_xep_hang[0]
    tong_contributor = len(danh_sach_xep_hang)

    if tong_contributor == 1:
        return "Repository hien tai chu yeu do mot contributor phu trach."

    if top["baseline_score"] > danh_sach_xep_hang[-1]["baseline_score"] * 2:
        return "Dong gop trong repo bi tap trung vao mot so contributor chinh."

    return "Dong gop trong repo duoc phan bo tuong doi dong deu giua cac contributor."