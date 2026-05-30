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
    ".toml",
}
SOURCE_CODE_FILENAMES = {
    "requirements.txt",
    "pyproject.toml",
    "setup.py",
}
UI_CONFIG_EXTENSIONS = {
    ".ui",
    ".qss",
    ".json",
    ".yaml",
    ".yml",
    ".ini",
}
DOC_REPORT_EXTENSIONS = {".md", ".rst", ".txt"}
DOC_REPORT_FILENAMES = {"readme.md", "report.md"}
DOC_REPORT_PREFIXES = ("docs/",)
LOCAL_GENERATED_PREFIXES = (
    ".idea/",
    ".venv/",
    "venv/",
    "env/",
    "reports/",
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
    "optimize",
    "document",
    "validate",
    "support",
    "export",
}
TECHNICAL_WORDS = {
    "ai",
    "summary",
    "dashboard",
    "analyzer",
    "github",
    "client",
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
    "readme",
    "dependency",
    "dependencies",
    "structure",
}
INTEGRATION_WORDS = {
    "merge",
    "integrate",
    "integration",
    "resolve",
    "conflict",
    "connect",
    "combine",
    "structure",
}


def _clamp(value, min_value=0.0, max_value=100.0):
    return max(min_value, min(max_value, value))


def quy_doi_diem_hien_thi(score_100):
    """Quy doi diem noi bo 0-100 sang diem hien thi /10."""
    try:
        score_100 = float(score_100)
    except (TypeError, ValueError):
        score_100 = 0.0

    display_score = round(_clamp(score_100) / 10, 1)
    return display_score


def quy_doi_diem_tru_hien_thi(penalty_score, max_internal=30.0):
    """Chuan hoa penalty noi bo thanh muc diem tru 0-10 de hien thi."""
    try:
        penalty_score = float(penalty_score)
    except (TypeError, ValueError):
        penalty_score = 0.0

    max_internal = max(float(max_internal or 1), 1.0)
    return round(_clamp(penalty_score, 0, max_internal) / max_internal * 10, 1)


def _xac_dinh_muc_do_nghi_ngo(penalty_score, reasons=None):
    reasons = reasons or []
    penalty_score = _clamp(penalty_score, 0, 25)
    if penalty_score >= 18 or len(reasons) >= 3:
        return "Cao"
    if penalty_score >= 10 or len(reasons) >= 2:
        return "Trung bình"
    return "Thấp"


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


def classify_file(path):
    """Phan loai file theo muc do anh huong de cham diem cong bang hon."""
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
        return "core"

    if suffix in UI_CONFIG_EXTENSIONS:
        return "ui_config"

    if (
        lower_path.startswith(DOC_REPORT_PREFIXES)
        or filename in DOC_REPORT_FILENAMES
        or suffix in DOC_REPORT_EXTENSIONS
    ):
        return "document"

    return "other"


def phan_loai_file(path):
    """Ham cu giu tuong thich voi cac phan code/report dang dung."""
    file_type = classify_file(path)
    if file_type in {"core", "ui_config"}:
        return "source"
    return file_type


def _file_impact_weight(file_type):
    return {
        "core": 1.0,
        "ui_config": 0.75,
        "document": 0.38,
        "other": 0.45,
        "generated": 0.05,
    }.get(file_type, 0.35)


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
        "core_files": set(),
        "ui_config_files": set(),
        "source_files": set(),
        "document_files": set(),
        "generated_files": set(),
        "other_files": set(),
        "core_changes": 0,
        "ui_config_changes": 0,
        "source_changes": 0,
        "document_changes": 0,
        "generated_changes": 0,
        "other_changes": 0,
        "file_impact_raw": 0.0,
    }

    for file_info in files_detail:
        filename = file_info.get("filename", "")
        file_type = classify_file(filename)
        changes = file_info.get("changes")
        if changes is None:
            changes = file_info.get("additions", 0) + file_info.get("deletions", 0)
        changes = max(int(changes or 0), 0)
        stats["file_impact_raw"] += changes * _file_impact_weight(file_type)

        if file_type == "core":
            stats["core_files"].add(filename)
            stats["source_files"].add(filename)
            stats["core_changes"] += changes
            stats["source_changes"] += changes
        elif file_type == "ui_config":
            stats["ui_config_files"].add(filename)
            stats["source_files"].add(filename)
            stats["ui_config_changes"] += changes
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


