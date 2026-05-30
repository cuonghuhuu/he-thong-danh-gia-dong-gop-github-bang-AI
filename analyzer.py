import math
import re
import unicodedata
from datetime import datetime
from pathlib import PurePosixPath

from ai_summary import (
    tao_nhan_xet_ai_rule_based,
    tao_nhan_xet_don_gian,
    tao_tong_ket_repo,
)
from github_client import lay_danh_sach_commit_chi_tiet, lay_thong_tin_repository
from github_client import normalize_contributor


SOURCE_CODE_EXTENSIONS = {
    ".py",
    ".ui",
    ".qss",
    ".toml",
    ".yaml",
    ".yml",
    ".json",
    ".ini",
}
SOURCE_CODE_FILENAMES = {
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
}
DOC_REPORT_EXTENSIONS = {".md", ".rst", ".txt"}
DOC_REPORT_FILENAMES = {"readme.md", "report.md"}
DOC_REPORT_PREFIXES = ("docs/", "reports/")
LOCAL_GENERATED_PREFIXES = (
    ".idea/",
    ".venv/",
    "venv/",
    "env/",
    "__pycache__/",
    ".pytest_cache/",
    ".mypy_cache/",
)
LOCAL_GENERATED_EXTENSIONS = {
    ".pyc",
    ".pyo",
    ".sqlite3",
    ".db",
    ".log",
    ".tmp",
}
LOCAL_GENERATED_FILENAMES = {
    ".env",
    ".env.local",
    "analysis_history.sqlite3",
}

SUSPICIOUS_EXACT_MESSAGES = {
    "test",
    "update",
    "abc",
    "ok",
    "nop",
    "final",
    "sua",
    "fix",
    "backup",
    "tmp",
    "demo",
    "hehe",
    "hihi",
}
SUSPICIOUS_PHRASES = {
    "auto update report": "commit tự động cập nhật báo cáo",
    "linh tinh": "commit message không nghiêm túc",
    "nop bai": "message không mô tả thay đổi kỹ thuật",
    "nop": "message quá chung chung",
    "backup": "commit dạng backup, khó đánh giá nội dung",
    "tmp": "commit tạm thời",
    "demo": "commit demo, cần mô tả rõ hơn",
    "hehe": "commit message không nghiêm túc",
    "hihi": "commit message không nghiêm túc",
}
GOOD_ACTION_WORDS = {
    "add",
    "fix",
    "handle",
    "refactor",
    "improve",
    "update",
    "create",
    "implement",
    "remove",
    "validate",
    "support",
    "export",
}
TECHNICAL_WORDS = {
    "github",
    "token",
    "api",
    "error",
    "ui",
    "database",
    "report",
    "chart",
    "commit",
    "quality",
    "score",
    "handler",
    "validation",
}


def _clamp(value, min_value=0.0, max_value=100.0):
    return max(min_value, min(max_value, value))


def _normalize_text(text):
    text = (text or "").strip().lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"[^a-z0-9_./ -]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def _first_line(message):
    return (message or "").strip().splitlines()[0].strip() if (message or "").strip() else ""


def _short_sha(sha):
    return (sha or "")[:7]


def _file_name(path):
    return PurePosixPath((path or "").replace("\\", "/")).name.lower()


def phan_loai_file(path):
    """Phan loai file de tinh diem tac dong code."""
    normalized_path = (path or "").replace("\\", "/").strip()
    lower_path = normalized_path.lower()
    filename = _file_name(lower_path)
    suffix = PurePosixPath(lower_path).suffix.lower()

    if (
        lower_path.startswith(LOCAL_GENERATED_PREFIXES)
        or suffix in LOCAL_GENERATED_EXTENSIONS
        or filename in LOCAL_GENERATED_FILENAMES
    ):
        return "generated"

    if suffix in SOURCE_CODE_EXTENSIONS or filename in SOURCE_CODE_FILENAMES:
        return "source"

    if (
        lower_path.startswith(DOC_REPORT_PREFIXES)
        or filename in DOC_REPORT_FILENAMES
        or suffix in DOC_REPORT_EXTENSIONS
    ):
        return "document"

    return "other"


