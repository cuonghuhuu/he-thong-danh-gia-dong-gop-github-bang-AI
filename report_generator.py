# -*- coding: utf-8 -*-

import csv
import html
import re
from datetime import datetime
from pathlib import Path


def tao_ten_file_an_toan(text):
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", str(text).strip())
    return text.strip("_") or "repository"


def tao_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _chuan_hoa_ket_qua(ket_qua_phan_tich, tong_ket_repo=None):
    if isinstance(ket_qua_phan_tich, list):
        return {
            "overview": {},
            "contributors": ket_qua_phan_tich,
            "ignored_commits": [],
            "ai_summary": tong_ket_repo or "",
        }
    return ket_qua_phan_tich or {}


def tao_duong_dan_bao_cao(ket_qua_phan_tich, reports_dir, extension):
    ket_qua_phan_tich = _chuan_hoa_ket_qua(ket_qua_phan_tich)
    overview = ket_qua_phan_tich.get("overview", {})
    repo_name = tao_ten_file_an_toan(overview.get("repo_full_name", "repository"))
    file_name = f"{repo_name}_{tao_timestamp()}.{extension}"
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir / file_name


def _lay_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _lay_score(item):
    return _lay_float(item.get("final_score", item.get("score", item.get("baseline_score", 0))))


def _diem_hien_thi(score_100):
    return round(max(0.0, min(100.0, _lay_float(score_100))) / 10, 1)


def _diem_tru_hien_thi(penalty_score):
    penalty_score = max(0.0, min(30.0, _lay_float(penalty_score)))
    return round(penalty_score / 30.0 * 10, 1)


def _lay_score_hien_thi(item):
    if "final_score_display" in item and item.get("final_score_display") is not None:
        return _lay_float(item.get("final_score_display"))
    return _diem_hien_thi(_lay_score(item))


def _lay_quality_hien_thi(item):
    if "quality_score_display" in item and item.get("quality_score_display") is not None:
        return _lay_float(item.get("quality_score_display"))
    return _diem_hien_thi(item.get("quality_score", 0))


def _lay_penalty_hien_thi(item):
    if "penalty_score_display" in item and item.get("penalty_score_display") is not None:
        return _lay_float(item.get("penalty_score_display"))
    return _diem_tru_hien_thi(item.get("penalty_score", 0))


def _lay_diem_hien_thi_item(item, display_key, raw_key):
    if display_key in item and item.get(display_key) is not None:
        return _lay_float(item.get(display_key))
    return _diem_hien_thi(item.get(raw_key, 0))


def _lay_overview_diem_hien_thi(overview, display_key, raw_key):
    if display_key in overview and overview.get(display_key) is not None:
        return _lay_float(overview.get(display_key))
    return _diem_hien_thi(overview.get(raw_key, 0))


def _lay_contributor(item):
    return item.get("contributor") or item.get("tac_gia") or item.get("ten_hien_thi") or ""


def _lay_files(item):
    return item.get("files_changed", item.get("changed_files_count", 0))


def _lay_nhan_xet_ai(item):
    return item.get("ai_summary") or item.get("short_summary") or ""


def _lay_sha_ngan(commit):
    return commit.get("short_sha") or str(commit.get("sha", ""))[:7] or "unknown"


def _lay_ly_do(commit, key="reasons"):
    reasons = commit.get(key) or commit.get("suspicious_reasons") or commit.get("ignored_reasons") or []
    if isinstance(reasons, str):
        return reasons
    return "; ".join(str(reason) for reason in reasons) if reasons else "Không có lý do cụ thể"


def _lay_muc_nghi_ngo(commit):
    level = commit.get("suspicion_level") or "Thấp"
    score = commit.get("suspicion_score_display", commit.get("penalty_score_display"))
    if score is None:
        return level
    return f"{level} ({_lay_float(score):.1f}/10)"


def _markdown_cell(value):
    text = str(value).replace("\r\n", "\n").replace("\r", "\n").replace("\n", "<br>")
    return text.replace("|", "\\|")


