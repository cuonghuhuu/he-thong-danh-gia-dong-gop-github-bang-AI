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
from db_manager import DatabaseManager
from github_client import chuan_hoa_owner_repo
from report_generator import (
    xuat_csv as export_csv_report,
    xuat_markdown as export_markdown_report,
    xuat_pdf as export_pdf_report,
)


BASE_DIR = Path(__file__).resolve().parent


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
        self.db_manager = DatabaseManager(BASE_DIR / "analysis_history.sqlite3")

        self.chart_widget = ChartWidget(self)
        self.chartContainerLayout.addWidget(self.chart_widget)

        self._setup_widgets()
        self._connect_signals()
        self._set_result_buttons_enabled(False)
        self.tai_lich_su()

    def _setup_widgets(self):
        self.tokenInput.setEchoMode(QLineEdit.EchoMode.Password)
        self.tokenInput.setText(os.getenv("GITHUB_TOKEN", ""))
        if hasattr(self, "repoUrlInput"):
            self.repoUrlInput.setText(os.getenv("GITHUB_REPO_URL", ""))
        self.ownerInput.setText(os.getenv("REPO_OWNER", ""))
        self.repoInput.setText(os.getenv("REPO_NAME", ""))
        self._nap_so_commit_tu_env()

        self.contributorTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.contributorTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.contributorTable.setWordWrap(True)
        self.contributorTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.contributorTable.verticalHeader().setVisible(False)

        self.historyTable.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.historyTable.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.historyTable.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.historyTable.verticalHeader().setVisible(False)

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
        if hasattr(self, "repoUrlInput"):
            self.repoUrlInput.editingFinished.connect(self.tu_dong_dien_owner_repo_tu_url)
        self.analyzeButton.clicked.connect(self.phan_tich)
        self.exportMarkdownButton.clicked.connect(self.xuat_markdown)
        self.exportCsvButton.clicked.connect(self.xuat_csv)
        self.exportPdfButton.clicked.connect(self.xuat_pdf)
        self.saveHistoryButton.clicked.connect(self.luu_lich_su)
        self.refreshHistoryButton.clicked.connect(self.tai_lich_su)

    def _set_result_buttons_enabled(self, enabled):
        self.exportMarkdownButton.setEnabled(enabled)
        self.exportCsvButton.setEnabled(enabled)
        self.exportPdfButton.setEnabled(enabled)
        self.saveHistoryButton.setEnabled(enabled)

    def tu_dong_dien_owner_repo_tu_url(self):
        if not hasattr(self, "repoUrlInput"):
            return

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
        repo_url = self.repoUrlInput.text().strip() if hasattr(self, "repoUrlInput") else ""
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
        self.chart_widget.update_charts(contributors)
        self.aiTextEdit.setPlainText(ket_qua.get("ai_summary", ""))
        self._set_result_buttons_enabled(True)
        self.statusbar.showMessage("Phân tích hoàn tất.")
        self.tabWidget.setCurrentWidget(self.dashboardTab)

    def hien_thi_tong_quan(self, ket_qua):
        overview = ket_qua.get("overview", {})
        self.repoNameLabel.setText(overview.get("repo_full_name", ""))
        self.totalCommitsLabel.setText(str(overview.get("analyzed_commit_count", 0)))
        self.totalContributorsLabel.setText(str(overview.get("contributor_count", 0)))
        self.totalAdditionsLabel.setText(str(overview.get("total_additions", 0)))
        self.totalDeletionsLabel.setText(str(overview.get("total_deletions", 0)))
        self.topContributorLabel.setText(
            f"{overview.get('top_contributor', 'Chưa có')} "
            f"({overview.get('top_score', 0):.2f})"
        )
        self.totalScoreLabel.setText(f"{overview.get('total_score', 0):.2f}")

    def hien_thi_bang_contributor(self, contributors):
        headers = [
            "STT",
            "Contributor",
            "Số commit",
            "Additions",
            "Deletions",
            "Files changed",
            "Total changes",
            "Commit score",
            "Code score",
            "File score",
            "Balance score",
            "Final score",
            "Mức đóng góp",
            "Loại đóng góp",
            "Nhận xét",
        ]
        self.contributorTable.setColumnCount(len(headers))
        self.contributorTable.setHorizontalHeaderLabels(headers)
        self.contributorTable.setRowCount(len(contributors))

        for row, item in enumerate(contributors):
            values = [
                row + 1,
                item.get("contributor", ""),
                item.get("commit_count", 0),
                item.get("total_additions", 0),
                item.get("total_deletions", 0),
                item.get("files_changed", item.get("changed_files_count", 0)),
                item.get("total_changes", 0),
                f"{item.get('commit_score', 0):.2f}",
                f"{item.get('code_score', 0):.2f}",
                f"{item.get('file_score', 0):.2f}",
                f"{item.get('balance_score', 0):.2f}",
                f"{item.get('final_score', item.get('score', 0)):.2f}",
                item.get("contribution_level", ""),
                item.get("contribution_type", ""),
                item.get("ai_summary", ""),
            ]

            for col, value in enumerate(values):
                table_item = QTableWidgetItem(str(value))
                if col not in {1, 12, 13, 14}:
                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.contributorTable.setItem(row, col, table_item)

        self.contributorTable.resizeRowsToContents()

    def _kiem_tra_co_ket_qua(self):
        if not self.current_result:
            QMessageBox.information(self, "Chưa có dữ liệu", "Hãy phân tích repository trước.")
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

    def luu_lich_su(self):
        if not self._kiem_tra_co_ket_qua():
            return

        try:
            new_id = self.db_manager.luu_lich_su(self.current_result)
        except Exception as exc:
            QMessageBox.critical(self, "Lỗi lưu lịch sử", str(exc))
            return

        self.tai_lich_su()
        QMessageBox.information(self, "Đã lưu lịch sử", f"Đã lưu lần phân tích ID {new_id}.")

    def tai_lich_su(self):
        rows = self.db_manager.lay_lich_su()
        headers = [
            "ID",
            "Thời gian",
            "Owner",
            "Repo",
            "Commit",
            "Contributor",
            "Top contributor",
            "Tổng điểm",
            "Additions",
            "Deletions",
        ]
        self.historyTable.setColumnCount(len(headers))
        self.historyTable.setHorizontalHeaderLabels(headers)
        self.historyTable.setRowCount(len(rows))

        for row_index, row in enumerate(rows):
            values = [
                row.get("id", ""),
                row.get("analyzed_at", ""),
                row.get("owner", ""),
                row.get("repo", ""),
                row.get("commit_count", 0),
                row.get("contributor_count", 0),
                row.get("top_contributor", ""),
                f"{row.get('total_score', 0):.2f}",
                row.get("total_additions", 0),
                row.get("total_deletions", 0),
            ]
            for col, value in enumerate(values):
                table_item = QTableWidgetItem(str(value))
                if col in {0, 4, 5, 7, 8, 9}:
                    table_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.historyTable.setItem(row_index, col, table_item)

        self.historyTable.resizeRowsToContents()

