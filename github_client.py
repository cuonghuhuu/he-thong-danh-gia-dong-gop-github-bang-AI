import os
import time
from datetime import datetime
from urllib.parse import urlparse

import requests


TIMEOUT_GITHUB_API = 15
SO_COMMIT_TOI_DA_MOI_TRANG = 100
GITHUB_API_ACCEPT = "application/vnd.github+json"
GITHUB_USER_AGENT = "GitHub-Contribution-AI"


class GitHubAPIError(RuntimeError):
    """Loi ro nghia hon khi goi GitHub API."""

    def __init__(self, message, status_code=None, detail=None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


def tach_owner_repo_tu_chuoi(gia_tri):
    """
    Tach owner/repo tu URL GitHub, SSH URL hoac chuoi owner/repo.
    Vi du hop le:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - git@github.com:owner/repo.git
    - owner/repo
    """
    gia_tri = (gia_tri or "").strip()
    if not gia_tri:
        raise ValueError("Duong dan GitHub repository khong duoc de trong.")

    if gia_tri.startswith("git@github.com:"):
        path = gia_tri.split(":", 1)[1]
    elif "://" in gia_tri:
        parsed = urlparse(gia_tri)
        netloc = parsed.netloc.lower()
        if netloc not in {"github.com", "www.github.com"}:
            raise ValueError("Chi ho tro URL repository tren github.com.")
        path = parsed.path
    else:
        path = gia_tri

    parts = [part for part in path.strip("/").split("/") if part]
    if len(parts) < 2:
        raise ValueError("URL GitHub repository phai co dang https://github.com/owner/repo.")

    owner = parts[0].strip()
    repo = parts[1].strip()
    if repo.endswith(".git"):
        repo = repo[:-4]

    if not owner or not repo:
        raise ValueError("Khong tach duoc Owner va Repository tu duong dan da nhap.")

    return owner, repo


def chuan_hoa_owner_repo(owner="", repo="", repo_url=""):
    """
    Chuan hoa thong tin repository.
    Neu co repo_url thi uu tien repo_url. Neu repo rong va owner co dang URL
    hoac owner/repo thi tu dong tach thanh owner va repo.
    """
    owner = (owner or "").strip()
    repo = (repo or "").strip()
    repo_url = (repo_url or "").strip()

    if repo_url:
        return tach_owner_repo_tu_chuoi(repo_url)

    if not repo and owner and ("/" in owner or "github.com" in owner):
        return tach_owner_repo_tu_chuoi(owner)

    if not owner or not repo:
        raise ValueError("Owner va Repository khong duoc de trong.")

    return owner, repo


def tao_headers(token=None):
    """
    Tao headers de goi GitHub API.
    Phan biet ro:
    - token is None: lay tu bien moi truong GITHUB_TOKEN neu co.
    - token == "" hoac chi co khoang trang: co tinh khong dung token.
    """
    headers = {
        "Accept": GITHUB_API_ACCEPT,
        "User-Agent": GITHUB_USER_AGENT,
    }

    if token is None:
        token = os.getenv("GITHUB_TOKEN")

    if token is not None:
        token = token.strip()

    if not token:
        return headers

    headers["Authorization"] = f"Bearer {token}"

    return headers


def _lay_so_nguyen_an_toan(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def rut_gon_noi_dung_loi(response):
    noi_dung = response.text.strip()
    if len(noi_dung) > 300:
        noi_dung = noi_dung[:300] + "..."
    return noi_dung


def tao_thong_bao_loi_http(response, url):
    status_code = response.status_code
    noi_dung_loi = rut_gon_noi_dung_loi(response)

    if status_code == 401:
        return "GitHub Token khong hop le hoac da het hieu luc. Hay kiem tra lai token."

    if status_code == 403:
        remaining = response.headers.get("X-RateLimit-Remaining")
        reset_time = response.headers.get("X-RateLimit-Reset")

        if remaining == "0":
            try:
                reset_text = datetime.fromtimestamp(int(reset_time)).strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            except (TypeError, ValueError):
                reset_text = "khong ro thoi gian"

            return f"GitHub API da bi gioi han request. Co the thu lai sau: {reset_text}."

        return (
            "GitHub API tu choi truy cap. Token co the thieu quyen, "
            "repository rieng tu, hoac request bi chan tam thoi."
        )

    if status_code == 404:
        return (
            "Khong tim thay repository hoac ban khong co quyen truy cap. "
            "Hay kiem tra Owner, Repository va Token."
        )

    if status_code == 409:
        return "Repository khong co commit nao de phan tich."

    if status_code == 422:
        return "Tham so Owner/Repository khong hop le hoac repository khong co du lieu phu hop."

    return (
        f"GitHub API tra ve loi {status_code}. URL: {url}. "
        f"Noi dung: {noi_dung_loi}"
    )


def goi_github_api_json(url, token=None, params=None):
    """
    Goi GitHub API va tra ve JSON.
    Neu co loi mang, HTTP hoac parse JSON thi raise GitHubAPIError.
    """
    try:
        response = requests.get(
            url,
            headers=tao_headers(token),
            params=params,
            timeout=TIMEOUT_GITHUB_API,
        )
    except requests.Timeout as exc:
        raise GitHubAPIError(
            "Ket noi GitHub API qua cham. Hay kiem tra internet roi thu lai."
        ) from exc
    except requests.ConnectionError as exc:
        raise GitHubAPIError(
            "Khong co internet hoac khong ket noi duoc toi GitHub API."
        ) from exc
    except requests.RequestException as exc:
        raise GitHubAPIError(f"Khong the ket noi GitHub API. Loi: {exc}") from exc

    if response.status_code != 200:
        raise GitHubAPIError(
            tao_thong_bao_loi_http(response, url),
            status_code=response.status_code,
            detail=rut_gon_noi_dung_loi(response),
        )

    try:
        return response.json()
    except ValueError as exc:
        raise GitHubAPIError(f"GitHub API khong tra ve JSON hop le. URL: {url}") from exc


def lay_thong_tin_repository(owner, repo, token=None):
    url = f"https://api.github.com/repos/{owner}/{repo}"
    du_lieu = goi_github_api_json(url, token=token)
    return {
        "id": du_lieu.get("id"),
        "name": du_lieu.get("name", repo),
        "full_name": du_lieu.get("full_name", f"{owner}/{repo}"),
        "default_branch": du_lieu.get("default_branch", ""),
        "private": du_lieu.get("private", False),
    }


def lay_thong_tin_contributor(commit):
    """
    Tach khoa contributor noi bo va ten hien thi.
    Uu tien GitHub login, fallback sang ten tac gia trong commit.
    """
    thong_tin_author = commit.get("author") or {}
    thong_tin_commit_author = commit.get("commit", {}).get("author", {}) or {}

    login = thong_tin_author.get("login")
    ten_commit_author = thong_tin_commit_author.get("name")

    khoa_contributor = login or ten_commit_author or "Khong xac dinh"
    ten_hien_thi = login or ten_commit_author or "Khong xac dinh"

    return khoa_contributor, ten_hien_thi


def lay_danh_sach_commit(owner, repo, so_luong=30, token=None):
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
            token=token,
            params={"per_page": so_commit_tren_trang, "page": trang_hien_tai},
        )

        if not du_lieu:
            break

        for commit in du_lieu:
            khoa_contributor, ten_hien_thi = lay_thong_tin_contributor(commit)
            danh_sach_commit.append(
                {
                    "sha": commit.get("sha"),
                    "khoa_contributor": khoa_contributor,
                    "ten_hien_thi": ten_hien_thi,
                    "message": commit.get("commit", {}).get("message", ""),
                }
            )

        if len(du_lieu) < so_commit_tren_trang:
            break

        trang_hien_tai += 1

    return danh_sach_commit[:so_luong]


def lay_chi_tiet_commit(owner, repo, sha, token=None):
    """Lay thong tin chi tiet cua mot commit."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    du_lieu = goi_github_api_json(url, token=token)

    stats = du_lieu.get("stats", {}) or {}
    files = du_lieu.get("files", []) or []

    danh_sach_file = []
    for file_info in files:
        ten_file = file_info.get("filename")
        if ten_file:
            danh_sach_file.append(ten_file)

    return {
        "sha": du_lieu.get("sha"),
        "additions": _lay_so_nguyen_an_toan(stats.get("additions", 0)),
        "deletions": _lay_so_nguyen_an_toan(stats.get("deletions", 0)),
        "changed_files": danh_sach_file,
    }


def lay_danh_sach_commit_chi_tiet(
    owner,
    repo,
    so_luong=30,
    token=None,
    progress_callback=None,
):
    """Lay danh sach commit kem additions, deletions va changed files."""
    danh_sach_commit = lay_danh_sach_commit(owner, repo, so_luong=so_luong, token=token)
    ket_qua = []
    tong_commit = len(danh_sach_commit)

    for index, commit in enumerate(danh_sach_commit, start=1):
        sha = commit.get("sha")
        if not sha:
            continue

        if progress_callback:
            progress_callback(f"Dang lay chi tiet commit {index}/{tong_commit}...")

        chi_tiet = lay_chi_tiet_commit(owner, repo, sha, token=token)
        ket_qua.append(
            {
                "sha": sha,
                "khoa_contributor": commit.get("khoa_contributor", "Khong xac dinh"),
                "ten_hien_thi": commit.get("ten_hien_thi", "Khong xac dinh"),
                "message": commit.get("message", ""),
                "additions": chi_tiet.get("additions", 0),
                "deletions": chi_tiet.get("deletions", 0),
                "changed_files": chi_tiet.get("changed_files", []),
            }
        )

        time.sleep(0.03)

    return ket_qua


def lay_toan_bo_commit_chi_tiet(owner, repo, so_luong=30, token=None):
    """
    Ham cu de giu tuong thich.
    Thuc te ham nay chi lay danh sach commit theo so_luong.
    """
    return lay_danh_sach_commit_chi_tiet(owner, repo, so_luong=so_luong, token=token)

