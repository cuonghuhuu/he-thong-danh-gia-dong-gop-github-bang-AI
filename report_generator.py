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
            f"{_lay_sha_ngan(commit)} - {commit.get('message', '')} ({_lay_ly_do(commit)})"
        )
    return " | ".join(parts)


def tao_bang_markdown(contributors):
    headers = [
        "STT",
        "Contributor",
        "Commit",
        "Additions",
        "Deletions",
        "Files",
        "Quality score",
        "Penalty",
        "Suspicious commits",
        "Final score",
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
            f"{_lay_float(item.get('quality_score')):.2f}",
            f"{_lay_float(item.get('penalty_score')):.2f}",
            item.get("suspicious_commit_count", 0),
            f"{_lay_score(item):.2f}",
            item.get("contribution_level", ""),
            _lay_nhan_xet_ai(item),
        ]
        lines.append("| " + " | ".join(_markdown_cell(value) for value in row) + " |")

    return "\n".join(lines)


def tao_danh_sach_commit_can_xem_lai_markdown(contributors):
    lines = ["## Commit cần xem lại", ""]
    has_suspicious_commit = False

    for item in contributors:
        suspicious_commits = item.get("suspicious_commits", [])
        if not suspicious_commits:
            continue

        has_suspicious_commit = True
        lines.append(f"### {_lay_contributor(item) or 'Không xác định'}")
        lines.append("")
        lines.extend(
            [
                "| SHA ngắn | Message | Lý do bị đánh dấu |",
                "| --- | --- | --- |",
            ]
        )
        for commit in suspicious_commits:
            row = [
                f"`{_lay_sha_ngan(commit)}`",
                commit.get("message", ""),
                _lay_ly_do(commit),
            ]
            lines.append("| " + " | ".join(_markdown_cell(value) for value in row) + " |")
        lines.append("")

    if not has_suspicious_commit:
        lines.append("Không có commit cần xem lại.")
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
        f"- Điểm chất lượng trung bình: {_lay_float(overview.get('average_quality_score')):.2f}",
        f"- Số commit cần xem lại: {overview.get('suspicious_commit_count', 0)}",
        f"- Số commit bot đã loại: {overview.get('ignored_bot_commit_count', 0)}",
        f"- Số commit tự động đã loại: {overview.get('ignored_auto_commit_count', 0)}",
        f"- Contributor điểm cao nhất: {overview.get('top_contributor', 'Chưa có')}",
        "",
        "## Công thức điểm",
        "",
        "```text",
        "final_score = 0.20 * commit_score",
        "            + 0.20 * code_volume_score",
        "            + 0.20 * file_impact_score",
        "            + 0.25 * quality_score",
        "            + 0.15 * consistency_score",
        "            - penalty_score",
        "```",
        "",
        "## Bảng tổng hợp contributor",
        "",
        tao_bang_markdown(contributors),
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
                "Contributor",
                "Commit",
                "Additions",
                "Deletions",
                "Files",
                "Quality score",
                "Penalty",
                "Suspicious commits",
                "Final score",
                "Mức đánh giá",
                "Nhận xét AI",
                "Commit cần xem lại",
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
                    f"{_lay_float(item.get('quality_score')):.2f}",
                    f"{_lay_float(item.get('penalty_score')):.2f}",
                    item.get("suspicious_commit_count", 0),
                    f"{_lay_score(item):.2f}",
                    item.get("contribution_level", ""),
                    _lay_nhan_xet_ai(item),
                    _tom_tat_commit_can_xem_lai(item),
                ]
            )

        writer.writerow([])
        writer.writerow(["Commit cần xem lại"])
        writer.writerow(["Contributor", "SHA ngắn", "Message", "Lý do bị đánh dấu"])
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
                    ]
                )
        if not has_suspicious_commit:
            writer.writerow(["Không có commit cần xem lại"])

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
            f"Điểm chất lượng trung bình: {_lay_float(overview.get('average_quality_score')):.2f}",
            f"Số commit cần xem lại: {overview.get('suspicious_commit_count', 0)}",
            "",
            "Bảng contributor:",
        ]
        for item in contributors:
            lines.append(
                f"- {_lay_contributor(item)} | commit={item.get('commit_count', 0)} | "
                f"add={item.get('total_additions', item.get('additions', 0))} | "
                f"del={item.get('total_deletions', item.get('deletions', 0))} | "
                f"files={_lay_files(item)} | quality={_lay_float(item.get('quality_score')):.2f} | "
                f"penalty={_lay_float(item.get('penalty_score')):.2f} | "
                f"suspicious={item.get('suspicious_commit_count', 0)} | "
                f"final={_lay_score(item):.2f} | mức={item.get('contribution_level', '')}"
            )
            if _lay_nhan_xet_ai(item):
                lines.append(f"  Nhận xét AI: {_lay_nhan_xet_ai(item)}")
        _them_trang_text_pdf(pdf, "Báo cáo đánh giá đóng góp GitHub bằng AI", lines, font_name)

        suspicious_lines = []
        for item in contributors:
            for commit in item.get("suspicious_commits", []):
                suspicious_lines.append(
                    f"- {_lay_contributor(item)} | {_lay_sha_ngan(commit)} | "
                    f"{commit.get('message', '')} | {_lay_ly_do(commit)}"
                )
        if not suspicious_lines:
            suspicious_lines.append("Không có commit cần xem lại.")
        _them_trang_text_pdf(pdf, "Commit cần xem lại", suspicious_lines, font_name)

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
        f"Điểm chất lượng trung bình: {_lay_float(overview.get('average_quality_score')):.2f}",
        f"Số commit cần xem lại: {overview.get('suspicious_commit_count', 0)}",
        f"Số commit bot đã loại: {overview.get('ignored_bot_commit_count', 0)}",
        f"Số commit tự động đã loại: {overview.get('ignored_auto_commit_count', 0)}",
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
            _paragraph("Quality score", table_header),
            _paragraph("Penalty", table_header),
            _paragraph("Suspicious commits", table_header),
            _paragraph("Final score", table_header),
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
                f"{_lay_float(item.get('quality_score')):.2f}",
                f"{_lay_float(item.get('penalty_score')):.2f}",
                str(item.get("suspicious_commit_count", 0)),
                f"{_lay_score(item):.2f}",
                _paragraph(item.get("contribution_level", ""), table_text),
                _paragraph(_lay_nhan_xet_ai(item), table_text),
            ]
        )

    table = LongTable(
        table_data,
        colWidths=[
            0.7 * cm,
            2.5 * cm,
            0.9 * cm,
            1.1 * cm,
            1.1 * cm,
            0.9 * cm,
            1.2 * cm,
            1.1 * cm,
            1.3 * cm,
            1.1 * cm,
            2.3 * cm,
            12.4 * cm,
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
                ("ALIGN", (2, 1), (9, -1), "RIGHT"),
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
                ]
            )

    if len(suspicious_rows) == 1:
        elements.append(_paragraph("Không có commit cần xem lại.", styles["Normal"]))
    else:
        suspicious_table = LongTable(
            suspicious_rows,
            colWidths=[3.2 * cm, 2.0 * cm, 8.5 * cm, 14.0 * cm],
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