def _dem_dong_logic(files_detail):
    logic_patterns = (
        "def ",
        "class ",
        "try:",
        "except ",
        "if ",
        "elif ",
        "for ",
        "while ",
        "return ",
        "raise ",
        "with ",
    )
    logic_count = 0
    changed_line_count = 0
    non_empty_changed_line_count = 0

    for file_info in files_detail:
        if phan_loai_file(file_info.get("filename", "")) != "source":
            continue

        patch = file_info.get("patch", "") or ""
        for line in patch.splitlines():
            if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
                continue

            changed_line_count += 1
            content = line[1:].strip()
            if content:
                non_empty_changed_line_count += 1

            if line.startswith("+") and any(pattern in content for pattern in logic_patterns):
                logic_count += 1

    return logic_count, changed_line_count, non_empty_changed_line_count


def _thong_ke_file_commit(commit):
    files_detail = commit.get("files_detail") or []
    if not files_detail:
        files_detail = [
            {
                "filename": filename,
                "additions": 0,
                "deletions": 0,
                "changes": 0,
                "patch": "",
            }
            for filename in commit.get("changed_files", [])
        ]

    stats = {
        "source_files": set(),
        "document_files": set(),
        "generated_files": set(),
        "other_files": set(),
        "source_changes": 0,
        "document_changes": 0,
        "generated_changes": 0,
        "other_changes": 0,
    }

    for file_info in files_detail:
        filename = file_info.get("filename", "")
        file_type = phan_loai_file(filename)
        changes = file_info.get("changes")
        if changes is None:
            changes = file_info.get("additions", 0) + file_info.get("deletions", 0)
        changes = max(int(changes or 0), 0)

        if file_type == "source":
            stats["source_files"].add(filename)
            stats["source_changes"] += changes
        elif file_type == "document":
            stats["document_files"].add(filename)
            stats["document_changes"] += changes
        elif file_type == "generated":
            stats["generated_files"].add(filename)
            stats["generated_changes"] += changes
        else:
            stats["other_files"].add(filename)
            stats["other_changes"] += changes

    return stats


def danh_gia_commit_message(message):
    """Cham diem message theo rule mem, khong phat tuyet doi chu 'fix'."""
    first_line = _first_line(message)
    normalized = _normalize_text(first_line)
    words = normalized.split()
    reasons = []

    if not normalized:
        return 10.0, ["commit message trống"]

    score = 70.0
    word_count = len(words)
    has_good_action = any(word in GOOD_ACTION_WORDS for word in words)
    has_technical_word = any(word in TECHNICAL_WORDS for word in words)

    if normalized in SUSPICIOUS_EXACT_MESSAGES:
        score = 25.0
        reasons.append("commit message quá chung chung")
    elif word_count <= 2:
        score = 45.0
        reasons.append("commit message quá ngắn")

    for phrase, reason in SUSPICIOUS_PHRASES.items():
        if phrase in normalized:
            score = min(score, 35.0)
            if reason not in reasons:
                reasons.append(reason)

    # "fix" don le la yeu, nhung "Fix GitHub token handling" la ro nghia.
    if "fix" in words and word_count >= 4 and has_technical_word:
        score = max(score, 82.0)
        reasons = [reason for reason in reasons if reason != "commit message quá chung chung"]

    if word_count >= 5 and has_good_action:
        score += 10
    if word_count >= 4 and has_technical_word:
        score += 8
    if len(first_line) > 72:
        score -= 6
        reasons.append("commit message hơi dài, nên viết gọn hơn")

    return _clamp(score), reasons


def danh_gia_y_nghia_thay_doi(commit, file_stats):
    additions = max(commit.get("additions", 0), 0)
    deletions = max(commit.get("deletions", 0), 0)
    total_changes = additions + deletions
    files_detail = commit.get("files_detail") or []
    logic_count, changed_lines, non_empty_changed_lines = _dem_dong_logic(files_detail)
    reasons = []

    if total_changes <= 0:
        score = 10.0
        reasons.append("commit không có thay đổi additions/deletions đáng kể")
    elif total_changes <= 2:
        score = 30.0
        reasons.append("thay đổi quá nhỏ")
    elif total_changes <= 10:
        score = 52.0
    elif total_changes <= 200:
        score = 72.0
    else:
        score = 82.0

    if file_stats["source_files"]:
        score += 10
    if logic_count > 0:
        score += min(12, logic_count * 3)
    if file_stats["document_files"] and not file_stats["source_files"]:
        score -= 18
        reasons.append("commit chủ yếu sửa tài liệu/báo cáo")
    if file_stats["generated_files"]:
        score -= 25
        reasons.append("commit có sửa file môi trường hoặc file tự động sinh")
    if changed_lines > 0 and non_empty_changed_lines == 0:
        score = min(score, 25.0)
        reasons.append("thay đổi chủ yếu là khoảng trắng hoặc dòng trống")

    return _clamp(score), reasons


