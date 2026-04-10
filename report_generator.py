def tao_bao_cao_markdown(danh_sach_xep_hang, tong_ket_repo="Chua co tong ket"):
    """
    Tạo nội dung báo cáo Markdown, có căn đều độ rộng các cột
    """
    tieu_de = [
        "Hang",
        "Tac gia",
        "Commit",
        "Additions",
        "Deletions",
        "Files",
        "Total changes",
        "Score",
        "Contribution type",
        "AI summary"
    ]

    du_lieu_bang = []

    for i, item in enumerate(danh_sach_xep_hang, start=1):
        dong = [
            str(i),
            str(item.get("tac_gia", "")),
            str(item.get("commit_count", 0)),
            str(item.get("total_additions", 0)),
            str(item.get("total_deletions", 0)),
            str(item.get("changed_files_count", 0)),
            str(item.get("total_changes", 0)),
            f"{item.get('baseline_score', 0):.2f}",
            str(item.get("contribution_type", "Chua xac dinh")),
            str(item.get("ai_summary", "Chua co nhan xet"))
        ]
        du_lieu_bang.append(dong)

    # Tính độ rộng lớn nhất cho từng cột
    do_rong_cot = []
    for chi_so_cot in range(len(tieu_de)):
        do_rong_lon_nhat = len(tieu_de[chi_so_cot])

        for dong in du_lieu_bang:
            gia_tri = dong[chi_so_cot]
            if len(gia_tri) > do_rong_lon_nhat:
                do_rong_lon_nhat = len(gia_tri)

        do_rong_cot.append(do_rong_lon_nhat)

    def tao_dong(cac_gia_tri):
        ket_qua = "|"
        for i, gia_tri in enumerate(cac_gia_tri):
            ket_qua += " " + gia_tri.ljust(do_rong_cot[i]) + " |"
        return ket_qua

    noi_dung = "# Bao cao dong gop contributor\n\n"
    noi_dung += "## Tong ket repo\n\n"
    noi_dung += f"{tong_ket_repo}\n\n"
    noi_dung += "## Bang xep hang\n\n"

    noi_dung += tao_dong(tieu_de) + "\n"

    noi_dung += "|"
    for do_rong in do_rong_cot:
        noi_dung += "-" * (do_rong + 2) + "|"
    noi_dung += "\n"

    for dong in du_lieu_bang:
        noi_dung += tao_dong(dong) + "\n"

    return noi_dung