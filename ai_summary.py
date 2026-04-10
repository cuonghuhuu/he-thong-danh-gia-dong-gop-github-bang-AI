def tao_nhan_xet_don_gian(danh_sach_xep_hang):
    """
    Tạo nhận xét đơn giản cho từng contributor dựa trên metrics đã tính
    """
    for item in danh_sach_xep_hang:
        commit_count = item.get("commit_count", 0)
        total_changes = item.get("total_changes", 0)
        changed_files_count = item.get("changed_files_count", 0)

        if commit_count >= 5 and total_changes >= 100:
            nhan_xet = "Dong gop rat tich cuc, khoi luong thay doi cao."
        elif changed_files_count >= 5:
            nhan_xet = "Pham vi anh huong rong, tham gia tren nhieu file."
        elif total_changes > 0:
            nhan_xet = "Co dong gop on dinh trong repository."
        else:
            nhan_xet = "Muc dong gop hien tai con han che."

        item["ai_summary"] = nhan_xet

    return danh_sach_xep_hang