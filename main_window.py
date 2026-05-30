import os
from pathlib import Path

from PyQt6 import uic
from PyQt6.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt6.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QTableWidgetItem,
)

from analyzer import phan_tich_repo
from chart_widget import ChartWidget
from github_client import chuan_hoa_owner_repo
from report_generator import (
    xuat_csv as export_csv_report,
    xuat_markdown as export_markdown_report,
    xuat_pdf as export_pdf_report,
)


BASE_DIR = Path(__file__).resolve().parent


def _diem_hien_thi(score_100):
    try:
        score_100 = float(score_100)
    except (TypeError, ValueError):
        score_100 = 0.0
    return round(max(0.0, min(100.0, score_100)) / 10, 1)


def _diem_tru_hien_thi(penalty_score):
    try:
        penalty_score = float(penalty_score)
    except (TypeError, ValueError):
        penalty_score = 0.0
    penalty_score = max(0.0, min(30.0, penalty_score))
    return round(penalty_score / 30.0 * 10, 1)


def _lay_diem_hien_thi(item, display_key, raw_key, fallback_key=None):
    if display_key in item and item.get(display_key) is not None:
        try:
            return float(item.get(display_key))
        except (TypeError, ValueError):
            pass
    raw_value = item.get(raw_key, item.get(fallback_key, 0)) if fallback_key else item.get(raw_key, 0)
    return _diem_hien_thi(raw_value)


def _lay_diem_tru_hien_thi(item):
    if "penalty_score_display" in item and item.get("penalty_score_display") is not None:
        try:
            return float(item.get("penalty_score_display"))
        except (TypeError, ValueError):
            pass
    return _diem_tru_hien_thi(item.get("penalty_score", 0))


def _lay_ly_do_commit(commit):
    reasons = commit.get("reasons") or commit.get("suspicious_reasons") or []
    if isinstance(reasons, str):
        return reasons
    return "; ".join(str(reason) for reason in reasons) if reasons else "Cần viết mô tả rõ hơn"


def _lay_muc_nghi_ngo(commit):
    level = commit.get("suspicion_level") or "Thấp"
    score = commit.get("suspicion_score_display", commit.get("penalty_score_display"))
    if score is None:
        return level
    try:
        score = float(score)
    except (TypeError, ValueError):
        return level
    return f"{level} ({score:.1f}/10)"


