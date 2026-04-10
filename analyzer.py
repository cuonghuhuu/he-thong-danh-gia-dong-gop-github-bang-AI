def gom_commit_theo_contributor(danh_sach_commit):
    """
    Gom danh sách commit theo từng contributor
    """
    ket_qua = {}

    for commit in danh_sach_commit:
        tac_gia = commit.get("tac_gia")

        if not tac_gia:
            tac_gia = "Khong xac dinh"

        if tac_gia not in ket_qua:
            ket_qua[tac_gia] = []

        ket_qua[tac_gia].append(commit)

    return ket_qua
def tinh_chi_so_contributor(du_lieu_gom):
    """
    Tính các chỉ số cơ bản cho từng contributor
    """
    ket_qua = []

    for tac_gia, danh_sach_commit in du_lieu_gom.items():
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
            "tac_gia": tac_gia,
            "commit_count": len(danh_sach_commit),
            "total_additions": tong_additions,
            "total_deletions": tong_deletions,
            "changed_files_count": len(tap_hop_file),
            "total_changes": tong_additions + tong_deletions
        }

        ket_qua.append(thong_tin)

    return ket_qua
import math

def tinh_diem_dong_gop_co_ban(danh_sach_thong_ke):
    """
    Tính điểm đóng góp cải tiến (dùng log để tránh bias)
    """
    for item in danh_sach_thong_ke:
        commit_count = item.get("commit_count", 0)
        total_changes = item.get("total_changes", 0)
        changed_files_count = item.get("changed_files_count", 0)

        diem = (
            math.log(commit_count + 1) * 0.4 +
            math.log(total_changes + 1) * 0.4 +
            math.log(changed_files_count + 1) * 0.2
        )

        item["baseline_score"] = diem

    return danh_sach_thong_ke
def xep_hang_contributor(danh_sach_thong_ke):
    """
    Sắp xếp contributor theo baseline_score giảm dần
    """
    return sorted(
        danh_sach_thong_ke,
        key=lambda item: item.get("baseline_score", 0),
        reverse=True
    )