from PyQt6.QtWidgets import QVBoxLayout, QWidget
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


def _to_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _score_display(item, display_key, raw_key, fallback_key=None):
    if display_key in item and item.get(display_key) is not None:
        return _to_float(item.get(display_key))
    raw_value = item.get(raw_key, item.get(fallback_key, 0)) if fallback_key else item.get(raw_key, 0)
    raw_value = _to_float(raw_value)
    return round(max(raw_value, 0.0) / 10, 1)


def _penalty_display(item):
    if "penalty_score_display" in item and item.get("penalty_score_display") is not None:
        return _to_float(item.get("penalty_score_display"))
    penalty = _to_float(item.get("penalty_score", 0))
    return round(max(0.0, min(30.0, penalty)) / 30.0 * 10, 1)


def _short_label(text, max_chars=12):
    text = str(text or "unknown")
    return text if len(text) <= max_chars else text[: max_chars - 3] + "..."


def _annotate_bars(ax, values, fmt="{:.1f}"):
    for index, value in enumerate(values):
        ax.text(index, value, fmt.format(value), ha="center", va="bottom", fontsize=7)


def _style_axis(ax, title, ylabel=None):
    ax.set_title(title, fontsize=10, pad=8)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=9)
    ax.tick_params(axis="x", rotation=25, labelsize=9)
    ax.tick_params(axis="y", labelsize=9)


def _collect_chart_data(contributors, limit=10):
    data = contributors[:limit]
    names = [_short_label(item.get("contributor", item.get("tac_gia", ""))) for item in data]
    return {
        "names": names,
        "final_scores": [
            max(_score_display(item, "final_score_display", "final_score", "score"), 0)
            for item in data
        ],
        "quality_scores": [
            _score_display(item, "quality_score_display", "quality_score") for item in data
        ],
        "suspicious_counts": [item.get("suspicious_commit_count", 0) for item in data],
        "additions": [item.get("total_additions", item.get("additions", 0)) for item in data],
        "deletions": [item.get("total_deletions", item.get("deletions", 0)) for item in data],
        "penalty_scores": [_penalty_display(item) for item in data],
        "estimated_hours": [item.get("estimated_coding_hours", 0) for item in data],
        "active_days": [item.get("active_days", 0) for item in data],
    }


class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure = Figure(figsize=(12, 9))
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

        chart_data = _collect_chart_data(contributors)
        names = chart_data["names"]
        final_scores = chart_data["final_scores"]
        quality_scores = chart_data["quality_scores"]
        suspicious_counts = chart_data["suspicious_counts"]
        additions = chart_data["additions"]
        deletions = chart_data["deletions"]
        penalty_scores = chart_data["penalty_scores"]
        estimated_hours = chart_data["estimated_hours"]
        active_days = chart_data["active_days"]

        grid = self.figure.add_gridspec(
            2,
            4,
            width_ratios=[1.85, 1.0, 1.0, 1.0],
            height_ratios=[1.0, 1.0],
        )
        ax_pie = self.figure.add_subplot(grid[:, 0])
        ax_quality = self.figure.add_subplot(grid[0, 1])
        ax_suspicious = self.figure.add_subplot(grid[0, 2])
        ax_changes = self.figure.add_subplot(grid[0, 3])
        ax_penalty = self.figure.add_subplot(grid[1, 1])
        ax_time = self.figure.add_subplot(grid[1, 2])
        ax_days = self.figure.add_subplot(grid[1, 3])

        total_score = sum(final_scores)
        if total_score > 0:
            _wedges, labels, autotexts = ax_pie.pie(
                final_scores,
                labels=names,
                autopct="%1.1f%%",
                startangle=90,
                radius=1.25,
                labeldistance=1.14,
                pctdistance=0.65,
                textprops={"fontsize": 8},
                wedgeprops={"linewidth": 0.8, "edgecolor": "white"},
            )
            for text in labels:
                text.set_fontsize(8)
            for text in autotexts:
                text.set_fontsize(9)
                text.set_weight("bold")
        else:
            ax_pie.text(0.5, 0.5, "Chưa có điểm", ha="center", va="center")
        ax_pie.set_title("Tỷ lệ điểm cuối", fontsize=12, pad=14)
        ax_pie.set_aspect("equal")

        ax_quality.bar(names, quality_scores, color="#2f7d5c")
        ax_quality.set_ylim(0, 10)
        _style_axis(ax_quality, "Điểm chất lượng", "Điểm /10")
        ax_quality.grid(axis="y", alpha=0.25)
        _annotate_bars(ax_quality, quality_scores)

        ax_suspicious.bar(names, suspicious_counts, color="#c75c5c")
        _style_axis(ax_suspicious, "Commit cần xem lại", "Số commit")
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
        _style_axis(ax_changes, "Dòng thêm / xoá", "Số dòng")
        ax_changes.set_xticks(x_positions)
        ax_changes.set_xticklabels(names, rotation=25, ha="right", fontsize=9)
        ax_changes.legend(fontsize=8)
        ax_changes.grid(axis="y", alpha=0.25)

        ax_penalty.bar(names, penalty_scores, color="#8e5ea2")
        ax_penalty.set_ylim(0, 10)
        _style_axis(ax_penalty, "Điểm trừ", "Điểm trừ /10")
        ax_penalty.grid(axis="y", alpha=0.25)
        _annotate_bars(ax_penalty, penalty_scores)

        ax_time.bar(names, estimated_hours, color="#6aa84f")
        _style_axis(ax_time, "Giờ code ước tính", "Giờ")
        ax_time.grid(axis="y", alpha=0.25)
        _annotate_bars(ax_time, estimated_hours)

        ax_days.bar(names, active_days, color="#45818e")
        _style_axis(ax_days, "Số ngày hoạt động", "Ngày")
        ax_days.grid(axis="y", alpha=0.25)
        _annotate_bars(ax_days, active_days, fmt="{:.0f}")

        self.figure.subplots_adjust(
            left=0.05,
            right=0.98,
            top=0.90,
            bottom=0.16,
            wspace=0.35,
            hspace=0.55,
        )
        self.canvas.draw()
