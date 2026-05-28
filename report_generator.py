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


def tao_bang_markdown(contributors):
    headers = [
        "STT",
        "Contributor",
        "Số commit",
        "Additions",
        "Deletions",
        "Files changed",
        "Total changes",
        "Commit score",
        "Code score",
        "File score",
        "Balance score",
        "Final score",
        "Mức đóng góp",
        "Loại đóng góp",
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
            str(item.get("total_changes", 0)),
            f"{item.get('commit_score', 0):.2f}",
            f"{item.get('code_score', 0):.2f}",
            f"{item.get('file_score', 0):.2f}",
            f"{item.get('balance_score', 0):.2f}",
            f"{_lay_score(item):.2f}",
            str(item.get("contribution_level", "")),
            str(item.get("contribution_type", "")),
            str(item.get("ai_summary", "")),
        ]
        lines.append("| " + " | ".join(_markdown_cell(value) for value in row) + " |")

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
    ai_summary = ket_qua_phan_tich.get("ai_summary", "")

    noi_dung = [
        "# Báo cáo đóng góp contributor trên GitHub",
        "",
        "## Tổng quan",
        "",
        f"- Repository: {overview.get('repo_full_name', '')}",
        f"- Thời gian phân tích: {overview.get('analyzed_at', '')}",
        f"- Số commit đã phân tích: {overview.get('analyzed_commit_count', 0)}",
        f"- Tổng contributor: {overview.get('contributor_count', 0)}",
        f"- Tổng additions: {overview.get('total_additions', 0)}",
        f"- Tổng deletions: {overview.get('total_deletions', 0)}",
        f"- Contributor điểm cao nhất: {overview.get('top_contributor', 'Chưa có')}",
        f"- Tổng điểm: {overview.get('total_score', 0):.2f}",
        "",
        "## Công thức điểm",
        "",
        "final_score = 0.35 * commit_score + 0.35 * code_score + 0.20 * file_score + 0.10 * balance_score",
        "",
        "## Bảng contributor",
        "",
        tao_bang_markdown(contributors),
        "",
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
                "Số commit",
                "Additions",
                "Deletions",
                "Files changed",
                "Total changes",
                "Commit score",
                "Code score",
                "File score",
                "Balance score",
                "Final score",
                "Mức đóng góp",
                "Loại đóng góp",
                "Nhận xét",
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
                    item.get("total_changes", 0),
                    f"{item.get('commit_score', 0):.2f}",
                    f"{item.get('code_score', 0):.2f}",
                    f"{item.get('file_score', 0):.2f}",
                    f"{item.get('balance_score', 0):.2f}",
                    f"{_lay_score(item):.2f}",
                    item.get("contribution_level", ""),
                    item.get("contribution_type", ""),
                    item.get("ai_summary", ""),
                ]
            )

    return path


def _xuat_pdf_bang_matplotlib(ket_qua_phan_tich, path):
    from matplotlib.backends.backend_pdf import PdfPages
    from matplotlib.figure import Figure

    overview = ket_qua_phan_tich.get("overview", {})
    contributors = ket_qua_phan_tich.get("contributors", [])
    ai_summary = ket_qua_phan_tich.get("ai_summary", "")

    with PdfPages(path) as pdf:
        fig = Figure(figsize=(8.27, 11.69))
        ax = fig.add_subplot(111)
        ax.axis("off")

        lines = [
            "Báo cáo đóng góp contributor trên GitHub",
            "",
            f"Repository: {overview.get('repo_full_name', '')}",
            f"Thời gian phân tích: {overview.get('analyzed_at', '')}",
            f"Số commit đã phân tích: {overview.get('analyzed_commit_count', 0)}",
            f"Tổng contributor: {overview.get('contributor_count', 0)}",
            f"Tổng additions: {overview.get('total_additions', 0)}",
            f"Tổng deletions: {overview.get('total_deletions', 0)}",
            f"Contributor điểm cao nhất: {overview.get('top_contributor', 'Chưa có')}",
            "",
            "Công thức điểm:",
            "final_score = 0.35 commit_score + 0.35 code_score + 0.20 file_score + 0.10 balance_score",
            "",
            "Nhận xét AI rule-based:",
            ai_summary,
        ]
        ax.text(0.04, 0.96, "\n".join(lines), va="top", ha="left", fontsize=10, wrap=True)
        pdf.savefig(fig, bbox_inches="tight")

        headers = ["STT", "Contributor", "Commit", "Add", "Del", "Files", "Final", "Mức", "Loại"]
        chunk_size = 25
        for start in range(0, len(contributors), chunk_size):
            fig = Figure(figsize=(11.69, 8.27))
            ax = fig.add_subplot(111)
            ax.axis("off")

            chunk = contributors[start : start + chunk_size]
            table_rows = []
            for index, item in enumerate(chunk, start=start + 1):
                table_rows.append(
                    [
                        index,
                        item.get("contributor", item.get("tac_gia", "")),
                        item.get("commit_count", 0),
                        item.get("total_additions", 0),
                        item.get("total_deletions", 0),
                        item.get("files_changed", item.get("changed_files_count", 0)),
                        f"{_lay_score(item):.2f}",
                        item.get("contribution_level", ""),
                        item.get("contribution_type", ""),
                    ]
                )

            table = ax.table(cellText=table_rows, colLabels=headers, loc="center")
            table.auto_set_font_size(False)
            table.set_fontsize(7)
            table.scale(1, 1.3)
            ax.set_title("Bảng contributor", fontsize=12, pad=16)
            pdf.savefig(fig, bbox_inches="tight")

    return path


