import csv
import html
import re
from datetime import datetime
from pathlib import Path


def tao_ten_file_an_toan(text):
    text = re.sub(r"[^A-Za-z0-9_.-]+", "_", text.strip())
    return text.strip("_") or "repository"


def tao_timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def tao_duong_dan_bao_cao(ket_qua_phan_tich, reports_dir, extension):
    overview = ket_qua_phan_tich.get("overview", {})
    repo_name = tao_ten_file_an_toan(overview.get("repo_full_name", "repository"))
    file_name = f"{repo_name}_{tao_timestamp()}.{extension}"
    reports_dir = Path(reports_dir)
    reports_dir.mkdir(parents=True, exist_ok=True)
    return reports_dir / file_name


def _lay_score(item):
    return item.get("final_score", item.get("score", item.get("baseline_score", 0)))


def _markdown_cell(value):
    text = str(value).replace("\n", "<br>")
    return text.replace("|", "\\|")


def _tom_tat_commit_dang_nghi(item):
    commits = item.get("suspicious_commits", [])
    if not commits:
        return "Không có"

    parts = []
    for commit in commits:
        reasons = "; ".join(commit.get("reasons", []))
        parts.append(f"{commit.get('short_sha', '')}: {commit.get('message', '')} ({reasons})")
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
        "Suspicious ratio",
        "Final score",
        "Mức đánh giá",
        "Nhận xét",
    ]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(["---"] * len(headers)) + " |",
    ]

    for index, item in enumerate(contributors, start=1):
        row = [
            str(index),
            str(item.get("contributor", item.get("tac_gia", ""))),
            str(item.get("commit_count", 0)),
            str(item.get("total_additions", 0)),
            str(item.get("total_deletions", 0)),
            str(item.get("files_changed", item.get("changed_files_count", 0))),
            f"{item.get('quality_score', 0):.2f}",
            f"{item.get('penalty_score', 0):.2f}",
            str(item.get("suspicious_commit_count", 0)),
            f"{item.get('suspicious_commit_ratio', 0) * 100:.1f}%",
            f"{_lay_score(item):.2f}",
            str(item.get("contribution_level", "")),
            str(item.get("short_summary", item.get("ai_summary", ""))),
        ]
        lines.append("| " + " | ".join(_markdown_cell(value) for value in row) + " |")

    return "\n".join(lines)


def tao_danh_sach_commit_dang_nghi_markdown(contributors):
    lines = ["## Commit cần xem lại", ""]
    has_suspicious_commit = False

    for item in contributors:
        suspicious_commits = item.get("suspicious_commits", [])
        if not suspicious_commits:
            continue

        has_suspicious_commit = True
        lines.append(f"### {item.get('contributor', 'Không xác định')}")
        lines.append("")
        for commit in suspicious_commits:
            reasons = "; ".join(commit.get("reasons", []))
            lines.append(
                f"- `{commit.get('short_sha', '')}` - {commit.get('message', '')}: {reasons}"
            )
        lines.append("")

    if not has_suspicious_commit:
        lines.append("Không có commit đáng nghi nổi bật.")
        lines.append("")

    return "\n".join(lines)


def tao_danh_sach_commit_bi_loai_markdown(ignored_commits):
    lines = ["## Commit bot/tự động đã loại", ""]

    if not ignored_commits:
        lines.append("Không có commit bot hoặc commit tự động bị loại.")
        lines.append("")
        return "\n".join(lines)

    for commit in ignored_commits:
        reasons = ", ".join(commit.get("reasons", []))
        lines.append(
            f"- `{commit.get('short_sha', '')}` - "
            f"{commit.get('contributor', '')}: {commit.get('message', '')} ({reasons})"
        )
    lines.append("")

    return "\n".join(lines)


