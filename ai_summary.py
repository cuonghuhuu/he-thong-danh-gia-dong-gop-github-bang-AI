# -*- coding: utf-8 -*-


def _lay_so(item, *keys, default=0):
    """Lay gia tri so dau tien ton tai trong item."""
    for key in keys:
        if key in item and item.get(key) is not None:
            try:
                return float(item.get(key, default))
            except (TypeError, ValueError):
                return default
    return default


def _lay_so_nguyen(item, *keys, default=0):
    return int(_lay_so(item, *keys, default=default))


def _dem_commit_theo_loai(item, key, file_count_key=None, change_key=None):
    """Uu tien count co san, neu khong co thi suy ra tu commit_quality_items."""
    if key in item and item.get(key) is not None:
        return _lay_so_nguyen(item, key)

    commits = item.get("commit_quality_items") or []
    if commits and file_count_key:
        return sum(1 for commit in commits if commit.get(file_count_key, 0) > 0)

    if file_count_key and file_count_key in item:
        return _lay_so_nguyen(item, file_count_key)

    if change_key and change_key in item:
        return 1 if _lay_so(item, change_key) > 0 else 0

    return 0


def _dem_documentation_commit(item):
    return _dem_commit_theo_loai(
        item,
        "documentation_commit_count",
        file_count_key="document_file_count",
        change_key="document_changes",
    )


def _dem_core_code_commit(item):
    return _dem_commit_theo_loai(
        item,
        "core_code_commit_count",
        file_count_key="source_file_count",
        change_key="source_changes",
    )


def _dem_integration_commit(item):
    return _dem_commit_theo_loai(
        item,
        "integration_commit_count",
        file_count_key="integration_file_count",
        change_key="integration_changes",
    )


def _la_nhieu(count, total, minimum=2, ratio=0.4):
    if count <= 0:
        return False
    if total <= 0:
        return count >= minimum
    return count >= minimum and (count / total >= ratio or count >= 3)


def xac_dinh_muc_dong_gop(score):
    """Phan loai contributor theo diem cuoi 0-100."""
    if score >= 85:
        return "Đóng góp chất lượng cao"
    if score >= 70:
        return "Đóng góp tốt"
    if score >= 50:
        return "Đóng góp trung bình"
    if score >= 30:
        return "Đóng góp thấp"
    return "Cần cải thiện"


def xac_dinh_loai_dong_gop(item):
    """Gắn nhãn phụ để người đọc hiểu contributor mạnh ở nhóm đóng góp nào."""
    final_score = _lay_so(item, "final_score", "score")
    quality_score = _lay_so(item, "quality_score")
    penalty_score = _lay_so(item, "penalty_score")
    commit_count = _lay_so_nguyen(item, "commit_count")
    suspicious_count = _lay_so_nguyen(item, "suspicious_commit_count")
    suspicious_ratio = _lay_so(item, "suspicious_commit_ratio")
    documentation_count = _dem_documentation_commit(item)
    core_code_count = _dem_core_code_commit(item)
    integration_count = _dem_integration_commit(item)

    if suspicious_ratio >= 0.4 and suspicious_count > 0:
        return "Contributor có nhiều commit cần xem lại"

    if commit_count <= 1 and final_score < 50:
        return "Contributor ít đóng góp"

    if _la_nhieu(integration_count, commit_count):
        return "Contributor thiên về tích hợp hệ thống"

    if _la_nhieu(core_code_count, commit_count):
        return "Contributor thiên về code chính"

    if _la_nhieu(documentation_count, commit_count):
        return "Contributor thiên về tài liệu/báo cáo"

    if final_score >= 70 and quality_score >= 75 and penalty_score < 8:
        return "Contributor có đóng góp chất lượng"

    if commit_count >= 3 and quality_score < 60:
        return "Contributor tích cực nhưng cần cải thiện chất lượng"

    return "Contributor cần theo dõi thêm"


def _mo_ta_muc_do_tham_gia(item):
    commit_count = _lay_so_nguyen(item, "commit_count")
    final_score = _lay_so(item, "final_score", "score")
    total_changes = _lay_so_nguyen(item, "total_changes")

    if commit_count >= 5 and final_score >= 70:
        return (
            f"tham gia tích cực với {commit_count} commit, điểm tổng hợp "
            f"{final_score:.1f}/100 và khối lượng thay đổi {total_changes} dòng"
        )
    if commit_count >= 3:
        return (
            f"tham gia ở mức khá với {commit_count} commit; cần xem thêm chất lượng "
            "và mức tác động của từng commit"
        )
    if commit_count == 1:
        return (
            "tham gia còn ít vì mới có 1 commit trong phạm vi phân tích; "
            "kết luận nên được xem cùng nội dung commit"
        )
    return "mức độ tham gia còn thấp hoặc chưa có commit được tính điểm"