def _dang_ky_font_pdf_tieng_viet():
    """
    ReportLab font mac dinh khong ho tro tot tieng Viet co dau.
    Dung DejaVu Sans di kem matplotlib de PDF xuat ra on dinh tren nhieu may.
    """
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


def xuat_pdf(ket_qua_phan_tich, reports_dir):
    path = tao_duong_dan_bao_cao(ket_qua_phan_tich, reports_dir, "pdf")

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
    except ImportError:
        return _xuat_pdf_bang_matplotlib(ket_qua_phan_tich, path)

    overview = ket_qua_phan_tich.get("overview", {})
    contributors = ket_qua_phan_tich.get("contributors", [])
    ai_summary = ket_qua_phan_tich.get("ai_summary", "")

    document = SimpleDocTemplate(
        str(path),
        pagesize=A4,
        rightMargin=1.2 * cm,
        leftMargin=1.2 * cm,
        topMargin=1.2 * cm,
        bottomMargin=1.2 * cm,
    )
    styles = getSampleStyleSheet()
    font_regular, font_bold = _dang_ky_font_pdf_tieng_viet()
    _cap_nhat_font_styles(styles, font_regular, font_bold)
    elements = []

    elements.append(Paragraph("Báo cáo đóng góp contributor trên GitHub", styles["Title"]))
    elements.append(Spacer(1, 0.4 * cm))

    overview_lines = [
        f"Repository: {overview.get('repo_full_name', '')}",
        f"Thời gian phân tích: {overview.get('analyzed_at', '')}",
        f"Số commit đã phân tích: {overview.get('analyzed_commit_count', 0)}",
        f"Tổng contributor: {overview.get('contributor_count', 0)}",
        f"Tổng additions: {overview.get('total_additions', 0)}",
        f"Tổng deletions: {overview.get('total_deletions', 0)}",
        f"Contributor điểm cao nhất: {overview.get('top_contributor', 'Chưa có')}",
    ]
    for line in overview_lines:
        elements.append(_paragraph(line, styles["Normal"]))

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph("Bảng contributor", styles["Heading2"]))

    table_data = [["STT", "Contributor", "Commit", "Add", "Del", "Files", "Final", "Mức", "Loại"]]
    for index, item in enumerate(contributors, start=1):
        table_data.append(
            [
                index,
                _paragraph(item.get("contributor", item.get("tac_gia", "")), styles["Normal"]),
                item.get("commit_count", 0),
                item.get("total_additions", 0),
                item.get("total_deletions", 0),
                item.get("files_changed", item.get("changed_files_count", 0)),
                f"{_lay_score(item):.2f}",
                _paragraph(item.get("contribution_level", ""), styles["Normal"]),
                _paragraph(item.get("contribution_type", ""), styles["Normal"]),
            ]
        )

    table = Table(
        table_data,
        colWidths=[0.8 * cm, 3.0 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.2 * cm, 1.4 * cm, 2.5 * cm, 3.2 * cm],
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
                ("ALIGN", (2, 1), (6, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elements.append(table)

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph("Nhận xét AI rule-based", styles["Heading2"]))
    for block in ai_summary.split("\n\n"):
        elements.append(_paragraph(block, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * cm))

    document.build(elements)
    return path

