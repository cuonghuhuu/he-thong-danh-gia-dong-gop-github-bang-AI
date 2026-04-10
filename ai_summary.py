def xac_dinh_loai_dong_gop(item):
    """
    Phan loai kieu dong gop dua tren additions va deletions.
    """
    total_additions = item.get("total_additions", 0)
    total_deletions = item.get("total_deletions", 0)

    if total_additions > total_deletions * 2:
        return "feature-focused"

    if total_deletions > total_additions:
        return "refactor-focused"

    return "balanced"


def tao_noi_dung_nhan_xet(item):
    """
    Tao nhan xet ngan gon cho tung contributor.
    """
    commit_count = item.get("commit_count", 0)
    total_changes = item.get("total_changes", 0)
    changed_files_count = item.get("changed_files_count", 0)

    if commit_count >= 5 and total_changes >= 100:
        return "Dong gop rat tich cuc, khoi luong thay doi cao."

    if changed_files_count >= 5:
        return "Pham vi anh huong rong, tham gia tren nhieu file."

    if total_changes > 0:
        return "Co dong gop on dinh trong repository."

    return "Muc dong gop hien tai con han che."


def tao_nhan_xet_don_gian(danh_sach_xep_hang):
    """
    Tao nhan xet cho tung contributor.
    Ham tra ve danh sach moi de tranh sua truc tiep dau vao.
    """
    ket_qua = []

    for item in danh_sach_xep_hang:
        thong_tin_moi = item.copy()
        thong_tin_moi["contribution_type"] = xac_dinh_loai_dong_gop(item)
        thong_tin_moi["ai_summary"] = tao_noi_dung_nhan_xet(item)
        ket_qua.append(thong_tin_moi)

    return ket_qua


def tao_tong_ket_repo(danh_sach_xep_hang):
    """
    Tao nhan xet tong quan toan repo.
    """
    if not danh_sach_xep_hang:
        return "Khong co du lieu."

    top = danh_sach_xep_hang[0]
    contributor_cuoi = danh_sach_xep_hang[-1]
    tong_contributor = len(danh_sach_xep_hang)

    if tong_contributor == 1:
        return "Repository hien tai chu yeu do mot contributor phu trach."

    diem_top = top.get("baseline_score", 0)
    diem_cuoi = contributor_cuoi.get("baseline_score", 0)

    if diem_top > diem_cuoi * 2:
        return "Dong gop trong repo bi tap trung vao mot so contributor chinh."

    return "Dong gop trong repo duoc phan bo tuong doi dong deu giua cac contributor."
