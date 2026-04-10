from github_client import lay_toan_bo_commit_chi_tiet
from ai_summary import tao_nhan_xet_don_gian
from analyzer import (
    gom_commit_theo_contributor,
    tinh_chi_so_contributor,
    tinh_diem_dong_gop_co_ban,
    xep_hang_contributor
)
from report_generator import tao_bao_cao_markdown
from dotenv import load_dotenv
import os

load_dotenv()


def main():
    owner = os.getenv("REPO_OWNER")
    repo = os.getenv("REPO_NAME")

    danh_sach_commit = lay_toan_bo_commit_chi_tiet(owner, repo, so_luong=5)
    du_lieu_gom = gom_commit_theo_contributor(danh_sach_commit)
    thong_ke = tinh_chi_so_contributor(du_lieu_gom)
    thong_ke = tinh_diem_dong_gop_co_ban(thong_ke)
    thong_ke = xep_hang_contributor(thong_ke)
    thong_ke = tao_nhan_xet_don_gian(thong_ke)

    noi_dung_bao_cao = tao_bao_cao_markdown(thong_ke)

    with open("report.md", "w", encoding="utf-8") as f:
        f.write(noi_dung_bao_cao)

    print("Da tao file report.md")

    print(noi_dung_bao_cao)


if __name__ == "__main__":
    main()
