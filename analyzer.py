import math
from datetime import datetime

from ai_summary import (
    tao_nhan_xet_ai_rule_based,
    tao_nhan_xet_don_gian,
    tao_tong_ket_repo,
)
from github_client import lay_danh_sach_commit_chi_tiet, lay_thong_tin_repository


def gom_commit_theo_contributor(danh_sach_commit):
    """Gom danh sach commit theo contributor."""
    ket_qua = {}

    for commit in danh_sach_commit:
        khoa_contributor = commit.get("khoa_contributor") or "Khong xac dinh"
        ten_hien_thi = commit.get("ten_hien_thi") or "Khong xac dinh"

        if khoa_contributor not in ket_qua:
            ket_qua[khoa_contributor] = {
                "ten_hien_thi": ten_hien_thi,
                "danh_sach_commit": [],
            }

        ket_qua[khoa_contributor]["danh_sach_commit"].append(commit)

    return ket_qua


def tinh_chi_so_contributor(du_lieu_gom):
    """Tinh commit, additions, deletions, files changed cho tung contributor."""
    ket_qua = []

    for khoa_contributor, du_lieu_contributor in du_lieu_gom.items():
        danh_sach_commit = du_lieu_contributor.get("danh_sach_commit", [])
        tong_additions = 0
        tong_deletions = 0
        tap_hop_file = set()

        for commit in danh_sach_commit:
            tong_additions += commit.get("additions", 0)
            tong_deletions += commit.get("deletions", 0)

            for ten_file in commit.get("changed_files", []):
                tap_hop_file.add(ten_file)

        ten_hien_thi = du_lieu_contributor.get("ten_hien_thi", "Khong xac dinh")
        total_changes = tong_additions + tong_deletions

        ket_qua.append(
            {
                "khoa_contributor": khoa_contributor,
                "ten_hien_thi": ten_hien_thi,
                "tac_gia": ten_hien_thi,
                "contributor": ten_hien_thi,
                "commit_count": len(danh_sach_commit),
                "total_additions": tong_additions,
                "total_deletions": tong_deletions,
                "additions": tong_additions,
                "deletions": tong_deletions,
                "changed_files_count": len(tap_hop_file),
                "files_changed": len(tap_hop_file),
                "total_changes": total_changes,
            }
        )

    return ket_qua


def _normalize_log_min_max(values):
    """
    Chuan hoa log1p(value) theo gia tri lon nhat ve thang 0-100.
    Cach nay giu diem cua contributor thap hon khong bi day ve 0 chi vi la
    nguoi co chi so nho nhat trong repo.
    """
    log_values = [math.log1p(max(value, 0)) for value in values]

    if not log_values:
        return []

    max_value = max(log_values)

    if max_value <= 0:
        return [0.0 for _ in values]

    return [log_value / max_value * 100 for log_value in log_values]


def _tinh_balance_score(additions, deletions):
    """
    Diem can bang additions/deletions.
    100 la rat can bang, 0 la chi nghieng ve mot phia.
    """
    total_changes = additions + deletions
    if total_changes <= 0:
        return 0.0

    imbalance = abs(additions - deletions) / total_changes
    return max(0.0, (1 - imbalance) * 100)


def tinh_diem_dong_gop_co_ban(danh_sach_thong_ke):
    """
    Tinh diem dong gop moi:
    final_score = 0.35 commit_score + 0.35 code_score
                + 0.20 file_score + 0.10 balance_score
    """
    commit_scores = _normalize_log_min_max(
        [item.get("commit_count", 0) for item in danh_sach_thong_ke]
    )
    code_scores = _normalize_log_min_max(
        [item.get("total_changes", 0) for item in danh_sach_thong_ke]
    )
    file_scores = _normalize_log_min_max(
        [item.get("changed_files_count", 0) for item in danh_sach_thong_ke]
    )

    ket_qua = []
    for index, item in enumerate(danh_sach_thong_ke):
        additions = item.get("total_additions", 0)
        deletions = item.get("total_deletions", 0)

        commit_score = commit_scores[index]
        code_score = code_scores[index]
        file_score = file_scores[index]
        balance_score = _tinh_balance_score(additions, deletions)
        final_score = (
            0.35 * commit_score
            + 0.35 * code_score
            + 0.20 * file_score
            + 0.10 * balance_score
        )
        final_score = max(0.0, min(100.0, final_score))

        thong_tin_moi = item.copy()
        thong_tin_moi.update(
            {
                "commit_score": commit_score,
                "code_score": code_score,
                "file_score": file_score,
                "balance_score": balance_score,
                "final_score": final_score,
                "score": final_score,
                "baseline_score": final_score,
            }
        )
        ket_qua.append(thong_tin_moi)

    return ket_qua