def _tom_tat_commit_can_xem_lai(item):
    commits = item.get("suspicious_commits", [])
    suspicious_count = item.get("suspicious_commit_count", 0)
    if not commits:
        if suspicious_count:
            return f"Có {suspicious_count} commit cần xem lại nhưng chưa có chi tiết."
        return "Không có"

    parts = []
    for commit in commits:
        parts.append(
            f"{_lay_sha_ngan(commit)} - {commit.get('message', '')} "
            f"({_lay_ly_do(commit)}; {_lay_muc_nghi_ngo(commit)})"
        )
    return " | ".join(parts)


def tao_bang_markdown(contributors):
    headers = [
        "STT",
        "Thành viên",
        "Số commit",
        "Dòng thêm",
        "Dòng xoá",
        "File đã sửa",
        "Giờ code ước tính",
        "Ngày hoạt động",
        "Phiên làm việc",
        "Điểm chất lượng /10",
        "Điểm thời gian /10",
        "Consistency /10",
        "Integration /10",
        "Điểm trừ /10",
        "Commit cần xem lại",
        "Điểm cuối /10",
        "Mức đánh giá",
        "Nhận xét AI",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for index, item in enumerate(contributors, start=1):
        row = [
            str(index),
            _lay_contributor(item),
            item.get("commit_count", 0),
            item.get("total_additions", item.get("additions", 0)),
            item.get("total_deletions", item.get("deletions", 0)),
            _lay_files(item),
            f"{_lay_float(item.get('estimated_coding_hours')):.1f}",
            item.get("active_days", 0),
            item.get("coding_sessions", 0),
            f"{_lay_quality_hien_thi(item):.1f}",
            f"{_lay_diem_hien_thi_item(item, 'estimated_time_score_display', 'estimated_time_score'):.1f}",
            f"{_lay_diem_hien_thi_item(item, 'consistency_score_display', 'consistency_score'):.1f}",
            f"{_lay_diem_hien_thi_item(item, 'integration_score_display', 'integration_score'):.1f}",
            f"{_lay_penalty_hien_thi(item):.1f}",
            item.get("suspicious_commit_count", 0),
            f"{_lay_score_hien_thi(item):.1f}",
            item.get("contribution_level", ""),
            _lay_nhan_xet_ai(item),
        ]
        lines.append("| " + " | ".join(_markdown_cell(value) for value in row) + " |")

    return "\n".join(lines)


def tao_danh_sach_commit_can_xem_lai_markdown(contributors):
    lines = ["## Commit cần xem lại", ""]
    has_suspicious_commit = False
    lines.extend(
        [
            "| Contributor | SHA | Message | Lý do bị đánh dấu | Mức độ nghi ngờ |",
            "| --- | --- | --- | --- | --- |",
        ]
    )

    for item in contributors:
        suspicious_commits = item.get("suspicious_commits", [])
        if not suspicious_commits:
            continue

        has_suspicious_commit = True
        for commit in suspicious_commits:
            row = [
                _lay_contributor(item) or "Không xác định",
                f"`{_lay_sha_ngan(commit)}`",
                commit.get("message", ""),
                _lay_ly_do(commit),
                _lay_muc_nghi_ngo(commit),
            ]
            lines.append("| " + " | ".join(_markdown_cell(value) for value in row) + " |")

    if not has_suspicious_commit:
        lines.append("| Không có commit kém chất lượng được phát hiện. |  |  |  |  |")
    lines.append("")

    return "\n".join(lines)


def _tao_dong_thong_ke_bieu_do(contributors):
    if not contributors:
        return ["Chưa có dữ liệu phân tích."]

    rows = []
    for item in contributors:
        rows.append(
            (
                _lay_contributor(item) or "Không xác định",
                _lay_score_hien_thi(item),
                _lay_quality_hien_thi(item),
                _lay_penalty_hien_thi(item),
                item.get("suspicious_commit_count", 0),
                item.get("total_additions", item.get("additions", 0)),
                item.get("total_deletions", item.get("deletions", 0)),
                _lay_float(item.get("estimated_coding_hours")),
                item.get("active_days", 0),
            )
        )

    top_final = max(rows, key=lambda row: row[1])
    top_quality = max(rows, key=lambda row: row[2])
    top_suspicious = max(rows, key=lambda row: row[4])
    total_additions = sum(row[5] for row in rows)
    total_deletions = sum(row[6] for row in rows)
    total_hours = sum(row[7] for row in rows)
    max_active = max(rows, key=lambda row: row[8])

    return [
        f"Điểm cuối cao nhất: {top_final[0]} ({top_final[1]:.1f}/10).",
        f"Điểm chất lượng cao nhất: {top_quality[0]} ({top_quality[2]:.1f}/10).",
        f"Commit cần xem lại nhiều nhất: {top_suspicious[0]} ({top_suspicious[4]} commit).",
        f"Tổng dòng thêm/xoá: +{total_additions} / -{total_deletions}.",
        f"Tổng giờ code ước tính: {total_hours:.1f} giờ.",
        f"Số ngày hoạt động nhiều nhất: {max_active[0]} ({max_active[8]} ngày).",
        "Điểm trừ trong báo cáo là mức 0-10 chuẩn hóa từ penalty nội bộ tối đa 30 điểm.",
    ]


def tao_thong_ke_bieu_do_markdown(contributors):
    lines = ["## Thống kê hỗ trợ biểu đồ", ""]
    lines.extend(f"- {line}" for line in _tao_dong_thong_ke_bieu_do(contributors))
    lines.append("")
    return "\n".join(lines)


def tao_danh_sach_commit_bi_loai_markdown(ignored_commits):
    if not ignored_commits:
        return ""

    lines = [
        "## Commit bot/tự động đã loại",
        "",
        "| SHA ngắn | Contributor | Message | Lý do loại |",
        "| --- | --- | --- | --- |",
    ]
    for commit in ignored_commits:
        row = [
            f"`{_lay_sha_ngan(commit)}`",
            commit.get("contributor", ""),
            commit.get("message", ""),
            _lay_ly_do(commit),
        ]
        lines.append("| " + " | ".join(_markdown_cell(value) for value in row) + " |")
    lines.append("")

    return "\n".join(lines)


def tao_bao_cao_markdown(ket_qua_phan_tich, tong_ket_repo=None):
    """
    Tạo nội dung Markdown.
    Hỗ trợ cả kiểu mới (dict kết quả phân tích) và kiểu cũ (list contributor).
    """
    ket_qua_phan_tich = _chuan_hoa_ket_qua(ket_qua_phan_tich, tong_ket_repo)
    overview = ket_qua_phan_tich.get("overview", {})
    contributors = ket_qua_phan_tich.get("contributors", [])
    ignored_commits = ket_qua_phan_tich.get("ignored_commits", [])
    ai_summary = ket_qua_phan_tich.get("ai_summary", "")

    noi_dung = [
        "# Báo cáo đánh giá đóng góp GitHub bằng AI",
        "",
        "## Tổng quan",
        "",
        f"- Repository: {overview.get('repo_full_name', '')}",
        f"- Thời gian phân tích: {overview.get('analyzed_at', '')}",
        f"- Số commit đã phân tích: {overview.get('analyzed_commit_count', 0)}",
        f"- Tổng contributor: {overview.get('contributor_count', 0)}",
        f"- Tổng additions: {overview.get('total_additions', 0)}",
        f"- Tổng deletions: {overview.get('total_deletions', 0)}",
        "- Điểm chất lượng trung bình: "
        f"{_lay_overview_diem_hien_thi(overview, 'average_quality_score_display', 'average_quality_score'):.1f}/10",
        f"- Tổng giờ code ước tính: {_lay_float(overview.get('total_estimated_coding_hours')):.1f}",
        f"- Tổng phiên làm việc: {overview.get('total_coding_sessions', 0)}",
        f"- Số commit cần xem lại: {overview.get('suspicious_commit_count', 0)}",
        f"- Số commit bot đã loại: {overview.get('ignored_bot_commit_count', 0)}",
        f"- Số commit tự động đã loại: {overview.get('ignored_auto_commit_count', 0)}",
        f"- Contributor điểm cao nhất: {overview.get('top_contributor', 'Chưa có')}",
        "",
        "## Công thức điểm",
        "",
        "```text",
        "raw_score = 0.10 * commit_score",
        "          + 0.15 * code_volume_score",
        "          + 0.15 * file_impact_score",
        "          + 0.25 * quality_score",
        "          + 0.15 * consistency_score",
        "          + 0.10 * estimated_time_score",
        "          + 0.10 * integration_score",
        "",
        "final_score = raw_score - penalty_score",
        "```",
        "",
        "Điểm chất lượng và điểm cuối hiển thị theo thang /10. Điểm trừ hiển thị theo thang 0-10, chuẩn hóa từ penalty nội bộ tối đa 30 điểm.",
        "",
        "## Bảng tổng hợp contributor",
        "",
        tao_bang_markdown(contributors),
        "",
        tao_thong_ke_bieu_do_markdown(contributors),
        "",
        tao_danh_sach_commit_can_xem_lai_markdown(contributors),
    ]

    ignored_section = tao_danh_sach_commit_bi_loai_markdown(ignored_commits)
    if ignored_section:
        noi_dung.append(ignored_section)

    noi_dung.extend(
        [
            "## Nhận xét AI tổng quan",
            "",
            ai_summary,
            "",
        ]
    )

    return "\n".join(noi_dung)


def xuat_markdown(ket_qua_phan_tich, reports_dir):
    ket_qua_phan_tich = _chuan_hoa_ket_qua(ket_qua_phan_tich)
    path = tao_duong_dan_bao_cao(ket_qua_phan_tich, reports_dir, "md")
    path.write_text(tao_bao_cao_markdown(ket_qua_phan_tich), encoding="utf-8")
    return path


def xuat_csv(ket_qua_phan_tich, reports_dir):
    ket_qua_phan_tich = _chuan_hoa_ket_qua(ket_qua_phan_tich)
    path = tao_duong_dan_bao_cao(ket_qua_phan_tich, reports_dir, "csv")
    contributors = ket_qua_phan_tich.get("contributors", [])
    ignored_commits = ket_qua_phan_tich.get("ignored_commits", [])

    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "STT",
                "Thành viên",
                "Số commit",
                "Dòng thêm",
                "Dòng xoá",
                "File đã sửa",
                "Giờ code ước tính",
                "Ngày hoạt động",
                "Phiên làm việc",
                "Điểm chất lượng /10",
                "Điểm thời gian /10",
                "Consistency /10",
                "Integration /10",
                "Điểm trừ /10",
                "Commit cần xem lại",
                "Điểm cuối /10",
                "Mức đánh giá",
                "Nhận xét AI",
                "Chi tiết commit cần xem lại",
            ]
        )

        for index, item in enumerate(contributors, start=1):
            writer.writerow(
                [
                    index,
                    _lay_contributor(item),
                    item.get("commit_count", 0),
                    item.get("total_additions", item.get("additions", 0)),
                    item.get("total_deletions", item.get("deletions", 0)),
                    _lay_files(item),
                    f"{_lay_float(item.get('estimated_coding_hours')):.1f}",
                    item.get("active_days", 0),
                    item.get("coding_sessions", 0),
                    f"{_lay_quality_hien_thi(item):.1f}",
                    f"{_lay_diem_hien_thi_item(item, 'estimated_time_score_display', 'estimated_time_score'):.1f}",
                    f"{_lay_diem_hien_thi_item(item, 'consistency_score_display', 'consistency_score'):.1f}",
                    f"{_lay_diem_hien_thi_item(item, 'integration_score_display', 'integration_score'):.1f}",
                    f"{_lay_penalty_hien_thi(item):.1f}",
                    item.get("suspicious_commit_count", 0),
                    f"{_lay_score_hien_thi(item):.1f}",
                    item.get("contribution_level", ""),
                    _lay_nhan_xet_ai(item),
                    _tom_tat_commit_can_xem_lai(item),
                ]
            )

        writer.writerow([])
        writer.writerow(["Commit cần xem lại"])
        writer.writerow(["Contributor", "SHA", "Message", "Lý do bị đánh dấu", "Mức độ nghi ngờ"])
        has_suspicious_commit = False
        for item in contributors:
            for commit in item.get("suspicious_commits", []):
                has_suspicious_commit = True
                writer.writerow(
                    [
                        _lay_contributor(item),
                        _lay_sha_ngan(commit),
                        commit.get("message", ""),
                        _lay_ly_do(commit),
                        _lay_muc_nghi_ngo(commit),
                    ]
                )
        if not has_suspicious_commit:
            writer.writerow(["Không có commit kém chất lượng được phát hiện."])

        writer.writerow([])
        writer.writerow(["Thống kê hỗ trợ biểu đồ"])
        for line in _tao_dong_thong_ke_bieu_do(contributors):
            writer.writerow([line])

        if ignored_commits:
            writer.writerow([])
            writer.writerow(["Commit bot/tự động đã loại"])
            writer.writerow(["SHA ngắn", "Contributor", "Message", "Lý do loại"])
            for commit in ignored_commits:
                writer.writerow(
                    [
                        _lay_sha_ngan(commit),
                        commit.get("contributor", ""),
                        commit.get("message", ""),
                        _lay_ly_do(commit),
                    ]
                )

    return path


