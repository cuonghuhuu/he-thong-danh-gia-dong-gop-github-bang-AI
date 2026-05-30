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
    """Gan nhan phu de nguoi doc hieu contributor manh/yếu o dau."""
    final_score = item.get("final_score", item.get("score", 0))
    quality_score = item.get("quality_score", 0)
    penalty_score = item.get("penalty_score", 0)
    commit_count = item.get("commit_count", 0)
    suspicious_ratio = item.get("suspicious_commit_ratio", 0)
    source_file_count = item.get("source_file_count", 0)
    document_file_count = item.get("document_file_count", 0)
    integration_commit_count = item.get("integration_commit_count", 0)

    if suspicious_ratio >= 0.4 and item.get("suspicious_commit_count", 0) > 0:
        return "Contributor có nhiều commit kém chất lượng"

    if commit_count <= 1 and final_score < 50:
        return "Contributor ít đóng góp"

    if final_score >= 70 and quality_score >= 75 and penalty_score < 8:
        return "Contributor chất lượng"

    if commit_count >= 3 and quality_score < 60:
        return "Contributor tích cực nhưng cần cải thiện chất lượng"

    if integration_commit_count >= 2 and quality_score >= 55 and penalty_score < 18:
        return "Contributor có vai trò tích hợp hệ thống"

    if document_file_count > 0 and document_file_count >= source_file_count:
        return "Contributor thiên về tài liệu/báo cáo"

    if source_file_count > document_file_count:
        return "Contributor thiên về code chính"

    return "Contributor cần theo dõi thêm"


def _mo_ta_muc_do_tham_gia(item):
    commit_count = item.get("commit_count", 0)
    final_score = item.get("final_score", item.get("score", 0))

    if commit_count >= 5 and final_score >= 70:
        return "tham gia khá đều và có điểm tổng hợp tốt"
    if commit_count >= 3:
        return "có tham gia ở nhiều commit nhưng cần xem thêm chất lượng"
    if commit_count == 1:
        return "mới có một commit trong phạm vi phân tích"
    return "mức độ tham gia còn thấp"


def _mo_ta_chat_luong(item):
    quality_score = item.get("quality_score", 0)
    penalty_score = item.get("penalty_score", 0)

    if quality_score >= 80 and penalty_score < 8:
        return "chất lượng đóng góp tốt, ít dấu hiệu commit kém chất lượng"
    if quality_score >= 65:
        return "chất lượng tương đối ổn nhưng vẫn có điểm cần cải thiện"
    if quality_score >= 45:
        return "chất lượng ở mức trung bình, cần viết commit rõ hơn hoặc tăng tác động code"
    return "chất lượng còn thấp, có nhiều dấu hiệu cần xem lại"


def _tao_diem_manh(item):
    strengths = []

    if item.get("integration_commit_count", 0) >= 2:
        strengths.append("có hoạt động tích hợp hệ thống rõ ràng")
    if item.get("source_file_count", 0) > item.get("document_file_count", 0):
        strengths.append("có tác động vào file source code chính")
    if item.get("core_code_commit_count", 0) > 0:
        strengths.append("có commit liên quan đến code lõi")
    if item.get("documentation_commit_count", 0) > 0:
        strengths.append("có đóng góp tài liệu/hướng dẫn")
    if item.get("commit_message_score", 0) >= 75:
        strengths.append("commit message tương đối rõ ràng")
    if item.get("meaningful_change_score", 0) >= 70:
        strengths.append("thay đổi có ý nghĩa, không chỉ là chỉnh sửa nhỏ")
    if item.get("quality_score", 0) >= 80:
        strengths.append("điểm chất lượng cao")

    return "; ".join(strengths) if strengths else "chưa có điểm mạnh nổi bật từ dữ liệu hiện tại"


def _tao_han_che(item):
    weaknesses = []

    if item.get("suspicious_commit_count", 0) > 0:
        weaknesses.append("có commit cần xem lại")
    if item.get("commit_message_score", 0) < 55:
        weaknesses.append("commit message còn chung chung")
    if item.get("code_impact_score", 0) < 50:
        weaknesses.append("tác động vào code chính còn thấp")
    if item.get("document_file_count", 0) > item.get("source_file_count", 0):
        weaknesses.append("đóng góp nghiêng nhiều về tài liệu/báo cáo")
    if item.get("generated_file_count", 0) > 0:
        weaknesses.append("có thay đổi file môi trường hoặc file tự động sinh")

    return "; ".join(weaknesses) if weaknesses else "chưa thấy hạn chế lớn từ các rule hiện tại"


def tao_ghi_chu_vai_tro_leader(item):
    integration_count = item.get("integration_commit_count", 0)
    core_count = item.get("core_code_commit_count", 0)
    documentation_count = item.get("documentation_commit_count", 0)
    review_or_merge_score = item.get("review_or_merge_activity_score", 0)

    if integration_count >= 2:
        return (
            f"Có {integration_count} commit tích hợp hợp lệ, "
            f"{core_count} commit code lõi và {documentation_count} commit tài liệu; "
            f"điểm hoạt động merge/review là {review_or_merge_score:.1f}."
        )
    if integration_count == 1:
        return (
            f"Có 1 commit tích hợp hợp lệ; nên tiếp tục tách rõ các commit merge, sửa lỗi "
            f"và tài liệu để thể hiện vai trò điều phối tốt hơn."
        )
    return "Chưa thấy nhiều dữ liệu commit tích hợp; vai trò trưởng nhóm chưa thể kết luận từ lịch sử commit."


