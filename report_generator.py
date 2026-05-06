import csv
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


def tao_bang_markdown(contributors):
    headers = [
        "STT",
        "Contributor",
        "So commit",
        "Additions",
        "Deletions",
        "Files changed",
        "Total changes",
        "Commit score",
        "Code score",
        "File score",
        "Balance score",
        "Final score",
        "Loai dong gop",
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
            str(item.get("contribution_type", "")),
        ]
        lines.append("| " + " | ".join(row) + " |")

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
        "# Bao cao dong gop contributor tren GitHub",
        "",
        "## Tong quan",
        "",
        f"- Repository: {overview.get('repo_full_name', '')}",
        f"- Thoi gian phan tich: {overview.get('analyzed_at', '')}",
        f"- So commit da phan tich: {overview.get('analyzed_commit_count', 0)}",
        f"- Tong contributor: {overview.get('contributor_count', 0)}",
        f"- Tong additions: {overview.get('total_additions', 0)}",
        f"- Tong deletions: {overview.get('total_deletions', 0)}",
        f"- Contributor diem cao nhat: {overview.get('top_contributor', 'Chua co')}",
        f"- Tong diem: {overview.get('total_score', 0):.2f}",
        "",
        "## Cong thuc diem",
        "",
        "final_score = 0.35 * commit_score + 0.35 * code_score + 0.2 * file_score + 0.1 * balance_score",
        "",
        "## Bang contributor",
        "",
        tao_bang_markdown(contributors),
        "",
        "## Nhan xet AI rule-based",
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
                "So commit",
                "Additions",
                "Deletions",
                "Files changed",
                "Total changes",
                "Commit score",
                "Code score",
                "File score",
                "Balance score",
                "Final score",
                "Loai dong gop",
                "Nhan xet",
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
            "Bao cao dong gop contributor tren GitHub",
            "",
            f"Repository: {overview.get('repo_full_name', '')}",
            f"Thoi gian phan tich: {overview.get('analyzed_at', '')}",
            f"So commit da phan tich: {overview.get('analyzed_commit_count', 0)}",
            f"Tong contributor: {overview.get('contributor_count', 0)}",
            f"Tong additions: {overview.get('total_additions', 0)}",
            f"Tong deletions: {overview.get('total_deletions', 0)}",
            f"Contributor diem cao nhat: {overview.get('top_contributor', 'Chua co')}",
            "",
            "Cong thuc diem:",
            "final_score = 0.35 commit_score + 0.35 code_score + 0.2 file_score + 0.1 balance_score",
            "",
            "Nhan xet AI rule-based:",
            ai_summary,
        ]
        ax.text(0.04, 0.96, "\n".join(lines), va="top", ha="left", fontsize=10, wrap=True)
        pdf.savefig(fig, bbox_inches="tight")

        headers = ["STT", "Contributor", "Commit", "Add", "Del", "Files", "Final", "Loai"]
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
                        item.get("contribution_type", ""),
                    ]
                )

            table = ax.table(cellText=table_rows, colLabels=headers, loc="center")
            table.auto_set_font_size(False)
            table.set_fontsize(7)
            table.scale(1, 1.3)
            ax.set_title("Bang contributor", fontsize=12, pad=16)
            pdf.savefig(fig, bbox_inches="tight")

    return path


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
    elements = []

    elements.append(Paragraph("Bao cao dong gop contributor tren GitHub", styles["Title"]))
    elements.append(Spacer(1, 0.4 * cm))

    overview_lines = [
        f"Repository: {overview.get('repo_full_name', '')}",
        f"Thoi gian phan tich: {overview.get('analyzed_at', '')}",
        f"So commit da phan tich: {overview.get('analyzed_commit_count', 0)}",
        f"Tong contributor: {overview.get('contributor_count', 0)}",
        f"Tong additions: {overview.get('total_additions', 0)}",
        f"Tong deletions: {overview.get('total_deletions', 0)}",
        f"Contributor diem cao nhat: {overview.get('top_contributor', 'Chua co')}",
    ]
    for line in overview_lines:
        elements.append(Paragraph(line, styles["Normal"]))

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph("Bang contributor", styles["Heading2"]))

    table_data = [["STT", "Contributor", "Commit", "Add", "Del", "Files", "Final", "Loai"]]
    for index, item in enumerate(contributors, start=1):
        table_data.append(
            [
                index,
                item.get("contributor", item.get("tac_gia", "")),
                item.get("commit_count", 0),
                item.get("total_additions", 0),
                item.get("total_deletions", 0),
                item.get("files_changed", item.get("changed_files_count", 0)),
                f"{_lay_score(item):.2f}",
                item.get("contribution_type", ""),
            ]
        )

    table = Table(table_data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2f5f8f")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("ALIGN", (0, 0), (0, -1), "CENTER"),
                ("ALIGN", (2, 1), (-2, -1), "RIGHT"),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    elements.append(table)

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(Paragraph("Nhan xet AI rule-based", styles["Heading2"]))
    for block in ai_summary.split("\n\n"):
        elements.append(Paragraph(block.replace("\n", "<br/>"), styles["Normal"]))
        elements.append(Spacer(1, 0.2 * cm))

    document.build(elements)
    return path

