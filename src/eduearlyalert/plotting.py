"""Style biểu đồ thống nhất cho cả nhóm (font hỗ trợ tiếng Việt, màu cố định)."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

OUTCOME_COLORS = {
    "Distinction": "#1b7837",
    "Pass": "#7fbf7b",
    "Fail": "#f4a582",
    "Withdrawn": "#b2182b",
}
GROUP_COLORS = {0: "#4575b4", 1: "#d73027"}  # 0 = hoàn thành, 1 = không hoàn thành
GROUP_LABELS = {0: "Hoàn thành", 1: "Không hoàn thành"}


def setup() -> None:
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",  # có đủ dấu tiếng Việt
            "figure.dpi": 110,
            "savefig.dpi": 150,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.titlesize": 12,
            "axes.titleweight": "bold",
        }
    )


def save(fig, path: Path, source_note: str = "Nguồn: OULAD (Kuzilek et al., 2017), CC-BY 4.0") -> Path:
    fig.text(0.01, 0.005, source_note, fontsize=7, color="#666")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path