def _tao_commit_can_xem_lai(item):
    suspicious_commits = item.get("suspicious_commits", [])
    if not suspicious_commits:
        return "không có commit đáng nghi nổi bật"

    parts = []
    for commit in suspicious_commits[:3]:
        reasons = "; ".join(commit.get("reasons", [])[:2])
        parts.append(
            f"{commit.get('short_sha', '')} - \"{commit.get('message', '')}\" ({reasons})"
        )

    if len(suspicious_commits) > 3:
        parts.append(f"còn {len(suspicious_commits) - 3} commit khác")

    return "; ".join(parts)


def _tao_goi_y(item):
    if item.get("suspicious_commit_count", 0) > 0:
        return "nên viết commit message cụ thể hơn và hạn chế commit kiểu test/update/nộp nếu không mô tả rõ thay đổi"
    if item.get("source_file_count", 0) == 0:
        return "nên tham gia thêm vào file source code chính hoặc logic xử lý để tăng tác động kỹ thuật"
    if item.get("penalty_score", 0) >= 10:
        return "nên tách commit rõ mục đích, tránh đưa file môi trường hoặc file tự động sinh vào commit"
    return "nên duy trì cách đóng góp hiện tại và bổ sung test/comment vừa đủ khi thay đổi logic"


def tao_noi_dung_nhan_xet(item):
    """Tao nhan xet rule-based bang tieng Viet cho tung contributor."""
    return "\n".join(
        [
            f"Mức độ tham gia: {_mo_ta_muc_do_tham_gia(item)}.",
            f"Chất lượng đóng góp: {_mo_ta_chat_luong(item)}.",
            f"Vai trò tích hợp: {item.get('leader_contribution_note', tao_ghi_chu_vai_tro_leader(item))}",
            f"Điểm mạnh: {_tao_diem_manh(item)}.",
            f"Điểm hạn chế: {_tao_han_che(item)}.",
            f"Commit cần xem lại: {_tao_commit_can_xem_lai(item)}.",
            f"Gợi ý cải thiện: {_tao_goi_y(item)}.",
        ]
    )


def tao_nhan_xet_ngan(item):
    quality_score = item.get("quality_score", 0)
    suspicious_count = item.get("suspicious_commit_count", 0)

    if suspicious_count:
        return f"Quality {quality_score:.1f}, có {suspicious_count} commit cần xem lại."
    if item.get("source_file_count", 0) > item.get("document_file_count", 0):
        return f"Quality {quality_score:.1f}, đóng góp tốt vào code chính."
    return f"Quality {quality_score:.1f}, cần tăng tác động kỹ thuật."


def tao_nhan_xet_don_gian(danh_sach_xep_hang):
    """
    Gan muc danh gia, nhan phu va nhan xet cho contributor.
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
        thong_tin_moi["leader_contribution_note"] = tao_ghi_chu_vai_tro_leader(thong_tin_moi)
        thong_tin_moi["ai_summary"] = tao_noi_dung_nhan_xet(thong_tin_moi)
        thong_tin_moi["short_summary"] = tao_nhan_xet_ngan(thong_tin_moi)
        ket_qua.append(thong_tin_moi)

    return ket_qua


def tao_tong_ket_repo(danh_sach_xep_hang):
    """Tao nhan xet tong quan toan repository."""
    if not danh_sach_xep_hang:
        return "Không có dữ liệu để đánh giá."

    average_quality = sum(item.get("quality_score", 0) for item in danh_sach_xep_hang) / len(
        danh_sach_xep_hang
    )
    suspicious_count = sum(item.get("suspicious_commit_count", 0) for item in danh_sach_xep_hang)

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
    ignored_note = (
        "Hệ thống đã loại bỏ commit tự động/bot để kết quả đánh giá công bằng hơn."
        if ignored_count > 0
        else ""
    )

    if not contributors:
        if ignored_note:
            return "\n\n".join(
                [
                    "Chưa có dữ liệu contributor để tạo nhận xét.",
                    ignored_note,
                ]
            )
        return "Chưa có dữ liệu contributor để tạo nhận xét."

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

    if ignored_note:
        tong_quan = f"{tong_quan} {ignored_note}"

    noi_bat = (
        f"Contributor có điểm cao nhất là {top.get('contributor', 'Không xác định')} "
        f"với final score {top.get('final_score', 0):.2f}, "
        f"quality score {top.get('quality_score', 0):.2f}, "
        f"penalty {top.get('penalty_score', 0):.2f}."
    )

    if suspicious_count > 0:
        goi_y = (
            "Nên rà soát các commit bị đánh dấu, đặc biệt commit message quá ngắn, "
            "commit chỉ sửa báo cáo hoặc commit có file môi trường/local."
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