def _is_initial_commit(message):
    normalized = _normalize_text(message)
    return normalized in {"initial commit", "init", "first commit"}


def _is_merge_or_integration_message(message):
    normalized = _normalize_text(message)
    words = set(normalized.split())
    return (
        normalized.startswith("merge ")
        or "merge pull request" in normalized
        or "resolve conflict" in normalized
        or bool(words & INTEGRATION_WORDS)
    )


def score_commit_message(message):
    """Cham diem commit message theo thang 0-10."""
    first_line = _first_line(message)
    normalized = _normalize_text(first_line)
    words = normalized.split()
    reasons = []

    if not normalized:
        return 1.0, ["commit message trống"]

    if _is_initial_commit(first_line):
        return 7.0, []

    score = 6.5
    word_count = len(words)
    has_good_action = any(word in GOOD_ACTION_WORDS for word in words)
    has_technical_word = any(word in TECHNICAL_WORDS for word in words)
    has_integration_word = any(word in INTEGRATION_WORDS for word in words)

    if normalized in SUSPICIOUS_EXACT_MESSAGES:
        score = 2.5
        reasons.append("commit message quá chung chung")
    elif word_count <= 2:
        if has_good_action and (has_technical_word or "readme" in words):
            score = 6.2
        else:
            score = 4.0
            reasons.append("commit message quá ngắn")

    for phrase, reason in SUSPICIOUS_PHRASES.items():
        if phrase in normalized:
            score = min(score, 3.5)
            if reason not in reasons:
                reasons.append(reason)

    # "fix" don le la yeu, nhung "Fix GitHub token handling" la ro nghia.
    if "fix" in words and word_count >= 4 and (has_technical_word or has_integration_word):
        score = max(score, 8.2)
        reasons = [reason for reason in reasons if reason != "commit message quá chung chung"]

    if 10 <= len(first_line) <= 80:
        score += 0.8
    elif len(first_line) < 10 and not reasons:
        score -= 0.8
        reasons.append("commit message nên mô tả rõ hơn")
    if word_count >= 5 and has_good_action:
        score += 1.0
    if word_count >= 4 and (has_technical_word or has_integration_word):
        score += 0.8
    if len(first_line) > 72:
        score -= 0.6
        reasons.append("commit message hơi dài, nên viết gọn hơn")

    return _clamp(score, 0, 10), reasons


def danh_gia_commit_message(message):
    """Wrapper cu: tra diem noi bo 0-100 de khong pha phan con lai."""
    score_10, reasons = score_commit_message(message)
    return score_10 * 10, reasons


def score_meaningful_change(commit, file_stats):
    """Cham diem y nghia thay doi va tac dong code theo thang 0-10."""
    additions = max(commit.get("additions", 0), 0)
    deletions = max(commit.get("deletions", 0), 0)
    total_changes = additions + deletions
    files_detail = commit.get("files_detail") or []
    logic_count, changed_lines, non_empty_changed_lines = _dem_dong_logic(files_detail)
    reasons = []
    message = commit.get("message", "")
    is_initial = _is_initial_commit(message)
    is_merge = _is_merge_or_integration_message(message)
    core_count = len(file_stats["core_files"])
    ui_count = len(file_stats["ui_config_files"])
    doc_count = len(file_stats["document_files"])
    generated_count = len(file_stats["generated_files"])
    changed_file_count = (
        core_count + ui_count + doc_count + len(file_stats["other_files"]) + generated_count
    )

    if total_changes <= 0:
        score = 1.0
        reasons.append("commit không có thay đổi additions/deletions đáng kể")
    elif total_changes <= 2:
        score = 3.0
        reasons.append("thay đổi quá nhỏ")
    elif total_changes <= 10:
        score = 5.2
    elif total_changes <= 200:
        score = 7.2
    else:
        score = 8.2

    if core_count:
        score += 1.2
    elif ui_count:
        score += 0.8
    if logic_count > 0:
        score += min(1.2, logic_count * 0.3)
    if changed_file_count >= 3 and (core_count or ui_count):
        score += 0.6
    if doc_count and not file_stats["source_files"]:
        if total_changes >= 40 and not generated_count:
            score = max(score, 5.8)
        else:
            score -= 1.4
        reasons.append("commit chủ yếu sửa tài liệu/báo cáo")
    if generated_count:
        score -= 2.5
        reasons.append("commit có sửa file môi trường hoặc file tự động sinh")
    if changed_lines > 0 and non_empty_changed_lines == 0:
        score = min(score, 2.5)
        reasons.append("thay đổi chủ yếu là khoảng trắng hoặc dòng trống")
    if is_initial and changed_file_count >= 3 and generated_count < changed_file_count:
        score = max(score, 7.2)
        reasons = [reason for reason in reasons if reason != "thay đổi quá nhỏ"]
    if is_merge and not generated_count:
        score = max(score, 6.2)

    code_impact_score = score_code_impact(file_stats, total_changes, is_merge=is_merge)
    return _clamp(score, 0, 10), code_impact_score, reasons


