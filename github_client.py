import requests
import os
from dotenv import load_dotenv

# Load biến môi trường từ file .env
load_dotenv()


def tao_headers():
    """
    Tạo headers để gọi GitHub API (có token)
    """
    token = os.getenv("GITHUB_TOKEN")

    return {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }


def lay_danh_sach_commit(owner, repo, so_luong=10):
    """
    Lấy danh sách commit từ GitHub

    owner: chủ repo
    repo: tên repo
    so_luong: số commit muốn lấy
    """

    url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    params = {
        "per_page": so_luong
    }

    response = requests.get(url, headers=tao_headers(), params=params)

    # Kiểm tra lỗi
    if response.status_code != 200:
        print("Loi khi goi API:", response.status_code)
        print(response.text)
        return []

    du_lieu = response.json()

    danh_sach_commit = []

    for commit in du_lieu:
        thong_tin = {
            "sha": commit.get("sha"),
            "tac_gia": commit.get("commit", {}).get("author", {}).get("name"),
            "message": commit.get("commit", {}).get("message")
        }

        danh_sach_commit.append(thong_tin)

    return danh_sach_commit

def lay_chi_tiet_commit(owner, repo, sha):
    """
    Lấy thông tin chi tiết của một commit
    """
    url = f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}"

    response = requests.get(url, headers=tao_headers())

    if response.status_code != 200:
        print("Loi khi lay chi tiet commit:", response.status_code)
        print(response.text)
        return None

    du_lieu = response.json()

    stats = du_lieu.get("stats", {})
    files = du_lieu.get("files", [])

    danh_sach_file = []
    for file in files:
        ten_file = file.get("filename")
        if ten_file:
            danh_sach_file.append(ten_file)

    ket_qua = {
        "sha": du_lieu.get("sha"),
        "additions": stats.get("additions", 0),
        "deletions": stats.get("deletions", 0),
        "changed_files": danh_sach_file
    }

    return ket_qua

def lay_toan_bo_commit_chi_tiet(owner, repo, so_luong=5):
    """
    Lấy danh sách commit kèm thông tin chi tiết
    """
    danh_sach_commit = lay_danh_sach_commit(owner, repo, so_luong=so_luong)

    ket_qua = []

    for commit in danh_sach_commit:
        sha = commit.get("sha")
        if not sha:
            continue

        chi_tiet = lay_chi_tiet_commit(owner, repo, sha)
        if not chi_tiet:
            continue

        commit_day_du = {
            "sha": sha,
            "tac_gia": commit.get("tac_gia"),
            "message": commit.get("message"),
            "additions": chi_tiet.get("additions", 0),
            "deletions": chi_tiet.get("deletions", 0),
            "changed_files": chi_tiet.get("changed_files", [])
        }

        ket_qua.append(commit_day_du)

    return ket_qua