def _dang_ky_font_pdf_tieng_viet():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    candidates = []

    try:
        import matplotlib

        font_dir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
        candidates.append((font_dir / "DejaVuSans.ttf", font_dir / "DejaVuSans-Bold.ttf"))
    except Exception:
        pass

    windows_font_dir = Path("C:/Windows/Fonts")
    candidates.extend(
        [
            (windows_font_dir / "segoeui.ttf", windows_font_dir / "segoeuib.ttf"),
            (windows_font_dir / "arial.ttf", windows_font_dir / "arialbd.ttf"),
            (windows_font_dir / "tahoma.ttf", windows_font_dir / "tahomabd.ttf"),
        ]
    )

    for regular_font, bold_font in candidates:
        if not regular_font.exists():
            continue
        if not bold_font.exists():
            bold_font = regular_font
        try:
            pdfmetrics.registerFont(TTFont("VietnameseRegular", str(regular_font)))
            pdfmetrics.registerFont(TTFont("VietnameseBold", str(bold_font)))
            return "VietnameseRegular", "VietnameseBold"
        except Exception:
            continue

    return "Helvetica", "Helvetica-Bold"


def _cap_nhat_font_styles(styles, font_regular, font_bold):
    for style_name in styles.byName:
        styles[style_name].fontName = font_regular

    for style_name in ("Title", "Heading1", "Heading2", "Heading3"):
        if style_name in styles.byName:
            styles[style_name].fontName = font_bold


