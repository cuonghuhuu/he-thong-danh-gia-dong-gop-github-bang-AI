import os

from dotenv import load_dotenv

from ai_summary import tao_nhan_xet_don_gian, tao_tong_ket_repo
from analyzer import (
    gom_commit_theo_contributor,
    tinh_chi_so_contributor,
    tinh_diem_dong_gop_co_ban,
    xep_hang_contributor
)
from github_client import lay_danh_sach_commit_chi_tiet
from report_generator import tao_bao_cao_markdown


DEFAULT_SO_LUONG_COMMIT = 30
TEN_FILE_BAO_CAO = "report.md"


def lay_thong_tin_repo():
    """
    Lay thong tin repo theo 2 che do:
    - Local: nhap tu ban phim khi chua co env
    - CI: doc tu bien moi truong
    """
    owner = os.getenv("REPO_OWNER", "").strip()
    repo = os.getenv("REPO_NAME", "").strip()

    if owner and repo:
        return owner, repo

    print("Khong tim thay REPO_OWNER va REPO_NAME trong moi truong.")

    if not owner:
        owner = input("Nhap REPO_OWNER: ").strip()

    if not repo:
        repo = input("Nhap REPO_NAME: ").strip()

    return owner, repo


def lay_so_luong_commit():
    """
    Lay so luong commit can phan tich tu bien moi truong.
    Neu du lieu khong hop le thi dung gia tri mac dinh.
    """
    gia_tri = os.getenv("SO_LUONG_COMMIT", "").strip()

    if not gia_tri:
        return DEFAULT_SO_LUONG_COMMIT

    try:
        so_luong = int(gia_tri)
    except ValueError:
        print(
            "SO_LUONG_COMMIT khong hop le. "
            f"Su dung gia tri mac dinh {DEFAULT_SO_LUONG_COMMIT}."
        )
        return DEFAULT_SO_LUONG_COMMIT

    if so_luong <= 0:
        print(
            "SO_LUONG_COMMIT phai lon hon 0. "
            f"Su dung gia tri mac dinh {DEFAULT_SO_LUONG_COMMIT}."
        )
        return DEFAULT_SO_LUONG_COMMIT

    return so_luong


def phan_tich_repo_va_tao_bao_cao(owner, repo, so_luong_commit):
    """
    Chay business flow chinh va tra ve noi dung bao cao Markdown.
    """
    danh_sach_commit = lay_danh_sach_commit_chi_tiet(
        owner,
        repo,
        so_luong=so_luong_commit
    )
    du_lieu_gom = gom_commit_theo_contributor(danh_sach_commit)
    thong_ke = tinh_chi_so_contributor(du_lieu_gom)
    thong_ke_co_diem = tinh_diem_dong_gop_co_ban(thong_ke)
    thong_ke_xep_hang = xep_hang_contributor(thong_ke_co_diem)
    thong_ke_co_nhan_xet = tao_nhan_xet_don_gian(thong_ke_xep_hang)
    tong_ket_repo = tao_tong_ket_repo(thong_ke_co_nhan_xet)

    return tao_bao_cao_markdown(thong_ke_co_nhan_xet, tong_ket_repo)


def in_noi_dung_bao_cao(noi_dung_bao_cao):
    """
    In bao cao ra man hinh neu console ho tro.
    Tren mot so may Windows, print Unicode co the gay crash.
    """
    try:
        print(noi_dung_bao_cao)
    except UnicodeEncodeError:
        print("Bao cao da duoc ghi vao report.md. Console hien tai khong ho tro day du Unicode.")


def main():
    load_dotenv()

    owner, repo = lay_thong_tin_repo()
    so_luong_commit = lay_so_luong_commit()

    try:
        noi_dung_bao_cao = phan_tich_repo_va_tao_bao_cao(
            owner,
            repo,
            so_luong_commit
        )
    except RuntimeError as exc:
        print(f"Loi khi phan tich repository: {exc}")
        return

    with open(TEN_FILE_BAO_CAO, "w", encoding="utf-8") as f:
        f.write(noi_dung_bao_cao)

    print(f"Da tao file {TEN_FILE_BAO_CAO}")
    in_noi_dung_bao_cao(noi_dung_bao_cao)


if __name__ == "__main__":
    main()