def danh_gia_y_nghia_thay_doi(commit, file_stats):
    meaningful_score, _code_impact_score, reasons = score_meaningful_change(commit, file_stats)
    return meaningful_score * 10, reasons


def score_code_impact(file_stats, total_changes=0, is_merge=False):
    """Cham diem tac dong vao code/file theo thang 0-10."""
    core_count = len(file_stats["core_files"])
    ui_count = len(file_stats["ui_config_files"])
    doc_count = len(file_stats["document_files"])
    generated_count = len(file_stats["generated_files"])
    other_count = len(file_stats["other_files"])

    if core_count:
        score = 7.5 + min(1.8, core_count * 0.45)
    elif ui_count:
        score = 6.5 + min(1.5, ui_count * 0.4)
    elif doc_count and not generated_count:
        score = 4.8 + (1.0 if total_changes >= 40 else 0.0)
    elif generated_count and not (core_count or ui_count):
        score = 1.2
    elif other_count:
        score = 4.5
    else:
        score = 2.0

    if generated_count:
        score -= min(2.5, generated_count * 0.8)
    if is_merge and (core_count or ui_count or doc_count):
        score = max(score, 5.8)

    return _clamp(score, 0, 10)


def danh_gia_tac_dong_code(file_stats):
    reasons = []
    source_count = len(file_stats["source_files"])
    core_count = len(file_stats["core_files"])
    ui_count = len(file_stats["ui_config_files"])
    doc_count = len(file_stats["document_files"])
    generated_count = len(file_stats["generated_files"])
    other_count = len(file_stats["other_files"])

    if core_count:
        score = 75.0 + min(18.0, core_count * 4.5)
    elif ui_count:
        score = 65.0 + min(15.0, ui_count * 4)
    elif doc_count and not generated_count:
        score = 48.0
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
    message_score_10, message_reasons = score_commit_message(commit.get("message", ""))
    meaningful_score_10, code_impact_score_10, meaningful_reasons = score_meaningful_change(
        commit, file_stats
    )
    message_score = message_score_10 * 10
    meaningful_score = meaningful_score_10 * 10
    code_impact_score = code_impact_score_10 * 10

    suspicious_reasons = []
    suspicious_reasons.extend(message_reasons)
    suspicious_reasons.extend(meaningful_reasons)

    penalty = 0.0
    penalty_reasons = []
    if message_score_10 < 4.5:
        penalty += 8
        penalty_reasons.append("commit message kém chất lượng")
    if meaningful_score_10 < 4.0:
        penalty += 6
        penalty_reasons.append("thay đổi quá nhỏ hoặc chưa rõ ý nghĩa")
    if code_impact_score_10 < 3.5:
        penalty += 8
        penalty_reasons.append("tác động vào file chính thấp")
    if file_stats["generated_files"]:
        penalty += 8
        penalty_reasons.append("có sửa file local/generated")
    if file_stats["document_files"] and not file_stats["source_files"]:
        if commit.get("additions", 0) + commit.get("deletions", 0) < 40:
            penalty += 4
            penalty_reasons.append("commit chủ yếu sửa tài liệu/báo cáo nhỏ")
    if _is_merge_or_integration_message(commit.get("message", "")) and not file_stats["generated_files"]:
        penalty = max(0.0, penalty - 4)
        penalty_reasons = [
            reason
            for reason in penalty_reasons
            if reason not in {"thay đổi quá nhỏ hoặc chưa rõ ý nghĩa", "tác động vào file chính thấp"}
        ]
    if _is_initial_commit(commit.get("message", "")) and file_stats["source_files"]:
        penalty = max(0.0, penalty - 5)

    quality_score = (
        0.40 * message_score
        + 0.30 * meaningful_score
        + 0.30 * code_impact_score
    )
    quality_score = _clamp(quality_score)
    penalty = _clamp(penalty, 0, 25)
    is_suspicious = bool(suspicious_reasons) or penalty >= 10
    unique_reasons = list(dict.fromkeys(suspicious_reasons))

    return {
        "sha": commit.get("sha", ""),
        "short_sha": _short_sha(commit.get("sha", "")),
        "message": _first_line(commit.get("message", "")),
        "commit_message_score": message_score,
        "commit_message_score_display": round(message_score_10, 1),
        "message_reason": "; ".join(message_reasons),
        "meaningful_change_score": meaningful_score,
        "meaningful_change_score_display": round(meaningful_score_10, 1),
        "code_impact_score": code_impact_score,
        "code_impact_score_display": round(code_impact_score_10, 1),
        "quality_score": quality_score,
        "penalty_score": penalty,
        "quality_score_display": quy_doi_diem_hien_thi(quality_score),
        "penalty_score_display": quy_doi_diem_tru_hien_thi(penalty, max_internal=25),
        "is_suspicious": is_suspicious,
        "suspicious_reasons": unique_reasons,
        "penalty_reasons": list(dict.fromkeys(penalty_reasons)),
        "suspicion_level": _xac_dinh_muc_do_nghi_ngo(penalty, unique_reasons),
        "suspicion_score_display": quy_doi_diem_tru_hien_thi(penalty, max_internal=25),
        "core_file_count": len(file_stats["core_files"]),
        "ui_config_file_count": len(file_stats["ui_config_files"]),
        "source_file_count": len(file_stats["source_files"]),
        "document_file_count": len(file_stats["document_files"]),
        "generated_file_count": len(file_stats["generated_files"]),
        "core_changes": file_stats["core_changes"],
        "ui_config_changes": file_stats["ui_config_changes"],
        "source_changes": file_stats["source_changes"],
        "document_changes": file_stats["document_changes"],
        "generated_changes": file_stats["generated_changes"],
        "other_changes": file_stats["other_changes"],
        "file_impact_raw": file_stats["file_impact_raw"],
        "is_integration_commit": _is_merge_or_integration_message(commit.get("message", "")),
    }