def _paragraph(text, style):
    from reportlab.platypus import Paragraph

    safe_text = html.escape(str(text or "")).replace("\r\n", "\n").replace("\r", "\n")
    return Paragraph(safe_text.replace("\n", "<br/>"), style)


def _chon_font_matplotlib():
    try:
        from matplotlib import font_manager

        candidates = []
        try:
            import matplotlib

            font_dir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
            candidates.append(font_dir / "DejaVuSans.ttf")
        except Exception:
            pass

        windows_font_dir = Path("C:/Windows/Fonts")
        candidates.extend(
            [
                windows_font_dir / "segoeui.ttf",
                windows_font_dir / "arial.ttf",
                windows_font_dir / "tahoma.ttf",
            ]
        )

        for font_path in candidates:
            if font_path.exists():
                font_manager.fontManager.addfont(str(font_path))
                return font_manager.FontProperties(fname=str(font_path)).get_name()
    except Exception:
        pass

    return "DejaVu Sans"


def _them_trang_text_pdf(pdf, title, lines, font_name):
    from matplotlib.figure import Figure

    fig = Figure(figsize=(8.27, 11.69))
    ax = fig.add_subplot(111)
    ax.axis("off")
    text = title + "\n\n" + "\n".join(lines)
    ax.text(
        0.04,
        0.96,
        text,
        va="top",
        ha="left",
        fontsize=9,
        wrap=True,
        family=font_name,
    )
    pdf.savefig(fig, bbox_inches="tight")