class AnalysisWorker(QObject):
    finished = pyqtSignal(dict)
    error = pyqtSignal(str)
    progress = pyqtSignal(str)

    def __init__(self, token, owner, repo, so_luong_commit):
        super().__init__()
        self.token = token
        self.owner = owner
        self.repo = repo
        self.so_luong_commit = so_luong_commit

    def run(self):
        try:
            ket_qua = phan_tich_repo(
                self.owner,
                self.repo,
                so_luong_commit=self.so_luong_commit,
                token=self.token,
                progress_callback=self.progress.emit,
            )
        except Exception as exc:
            self.error.emit(str(exc))
            return

        self.finished.emit(ket_qua)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi(BASE_DIR / "main_window.ui", self)

        self.current_result = None
        self.worker_thread = None
        self.worker = None
        self.reports_dir = BASE_DIR / "reports"

        self.chart_widget = ChartWidget(self)
        self.chartContainerLayout.addWidget(self.chart_widget)

        self._setup_widgets()
        self._connect_signals()
        self._set_result_buttons_enabled(False)

    def _setup_widgets(self):
        self.tokenInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.tokenInput.setText(os.getenv("GITHUB_TOKEN", ""))
        self.repoUrlInput.setText(os.getenv("GITHUB_REPO_URL", ""))
        self.ownerInput.setText(os.getenv("REPO_OWNER", ""))
        self.repoInput.setText(os.getenv("REPO_NAME", ""))
        self._nap_so_commit_tu_env()

        self.contributorTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.contributorTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.contributorTable.setAlternatingRowColors(True)
        self.contributorTable.setShowGrid(True)
        self.contributorTable.setWordWrap(True)
        self.contributorTable.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.contributorTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.contributorTable.horizontalHeader().setStretchLastSection(False)
        self.contributorTable.horizontalHeader().setMinimumSectionSize(80)
        self.contributorTable.verticalHeader().setVisible(False)

        if hasattr(self, "suspiciousCommitTable"):
            self.suspiciousCommitTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
            self.suspiciousCommitTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
            self.suspiciousCommitTable.setAlternatingRowColors(True)
            self.suspiciousCommitTable.setShowGrid(True)
            self.suspiciousCommitTable.setWordWrap(True)
            self.suspiciousCommitTable.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.suspiciousCommitTable.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Interactive
            )
            self.suspiciousCommitTable.horizontalHeader().setStretchLastSection(False)
            self.suspiciousCommitTable.horizontalHeader().setMinimumSectionSize(90)
            self.suspiciousCommitTable.verticalHeader().setVisible(False)
            self.hien_thi_commit_can_xem_lai([])

        self.aiTextEdit.setReadOnly(True)
        self.statusbar.showMessage("Sẵn sàng.")

    def _nap_so_commit_tu_env(self):
        try:
            so_commit = int(os.getenv("SO_LUONG_COMMIT", "30"))
        except ValueError:
            so_commit = 30

        so_commit = max(self.commitSpinBox.minimum(), min(self.commitSpinBox.maximum(), so_commit))
        self.commitSpinBox.setValue(so_commit)

    def _connect_signals(self):
        self.repoUrlInput.editingFinished.connect(self.tu_dong_dien_owner_repo_tu_url)
        self.analyzeButton.clicked.connect(self.phan_tich)
        self.exportMarkdownButton.clicked.connect(self.xuat_markdown)
        self.exportCsvButton.clicked.connect(self.xuat_csv)
        self.exportPdfButton.clicked.connect(self.xuat_pdf)

    def _set_result_buttons_enabled(self, enabled):
        self.exportMarkdownButton.setEnabled(enabled)
        self.exportCsvButton.setEnabled(enabled)
        self.exportPdfButton.setEnabled(enabled)

    def tu_dong_dien_owner_repo_tu_url(self):
        repo_url = self.repoUrlInput.text().strip()
        if not repo_url:
            return

        try:
            owner, repo = chuan_hoa_owner_repo(repo_url=repo_url)
        except ValueError:
            return

        self.ownerInput.setText(owner)
        self.repoInput.setText(repo)

    def lay_thong_tin_repo_tu_form(self):
        repo_url = self.repoUrlInput.text().strip()
        owner = self.ownerInput.text().strip()
        repo = self.repoInput.text().strip()
        return chuan_hoa_owner_repo(owner, repo, repo_url=repo_url)

    def phan_tich(self):
        token = self.tokenInput.text().strip()
        so_luong_commit = self.commitSpinBox.value()

        try:
            owner, repo = self.lay_thong_tin_repo_tu_form()
        except ValueError as exc:
            QMessageBox.warning(self, "Thiếu thông tin", str(exc))
            return

        self.ownerInput.setText(owner)
        self.repoInput.setText(repo)
        self.analyzeButton.setEnabled(False)
        self._set_result_buttons_enabled(False)
        self.statusbar.showMessage("Đang bắt đầu phân tích...")

        self.worker_thread = QThread(self)
        self.worker = AnalysisWorker(token, owner, repo, so_luong_commit)
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.cap_nhat_trang_thai)
        self.worker.finished.connect(self.hoan_tat_phan_tich)
        self.worker.error.connect(self.hien_thi_loi_phan_tich)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.error.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)
        self.worker_thread.finished.connect(self._reset_worker_refs)

        self.worker_thread.start()

    def _reset_worker_refs(self):
        self.worker = None
        self.worker_thread = None
        self.analyzeButton.setEnabled(True)

    def cap_nhat_trang_thai(self, message):
        self.statusbar.showMessage(message)

    def hien_thi_loi_phan_tich(self, message):
        QMessageBox.critical(self, "Lỗi phân tích", message)
        self.statusbar.showMessage("Phân tích thất bại.")

    def hoan_tat_phan_tich(self, ket_qua):
        self.current_result = ket_qua
        contributors = ket_qua.get("contributors", [])

        self.hien_thi_tong_quan(ket_qua)
        self.hien_thi_bang_contributor(contributors)
        self.hien_thi_commit_can_xem_lai(contributors)
        self.chart_widget.update_charts(contributors)
        self.aiTextEdit.setPlainText(ket_qua.get("ai_summary", ""))
        self._set_result_buttons_enabled(True)
        ignored_count = ket_qua.get("overview", {}).get("ignored_commit_count", 0)
        if ignored_count:
            self.statusbar.showMessage(
                f"Phân tích hoàn tất. Đã loại {ignored_count} commit bot/tự động."
            )
        else:
            self.statusbar.showMessage("Phân tích hoàn tất.")

    def hien_thi_tong_quan(self, ket_qua):
        overview = ket_qua.get("overview", {})
        self.repoNameLabel.setText(overview.get("repo_full_name", ""))
        analyzed_commit_count = overview.get("analyzed_commit_count", 0)
        ignored_commit_count = overview.get("ignored_commit_count", 0)
        if ignored_commit_count:
            self.totalCommitsLabel.setText(
                f"{analyzed_commit_count} (+{ignored_commit_count} loại)"
            )
        else:
            self.totalCommitsLabel.setText(str(analyzed_commit_count))
        self.totalContributorsLabel.setText(str(overview.get("contributor_count", 0)))
        self.totalAdditionsLabel.setText(str(overview.get("total_additions", 0)))
        self.totalDeletionsLabel.setText(str(overview.get("total_deletions", 0)))
        average_quality = overview.get(
            "average_quality_score_display",
            _diem_hien_thi(overview.get("average_quality_score", 0)),
        )
        self.averageQualityLabel.setText(f"{average_quality:.1f}/10")
        self.suspiciousCommitLabel.setText(str(overview.get("suspicious_commit_count", 0)))
        if hasattr(self, "totalCodingHoursLabel"):
            self.totalCodingHoursLabel.setText(
                f"{overview.get('total_estimated_coding_hours', 0):.1f}h"
            )
        if hasattr(self, "totalCodingSessionsLabel"):
            self.totalCodingSessionsLabel.setText(str(overview.get("total_coding_sessions", 0)))

        if hasattr(self, "topContributorLabel"):
            self.topContributorLabel.setText(
                f"{overview.get('top_contributor', 'Chưa có')} "
                f"({overview.get('top_score_display', _diem_hien_thi(overview.get('top_score', 0))):.1f}/10)"
            )
        if hasattr(self, "totalScoreLabel"):
            self.totalScoreLabel.setText(
                f"{overview.get('total_score_display', _diem_hien_thi(overview.get('total_score', 0))):.1f}/10"
            )

    def hien_thi_bang_contributor(self, contributors):
        headers = [
            "Thành viên",
            "Số commit",
            "Dòng thêm",
            "Dòng xoá",
            "File sửa",
            "Giờ code ước tính",
            "Số ngày hoạt động",
            "Điểm chất lượng /10",
            "Điểm thời gian /10",
            "Điểm cuối /10",
            "Điểm trừ",
            "Mức đánh giá",
            "Commit cần xem lại",
            "Nhận xét ngắn",
        ]
        self.contributorTable.setColumnCount(len(headers))
        self.contributorTable.setHorizontalHeaderLabels(headers)
        self.contributorTable.setRowCount(len(contributors))

        for row, item in enumerate(contributors):
            values = [
                item.get("contributor", ""),
                item.get("commit_count", 0),
                item.get("total_additions", 0),
                item.get("total_deletions", 0),
                item.get("files_changed", item.get("changed_files_count", 0)),
                f"{item.get('estimated_coding_hours', 0):.1f}",
                item.get("active_days", 0),
                f"{_lay_diem_hien_thi(item, 'quality_score_display', 'quality_score'):.1f}",
                f"{_lay_diem_hien_thi(item, 'estimated_time_score_display', 'estimated_time_score'):.1f}",
                f"{_lay_diem_hien_thi(item, 'final_score_display', 'final_score', 'score'):.1f}",
                f"{_lay_diem_tru_hien_thi(item):.1f}",
                item.get("contribution_level", ""),
                item.get("suspicious_commit_count", 0),
                item.get("short_summary", item.get("ai_summary", "")),
            ]

            for col, value in enumerate(values):
                table_item = QTableWidgetItem(str(value))
                if col in {1, 4, 5, 6, 7, 8, 9, 10, 12}:
                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                elif col in {2, 3}:
                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.contributorTable.setItem(row, col, table_item)

        self.contributorTable.resizeRowsToContents()
        self._dat_do_rong_cot_contributor()

    def _dat_do_rong_cot_contributor(self):
        column_widths = {
            0: 140,
            1: 90,
            2: 100,
            3: 100,
            4: 90,
            5: 130,
            6: 125,
            7: 140,
            8: 130,
            9: 120,
            10: 100,
            11: 160,
            12: 150,
            13: 300,
        }
        for column, width in column_widths.items():
            self.contributorTable.setColumnWidth(column, width)

    def hien_thi_commit_can_xem_lai(self, contributors):
        if not hasattr(self, "suspiciousCommitTable"):
            return

        headers = [
            "Contributor",
            "SHA",
            "Message",
            "Lý do bị đánh dấu",
            "Mức độ nghi ngờ",
        ]
        rows = []
        for item in contributors:
            contributor = item.get("contributor", item.get("tac_gia", ""))
            for commit in item.get("suspicious_commits", []):
                rows.append(
                    [
                        contributor,
                        commit.get("short_sha") or str(commit.get("sha", ""))[:7],
                        commit.get("message", ""),
                        _lay_ly_do_commit(commit),
                        _lay_muc_nghi_ngo(commit),
                    ]
                )

        self.suspiciousCommitTable.clearSpans()
        self.suspiciousCommitTable.setColumnCount(len(headers))
        self.suspiciousCommitTable.setHorizontalHeaderLabels(headers)

        if not rows:
            self.suspiciousCommitTable.setRowCount(1)
            message_item = QTableWidgetItem("Không có commit kém chất lượng được phát hiện.")
            message_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            self.suspiciousCommitTable.setItem(0, 0, message_item)
            self.suspiciousCommitTable.setSpan(0, 0, 1, len(headers))
        else:
            self.suspiciousCommitTable.setRowCount(len(rows))
            for row_index, row_values in enumerate(rows):
                for col, value in enumerate(row_values):
                    table_item = QTableWidgetItem(str(value))
                    if col in {1, 4}:
                        table_item.setTextAlignment(
                            Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter
                        )
                    self.suspiciousCommitTable.setItem(row_index, col, table_item)

        self.suspiciousCommitTable.resizeRowsToContents()
        for column, width in {0: 130, 1: 90, 2: 320, 3: 420, 4: 150}.items():
            self.suspiciousCommitTable.setColumnWidth(column, width)

    def _kiem_tra_co_ket_qua(self):
        if not self.current_result:
            QMessageBox.information(self, "Chưa có dữ liệu", "Hãy phân tích kho GitHub trước.")
            return False
        return True

    def xuat_markdown(self):
        if not self._kiem_tra_co_ket_qua():
            return

        try:
            path = export_markdown_report(self.current_result, self.reports_dir)
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi xuất Markdown", str(exc))
            return

        QMessageBox.information(self, "Đã xuất Markdown", f"Đã tạo file:\n{path}")

    def xuat_csv(self):
        if not self._kiem_tra_co_ket_qua():
            return

        try:
            path = export_csv_report(self.current_result, self.reports_dir)
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi xuất CSV", str(exc))
            return

        QMessageBox.information(self, "Đã xuất CSV", f"Đã tạo file:\n{path}")

    def xuat_pdf(self):
        if not self._kiem_tra_co_ket_qua():
            return

        try:
            path = export_pdf_report(self.current_result, self.reports_dir)
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi xuất PDF", str(exc))
            return

        QMessageBox.information(self, "Đã xuất PDF", f"Đã tạo file:\n{path}")