def danh_gia_tac_dong_code(file_stats):
    reasons = []
    source_count = len(file_stats["source_files"])
    doc_count = len(file_stats["document_files"])
    generated_count = len(file_stats["generated_files"])
    other_count = len(file_stats["other_files"])

    if source_count:
        score = 70.0 + min(25.0, source_count * 6)
    elif doc_count and not generated_count:
        score = 38.0
        reasons.append("commit thiên về tài liệu/báo cáo")
    elif generated_count and not source_count:
        score = 12.0
        reasons.append("commit chủ yếu sửa file rác/môi trường local")
    elif other_count:
        score = 45.0
    else:
        score = 20.0
        reasons.append("không xác định được file thay đổi")

    if generated_count:
        score -= min(25.0, generated_count * 8)
        if "commit có sửa file rác/môi trường local" not in reasons:
            reasons.append("commit có sửa file rác/môi trường local")

    return _clamp(score), reasons


def danh_gia_chat_luong_commit(commit):
    """Tra ve diem chat luong va ly do commit dang nghi neu co."""
    file_stats = _thong_ke_file_commit(commit)
    message_score, message_reasons = danh_gia_commit_message(commit.get("message", ""))
    meaningful_score, meaningful_reasons = danh_gia_y_nghia_thay_doi(commit, file_stats)
    code_impact_score, code_reasons = danh_gia_tac_dong_code(file_stats)

    suspicious_reasons = []
    suspicious_reasons.extend(message_reasons)
    suspicious_reasons.extend(meaningful_reasons)
    suspicious_reasons.extend(code_reasons)

    penalty = 0.0
    if message_score < 50:
        penalty += 8
    if meaningful_score < 45:
        penalty += 6
    if code_impact_score < 35:
        penalty += 8
    if file_stats["generated_files"]:
        penalty += 8
    if file_stats["document_files"] and not file_stats["source_files"]:
        penalty += 4

    quality_score = (
        0.40 * message_score
        + 0.30 * meaningful_score
        + 0.30 * code_impact_score
    )
    quality_score = _clamp(quality_score)
    penalty = _clamp(penalty, 0, 25)
    is_suspicious = bool(suspicious_reasons) or penalty >= 10

    return {
        "sha": commit.get("sha", ""),
        "short_sha": _short_sha(commit.get("sha", "")),
        "message": _first_line(commit.get("message", "")),
        "commit_message_score": message_score,
        "meaningful_change_score": meaningful_score,
        "code_impact_score": code_impact_score,
        "quality_score": quality_score,
        "penalty_score": penalty,
        "is_suspicious": is_suspicious,
        "suspicious_reasons": list(dict.fromkeys(suspicious_reasons)),
        "source_file_count": len(file_stats["source_files"]),
        "document_file_count": len(file_stats["document_files"]),
        "generated_file_count": len(file_stats["generated_files"]),
        "source_changes": file_stats["source_changes"],
        "document_changes": file_stats["document_changes"],
        "generated_changes": file_stats["generated_changes"],
        "other_changes": file_stats["other_changes"],
    }


