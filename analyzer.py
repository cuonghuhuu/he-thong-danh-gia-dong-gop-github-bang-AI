import math


def gom_commit_theo_contributor(danh_sach_commit):
    """
    Gom danh sach commit theo khoa contributor noi bo.
    """
    ket_qua = {}

    for commit in danh_sach_commit:
        khoa_contributor = commit.get("khoa_contributor") or "Khong xac dinh"
        ten_hien_thi = commit.get("ten_hien_thi") or "Khong xac dinh"

        if khoa_contributor not in ket_qua:
            ket_qua[khoa_contributor] = {
                "ten_hien_thi": ten_hien_thi,
                "danh_sach_commit": []
            }

        ket_qua[khoa_contributor]["danh_sach_commit"].append(commit)

    return ket_qua


def tinh_chi_so_contributor(du_lieu_gom):
    """
    Tinh cac chi so co ban cho tung contributor.
    """
    ket_qua = []

    for khoa_contributor, du_lieu_contributor in du_lieu_gom.items():
        danh_sach_commit = du_lieu_contributor.get("danh_sach_commit", [])
        tong_additions = 0
        tong_deletions = 0
        tap_hop_file = set()

        for commit in danh_sach_commit:
            tong_additions += commit.get("additions", 0)
            tong_deletions += commit.get("deletions", 0)

            danh_sach_file = commit.get("changed_files", [])
            for ten_file in danh_sach_file:
                tap_hop_file.add(ten_file)

        thong_tin = {
            "khoa_contributor": khoa_contributor,
            "ten_hien_thi": du_lieu_contributor.get("ten_hien_thi", "Khong xac dinh"),
            "tac_gia": du_lieu_contributor.get("ten_hien_thi", "Khong xac dinh"),
            "commit_count": len(danh_sach_commit),
            "total_additions": tong_additions,
            "total_deletions": tong_deletions,
            "changed_files_count": len(tap_hop_file),
            "total_changes": tong_additions + tong_deletions
        }
        ket_qua.append(thong_tin)

    return ket_qua


def tinh_diem_dong_gop_co_ban(danh_sach_thong_ke):
    """
    Tinh baseline_score cho tung contributor.
    Ham tra ve danh sach moi de giam side effect.
    """
    ket_qua = []

    for item in danh_sach_thong_ke:
        commit_count = item.get("commit_count", 0)
        total_changes = item.get("total_changes", 0)
        changed_files_count = item.get("changed_files_count", 0)

        diem = (
            math.log(commit_count + 1) * 0.4 +
            math.log(total_changes + 1) * 0.4 +
            math.log(changed_files_count + 1) * 0.2
        )

        thong_tin_moi = item.copy()
        thong_tin_moi["baseline_score"] = diem
        ket_qua.append(thong_tin_moi)

    return ket_qua


def xep_hang_contributor(danh_sach_thong_ke):
    """
    Sap xep contributor theo baseline_score giam dan.
    """
    return sorted(
        danh_sach_thong_ke,
        key=lambda item: item.get("baseline_score", 0),
        reverse=True
    )