def _xuat_pdf_bang_matplotlib(ket_qua_phan_tich, path):
    from matplotlib.backends.backend_pdf import PdfPages

    overview = ket_qua_phan_tich.get("overview", {})
    contributors = ket_qua_phan_tich.get("contributors", [])
    ignored_commits = ket_qua_phan_tich.get("ignored_commits", [])
    font_name = _chon_font_matplotlib()

    with PdfPages(path) as pdf:
        lines = [
            f"Repository: {overview.get('repo_full_name', '')}",
            f"Thời gian phân tích: {overview.get('analyzed_at', '')}",
            f"Số commit đã phân tích: {overview.get('analyzed_commit_count', 0)}",
            f"Tổng contributor: {overview.get('contributor_count', 0)}",
            "Điểm chất lượng trung bình: "
            f"{_lay_overview_diem_hien_thi(overview, 'average_quality_score_display', 'average_quality_score'):.1f}/10",
            f"Tổng giờ code ước tính: {_lay_float(overview.get('total_estimated_coding_hours')):.1f}",
            f"Tổng phiên làm việc: {overview.get('total_coding_sessions', 0)}",
            f"Số commit cần xem lại: {overview.get('suspicious_commit_count', 0)}",
            "Điểm trừ hiển thị theo thang 0-10, chuẩn hóa từ penalty nội bộ tối đa 30 điểm.",
            "",
            "Bảng contributor:",
        ]
        for item in contributors:
            lines.append(
                f"- {_lay_contributor(item)} | commit={item.get('commit_count', 0)} | "
                f"add={item.get('total_additions', item.get('additions', 0))} | "
                f"del={item.get('total_deletions', item.get('deletions', 0))} | "
                f"files={_lay_files(item)} | quality={_lay_quality_hien_thi(item):.1f}/10 | "
                f"hours={_lay_float(item.get('estimated_coding_hours')):.1f} | "
                f"days={item.get('active_days', 0)} | sessions={item.get('coding_sessions', 0)} | "
                f"time={_lay_diem_hien_thi_item(item, 'estimated_time_score_display', 'estimated_time_score'):.1f}/10 | "
                f"consistency={_lay_diem_hien_thi_item(item, 'consistency_score_display', 'consistency_score'):.1f}/10 | "
                f"integration={_lay_diem_hien_thi_item(item, 'integration_score_display', 'integration_score'):.1f}/10 | "
                f"penalty={_lay_penalty_hien_thi(item):.1f}/10 | "
                f"suspicious={item.get('suspicious_commit_count', 0)} | "
                f"final={_lay_score_hien_thi(item):.1f}/10 | mức={item.get('contribution_level', '')}"
            )
            if _lay_nhan_xet_ai(item):
                lines.append(f"  Nhận xét AI: {_lay_nhan_xet_ai(item)}")
        _them_trang_text_pdf(pdf, "Báo cáo đánh giá đóng góp GitHub bằng AI", lines, font_name)

        suspicious_lines = []
        for item in contributors:
            for commit in item.get("suspicious_commits", []):
                suspicious_lines.append(
                    f"- {_lay_contributor(item)} | {_lay_sha_ngan(commit)} | "
                    f"{commit.get('message', '')} | {_lay_ly_do(commit)} | {_lay_muc_nghi_ngo(commit)}"
                )
        if not suspicious_lines:
            suspicious_lines.append("Không có commit kém chất lượng được phát hiện.")
        _them_trang_text_pdf(pdf, "Commit cần xem lại", suspicious_lines, font_name)

        _them_trang_text_pdf(
            pdf,
            "Thống kê hỗ trợ biểu đồ",
            _tao_dong_thong_ke_bieu_do(contributors),
            font_name,
        )

        if ignored_commits:
            ignored_lines = [
                f"- {_lay_sha_ngan(commit)} | {commit.get('contributor', '')} | "
                f"{commit.get('message', '')} | {_lay_ly_do(commit)}"
                for commit in ignored_commits
            ]
            _them_trang_text_pdf(pdf, "Commit bot/tự động đã loại", ignored_lines, font_name)

    return path