def loc_commit_duoc_tinh_diem(danh_sach_commit):
    """Loai commit bot/tu dong khoi tap du lieu cham diem chinh."""
    commits_duoc_tinh = []
    ignored_commits = []
    ignored_bot_commit_count = 0
    ignored_auto_commit_count = 0

    for commit in danh_sach_commit:
        contributor = normalize_contributor(commit)
        commit_moi = commit.copy()
        for key in (
            "khoa_contributor",
            "ten_hien_thi",
            "github_login",
            "author_name",
            "author_email",
            "committer_login",
            "committer_name",
            "committer_email",
        ):
            if contributor.get(key):
                commit_moi[key] = contributor[key]

        if contributor.get("message") and not commit_moi.get("message"):
            commit_moi["message"] = contributor["message"]

        is_bot = bool(commit.get("is_bot") or contributor.get("is_bot"))
        is_auto_commit = bool(
            commit.get("is_auto_commit") or contributor.get("is_auto_commit")
        )

        ignored_reasons = []
        if is_bot:
            ignored_bot_commit_count += 1
            ignored_reasons.append("bot")
        if is_auto_commit:
            ignored_auto_commit_count += 1
            ignored_reasons.append("auto_commit")

        commit_moi["is_bot"] = is_bot
        commit_moi["is_auto_commit"] = is_auto_commit
        commit_moi["is_ignored"] = bool(ignored_reasons)
        commit_moi["ignored_reasons"] = ignored_reasons

        if ignored_reasons:
            ignored_commits.append(
                {
                    "sha": commit_moi.get("sha", ""),
                    "short_sha": _short_sha(commit_moi.get("sha", "")),
                    "contributor": commit_moi.get("ten_hien_thi", ""),
                    "message": _first_line(commit_moi.get("message", "")),
                    "reasons": ignored_reasons,
                }
            )
            continue

        commits_duoc_tinh.append(commit_moi)

    return commits_duoc_tinh, {
        "ignored_bot_commit_count": ignored_bot_commit_count,
        "ignored_auto_commit_count": ignored_auto_commit_count,
        "ignored_commit_count": len(ignored_commits),
        "ignored_commits": ignored_commits,
    }


def gom_commit_theo_contributor(danh_sach_commit):
    """Gom danh sach commit theo contributor."""
    ket_qua = {}

    for commit in danh_sach_commit:
        contributor = normalize_contributor(commit)
        khoa_contributor = (
            contributor.get("khoa_contributor")
            or commit.get("khoa_contributor")
            or "Khong xac dinh"
        )
        ten_hien_thi = (
            contributor.get("ten_hien_thi")
            or commit.get("ten_hien_thi")
            or "Khong xac dinh"
        )

        if khoa_contributor not in ket_qua:
            ket_qua[khoa_contributor] = {
                "ten_hien_thi": ten_hien_thi,
                "danh_sach_commit": [],
            }

        ket_qua[khoa_contributor]["danh_sach_commit"].append(commit)

    return ket_qua


def tinh_chi_so_contributor(du_lieu_gom):
    """Tinh metrics va metrics chat luong cho tung contributor."""
    ket_qua = []

    for khoa_contributor, du_lieu_contributor in du_lieu_gom.items():
        danh_sach_commit = du_lieu_contributor.get("danh_sach_commit", [])
        tong_additions = 0
        tong_deletions = 0
        tap_hop_file = set()
        quality_items = []
        suspicious_commits = []
        source_files = set()
        document_files = set()
        generated_files = set()
        source_changes = 0
        document_changes = 0
        generated_changes = 0

        for commit in danh_sach_commit:
            tong_additions += commit.get("additions", 0)
            tong_deletions += commit.get("deletions", 0)

            for ten_file in commit.get("changed_files", []):
                tap_hop_file.add(ten_file)
                file_type = phan_loai_file(ten_file)
                if file_type == "source":
                    source_files.add(ten_file)
                elif file_type == "document":
                    document_files.add(ten_file)
                elif file_type == "generated":
                    generated_files.add(ten_file)

            quality_item = danh_gia_chat_luong_commit(commit)
            quality_items.append(quality_item)
            source_changes += quality_item.get("source_changes", 0)
            document_changes += quality_item.get("document_changes", 0)
            generated_changes += quality_item.get("generated_changes", 0)

            if quality_item.get("is_suspicious"):
                suspicious_commits.append(
                    {
                        "sha": quality_item.get("sha", ""),
                        "short_sha": quality_item.get("short_sha", ""),
                        "message": quality_item.get("message", ""),
                        "reasons": quality_item.get("suspicious_reasons", []),
                    }
                )

        commit_count = len(danh_sach_commit)
        ten_hien_thi = du_lieu_contributor.get("ten_hien_thi", "Khong xac dinh")
        total_changes = tong_additions + tong_deletions
        suspicious_commit_count = len(suspicious_commits)
        suspicious_commit_ratio = suspicious_commit_count / commit_count if commit_count else 0

        def avg(key):
            if not quality_items:
                return 0.0
            return sum(item.get(key, 0) for item in quality_items) / len(quality_items)

        raw_penalty = avg("penalty_score") + suspicious_commit_ratio * 12
        file_impact_raw = source_changes + 0.35 * document_changes + 0.15 * generated_changes

        ket_qua.append(
            {
                "khoa_contributor": khoa_contributor,
                "ten_hien_thi": ten_hien_thi,
                "tac_gia": ten_hien_thi,
                "contributor": ten_hien_thi,
                "commit_count": commit_count,
                "total_additions": tong_additions,
                "total_deletions": tong_deletions,
                "additions": tong_additions,
                "deletions": tong_deletions,
                "changed_files_count": len(tap_hop_file),
                "files_changed": len(tap_hop_file),
                "total_changes": total_changes,
                "source_file_count": len(source_files),
                "document_file_count": len(document_files),
                "generated_file_count": len(generated_files),
                "source_changes": source_changes,
                "document_changes": document_changes,
                "generated_changes": generated_changes,
                "file_impact_raw": file_impact_raw,
                "commit_quality_items": quality_items,
                "suspicious_commits": suspicious_commits,
                "suspicious_commit_count": suspicious_commit_count,
                "suspicious_commit_ratio": suspicious_commit_ratio,
                "commit_message_score": avg("commit_message_score"),
                "meaningful_change_score": avg("meaningful_change_score"),
                "code_impact_score": avg("code_impact_score"),
                "quality_score": avg("quality_score"),
                "penalty_score": _clamp(raw_penalty, 0, 30),
            }
        )

    return ket_qua