def _mo_ta_chat_luong(item):
    quality_score = _lay_so(item, "quality_score")
    penalty_score = _lay_so(item, "penalty_score")
    suspicious_count = _lay_so_nguyen(item, "suspicious_commit_count")
    commit_count = _lay_so_nguyen(item, "commit_count")

    if quality_score >= 80 and penalty_score < 8:
        text = (
            f"quality_score {quality_score:.1f}/100 cho thấy đóng góp có chất lượng cao, "
            "message và nội dung thay đổi nhìn chung rõ ràng"
        )
    elif quality_score >= 65:
        text = (
            f"quality_score {quality_score:.1f}/100 ở mức khá; đóng góp có giá trị "
            "nhưng vẫn còn điểm có thể cải thiện"
        )
    elif quality_score >= 45:
        text = (
            f"quality_score {quality_score:.1f}/100 ở mức trung bình; nên làm rõ mục đích "
            "commit và tăng tác động vào phần chính của dự án"
        )
    else:
        text = (
            f"quality_score {quality_score:.1f}/100 còn thấp; nhiều thay đổi chưa thể hiện "
            "rõ giá trị hoặc tác động kỹ thuật"
        )

    if _la_nhieu(suspicious_count, commit_count, minimum=2, ratio=0.3):
        text += (
            f"; có {suspicious_count} commit cần xem lại nên cần viết commit message "
            "rõ hơn và tránh các message quá chung chung"
        )
    elif suspicious_count > 0:
        text += f"; có {suspicious_count} commit cần xem lại"

    return text


def _tao_diem_manh(item):
    strengths = []
    commit_count = _lay_so_nguyen(item, "commit_count")
    quality_score = _lay_so(item, "quality_score")
    documentation_count = _dem_documentation_commit(item)
    core_code_count = _dem_core_code_commit(item)
    integration_count = _dem_integration_commit(item)

    if quality_score >= 75:
        strengths.append("đóng góp có chất lượng tốt, quality_score cao")
    if _la_nhieu(core_code_count, commit_count):
        strengths.append("thiên về code chính, có tác động trực tiếp đến logic/source code")
    if _la_nhieu(integration_count, commit_count):
        strengths.append("có vai trò tích hợp hệ thống, kết nối các phần của dự án")
    if _la_nhieu(documentation_count, commit_count):
        strengths.append("đóng góp nhiều cho tài liệu/báo cáo, giúp dự án dễ theo dõi hơn")
    if _lay_so(item, "commit_message_score") >= 75:
        strengths.append("commit message tương đối rõ ràng")
    if _lay_so(item, "meaningful_change_score") >= 70:
        strengths.append("thay đổi có ý nghĩa, không chỉ là chỉnh sửa nhỏ")

    if strengths:
        return "; ".join(strengths)
    return "chưa có điểm mạnh nổi bật từ dữ liệu hiện tại"


def _tao_han_che(item):
    weaknesses = []
    commit_count = _lay_so_nguyen(item, "commit_count")
    suspicious_count = _lay_so_nguyen(item, "suspicious_commit_count")
    documentation_count = _dem_documentation_commit(item)
    core_code_count = _dem_core_code_commit(item)

    if _la_nhieu(suspicious_count, commit_count, minimum=2, ratio=0.3):
        weaknesses.append("có nhiều commit cần xem lại, đặc biệt về độ rõ của commit message")
    elif suspicious_count > 0:
        weaknesses.append("có commit cần xem lại")
    if _lay_so(item, "commit_message_score") < 55:
        weaknesses.append("commit message còn chung chung hoặc quá ngắn")
    if _lay_so(item, "code_impact_score") < 50:
        weaknesses.append("tác động vào code chính còn thấp")
    if _la_nhieu(documentation_count, commit_count) and not _la_nhieu(core_code_count, commit_count):
        weaknesses.append("đóng góp nghiêng về tài liệu/báo cáo nên tác động kỹ thuật chưa nhiều")
    if _lay_so_nguyen(item, "generated_file_count") > 0:
        weaknesses.append("có thay đổi file môi trường hoặc file tự động sinh")

    if weaknesses:
        return "; ".join(weaknesses)
    return "chưa thấy hạn chế lớn từ các rule hiện tại"


