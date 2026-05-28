from PyQt6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(10, 7), tight_layout=True)
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
        scores = [item.get("final_score", item.get("score", 0)) for item in data]
        commits = [item.get("commit_count", 0) for item in data]
        additions = [item.get("total_additions", 0) for item in data]
        deletions = [item.get("total_deletions", 0) for item in data]

        ax_score = self.figure.add_subplot(221)
        ax_commit = self.figure.add_subplot(222)
        ax_change = self.figure.add_subplot(223)
        ax_component = self.figure.add_subplot(224)

        ax_score.bar(names, scores, color="#2f7d5c")
        ax_score.set_title("Điểm đóng góp")
        ax_score.set_ylabel("Final score")
        ax_score.tick_params(axis="x", rotation=35, labelsize=8)

        ax_commit.bar(names, commits, color="#3b6ea8")
        ax_commit.set_title("Số commit")
        ax_commit.set_ylabel("Commit")
        ax_commit.tick_params(axis="x", rotation=35, labelsize=8)

        x_positions = range(len(names))
        width = 0.38
        ax_change.bar(
            [x - width / 2 for x in x_positions],
            additions,
            width=width,
            label="Additions",
            color="#4f9d69",
        )
        ax_change.bar(
            [x + width / 2 for x in x_positions],
            deletions,
            width=width,
            label="Deletions",
            color="#c75c5c",
        )
        ax_change.set_title("Additions / Deletions")
        ax_change.set_xticks(list(x_positions))
        ax_change.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
        ax_change.legend(fontsize=8)

        top = data[0]
        component_names = ["Commit", "Code", "File", "Balance"]
        component_scores = [
            top.get("commit_score", 0),
            top.get("code_score", 0),
            top.get("file_score", 0),
            top.get("balance_score", 0),
        ]
        ax_component.bar(component_names, component_scores, color="#8b6f3d")
        ax_component.set_ylim(0, 100)
        ax_component.set_title("Điểm thành phần của top contributor")
        ax_component.tick_params(axis="x", labelsize=8)

        self.canvas.draw()

