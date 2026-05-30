from PyQt6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


def _score_display(item, display_key, raw_key, fallback_key=None):
    if display_key in item and item.get(display_key) is not None:
        return float(item.get(display_key, 0))
    raw_value = item.get(raw_key, item.get(fallback_key, 0)) if fallback_key else item.get(raw_key, 0)
    try:
        raw_value = float(raw_value)
    except (TypeError, ValueError):
        raw_value = 0.0
    return round(max(raw_value, 0.0) / 10, 1)


def _penalty_display(item):
    if "penalty_score_display" in item and item.get("penalty_score_display") is not None:
        return float(item.get("penalty_score_display", 0))
    try:
        penalty = float(item.get("penalty_score", 0))
    except (TypeError, ValueError):
        penalty = 0.0
    return round(max(0.0, min(30.0, penalty)) / 30.0 * 10, 1)


def _short_label(text, max_chars=14):
    text = str(text or "Không rõ")
    return text if len(text) <= max_chars else text[: max_chars - 3] + "..."


def _annotate_bars(ax, values, fmt="{:.1f}"):
    for index, value in enumerate(values):
        ax.text(index, value, fmt.format(value), ha="center", va="bottom", fontsize=7)


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(12, 7), tight_layout=False)
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
                "Chưa có dữ liệu phân tích",
                ha="center",
                va="center",
                fontsize=12,
            )
            ax.axis("off")
            self.canvas.draw()
            return

        data = contributors[:10]
        names = [_short_label(item.get("contributor", item.get("tac_gia", ""))) for item in data]
        final_scores = [
            max(_score_display(item, "final_score_display", "final_score", "score"), 0)
            for item in data
        ]
        quality_scores = [
            _score_display(item, "quality_score_display", "quality_score") for item in data
        ]
        suspicious_counts = [item.get("suspicious_commit_count", 0) for item in data]
        additions = [item.get("total_additions", item.get("additions", 0)) for item in data]
        deletions = [item.get("total_deletions", item.get("deletions", 0)) for item in data]
        penalty_scores = [_penalty_display(item) for item in data]

        axes = self.figure.subplots(2, 3)
        ax_pie = axes[0][0]
        ax_quality = axes[0][1]
        ax_suspicious = axes[0][2]
        ax_changes = axes[1][0]
        ax_penalty = axes[1][1]
        axes[1][2].axis("off")

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
        ax_quality.set_ylabel("Điểm /10")
        ax_quality.set_ylim(0, 10)
        ax_quality.tick_params(axis="x", rotation=35, labelsize=8)
        ax_quality.grid(axis="y", alpha=0.25)
        _annotate_bars(ax_quality, quality_scores)

        ax_suspicious.bar(names, suspicious_counts, color="#c75c5c")
        ax_suspicious.set_title("Commit cần xem lại theo thành viên")
        ax_suspicious.set_ylabel("Số commit")
        ax_suspicious.tick_params(axis="x", rotation=35, labelsize=8)
        ax_suspicious.grid(axis="y", alpha=0.25)
        _annotate_bars(ax_suspicious, suspicious_counts, fmt="{:.0f}")

        x_positions = list(range(len(names)))
        bar_width = 0.38
        ax_changes.bar(
            [x - bar_width / 2 for x in x_positions],
            additions,
            width=bar_width,
            label="Dòng thêm",
            color="#3c78d8",
        )
        ax_changes.bar(
            [x + bar_width / 2 for x in x_positions],
            deletions,
            width=bar_width,
            label="Dòng xoá",
            color="#e69138",
        )
        ax_changes.set_title("So sánh dòng thêm và dòng xoá")
        ax_changes.set_ylabel("Số dòng")
        ax_changes.set_xticks(x_positions)
        ax_changes.set_xticklabels(names, rotation=35, ha="right", fontsize=8)
        ax_changes.legend(fontsize=8)
        ax_changes.grid(axis="y", alpha=0.25)

        ax_penalty.bar(names, penalty_scores, color="#8e5ea2")
        ax_penalty.set_title("Điểm trừ theo thành viên")
        ax_penalty.set_ylabel("Điểm trừ /10")
        ax_penalty.set_ylim(0, 10)
        ax_penalty.tick_params(axis="x", rotation=35, labelsize=8)
        ax_penalty.grid(axis="y", alpha=0.25)
        _annotate_bars(ax_penalty, penalty_scores)

        self.figure.subplots_adjust(
            left=0.06,
            right=0.98,
            top=0.92,
            bottom=0.12,
            wspace=0.35,
            hspace=0.62,
        )
        self.canvas.draw()