def tao_bao_cao_markdown(ket_qua_phan_tich, tong_ket_repo=None):
    """
    Tao noi dung Markdown.
    Ho tro ca kieu moi (dict ket_qua_phan_tich) va kieu cu (list contributor).
    """
    if isinstance(ket_qua_phan_tich, list):
        ket_qua_phan_tich = {
            "overview": {},
            "contributors": ket_qua_phan_tich,
            "ai_summary": tong_ket_repo or "",
        }

    overview = ket_qua_phan_tich.get("overview", {})
    contributors = ket_qua_phan_tich.get("contributors", [])
    ignored_commits = ket_qua_phan_tich.get("ignored_commits", [])
    ai_summary = ket_qua_phan_tich.get("ai_summary", "")

    noi_dung = [
        "# Báo cáo đánh giá đóng góp contributor trên GitHub",
        "",
        "## Tổng quan",
        "",
        f"- Repository: {overview.get('repo_full_name', '')}",
        f"- Thời gian phân tích: {overview.get('analyzed_at', '')}",
        f"- Số commit đã phân tích: {overview.get('analyzed_commit_count', 0)}",
        f"- Tổng contributor: {overview.get('contributor_count', 0)}",
        f"- Tổng additions: {overview.get('total_additions', 0)}",
        f"- Tổng deletions: {overview.get('total_deletions', 0)}",
        f"- Điểm chất lượng trung bình: {overview.get('average_quality_score', 0):.2f}",
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
        "## Bảng contributor",
        "",
        tao_bang_markdown(contributors),
        "",
        tao_danh_sach_commit_dang_nghi_markdown(contributors),
        tao_danh_sach_commit_bi_loai_markdown(ignored_commits),
        "## Nhận xét AI rule-based",
        "",
        ai_summary,
        "",
    ]

    return "\n".join(noi_dung)


def xuat_markdown(ket_qua_phan_tich, reports_dir):
    path = tao_duong_dan_bao_cao(ket_qua_phan_tich, reports_dir, "md")
    path.write_text(tao_bao_cao_markdown(ket_qua_phan_tich), encoding="utf-8")
    return path


def xuat_csv(ket_qua_phan_tich, reports_dir):
    path = tao_duong_dan_bao_cao(ket_qua_phan_tich, reports_dir, "csv")
    contributors = ket_qua_phan_tich.get("contributors", [])

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
                "Commit score",
                "Code volume score",
                "File impact score",
                "Commit message score",
                "Meaningful change score",
                "Code impact score",
                "Quality score",
                "Consistency score",
                "Penalty score",
                "Suspicious commit count",
                "Suspicious commit ratio",
                "Final score",
                "Mức đánh giá",
                "Nhãn phụ",
                "Nhận xét AI",
                "Commit đáng nghi",
            ]
        )

        for index, item in enumerate(contributors, start=1):
            writer.writerow(
                [
                    index,
                    item.get("contributor", item.get("tac_gia", "")),
                    item.get("commit_count", 0),
                    item.get("total_additions", 0),
                    item.get("total_deletions", 0),
                    item.get("files_changed", item.get("changed_files_count", 0)),
                    f"{item.get('commit_score', 0):.2f}",
                    f"{item.get('code_volume_score', 0):.2f}",
                    f"{item.get('file_impact_score', 0):.2f}",
                    f"{item.get('commit_message_score', 0):.2f}",
                    f"{item.get('meaningful_change_score', 0):.2f}",
                    f"{item.get('code_impact_score', 0):.2f}",
                    f"{item.get('quality_score', 0):.2f}",
                    f"{item.get('consistency_score', 0):.2f}",
                    f"{item.get('penalty_score', 0):.2f}",
                    item.get("suspicious_commit_count", 0),
                    f"{item.get('suspicious_commit_ratio', 0) * 100:.1f}%",
                    f"{_lay_score(item):.2f}",
                    item.get("contribution_level", ""),
                    item.get("contribution_type", ""),
                    item.get("ai_summary", ""),
                    _tom_tat_commit_dang_nghi(item),
                ]
            )

    return path