def _tao_commit_can_xem_lai(item):
    suspicious_commits = item.get("suspicious_commits", [])
    suspicious_count = _lay_so_nguyen(item, "suspicious_commit_count")

    if not suspicious_commits:
        if suspicious_count > 0:
            return f"có {suspicious_count} commit được đánh dấu cần xem lại nhưng chưa có chi tiết commit"
        return "không có commit đáng nghi nổi bật"

    parts = []
    for commit in suspicious_commits[:3]:
        reasons = commit.get("reasons") or commit.get("suspicious_reasons") or []
        reason_text = "; ".join(reasons[:2]) if reasons else "cần kiểm tra lại nội dung thay đổi"
        short_sha = commit.get("short_sha") or commit.get("sha", "")[:7] or "unknown"
        message = commit.get("message", "").strip() or "không có message"
        parts.append(f'{short_sha} - "{message}" ({reason_text})')

    remaining = max(suspicious_count, len(suspicious_commits)) - len(parts)
    if remaining > 0:
        parts.append(f"còn {remaining} commit khác")

    return "; ".join(parts)


def _tao_goi_y(item):
    commit_count = _lay_so_nguyen(item, "commit_count")
    suspicious_count = _lay_so_nguyen(item, "suspicious_commit_count")
    documentation_count = _dem_documentation_commit(item)
    core_code_count = _dem_core_code_commit(item)
    integration_count = _dem_integration_commit(item)
    quality_score = _lay_so(item, "quality_score")

    if _la_nhieu(suspicious_count, commit_count, minimum=2, ratio=0.3):
        return (
            "viết commit message cụ thể hơn, nêu rõ phần đã sửa và lý do sửa; "
            "hạn chế các message kiểu test/update/nộp/final nếu không mô tả rõ thay đổi"
        )
    if suspicious_count > 0:
        return "xem lại các commit bị đánh dấu và bổ sung commit message rõ mục đích hơn"
    if _la_nhieu(documentation_count, commit_count) and not _la_nhieu(core_code_count, commit_count):
        return (
            "tiếp tục giữ phần tài liệu/báo cáo tốt, đồng thời tham gia thêm vào logic "
            "hoặc source code chính để tăng tác động kỹ thuật"
        )
    if _la_nhieu(integration_count, commit_count):
        return (
            "khi làm phần tích hợp, nên mô tả rõ module được kết nối, luồng dữ liệu "
            "và cách kiểm thử để người review dễ đánh giá"
        )
    if _la_nhieu(core_code_count, commit_count):
        return "duy trì đóng góp vào code chính và bổ sung test/comment vừa đủ khi thay đổi logic quan trọng"
    if quality_score >= 75:
        return "duy trì chất lượng hiện tại, tiếp tục viết commit message rõ và chia commit theo từng mục đích"
    return "tăng số commit có nội dung rõ ràng, ưu tiên thay đổi có tác động thực tế đến chức năng của dự án"


def tao_noi_dung_nhan_xet(item):
    """Tao nhan xet rule-based bang tieng Viet cho tung contributor."""
    return "\n".join(
        [
            f"Mức độ tham gia: {_mo_ta_muc_do_tham_gia(item)}.",
            f"Chất lượng đóng góp: {_mo_ta_chat_luong(item)}.",
            f"Điểm mạnh: {_tao_diem_manh(item)}.",
            f"Điểm hạn chế: {_tao_han_che(item)}.",
            f"Commit cần xem lại: {_tao_commit_can_xem_lai(item)}.",
            f"Gợi ý cải thiện: {_tao_goi_y(item)}.",
        ]
    )


def tao_nhan_xet_ngan(item):
    quality_score = _lay_so(item, "quality_score")
    suspicious_count = _lay_so_nguyen(item, "suspicious_commit_count")
    commit_count = _lay_so_nguyen(item, "commit_count")
    documentation_count = _dem_documentation_commit(item)
    core_code_count = _dem_core_code_commit(item)
    integration_count = _dem_integration_commit(item)

    if _la_nhieu(suspicious_count, commit_count, minimum=2, ratio=0.3):
        return f"Quality {quality_score:.1f}, có nhiều commit cần xem lại."
    if quality_score >= 75:
        return f"Quality {quality_score:.1f}, đóng góp có chất lượng tốt."
    if _la_nhieu(integration_count, commit_count):
        return f"Quality {quality_score:.1f}, nổi bật ở vai trò tích hợp hệ thống."
    if _la_nhieu(core_code_count, commit_count):
        return f"Quality {quality_score:.1f}, đóng góp tốt vào code chính."
    if _la_nhieu(documentation_count, commit_count):
        return f"Quality {quality_score:.1f}, đóng góp thiên về tài liệu/báo cáo."
    return f"Quality {quality_score:.1f}, cần tăng tác động kỹ thuật."


