import os
import sys
from pathlib import Path

from dotenv import load_dotenv

from analyzer import phan_tich_repo
from report_generator import tao_bao_cao_markdown


DEFAULT_SO_LUONG_COMMIT = 30
TEN_FILE_BAO_CAO_CI = "report.md"


def lay_so_luong_commit_tu_env():
    try:
        so_luong = int(os.getenv("SO_LUONG_COMMIT", str(DEFAULT_SO_LUONG_COMMIT)))
    except ValueError:
        return DEFAULT_SO_LUONG_COMMIT

    return so_luong if so_luong > 0 else DEFAULT_SO_LUONG_COMMIT


def chay_cli():
    """
    Giu flow terminal cho GitHub Actions hoac khi can chay nhanh bang --cli.
    Chay app.py binh thuong tren may local van mo giao dien PyQt6.
    """
    owner = os.getenv("REPO_OWNER", "").strip()
    repo = os.getenv("REPO_NAME", "").strip()
    token = os.getenv("GITHUB_TOKEN", "").strip()
    so_luong_commit = lay_so_luong_commit_tu_env()

    if not owner:
        owner = input("Nhap REPO_OWNER: ").strip()

    if not repo:
        repo = input("Nhap REPO_NAME: ").strip()

    ket_qua = phan_tich_repo(owner, repo, so_luong_commit=so_luong_commit, token=token)
    noi_dung_bao_cao = tao_bao_cao_markdown(ket_qua)

    report_path = Path(__file__).resolve().parent / TEN_FILE_BAO_CAO_CI
    report_path.write_text(noi_dung_bao_cao, encoding="utf-8")
    print(f"Da tao file {report_path}")


def chay_gui():
    from PyQt6.QtWidgets import QApplication

    from main_window import MainWindow

    app = QApplication(sys.argv)
    app.setApplicationName("GitHub AI Contributor Analyzer")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())


def main():
    project_dir = Path(__file__).resolve().parent
    load_dotenv(project_dir / ".env")

    if "--cli" in sys.argv or os.getenv("GITHUB_ACTIONS", "").lower() == "true":
        chay_cli()
        return

    chay_gui()


if __name__ == "__main__":
    main()