def loc_commit_duoc_tinh_diem(danh_sach_commit):
    """Loai commit bot khoi tap du lieu cham diem chinh.

    Commit auto report cua contributor that van duoc tinh va co the bi danh dau
    can xem lai, vi day la tin hieu chat luong dong gop chua tot.
    """
    commits_duoc_tinh = []
    ignored_commits = []
    ignored_bot_commit_count = 0
    ignored_auto_commit_count = 0
    auto_report_commit_count = 0

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
            ignored_reasons.append("bot commit")
        if is_auto_commit:
            auto_report_commit_count += 1
            if is_bot:
                ignored_auto_commit_count += 1
                ignored_reasons.append("auto report bot")

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
                    "reason": " / ".join(ignored_reasons),
                }
            )
            continue

        commits_duoc_tinh.append(commit_moi)

    return commits_duoc_tinh, {
        "ignored_bot_commit_count": ignored_bot_commit_count,
        "ignored_auto_commit_count": ignored_auto_commit_count,
        "auto_report_commit_count": auto_report_commit_count,
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


def _parse_commit_datetime(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except ValueError:
        return None


def _tinh_thoi_gian_code_uoc_tinh(danh_sach_commit):
    datetimes = [
        parsed
        for parsed in (_parse_commit_datetime(commit.get("commit_date")) for commit in danh_sach_commit)
        if parsed is not None
    ]
    datetimes.sort()
    active_days = len({item.date().isoformat() for item in datetimes})

    if not datetimes:
        return {
            "estimated_coding_minutes": 0,
            "estimated_coding_hours": 0.0,
            "active_days": 0,
            "coding_sessions": 0,
        }

    sessions = []
    current_minutes = 30.0
    previous = datetimes[0]

    for current in datetimes[1:]:
        gap_minutes = max((current - previous).total_seconds() / 60.0, 0.0)
        if gap_minutes <= 120:
            current_minutes = min(360.0, current_minutes + min(gap_minutes, 120.0))
        else:
            sessions.append(current_minutes)
            current_minutes = 30.0
        previous = current

    sessions.append(current_minutes)
    total_minutes = round(sum(sessions), 1)

    return {
        "estimated_coding_minutes": total_minutes,
        "estimated_coding_hours": round(total_minutes / 60.0, 2),
        "active_days": active_days,
        "coding_sessions": len(sessions),
    }


def _tinh_integration_points(commit, quality_item):
    message = commit.get("message", "")
    if not _is_merge_or_integration_message(message):
        return 0.0
    if quality_item.get("generated_file_count", 0) and quality_item.get("source_file_count", 0) == 0:
        return 0.0

    points = 28.0
    normalized = _normalize_text(message)
    if "merge pull request" in normalized or "resolve conflict" in normalized:
        points += 20.0
    if quality_item.get("source_file_count", 0):
        points += 18.0
    if quality_item.get("document_file_count", 0):
        points += 8.0
    return _clamp(points, 0, 55)


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
        penalty_reasons = []
        integration_commit_count = 0
        integration_raw = 0.0
        core_files = set()
        ui_config_files = set()
        source_files = set()
        document_files = set()
        generated_files = set()
        core_changes = 0
        ui_config_changes = 0
        source_changes = 0
        document_changes = 0
        generated_changes = 0
        file_impact_raw = 0.0

        for commit in danh_sach_commit:
            tong_additions += commit.get("additions", 0)
            tong_deletions += commit.get("deletions", 0)

            for ten_file in commit.get("changed_files", []):
                tap_hop_file.add(ten_file)
                file_type = classify_file(ten_file)
                if file_type == "core":
                    core_files.add(ten_file)
                    source_files.add(ten_file)
                elif file_type == "ui_config":
                    ui_config_files.add(ten_file)
                    source_files.add(ten_file)
                elif file_type == "document":
                    document_files.add(ten_file)
                elif file_type == "generated":
                    generated_files.add(ten_file)

            quality_item = danh_gia_chat_luong_commit(commit)
            quality_items.append(quality_item)
            core_changes += quality_item.get("core_changes", 0)
            ui_config_changes += quality_item.get("ui_config_changes", 0)
            source_changes += quality_item.get("source_changes", 0)
            document_changes += quality_item.get("document_changes", 0)
            generated_changes += quality_item.get("generated_changes", 0)
            file_impact_raw += quality_item.get("file_impact_raw", 0)
            penalty_reasons.extend(quality_item.get("penalty_reasons", []))

            integration_points = _tinh_integration_points(commit, quality_item)
            if integration_points > 0:
                integration_commit_count += 1
                integration_raw += integration_points

            if quality_item.get("is_suspicious"):
                suspicious_commits.append(
                    {
                        "sha": quality_item.get("sha", ""),
                        "short_sha": quality_item.get("short_sha", ""),
                        "message": quality_item.get("message", ""),
                        "reasons": quality_item.get("suspicious_reasons", []),
                        "penalty_score": quality_item.get("penalty_score", 0),
                        "penalty_score_display": quality_item.get("penalty_score_display", 0),
                        "suspicion_score_display": quality_item.get("suspicion_score_display", 0),
                        "suspicion_level": quality_item.get("suspicion_level", "Thấp"),
                    }
                )

        commit_count = len(danh_sach_commit)
        ten_hien_thi = du_lieu_contributor.get("ten_hien_thi", "Khong xac dinh")
        total_changes = tong_additions + tong_deletions
        suspicious_commit_count = len(suspicious_commits)
        suspicious_commit_ratio = suspicious_commit_count / commit_count if commit_count else 0
        time_stats = _tinh_thoi_gian_code_uoc_tinh(danh_sach_commit)

        def avg(key):
            if not quality_items:
                return 0.0
            return sum(item.get(key, 0) for item in quality_items) / len(quality_items)

        quality_score = avg("quality_score")
        penalty_score = _clamp(avg("penalty_score") + suspicious_commit_ratio * 12, 0, 30)
        if suspicious_commit_ratio >= 0.4:
            penalty_reasons.append("tỷ lệ commit cần xem lại cao")

        core_code_commit_count = sum(
            1 for item in quality_items if item.get("source_file_count", 0) > 0
        )
        ui_config_commit_count = sum(
            1 for item in quality_items if item.get("ui_config_file_count", 0) > 0
        )
        documentation_commit_count = sum(
            1 for item in quality_items if item.get("document_file_count", 0) > 0
        )
        generated_commit_count = sum(
            1 for item in quality_items if item.get("generated_file_count", 0) > 0
        )

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
                "core_file_count": len(core_files),
                "ui_config_file_count": len(ui_config_files),
                "source_file_count": len(source_files),
                "document_file_count": len(document_files),
                "generated_file_count": len(generated_files),
                "core_changes": core_changes,
                "ui_config_changes": ui_config_changes,
                "source_changes": source_changes,
                "document_changes": document_changes,
                "generated_changes": generated_changes,
                "file_impact_raw": file_impact_raw,
                "core_code_commit_count": core_code_commit_count,
                "ui_config_commit_count": ui_config_commit_count,
                "documentation_commit_count": documentation_commit_count,
                "generated_commit_count": generated_commit_count,
                "commit_quality_items": quality_items,
                "suspicious_commits": suspicious_commits,
                "suspicious_commit_count": suspicious_commit_count,
                "suspicious_commit_ratio": suspicious_commit_ratio,
                "suspicious_commit_ratio_display": round(suspicious_commit_ratio * 100, 1),
                "estimated_coding_minutes": time_stats["estimated_coding_minutes"],
                "estimated_coding_hours": time_stats["estimated_coding_hours"],
                "active_days": time_stats["active_days"],
                "coding_sessions": time_stats["coding_sessions"],
                "integration_commit_count": integration_commit_count,
                "integration_raw": integration_raw,
                "commit_message_score": avg("commit_message_score"),
                "commit_message_score_display": quy_doi_diem_hien_thi(avg("commit_message_score")),
                "meaningful_change_score": avg("meaningful_change_score"),
                "meaningful_change_score_display": quy_doi_diem_hien_thi(avg("meaningful_change_score")),
                "code_impact_score": avg("code_impact_score"),
                "code_impact_score_display": quy_doi_diem_hien_thi(avg("code_impact_score")),
                "quality_score": quality_score,
                "quality_score_display": quy_doi_diem_hien_thi(quality_score),
                "penalty_score": penalty_score,
                "penalty_score_display": quy_doi_diem_tru_hien_thi(penalty_score),
                "penalty_reasons": list(dict.fromkeys(penalty_reasons)),
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
    commit_count = item.get("commit_count", 0)
    active_days = item.get("active_days", 0)
    coding_sessions = item.get("coding_sessions", 0)

    if commit_count <= 0:
        return 0.0

    active_day_score = min(45.0, active_days * 15.0)
    session_score = min(35.0, coding_sessions * 10.0)
    spread_ratio = active_days / commit_count if commit_count else 0.0
    spread_score = min(20.0, spread_ratio * 60.0)
    if commit_count == 1:
        spread_score = min(spread_score, 10.0)

    return _clamp(active_day_score + session_score + spread_score)


def tinh_diem_dong_gop_co_ban(danh_sach_thong_ke):
    """
    Tinh diem dong gop theo cong thuc rule-based moi:
    raw_score = 0.10 commit_score + 0.15 code_volume_score
              + 0.15 file_impact_score + 0.25 quality_score
              + 0.15 consistency_score + 0.10 estimated_time_score
              + 0.10 integration_score
    final_score = raw_score - penalty_score
    """
    commit_scores = _normalize_log_max(
        [item.get("commit_count", 0) for item in danh_sach_thong_ke]
    )
    code_volume_scores = _normalize_log_max(
        [item.get("total_changes", 0) for item in danh_sach_thong_ke],
        cap=4000,
    )
    file_impact_scores = _normalize_log_max(
        [item.get("file_impact_raw", 0) for item in danh_sach_thong_ke],
        cap=4000,
    )
    estimated_time_scores = _normalize_log_max(
        [item.get("estimated_coding_minutes", 0) for item in danh_sach_thong_ke],
        cap=2400,
    )

    ket_qua = []
    for index, item in enumerate(danh_sach_thong_ke):
        commit_score = commit_scores[index]
        code_volume_score = code_volume_scores[index]
        file_impact_score = file_impact_scores[index]
        quality_score = item.get("quality_score", 0)
        consistency_score = _tinh_consistency_score(item)
        estimated_time_score = estimated_time_scores[index]
        integration_score = _clamp(item.get("integration_raw", 0), 0, 100)
        penalty_score = item.get("penalty_score", 0)

        raw_score = (
            0.10 * commit_score
            + 0.15 * code_volume_score
            + 0.15 * file_impact_score
            + 0.25 * quality_score
            + 0.15 * consistency_score
            + 0.10 * estimated_time_score
            + 0.10 * integration_score
        )
        final_score = (
            raw_score
            - penalty_score
        )
        final_score = _clamp(final_score)
        display_score_10 = quy_doi_diem_hien_thi(final_score)

        thong_tin_moi = item.copy()
        thong_tin_moi.update(
            {
                "commit_score": commit_score,
                "code_volume_score": code_volume_score,
                "code_score": code_volume_score,
                "file_impact_score": file_impact_score,
                "file_score": file_impact_score,
                "consistency_score": consistency_score,
                "estimated_time_score": estimated_time_score,
                "integration_score": integration_score,
                "raw_score": raw_score,
                "final_score_100": final_score,
                "final_score": final_score,
                "score": final_score,
                "baseline_score": final_score,
                "display_score_10": display_score_10,
                "quality_score_display": quy_doi_diem_hien_thi(quality_score),
                "estimated_time_score_display": quy_doi_diem_hien_thi(estimated_time_score),
                "consistency_score_display": quy_doi_diem_hien_thi(consistency_score),
                "integration_score_display": quy_doi_diem_hien_thi(integration_score),
                "penalty_score_display": quy_doi_diem_tru_hien_thi(penalty_score),
                "final_score_display": display_score_10,
                "score_display": display_score_10,
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
    total_estimated_minutes = sum(item.get("estimated_coding_minutes", 0) for item in contributors)

    return {
        "owner": owner,
        "repo": repo,
        "repo_full_name": repo_info.get("full_name", f"{owner}/{repo}"),
        "requested_commit_count": so_luong_commit,
        "analyzed_commit_count": len(danh_sach_commit),
        "ignored_commit_count": ignored_stats.get("ignored_commit_count", 0),
        "ignored_bot_commit_count": ignored_stats.get("ignored_bot_commit_count", 0),
        "ignored_auto_commit_count": ignored_stats.get("ignored_auto_commit_count", 0),
        "auto_report_commit_count": ignored_stats.get("auto_report_commit_count", 0),
        "contributor_count": len(contributors),
        "total_additions": sum(item.get("total_additions", 0) for item in contributors),
        "total_deletions": sum(item.get("total_deletions", 0) for item in contributors),
        "total_estimated_coding_minutes": round(total_estimated_minutes, 1),
        "total_estimated_coding_hours": round(total_estimated_minutes / 60.0, 2),
        "total_coding_sessions": sum(item.get("coding_sessions", 0) for item in contributors),
        "total_active_days": sum(item.get("active_days", 0) for item in contributors),
        "top_contributor": top_contributor.get("contributor", "Chưa có"),
        "top_score": top_contributor.get("final_score", 0),
        "top_score_display": quy_doi_diem_hien_thi(top_contributor.get("final_score", 0)),
        "total_score": tong_diem,
        "total_score_display": quy_doi_diem_hien_thi(tong_diem),
        "average_quality_score": average_quality_score,
        "average_quality_score_display": quy_doi_diem_hien_thi(average_quality_score),
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
