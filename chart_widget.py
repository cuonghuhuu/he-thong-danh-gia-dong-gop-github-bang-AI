from PyQt6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(11, 5), tight_layout=True)
        self.canvas = FigureCanvas(self.figure)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self.update_charts([])

    def update_charts(self, contributors):
        self.figure.clear()

        if not contributors:
            ax = self.figure.add_subplot(111)
            ax.text(
                0.5,
                0.5,
                "Chưa có dữ liệu biểu đồ",
                ha="center",
                va="center",
                fontsize=12,
            )
            ax.axis("off")
            self.canvas.draw()
            return

        data = contributors[:10]
        names = [item.get("contributor", item.get("tac_gia", "")) for item in data]
        final_scores = [max(item.get("final_score", item.get("score", 0)), 0) for item in data]
        quality_scores = [item.get("quality_score", 0) for item in data]
        suspicious_counts = [item.get("suspicious_commit_count", 0) for item in data]

        ax_pie = self.figure.add_subplot(131)
        ax_quality = self.figure.add_subplot(132)
        ax_suspicious = self.figure.add_subplot(133)

        total_score = sum(final_scores)
        if total_score > 0:
            ax_pie.pie(
                final_scores,
                labels=names,
                autopct="%1.1f%%",
                textprops={"fontsize": 8},
                startangle=90,
            )
        else:
            ax_pie.text(0.5, 0.5, "Chưa có điểm", ha="center", va="center")
        ax_pie.set_title("Tỷ lệ đóng góp theo điểm cuối")

        ax_quality.bar(names, quality_scores, color="#2f7d5c")
        ax_quality.set_title("Điểm chất lượng của thành viên")
        ax_quality.set_ylabel("Điểm")
        ax_quality.set_ylim(0, 100)
        ax_quality.tick_params(axis="x", rotation=35, labelsize=8)

        ax_suspicious.bar(names, suspicious_counts, color="#c75c5c")
        ax_suspicious.set_title("Số commit cần xem lại")
        ax_suspicious.set_ylabel("Số commit")
        ax_suspicious.tick_params(axis="x", rotation=35, labelsize=8)

        self.canvas.draw()
