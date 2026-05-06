def xac_dinh_loai_dong_gop(item):
    """
    Phan loai contributor theo hanh vi dong gop.
    Cac nguong duoc giu don gian de phu hop bai thuc hanh sinh vien.
    """
    commit_count = item.get("commit_count", 0)
    total_additions = item.get("total_additions", item.get("additions", 0))
    total_deletions = item.get("total_deletions", item.get("deletions", 0))
    total_changes = item.get("total_changes", 0)
    files_changed = item.get("changed_files_count", item.get("files_changed", 0))

    if commit_count <= 1 and total_changes < 50:
        return "Low Activity Contributor"

    if total_additions >= max(50, total_deletions * 1.6):
        return "Feature Contributor"

    if total_deletions >= max(30, total_additions * 1.2) or files_changed >= 10:
        return "Refactor Contributor"

    if total_changes > 0:
        chenhlech = abs(total_additions - total_deletions) / total_changes
        if chenhlech <= 0.35:
            return "Balanced Contributor"

    return "Balanced Contributor"


def tao_noi_dung_nhan_xet(item):
    """Tao nhan xet ngan gon cho tung contributor."""
    commit_count = item.get("commit_count", 0)
    total_changes = item.get("total_changes", 0)
    changed_files_count = item.get("changed_files_count", 0)
    final_score = item.get("final_score", item.get("score", 0))
    contribution_type = item.get("contribution_type") or xac_dinh_loai_dong_gop(item)

    if contribution_type == "Low Activity Contributor":
        return "Muc hoat dong thap trong tap commit da phan tich."

    if final_score >= 75:
        return "Dong gop noi bat, diem tong hop cao tren nhieu chi so."

    if commit_count >= 5 and total_changes >= 300:
        return "Tan suat commit va khoi luong thay doi deu cao."

    if changed_files_count >= 8:
        return "Pham vi tac dong rong, tham gia vao nhieu file."

    if total_changes > 0:
        return "Co dong gop on dinh, phu hop voi nhom tac vu vua va nho."

    return "Chua co thay doi dang ke trong tap commit da phan tich."


def tao_nhan_xet_don_gian(danh_sach_xep_hang):
    """
    Tao loai dong gop va nhan xet cho tung contributor.
    Ham tra ve danh sach moi de tranh sua truc tiep dau vao.
    """
    ket_qua = []

    for item in danh_sach_xep_hang:
        thong_tin_moi = item.copy()
        contribution_type = xac_dinh_loai_dong_gop(item)
        thong_tin_moi["contribution_type"] = contribution_type
        thong_tin_moi["ai_summary"] = tao_noi_dung_nhan_xet(thong_tin_moi)
        ket_qua.append(thong_tin_moi)

    return ket_qua


def tao_tong_ket_repo(danh_sach_xep_hang):
    """Tao nhan xet tong quan toan repository."""
    if not danh_sach_xep_hang:
        return "Khong co du lieu de danh gia."

    top = danh_sach_xep_hang[0]
    tong_contributor = len(danh_sach_xep_hang)

    if tong_contributor == 1:
        return "Repository hien tai chu yeu do mot contributor phu trach."

    tong_diem = sum(item.get("final_score", item.get("score", 0)) for item in danh_sach_xep_hang)
    diem_top = top.get("final_score", top.get("score", 0))
    ti_le_top = diem_top / tong_diem if tong_diem > 0 else 0

    if ti_le_top >= 0.5:
        return "Dong gop dang tap trung manh vao contributor co diem cao nhat."

    if ti_le_top >= 0.35:
        return "Dong gop co su chenh lech nhat dinh nhung van co nhieu contributor tham gia."

    return "Dong gop trong repository duoc phan bo tuong doi can bang."


def tao_nhan_xet_ai_rule_based(ket_qua_phan_tich):
    """Nhan xet AI gia lap bang rule-based, chua can API AI that."""
    contributors = ket_qua_phan_tich.get("contributors", [])
    overview = ket_qua_phan_tich.get("overview", {})

    if not contributors:
        return "Chua co du lieu contributor de tao nhan xet."

    top = contributors[0]
    tong_diem = overview.get("total_score", 0)
    diem_top = top.get("final_score", top.get("score", 0))
    ti_le_top = diem_top / tong_diem if tong_diem > 0 else 0

    tong_quan = (
        f"Repository {overview.get('repo_full_name', '')} co "
        f"{overview.get('contributor_count', 0)} contributor trong "
        f"{overview.get('analyzed_commit_count', 0)} commit da phan tich. "
        f"Tong additions la {overview.get('total_additions', 0)}, "
        f"tong deletions la {overview.get('total_deletions', 0)}."
    )

    noi_bat = (
        f"Contributor noi bat nhat la {top.get('contributor', 'Khong xac dinh')} "
        f"voi {top.get('commit_count', 0)} commit, "
        f"{top.get('total_changes', 0)} total changes, "
        f"{top.get('files_changed', 0)} files changed va diem {diem_top:.2f}."
    )

    if ti_le_top >= 0.5:
        muc_chenh_lech = "Muc do chenh lech cao: mot contributor dang chiem ty trong diem lon."
        goi_y = (
            "Nen chia task theo module nho hon, tang review cheo, va giao cac issue vua suc "
            "cho contributor con lai de giam phu thuoc."
        )
    elif ti_le_top >= 0.35:
        muc_chenh_lech = (
            "Muc do chenh lech trung binh: nhom co contributor noi bat "
            "nhung van co su tham gia tu cac thanh vien khac."
        )
        goi_y = (
            "Nen duy tri contributor chinh o vai tro review/huong dan, dong thoi phan cong them "
            "task sua loi, test va tai lieu cho cac thanh vien con lai."
        )
    else:
        muc_chenh_lech = "Muc do chenh lech thap: dong gop cua nhom kha can bang."
        goi_y = (
            "Co the tiep tuc cach phan cong hien tai, nhung nen theo doi them chat luong commit "
            "va muc do review de danh gia day du hon."
        )

    return "\n\n".join(
        [
            "Nhan xet tong quan ve nhom:\n" + tong_quan,
            "Nhan xet contributor noi bat:\n" + noi_bat,
            "Nhan xet muc do chenh lech dong gop:\n" + muc_chenh_lech,
            "Goi y cai thien phan chia cong viec:\n" + goi_y,
        ]
    )