def tao_nhan_xet_don_gian(danh_sach_xep_hang):
    """
    Gan muc danh gia, nhan phu va nhan xet cho contributor.
    Ham tra ve danh sach moi de tranh sua truc tiep dau vao.
    """
    ket_qua = []

    for item in danh_sach_xep_hang:
        thong_tin_moi = item.copy()
        final_score = _lay_so(thong_tin_moi, "final_score", "score")
        contribution_level = xac_dinh_muc_dong_gop(final_score)
        contribution_type = xac_dinh_loai_dong_gop(thong_tin_moi)

        thong_tin_moi["contribution_level"] = contribution_level
        thong_tin_moi["contribution_type"] = contribution_type
        thong_tin_moi["ai_summary"] = tao_noi_dung_nhan_xet(thong_tin_moi)
        thong_tin_moi["short_summary"] = tao_nhan_xet_ngan(thong_tin_moi)
        ket_qua.append(thong_tin_moi)

    return ket_qua


def tao_tong_ket_repo(danh_sach_xep_hang):
    """Tao nhan xet tong quan toan repository."""
    if not danh_sach_xep_hang:
        return "Không có dữ liệu để đánh giá."

    average_quality = sum(_lay_so(item, "quality_score") for item in danh_sach_xep_hang) / len(
        danh_sach_xep_hang
    )
    suspicious_count = sum(
        _lay_so_nguyen(item, "suspicious_commit_count") for item in danh_sach_xep_hang
    )

    if average_quality >= 75 and suspicious_count == 0:
        return "Repository có chất lượng đóng góp khá tốt, chưa thấy commit đáng nghi nổi bật."
    if suspicious_count > 0:
        return "Repository có một số commit cần xem lại về message, loại file hoặc ý nghĩa thay đổi."
    return "Repository có chất lượng đóng góp ở mức trung bình, cần theo dõi thêm tác động vào code chính."


def tao_nhan_xet_ai_rule_based(ket_qua_phan_tich):
    """Nhan xet AI gia lap bang rule-based, chua can API AI that."""
    contributors = ket_qua_phan_tich.get("contributors", [])
    overview = ket_qua_phan_tich.get("overview", {})
    ignored_count = overview.get("ignored_commit_count", 0)
    normalized_note = (
        "Hệ thống đã chuẩn hóa contributor theo GitHub login, alias, author name/email "
        "để tránh tách sai cùng một người."
    )
    ignored_note = (
        "Hệ thống đã loại bỏ commit bot/tự động để kết quả đánh giá công bằng hơn."
        if ignored_count > 0
        else "Hệ thống đã kiểm tra và sẽ loại bỏ commit bot/tự động nếu phát hiện."
    )
    data_handling_note = f"{normalized_note} {ignored_note}"

    if not contributors:
        return "\n\n".join(
            [
                "Chưa có dữ liệu contributor để tạo nhận xét.",
                data_handling_note,
            ]
        )

    top = contributors[0]
    average_quality = overview.get("average_quality_score", 0)
    suspicious_count = overview.get("suspicious_commit_count", 0)

    tong_quan = (
        f"Repository {overview.get('repo_full_name', '')} có "
        f"{overview.get('contributor_count', 0)} contributor trong "
        f"{overview.get('analyzed_commit_count', 0)} commit đã phân tích. "
        f"Điểm chất lượng trung bình là {average_quality:.2f}, "
        f"số commit cần xem lại là {suspicious_count}."
    )

    tong_quan = f"{tong_quan} {data_handling_note}"

    noi_bat = (
        f"Contributor có điểm cao nhất là {top.get('contributor', 'Không xác định')} "
        f"với final_score {top.get('final_score', 0):.2f}, "
        f"quality_score {top.get('quality_score', 0):.2f}, "
        f"penalty_score {top.get('penalty_score', 0):.2f}."
    )

    if suspicious_count > 0:
        goi_y = (
            "Nên rà soát các commit bị đánh dấu, đặc biệt là commit message quá ngắn, "
            "commit chỉ sửa báo cáo hoặc commit có file môi trường/local. "
            "Contributor có nhiều commit cần xem lại nên viết message rõ phần thay đổi và lý do thay đổi."
        )
    else:
        goi_y = (
            "Có thể tiếp tục cách đóng góp hiện tại, đồng thời khuyến khích viết commit message "
            "rõ mục đích và ưu tiên thay đổi có tác động vào source code chính."
        )

    return "\n\n".join(
        [
            "Nhận xét tổng quan:\n" + tong_quan,
            "Contributor nổi bật:\n" + noi_bat,
            "Gợi ý cải thiện:\n" + goi_y,
        ]
    )