def xuat_pdf(ket_qua_phan_tich, reports_dir):
    ket_qua_phan_tich = _chuan_hoa_ket_qua(ket_qua_phan_tich)
    path = tao_duong_dan_bao_cao(ket_qua_phan_tich, reports_dir, "pdf")

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import LongTable, Paragraph, SimpleDocTemplate, Spacer, TableStyle
    except ImportError:
        try:
            return _xuat_pdf_bang_matplotlib(ket_qua_phan_tich, path)
        except ImportError as exc:
            raise RuntimeError(
                "Cần cài reportlab hoặc matplotlib để xuất PDF. "
                "Hãy chạy: pip install -r requirements.txt"
            ) from exc

    overview = ket_qua_phan_tich.get("overview", {})
    contributors = ket_qua_phan_tich.get("contributors", [])
    ignored_commits = ket_qua_phan_tich.get("ignored_commits", [])
    ai_summary = ket_qua_phan_tich.get("ai_summary", "")

    document = SimpleDocTemplate(
        str(path),
        pagesize=landscape(A4),
        rightMargin=1.0 * cm,
        leftMargin=1.0 * cm,
        topMargin=1.0 * cm,
        bottomMargin=1.0 * cm,
    )
    styles = getSampleStyleSheet()
    font_regular, font_bold = _dang_ky_font_pdf_tieng_viet()
    _cap_nhat_font_styles(styles, font_regular, font_bold)

    table_text = ParagraphStyle(
        "TableText",
        parent=styles["Normal"],
        fontName=font_regular,
        fontSize=6.5,
        leading=8,
        wordWrap="CJK",
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=table_text,
        fontName=font_bold,
        textColor=colors.white,
        alignment=1,
    )

    elements = []

    elements.append(Paragraph("Báo cáo đánh giá đóng góp GitHub bằng AI", styles["Title"]))
    elements.append(Spacer(1, 0.35 * cm))

    overview_lines = [
        f"Repository: {overview.get('repo_full_name', '')}",
        f"Thời gian phân tích: {overview.get('analyzed_at', '')}",
        f"Số commit đã phân tích: {overview.get('analyzed_commit_count', 0)}",
        f"Tổng contributor: {overview.get('contributor_count', 0)}",
        f"Tổng additions: {overview.get('total_additions', 0)}",
        f"Tổng deletions: {overview.get('total_deletions', 0)}",
        "Điểm chất lượng trung bình: "
        f"{_lay_overview_diem_hien_thi(overview, 'average_quality_score_display', 'average_quality_score'):.1f}/10",
        f"Tổng giờ code ước tính: {_lay_float(overview.get('total_estimated_coding_hours')):.1f}",
        f"Tổng phiên làm việc: {overview.get('total_coding_sessions', 0)}",
        f"Số commit cần xem lại: {overview.get('suspicious_commit_count', 0)}",
        f"Số commit bot đã loại: {overview.get('ignored_bot_commit_count', 0)}",
        f"Số commit tự động đã loại: {overview.get('ignored_auto_commit_count', 0)}",
        "Điểm trừ hiển thị theo thang 0-10, chuẩn hóa từ penalty nội bộ tối đa 30 điểm.",
    ]
    for line in overview_lines:
        elements.append(_paragraph(line, styles["Normal"]))

    elements.append(Spacer(1, 0.35 * cm))
    elements.append(Paragraph("Bảng tổng hợp contributor", styles["Heading2"]))

    table_data = [
        [
            _paragraph("STT", table_header),
            _paragraph("Contributor", table_header),
            _paragraph("Commit", table_header),
            _paragraph("Additions", table_header),
            _paragraph("Deletions", table_header),
            _paragraph("Files", table_header),
            _paragraph("Hours", table_header),
            _paragraph("Days", table_header),
            _paragraph("Sessions", table_header),
            _paragraph("Quality /10", table_header),
            _paragraph("Time /10", table_header),
            _paragraph("Cons. /10", table_header),
            _paragraph("Integr. /10", table_header),
            _paragraph("Penalty /10", table_header),
            _paragraph("Commit cần xem lại", table_header),
            _paragraph("Final /10", table_header),
            _paragraph("Mức đánh giá", table_header),
            _paragraph("Nhận xét AI", table_header),
        ]
    ]
    for index, item in enumerate(contributors, start=1):
        table_data.append(
            [
                str(index),
                _paragraph(_lay_contributor(item), table_text),
                str(item.get("commit_count", 0)),
                str(item.get("total_additions", item.get("additions", 0))),
                str(item.get("total_deletions", item.get("deletions", 0))),
                str(_lay_files(item)),
                f"{_lay_float(item.get('estimated_coding_hours')):.1f}",
                str(item.get("active_days", 0)),
                str(item.get("coding_sessions", 0)),
                f"{_lay_quality_hien_thi(item):.1f}",
                f"{_lay_diem_hien_thi_item(item, 'estimated_time_score_display', 'estimated_time_score'):.1f}",
                f"{_lay_diem_hien_thi_item(item, 'consistency_score_display', 'consistency_score'):.1f}",
                f"{_lay_diem_hien_thi_item(item, 'integration_score_display', 'integration_score'):.1f}",
                f"{_lay_penalty_hien_thi(item):.1f}",
                str(item.get("suspicious_commit_count", 0)),
                f"{_lay_score_hien_thi(item):.1f}",
                _paragraph(item.get("contribution_level", ""), table_text),
                _paragraph(_lay_nhan_xet_ai(item), table_text),
            ]
        )

    table = LongTable(
        table_data,
        colWidths=[
            0.7 * cm,
            2.0 * cm,
            0.9 * cm,
            1.1 * cm,
            1.1 * cm,
            0.9 * cm,
            0.9 * cm,
            0.8 * cm,
            0.8 * cm,
            1.2 * cm,
            0.9 * cm,
            0.9 * cm,
            0.9 * cm,
            1.1 * cm,
            1.3 * cm,
            1.1 * cm,
            2.0 * cm,
            7.0 * cm,
        ],
        repeatRows=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f5f8f")),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("FONTNAME", (0, 1), (-1, -1), font_regular),
                ("FONTSIZE", (0, 0), (-1, -1), 6.5),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 1), (15, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elements.append(table)

    elements.append(Spacer(1, 0.35 * cm))
    elements.append(Paragraph("Commit cần xem lại", styles["Heading2"]))
    suspicious_rows = [
        [
            _paragraph("Contributor", table_header),
            _paragraph("SHA ngắn", table_header),
            _paragraph("Message", table_header),
            _paragraph("Lý do bị đánh dấu", table_header),
            _paragraph("Mức độ nghi ngờ", table_header),
        ]
    ]
    for item in contributors:
        for commit in item.get("suspicious_commits", []):
            suspicious_rows.append(
                [
                    _paragraph(_lay_contributor(item), table_text),
                    _paragraph(_lay_sha_ngan(commit), table_text),
                    _paragraph(commit.get("message", ""), table_text),
                    _paragraph(_lay_ly_do(commit), table_text),
                    _paragraph(_lay_muc_nghi_ngo(commit), table_text),
                ]
            )

    if len(suspicious_rows) == 1:
        elements.append(_paragraph("Không có commit kém chất lượng được phát hiện.", styles["Normal"]))
    else:
        suspicious_table = LongTable(
            suspicious_rows,
            colWidths=[3.0 * cm, 1.8 * cm, 7.4 * cm, 11.4 * cm, 4.0 * cm],
            repeatRows=1,
        )
        suspicious_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f5f8f")),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 0), (-1, 0), font_bold),
                    ("FONTNAME", (0, 1), (-1, -1), font_regular),
                ]
            )
        )
        elements.append(suspicious_table)

    elements.append(Spacer(1, 0.35 * cm))
    elements.append(Paragraph("Thống kê hỗ trợ biểu đồ", styles["Heading2"]))
    for line in _tao_dong_thong_ke_bieu_do(contributors):
        elements.append(_paragraph(line, styles["Normal"]))

    if ignored_commits:
        elements.append(Spacer(1, 0.35 * cm))
        elements.append(Paragraph("Commit bot/tự động đã loại", styles["Heading2"]))
        ignored_rows = [
            [
                _paragraph("SHA ngắn", table_header),
                _paragraph("Contributor", table_header),
                _paragraph("Message", table_header),
                _paragraph("Lý do loại", table_header),
            ]
        ]
        for commit in ignored_commits:
            ignored_rows.append(
                [
                    _paragraph(_lay_sha_ngan(commit), table_text),
                    _paragraph(commit.get("contributor", ""), table_text),
                    _paragraph(commit.get("message", ""), table_text),
                    _paragraph(_lay_ly_do(commit), table_text),
                ]
            )
        ignored_table = LongTable(
            ignored_rows,
            colWidths=[2.0 * cm, 3.2 * cm, 12.5 * cm, 10.0 * cm],
            repeatRows=1,
        )
        ignored_table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f5f8f")),
                    ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("FONTNAME", (0, 0), (-1, 0), font_bold),
                    ("FONTNAME", (0, 1), (-1, -1), font_regular),
                ]
            )
        )
        elements.append(ignored_table)

    elements.append(Spacer(1, 0.35 * cm))
    elements.append(Paragraph("Nhận xét AI tổng quan", styles["Heading2"]))
    for block in str(ai_summary or "").split("\n\n"):
        if block.strip():
            elements.append(_paragraph(block, styles["Normal"]))
            elements.append(Spacer(1, 0.15 * cm))

    document.build(elements)
    return path