def _dang_ky_font_pdf_tieng_viet():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont

    try:
        import matplotlib

        font_dir = Path(matplotlib.get_data_path()) / "fonts" / "ttf"
        regular_font = font_dir / "DejaVuSans.ttf"
        bold_font = font_dir / "DejaVuSans-Bold.ttf"

        if not regular_font.exists() or not bold_font.exists():
            raise FileNotFoundError("Khong tim thay font DejaVu Sans.")

        pdfmetrics.registerFont(TTFont("DejaVuSans", str(regular_font)))
        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", str(bold_font)))
        return "DejaVuSans", "DejaVuSans-Bold"
    except Exception:
        return "Helvetica", "Helvetica-Bold"


def _cap_nhat_font_styles(styles, font_regular, font_bold):
    for style_name in styles.byName:
        styles[style_name].fontName = font_regular

    for style_name in ("Title", "Heading1", "Heading2", "Heading3"):
        if style_name in styles.byName:
            styles[style_name].fontName = font_bold


def _paragraph(text, style):
    from reportlab.platypus import Paragraph

    return Paragraph(html.escape(str(text)).replace("\n", "<br/>"), style)


def _xuat_pdf_bang_matplotlib(ket_qua_phan_tich, path):
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.figure import Figure

    overview = ket_qua_phan_tich.get("overview", {})
    contributors = ket_qua_phan_tich.get("contributors", [])
    ignored_commits = ket_qua_phan_tich.get("ignored_commits", [])

    with PdfPages(path) as pdf:
        fig = Figure(figsize=(8.27, 11.69))
        ax = fig.add_subplot(111)
        ax.axis("off")

        lines = [
            "Báo cáo đánh giá đóng góp contributor trên GitHub",
            "",
            f"Repository: {overview.get('repo_full_name', '')}",
            f"Số commit đã phân tích: {overview.get('analyzed_commit_count', 0)}",
            f"Điểm chất lượng trung bình: {overview.get('average_quality_score', 0):.2f}",
            f"Số commit cần xem lại: {overview.get('suspicious_commit_count', 0)}",
            f"Số commit bot đã loại: {overview.get('ignored_bot_commit_count', 0)}",
            f"Số commit tự động đã loại: {overview.get('ignored_auto_commit_count', 0)}",
            "",
            "Contributor:",
        ]
        for item in contributors:
            lines.append(
                f"- {item.get('contributor', '')}: final={_lay_score(item):.2f}, "
                f"quality={item.get('quality_score', 0):.2f}, "
                f"suspicious={item.get('suspicious_commit_count', 0)}"
            )

        lines.extend(["", "Commit bot/tu dong da loai:"])
        if ignored_commits:
            for commit in ignored_commits[:10]:
                reasons = ", ".join(commit.get("reasons", []))
                lines.append(
                    f"- {commit.get('short_sha', '')} - "
                    f"{commit.get('contributor', '')}: {commit.get('message', '')} ({reasons})"
                )
            if len(ignored_commits) > 10:
                lines.append(f"- Con {len(ignored_commits) - 10} commit khac")
        else:
            lines.append("- Khong co commit bot hoac commit tu dong bi loai.")

        ax.text(0.04, 0.96, "\n".join(lines), va="top", ha="left", fontsize=10, wrap=True)
        pdf.savefig(fig, bbox_inches="tight")

    return path