def _normalize_log_max(values, cap=None):
    effective_values = []
    for value in values:
        value = max(value or 0, 0)
        if cap is not None:
            value = min(value, cap)
        effective_values.append(value)

    log_values = [math.log1p(value) for value in effective_values]
    if not log_values:
        return []

    max_value = max(log_values)
    if max_value <= 0:
        return [0.0 for _ in values]

    return [log_value / max_value * 100 for log_value in log_values]


def _tinh_consistency_score(item):
    commits = item.get("commit_quality_items", [])
    commit_count = item.get("commit_count", 0)
    total_changes = item.get("total_changes", 0)

    if commit_count <= 0 or total_changes <= 0:
        return 0.0

    if commit_count == 1:
        return 42.0 if item.get("quality_score", 0) >= 70 else 30.0

    changes_per_commit = []
    for commit_quality in commits:
        source = commit_quality.get("source_changes", 0)
        document = commit_quality.get("document_changes", 0)
        generated = commit_quality.get("generated_changes", 0)
        changes_per_commit.append(source + document + generated)

    max_commit_changes = max(changes_per_commit) if changes_per_commit else total_changes
    dominance_ratio = max_commit_changes / total_changes if total_changes else 1
    spread_score = (1 - dominance_ratio) * 100
    count_bonus = min(25, commit_count * 5)
    quality_bonus = min(15, item.get("quality_score", 0) * 0.15)

    return _clamp(spread_score + count_bonus + quality_bonus)


