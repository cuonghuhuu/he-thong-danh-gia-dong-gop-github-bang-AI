import os

import requests


TIMEOUT_GITHUB_API = 10
SO_COMMIT_TOI_DA_MOI_TRANG = 100
GITHUB_API_ACCEPT = "application/vnd.github.v3+json"


def tao_headers():
    """
    Tao headers de goi GitHub API.
    Chi them Authorization khi thuc su co token.
    """
    headers = {
        "Accept": GITHUB_API_ACCEPT
    }

    token = os.getenv("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"token {token}"

    return headers


def goi_github_api_json(url, params=None):
    """
    Goi GitHub API va tra ve JSON.
    Neu co loi mang, loi HTTP hoac loi parse JSON thi raise RuntimeError.
    """
    try:
        response = requests.get(
            url,
            headers=tao_headers(),
            params=params,
            timeout=TIMEOUT_GITHUB_API
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Khong the ket noi GitHub API. URL: {url}. Loi: {exc}"
        ) from exc

    if response.status_code != 200:
        noi_dung_loi = response.text.strip()
        if len(noi_dung_loi) > 300:
            noi_dung_loi = noi_dung_loi[:300] + "..."

        raise RuntimeError(
            "GitHub API tra ve loi "
            f"{response.status_code}. URL: {url}. Noi dung: {noi_dung_loi}"
        )

    try:
        return response.json()
    except ValueError as exc:
        raise RuntimeError(
            f"GitHub API khong tra ve JSON hop le. URL: {url}"
        ) from exc


def lay_thong_tin_contributor(commit):
    """
    Tach khoa contributor noi bo va ten hien thi.

    - khoa_contributor uu tien author.login
    - fallback sang ten tac gia trong commit
    - neu khong co du lieu thi dung 'Khong xac dinh'
    """
    thong_tin_author = commit.get("author") or {}
    thong_tin_commit_author = commit.get("commit", {}).get("author", {}) or {}

    login = thong_tin_author.get("login")
    ten_commit_author = thong_tin_commit_author.get("name")

    khoa_contributor = login or ten_commit_author or "Khong xac dinh"
    ten_hien_thi = ten_commit_author or login or "Khong xac dinh"

    return khoa_contributor, ten_hien_thi


def lay_danh_sach_commit(owner, repo, so_luong=30):
    """
    Lay mot phan danh sach commit tu GitHub theo so_luong.
    Ham nay khong co y nghia la lay toan bo lich su commit.
    """
    if so_luong <= 0:
        return []

    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    danh_sach_commit = []
    trang_hien_tai = 1

    while len(danh_sach_commit) < so_luong:
        so_commit_con_lai = so_luong - len(danh_sach_commit)
        so_commit_tren_trang = min(SO_COMMIT_TOI_DA_MOI_TRANG, so_commit_con_lai)

        du_lieu = goi_github_api_json(
            url,
            params={
                "per_page": so_commit_tren_trang,
                "page": trang_hien_tai
            }
        )

        if not du_lieu:
            break

        for commit in du_lieu:
            khoa_contributor, ten_hien_thi = lay_thong_tin_contributor(commit)

            thong_tin = {
                "sha": commit.get("sha"),
                "khoa_contributor": khoa_contributor,
                "ten_hien_thi": ten_hien_thi,
                "message": commit.get("commit", {}).get("message")
            }
            danh_sach_commit.append(thong_tin)

        if len(du_lieu) < so_commit_tren_trang:
            break

        trang_hien_tai += 1

    return danh_sach_commit[:so_luong]


def lay_chi_tiet_commit(owner, repo, sha):
    """
    Lay thong tin chi tiet cua mot commit.
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    du_lieu = goi_github_api_json(url)

    stats = du_lieu.get("stats", {})
    files = du_lieu.get("files", [])

    danh_sach_file = []
    for file in files:
        ten_file = file.get("filename")
        if ten_file:
            danh_sach_file.append(ten_file)

    return {
        "sha": du_lieu.get("sha"),
        "additions": stats.get("additions", 0),
        "deletions": stats.get("deletions", 0),
        "changed_files": danh_sach_file
    }


def lay_danh_sach_commit_chi_tiet(owner, repo, so_luong=30):
    """
    Lay danh sach commit kem thong tin chi tiet theo so_luong.
    """
    danh_sach_commit = lay_danh_sach_commit(owner, repo, so_luong=so_luong)
    ket_qua = []

    for commit in danh_sach_commit:
        sha = commit.get("sha")
        if not sha:
            continue

        chi_tiet = lay_chi_tiet_commit(owner, repo, sha)

        commit_day_du = {
            "sha": sha,
            "khoa_contributor": commit.get("khoa_contributor", "Khong xac dinh"),
            "ten_hien_thi": commit.get("ten_hien_thi", "Khong xac dinh"),
            "message": commit.get("message"),
            "additions": chi_tiet.get("additions", 0),
            "deletions": chi_tiet.get("deletions", 0),
            "changed_files": chi_tiet.get("changed_files", [])
        }
        ket_qua.append(commit_day_du)

    return ket_qua


def lay_toan_bo_commit_chi_tiet(owner, repo, so_luong=30):
    """
    Ham cu de giu tuong thich.
    Thuc te ham nay chi lay danh sach commit theo so_luong.
    """
    return lay_danh_sach_commit_chi_tiet(owner, repo, so_luong=so_luong)