def xuat_pdf(ket_qua_phan_tich, reports_dir):
    path = tao_duong_dan_bao_cao(ket_qua_phan_tich, reports_dir, "pdf")

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError:
        return _xuat_pdf_bang_matplotlib(ket_qua_phan_tich, path)

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
    elements = []

    elements.append(Paragraph("Báo cáo đánh giá đóng góp contributor trên GitHub", styles["Title"]))
    elements.append(Spacer(1, 0.35 * cm))

    overview_lines = [
        f"Repository: {overview.get('repo_full_name', '')}",
        f"Thời gian phân tích: {overview.get('analyzed_at', '')}",
        f"Số commit đã phân tích: {overview.get('analyzed_commit_count', 0)}",
        f"Tổng contributor: {overview.get('contributor_count', 0)}",
        f"Tổng additions: {overview.get('total_additions', 0)}",
        f"Tổng deletions: {overview.get('total_deletions', 0)}",
        f"Điểm chất lượng trung bình: {overview.get('average_quality_score', 0):.2f}",
        f"Số commit cần xem lại: {overview.get('suspicious_commit_count', 0)}",
        f"Số commit bot đã loại: {overview.get('ignored_bot_commit_count', 0)}",
        f"Số commit tự động đã loại: {overview.get('ignored_auto_commit_count', 0)}",
    ]
    for line in overview_lines:
        elements.append(_paragraph(line, styles["Normal"]))

    elements.append(Spacer(1, 0.35 * cm))
    elements.append(Paragraph("Bảng contributor", styles["Heading2"]))

    table_data = [[
        "STT",
        "Contributor",
        "Commit",
        "Add",
        "Del",
        "Files",
        "Quality",
        "Penalty",
        "Suspicious",
        "Final",
        "Mức đánh giá",
    ]]
    for index, item in enumerate(contributors, start=1):
        table_data.append(
            [
                index,
                _paragraph(item.get("contributor", item.get("tac_gia", "")), styles["Normal"]),
                item.get("commit_count", 0),
                item.get("total_additions", 0),
                item.get("total_deletions", 0),
                item.get("files_changed", item.get("changed_files_count", 0)),
                f"{item.get('quality_score', 0):.2f}",
                f"{item.get('penalty_score', 0):.2f}",
                item.get("suspicious_commit_count", 0),
                f"{_lay_score(item):.2f}",
                _paragraph(item.get("contribution_level", ""), styles["Normal"]),
            ]
        )

    table = Table(
        table_data,
        colWidths=[
            0.8 * cm,
            3.1 * cm,
            1.2 * cm,
            1.4 * cm,
            1.4 * cm,
            1.2 * cm,
            1.6 * cm,
            1.4 * cm,
            1.6 * cm,
            1.4 * cm,
            4.0 * cm,
        ],
        repeatRows=1,
    )
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f5f8f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), font_bold),
                ("FONTNAME", (0, 1), (-1, -1), font_regular),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 1), (9, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elements.append(table)

    elements.append(Spacer(1, 0.35 * cm))
    elements.append(Paragraph("Commit cần xem lại", styles["Heading2"]))
    has_suspicious_commit = False
    for item in contributors:
        for commit in item.get("suspicious_commits", []):
            has_suspicious_commit = True
            reasons = "; ".join(commit.get("reasons", []))
            text = (
                f"{item.get('contributor', '')} - {commit.get('short_sha', '')}: "
                f"{commit.get('message', '')} ({reasons})"
            )
            elements.append(_paragraph(text, styles["Normal"]))

    if not has_suspicious_commit:
        elements.append(_paragraph("Không có commit đáng nghi nổi bật.", styles["Normal"]))

    elements.append(Spacer(1, 0.35 * cm))
    elements.append(Paragraph("Commit bot/tự động đã loại", styles["Heading2"]))
    if ignored_commits:
        for commit in ignored_commits:
            reasons = ", ".join(commit.get("reasons", []))
            text = (
                f"{commit.get('short_sha', '')} - {commit.get('contributor', '')}: "
                f"{commit.get('message', '')} ({reasons})"
            )
            elements.append(_paragraph(text, styles["Normal"]))
    else:
        elements.append(_paragraph("Không có commit bot hoặc commit tự động bị loại.", styles["Normal"]))

    elements.append(Spacer(1, 0.35 * cm))
    elements.append(Paragraph("Nhận xét AI rule-based", styles["Heading2"]))
    for block in ai_summary.split("\n\n"):
        elements.append(_paragraph(block, styles["Normal"]))
        elements.append(Spacer(1, 0.15 * cm))

    document.build(elements)
    return path