def tinh_diem_dong_gop_co_ban(danh_sach_thong_ke):
    """
    Tinh diem dong gop theo cong thuc moi:
    final_score = 0.20 commit_score + 0.20 code_volume_score
                + 0.20 file_impact_score + 0.25 quality_score
                + 0.15 consistency_score - penalty_score
    """
    commit_scores = _normalize_log_max(
        [item.get("commit_count", 0) for item in danh_sach_thong_ke]
    )
    code_volume_scores = _normalize_log_max(
        [item.get("total_changes", 0) for item in danh_sach_thong_ke],
        cap=2500,
    )
    file_impact_scores = _normalize_log_max(
        [item.get("file_impact_raw", 0) for item in danh_sach_thong_ke],
        cap=2500,
    )

    ket_qua = []
    for index, item in enumerate(danh_sach_thong_ke):
        commit_score = commit_scores[index]
        code_volume_score = code_volume_scores[index]
        file_impact_score = file_impact_scores[index]
        quality_score = item.get("quality_score", 0)
        consistency_score = _tinh_consistency_score(item)
        penalty_score = item.get("penalty_score", 0)

        final_score = (
            0.20 * commit_score
            + 0.20 * code_volume_score
            + 0.20 * file_impact_score
            + 0.25 * quality_score
            + 0.15 * consistency_score
            - penalty_score
        )
        final_score = _clamp(final_score)

        thong_tin_moi = item.copy()
        thong_tin_moi.update(
            {
                "commit_score": commit_score,
                "code_volume_score": code_volume_score,
                "code_score": code_volume_score,
                "file_impact_score": file_impact_score,
                "file_score": file_impact_score,
                "consistency_score": consistency_score,
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


def tao_overview(
    owner,
    repo,
    repo_info,
    so_luong_commit,
    danh_sach_commit,
    contributors,
    ignored_stats=None,
):
    ignored_stats = ignored_stats or {}
    top_contributor = contributors[0] if contributors else {}
    tong_diem = sum(item.get("final_score", item.get("score", 0)) for item in contributors)
    average_quality_score = (
        sum(item.get("quality_score", 0) for item in contributors) / len(contributors)
        if contributors
        else 0
    )
    suspicious_commit_count = sum(
        item.get("suspicious_commit_count", 0) for item in contributors
    )

    return {
        "owner": owner,
        "repo": repo,
        "repo_full_name": repo_info.get("full_name", f"{owner}/{repo}"),
        "requested_commit_count": so_luong_commit,
        "analyzed_commit_count": len(danh_sach_commit),
        "ignored_commit_count": ignored_stats.get("ignored_commit_count", 0),
        "ignored_bot_commit_count": ignored_stats.get("ignored_bot_commit_count", 0),
        "ignored_auto_commit_count": ignored_stats.get("ignored_auto_commit_count", 0),
        "contributor_count": len(contributors),
        "total_additions": sum(item.get("total_additions", 0) for item in contributors),
        "total_deletions": sum(item.get("total_deletions", 0) for item in contributors),
        "top_contributor": top_contributor.get("contributor", "Chưa có"),
        "top_score": top_contributor.get("final_score", 0),
        "total_score": tong_diem,
        "average_quality_score": average_quality_score,
        "suspicious_commit_count": suspicious_commit_count,
        "analyzed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }


def phan_tich_commit_da_lay(owner, repo, repo_info, so_luong_commit, danh_sach_commit):
    danh_sach_commit_duoc_tinh, ignored_stats = loc_commit_duoc_tinh_diem(danh_sach_commit)
    du_lieu_gom = gom_commit_theo_contributor(danh_sach_commit_duoc_tinh)
    thong_ke = tinh_chi_so_contributor(du_lieu_gom)
    thong_ke_co_diem = tinh_diem_dong_gop_co_ban(thong_ke)
    thong_ke_xep_hang = xep_hang_contributor(thong_ke_co_diem)
    contributors = tao_nhan_xet_don_gian(thong_ke_xep_hang)

    overview = tao_overview(
        owner,
        repo,
        repo_info,
        so_luong_commit,
        danh_sach_commit_duoc_tinh,
        contributors,
        ignored_stats,
    )

    ket_qua = {
        "owner": owner,
        "repo": repo,
        "repo_info": repo_info,
        "overview": overview,
        "contributors": contributors,
        "ignored_commit_count": ignored_stats.get("ignored_commit_count", 0),
        "ignored_bot_commit_count": ignored_stats.get("ignored_bot_commit_count", 0),
        "ignored_auto_commit_count": ignored_stats.get("ignored_auto_commit_count", 0),
        "ignored_commits": ignored_stats.get("ignored_commits", []),
        "repo_summary": tao_tong_ket_repo(contributors),
    }
    ket_qua["ai_summary"] = tao_nhan_xet_ai_rule_based(ket_qua)

    return ket_qua


def phan_tich_repo(owner, repo, so_luong_commit=30, token=None, progress_callback=None):
    owner = owner.strip()
    repo = repo.strip()

    if not owner or not repo:
        raise ValueError("Owner và Repository không được để trống.")

    if so_luong_commit <= 0:
        raise ValueError("Số commit cần phân tích phải lớn hơn 0.")

    if progress_callback:
        progress_callback("Đang kiểm tra repository...")

    repo_info = lay_thong_tin_repository(owner, repo, token=token)

    if progress_callback:
        progress_callback("Đang lấy danh sách commit...")

    danh_sach_commit = lay_danh_sach_commit_chi_tiet(
        owner,
        repo,
        so_luong=so_luong_commit,
        token=token,
        progress_callback=progress_callback,
    )

    if not danh_sach_commit:
        raise ValueError("Repository không có commit nào để phân tích.")

    if progress_callback:
        progress_callback("Đang tính điểm chất lượng và tạo nhận xét...")

    return phan_tich_commit_da_lay(
        owner,
        repo,
        repo_info,
        so_luong_commit,
        danh_sach_commit,
    )