def xep_hang_contributor(danh_sach_thong_ke):
    """Sap xep contributor theo final_score giam dan."""
    return sorted(
        danh_sach_thong_ke,
        key=lambda item: item.get("final_score", item.get("score", 0)),
        reverse=True,
    )


def tao_overview(owner, repo, repo_info, so_luong_commit, danh_sach_commit, contributors):
    top_contributor = contributors[0] if contributors else {}
    tong_diem = sum(item.get("final_score", item.get("score", 0)) for item in contributors)

    return {
        "owner": owner,
        "repo": repo,
        "repo_full_name": repo_info.get("full_name", f"{owner}/{repo}"),
        "requested_commit_count": so_luong_commit,
        "analyzed_commit_count": len(danh_sach_commit),
        "contributor_count": len(contributors),
        "total_additions": sum(item.get("total_additions", 0) for item in contributors),
        "total_deletions": sum(item.get("total_deletions", 0) for item in contributors),
        "top_contributor": top_contributor.get("contributor", "Chua co"),
        "top_score": top_contributor.get("final_score", 0),
        "total_score": tong_diem,
        "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def phan_tich_commit_da_lay(owner, repo, repo_info, so_luong_commit, danh_sach_commit):
    du_lieu_gom = gom_commit_theo_contributor(danh_sach_commit)
    thong_ke = tinh_chi_so_contributor(du_lieu_gom)
    thong_ke_co_diem = tinh_diem_dong_gop_co_ban(thong_ke)
    thong_ke_xep_hang = xep_hang_contributor(thong_ke_co_diem)
    contributors = tao_nhan_xet_don_gian(thong_ke_xep_hang)

    overview = tao_overview(
        owner,
        repo,
        repo_info,
        so_luong_commit,
        danh_sach_commit,
        contributors,
    )

    ket_qua = {
        "owner": owner,
        "repo": repo,
        "repo_info": repo_info,
        "overview": overview,
        "contributors": contributors,
        "repo_summary": tao_tong_ket_repo(contributors),
    }
    ket_qua["ai_summary"] = tao_nhan_xet_ai_rule_based(ket_qua)

    return ket_qua


def phan_tich_repo(owner, repo, so_luong_commit=30, token=None, progress_callback=None):
    owner = owner.strip()
    repo = repo.strip()

    if not owner or not repo:
        raise ValueError("Owner va Repository khong duoc de trong.")

    if so_luong_commit <= 0:
        raise ValueError("So commit can phan tich phai lon hon 0.")

    if progress_callback:
        progress_callback("Dang kiem tra repository...")

    repo_info = lay_thong_tin_repository(owner, repo, token=token)

    if progress_callback:
        progress_callback("Dang lay danh sach commit...")

    danh_sach_commit = lay_danh_sach_commit_chi_tiet(
        owner,
        repo,
        so_luong=so_luong_commit,
        token=token,
        progress_callback=progress_callback,
    )

    if not danh_sach_commit:
        raise ValueError("Repository khong co commit nao de phan tich.")

    if progress_callback:
        progress_callback("Dang tinh metrics va tao nhan xet...")

    return phan_tich_commit_da_lay(
        owner,
        repo,
        repo_info,
        so_luong_commit,
        danh_sach_commit,
    )

