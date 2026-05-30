import os
import re
import time
import unicodedata
from datetime import datetime
from urllib.parse import urlparse

import requests


TIMEOUT_GITHUB_API = 15
SO_COMMIT_TOI_DA_MOI_TRANG = 100
GITHUB_API_ACCEPT = "application/vnd.github+json"
GITHUB_USER_AGENT = "GitHub-Contribution-AI"

CONTRIBUTOR_ALIASES = {
    "le van cuong": "cuonghuhuu",
    "cuonghuhuu": "cuonghuhuu",
    "ngoc linh": "ngoclinh205",
    "ngoclinh205": "ngoclinh205",
}
BOT_CONTRIBUTORS = {
    "actions-user",
    "github-actions[bot]",
    "dependabot[bot]",
}
AUTO_COMMIT_MESSAGE_PHRASES = (
    "auto update report",
    "automatic report",
    "generated report",
)


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


def _lay_dict_an_toan(value):
    return value if isinstance(value, dict) else {}


def _lay_list_an_toan(value):
    return value if isinstance(value, list) else []


def _normalize_identity_text(value):
    value = (value or "").strip().lower()
    value = unicodedata.normalize("NFD", value)
    value = "".join(ch for ch in value if unicodedata.category(ch) != "Mn")
    value = re.sub(r"[^a-z0-9_./@+\-\[\] ]+", " ", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def _identity_candidates(value):
    normalized = _normalize_identity_text(value)
    if not normalized:
        return set()

    candidates = {normalized}
    if normalized in CONTRIBUTOR_ALIASES:
        candidates.add(CONTRIBUTOR_ALIASES[normalized])

    if "@" in normalized:
        local_part = normalized.split("@", 1)[0]
        candidates.add(local_part)
        if "+" in local_part:
            candidates.add(local_part.rsplit("+", 1)[-1])

    return {candidate for candidate in candidates if candidate}


def _la_github_login_hop_le(login):
    normalized = _normalize_identity_text(login)
    if not normalized:
        return False

    return normalized not in {"khong xac dinh", "unknown", "none", "null"}


def _canonicalize_identity(value):
    candidates = _identity_candidates(value)
    for candidate in candidates:
        if candidate in CONTRIBUTOR_ALIASES:
            return CONTRIBUTOR_ALIASES[candidate]

    normalized = _normalize_identity_text(value)
    return CONTRIBUTOR_ALIASES.get(normalized, normalized)


def _lay_alias_da_biet(*values):
    for value in values:
        for candidate in _identity_candidates(value):
            if candidate in CONTRIBUTOR_ALIASES:
                return CONTRIBUTOR_ALIASES[candidate]
    return ""


def _la_bot_identity(*values):
    for value in values:
        for candidate in _identity_candidates(value):
            if candidate in BOT_CONTRIBUTORS or candidate.endswith("[bot]"):
                return True
    return False


def la_commit_tu_dong(message):
    normalized_message = _normalize_identity_text(message)
    return any(phrase in normalized_message for phrase in AUTO_COMMIT_MESSAGE_PHRASES)


def _lay_thong_tin_identity_raw(commit):
    commit_info = _lay_dict_an_toan(commit.get("commit"))
    commit_author = _lay_dict_an_toan(commit_info.get("author"))
    commit_committer = _lay_dict_an_toan(commit_info.get("committer"))
    github_author = _lay_dict_an_toan(commit.get("author"))
    github_committer = _lay_dict_an_toan(commit.get("committer"))

    return {
        "github_login": (
            commit.get("github_login")
            or commit.get("author_login")
            or github_author.get("login")
            or ""
        ),
        "committer_login": (
            commit.get("committer_login")
            or github_committer.get("login")
            or ""
        ),
        "author_name": (
            commit.get("author_name")
            or commit_author.get("name")
            or commit.get("ten_hien_thi")
            or commit.get("khoa_contributor")
            or ""
        ),
        "author_email": (
            commit.get("author_email")
            or commit_author.get("email")
            or ""
        ),
        "committer_name": (
            commit.get("committer_name")
            or commit_committer.get("name")
            or ""
        ),
        "committer_email": (
            commit.get("committer_email")
            or commit_committer.get("email")
            or ""
        ),
        "message": commit.get("message") or commit_info.get("message") or "",
    }


def _tao_files_detail(files):
    danh_sach_file = []
    files_detail = []

    for file_info in _lay_list_an_toan(files):
        if not isinstance(file_info, dict):
            continue

        ten_file = file_info.get("filename")
        if not ten_file:
            continue

        danh_sach_file.append(ten_file)
        files_detail.append(
            {
                "filename": ten_file,
                "status": file_info.get("status", "") or "",
                "additions": _lay_so_nguyen_an_toan(file_info.get("additions", 0)),
                "deletions": _lay_so_nguyen_an_toan(file_info.get("deletions", 0)),
                "changes": _lay_so_nguyen_an_toan(file_info.get("changes", 0)),
                "patch": file_info.get("patch", "") or "",
            }
        )

    return danh_sach_file, files_detail


def _tao_commit_day_du(commit, chi_tiet=None):
    """
    Tao dict commit on dinh tu response list/detail cua GitHub.
    GitHub co the tra null cho author/committer khi email khong lien ket account.
    """
    commit = _lay_dict_an_toan(commit)
    chi_tiet = _lay_dict_an_toan(chi_tiet)
    nguon = chi_tiet or commit

    contributor = normalize_contributor(nguon)
    stats = _lay_dict_an_toan(nguon.get("stats"))
    changed_files, files_detail = _tao_files_detail(nguon.get("files"))

    return {
        "sha": nguon.get("sha") or commit.get("sha"),
        "khoa_contributor": contributor["khoa_contributor"],
        "ten_hien_thi": contributor["ten_hien_thi"],
        "github_login": contributor["github_login"],
        "author_login": contributor["github_login"],
        "author_name": contributor["author_name"],
        "author_email": contributor["author_email"],
        "committer_login": contributor["committer_login"],
        "committer_name": contributor["committer_name"],
        "committer_email": contributor["committer_email"],
        "message": contributor["message"],
        "additions": _lay_so_nguyen_an_toan(stats.get("additions", 0)),
        "deletions": _lay_so_nguyen_an_toan(stats.get("deletions", 0)),
        "changed_files": changed_files,
        "changed_files_count": len(changed_files),
        "files_detail": files_detail,
        "is_bot": contributor["is_bot"],
        "is_auto_commit": contributor["is_auto_commit"],
        "is_ignored": contributor["is_ignored"],
        "ignored_reasons": contributor["ignored_reasons"],
    }


def normalize_contributor(commit):
    """
    Chuan hoa contributor cho mot commit.
    Uu tien GitHub author login, sau do den email/name trong commit va alias da biet.
    """
    raw = _lay_thong_tin_identity_raw(commit)

    github_login = raw["github_login"]
    author_email = raw["author_email"]
    author_name = raw["author_name"]
    committer_login = raw["committer_login"]
    committer_email = raw["committer_email"]
    committer_name = raw["committer_name"]
    alias_da_biet = _lay_alias_da_biet(
        author_name,
        author_email,
        committer_name,
        committer_email,
    )

    if _la_github_login_hop_le(github_login):
        khoa_contributor = _canonicalize_identity(github_login)
        ten_hien_thi = khoa_contributor
    elif alias_da_biet:
        khoa_contributor = alias_da_biet
        ten_hien_thi = alias_da_biet
    elif author_email:
        khoa_contributor = _canonicalize_identity(author_email)
        ten_hien_thi = (
            khoa_contributor
            if khoa_contributor != _normalize_identity_text(author_email)
            else author_name or author_email
        )
    elif author_name:
        khoa_contributor = _canonicalize_identity(author_name)
        ten_hien_thi = khoa_contributor
    elif _la_github_login_hop_le(committer_login):
        khoa_contributor = _canonicalize_identity(committer_login)
        ten_hien_thi = khoa_contributor
    elif committer_email:
        khoa_contributor = _canonicalize_identity(committer_email)
        ten_hien_thi = (
            khoa_contributor
            if khoa_contributor != _normalize_identity_text(committer_email)
            else committer_name or committer_email
        )
    elif committer_name:
        khoa_contributor = _canonicalize_identity(committer_name)
        ten_hien_thi = khoa_contributor
    else:
        khoa_contributor = "Khong xac dinh"
        ten_hien_thi = "Khong xac dinh"

    is_bot = _la_bot_identity(
        github_login,
        author_name,
        author_email,
        committer_login,
        committer_name,
        committer_email,
        khoa_contributor,
    )
    is_auto_commit = la_commit_tu_dong(raw["message"])

    ignored_reasons = []
    if is_bot:
        ignored_reasons.append("bot")
    if is_auto_commit:
        ignored_reasons.append("auto_commit")

    return {
        "khoa_contributor": khoa_contributor,
        "ten_hien_thi": ten_hien_thi,
        "github_login": github_login,
        "author_name": author_name,
        "author_email": author_email,
        "committer_login": committer_login,
        "committer_name": committer_name,
        "committer_email": committer_email,
        "message": raw["message"],
        "is_bot": is_bot,
        "is_auto_commit": is_auto_commit,
        "is_ignored": bool(ignored_reasons),
        "ignored_reasons": ignored_reasons,
    }


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
    Uu tien GitHub login, fallback sang email/name va alias da biet.
    """
    contributor = normalize_contributor(commit)
    return contributor["khoa_contributor"], contributor["ten_hien_thi"]


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
            danh_sach_commit.append(_tao_commit_day_du(commit))

        if len(du_lieu) < so_commit_tren_trang:
            break

        trang_hien_tai += 1

    return danh_sach_commit[:so_luong]


def lay_chi_tiet_commit(owner, repo, sha, token=None):
    """Lay thong tin chi tiet cua mot commit."""
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"
    du_lieu = goi_github_api_json(url, token=token)
    return _tao_commit_day_du(du_lieu)


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

        metadata = {
            "sha": sha,
            "khoa_contributor": commit.get("khoa_contributor", "Khong xac dinh"),
            "ten_hien_thi": commit.get("ten_hien_thi", "Khong xac dinh"),
            "github_login": commit.get("github_login", ""),
            "author_login": commit.get("author_login", commit.get("github_login", "")),
            "author_name": commit.get("author_name", ""),
            "author_email": commit.get("author_email", ""),
            "committer_login": commit.get("committer_login", ""),
            "committer_name": commit.get("committer_name", ""),
            "committer_email": commit.get("committer_email", ""),
            "message": commit.get("message", ""),
            "is_bot": bool(commit.get("is_bot", False)),
            "is_auto_commit": bool(commit.get("is_auto_commit", False)),
            "is_ignored": bool(commit.get("is_ignored", False)),
            "ignored_reasons": commit.get("ignored_reasons", []),
        }

        if metadata["is_ignored"]:
            ket_qua.append(
                {
                    **metadata,
                    "additions": 0,
                    "deletions": 0,
                    "changed_files": [],
                    "files_detail": [],
                }
            )
            continue

        if progress_callback:
            progress_callback(f"Dang lay chi tiet commit {index}/{tong_commit}...")

        chi_tiet = lay_chi_tiet_commit(owner, repo, sha, token=token)
        metadata.update(
            {
                "khoa_contributor": chi_tiet.get(
                    "khoa_contributor", metadata["khoa_contributor"]
                ),
                "ten_hien_thi": chi_tiet.get("ten_hien_thi", metadata["ten_hien_thi"]),
                "github_login": chi_tiet.get("github_login", metadata["github_login"]),
                "author_login": chi_tiet.get("author_login", metadata["author_login"]),
                "author_name": chi_tiet.get("author_name", metadata["author_name"]),
                "author_email": chi_tiet.get("author_email", metadata["author_email"]),
                "committer_login": chi_tiet.get(
                    "committer_login", metadata["committer_login"]
                ),
                "committer_name": chi_tiet.get(
                    "committer_name", metadata["committer_name"]
                ),
                "committer_email": chi_tiet.get(
                    "committer_email", metadata["committer_email"]
                ),
                "message": chi_tiet.get("message", metadata["message"]),
                "is_bot": bool(chi_tiet.get("is_bot", metadata["is_bot"])),
                "is_auto_commit": bool(
                    chi_tiet.get("is_auto_commit", metadata["is_auto_commit"])
                ),
                "is_ignored": bool(chi_tiet.get("is_ignored", metadata["is_ignored"])),
                "ignored_reasons": chi_tiet.get(
                    "ignored_reasons", metadata["ignored_reasons"]
                ),
            }
        )
        ket_qua.append(
            {
                **metadata,
                "additions": chi_tiet.get("additions", 0),
                "deletions": chi_tiet.get("deletions", 0),
                "changed_files": chi_tiet.get("changed_files", []),
                "changed_files_count": chi_tiet.get("changed_files_count", 0),
                "files_detail": chi_tiet.get("files_detail", []),
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

