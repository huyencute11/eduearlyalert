"""M4 Level 2 - ba hình tổng hợp tám thực nghiệm (4 bộ dữ liệu x 2 mốc dự báo), chỉ trên tập kiểm tra.

Đọc output của scripts/m4_level2.py ở reports/m4_level2/<tag>/ (không huấn luyện lại, không đọc dữ liệu sinh viên):
  aq7_pr_curve_test.csv, aq7_calibration_test.csv, aq7_metrics.csv, aq10_coverage_by_k.csv, experiment_log.json
Ghi vào reports/m4_level2/summary/:
  aq7_pr_tam_thuc_nghiem.png            AQ7: đường precision-recall
  aq7_calibration_tam_thuc_nghiem.png   AQ7: calibration (10 nhóm theo phân vị)
  aq10_coverage_tam_thuc_nghiem.png     AQ10: độ bao phủ theo K
Bố cục giống Bảng 7.1a, 7.1b của N03_Milestone4: hàng = mốc dự báo (Tuần 4, Tuần 6), cột = bộ dữ liệu.
Chạy: python scripts/m4_level2_figures.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from matplotlib.ticker import FuncFormatter

from eduearlyalert import plotting

plt = plotting.plt
ROOT = Path(__file__).resolve().parents[1]
REP = ROOT / "reports" / "m4_level2"
DATASETS = [("FFF 2013B:2014B", "fff_13b_14b"), ("FFF 2013J:2014J", "fff_13j_14j"), ("FFF 2013B:2014J", ""), ("EEE 2013J:2014J", "eee")]
WEEKS = [("Tuần 4", "week4"), ("Tuần 6", "week6")]
# Hai màu phân loại đã kiểm tra khả năng phân biệt (kể cả mù màu); nét đứt / nét liền là mã hoá thứ hai khi in đen trắng.
C_GB, C_LR, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#1f1f1e", "#8a8984", "#e4e3df"


def tag_of(ds: str, wk: str) -> str:
    """Tag của thực nghiệm: bộ FFF 2013B:2014J dùng tag week4 / week6, EEE ở Tuần 6 dùng tag eee."""
    if ds == "":
        return wk
    if ds == "eee":
        return "eee" if wk == "week6" else "eee_week4"
    return f"{ds}_{wk}"


def load(tag: str) -> dict:
    d = REP / tag
    m = pd.read_csv(d / "aq7_metrics.csv"); m = m[m["split"] == "test"].set_index("model")
    cov = pd.read_csv(d / "aq10_coverage_by_k.csv")
    return {"pr": pd.read_csv(d / "aq7_pr_curve_test.csv"), "cal": pd.read_csv(d / "aq7_calibration_test.csv"), "m": m,
            "cov": cov[cov["split"] == "test"], "log": json.loads((d / "experiment_log.json").read_text())}


def grid(title: str, xlabel: str, ylabel: str, xlim, ylim):
    fig, axes = plt.subplots(2, 4, figsize=(7.4, 4.5), sharex=True, sharey=True)
    for i, (wk_label, _) in enumerate(WEEKS):
        for j, (ds_label, _) in enumerate(DATASETS):
            ax = axes[i, j]
            ax.set_xlim(*xlim); ax.set_ylim(*ylim)
            ax.grid(True, color=GRID, lw=0.6); ax.set_axisbelow(True)
            ax.tick_params(labelsize=7, colors=INK, length=2)
            for sp in ("left", "bottom"):
                ax.spines[sp].set_color(MUTED); ax.spines[sp].set_linewidth(0.6)
            if i == 0:
                ax.set_title(ds_label, fontsize=8.5, fontweight="bold", color=INK, pad=4)
            if j == 0:
                ax.set_ylabel(f"{wk_label}\n{ylabel}", fontsize=8, color=INK)
    fig.supxlabel(xlabel, fontsize=8, color=INK, y=0.06)
    fig.suptitle(title, fontsize=10, fontweight="bold", color=INK, x=0.01, y=0.995, ha="left")
    return fig, axes


def comma(nd: int):
    """Số thập phân dùng dấu phẩy như trong báo cáo."""
    return FuncFormatter(lambda v, _: f"{v:.{nd}f}".replace(".", ","))


def finish(fig, axes, path: Path, ncol: int):
    handles, labels = axes[1, 0].get_legend_handles_labels()   # ô FFF 2013B:2014B ở Tuần 6 có đủ mọi thành phần
    fig.legend(handles, labels, loc="upper left", bbox_to_anchor=(0.005, 0.955), ncol=ncol, fontsize=7.5, frameon=False,
               handlelength=2.6, columnspacing=1.4)   # chú giải nằm riêng một dòng dưới tiêu đề
    fig.tight_layout(rect=(0, 0.075, 1, 0.865))
    plotting.save(fig, path)
    print("đã ghi", path.relative_to(ROOT))


def main() -> None:
    plotting.setup()
    plt.rcParams["savefig.dpi"] = 220
    out = REP / "summary"; out.mkdir(parents=True, exist_ok=True)
    data = {(wk, ds): load(tag_of(ds, wk)) for _, wk in WEEKS for _, ds in DATASETS}

    # ---- AQ7: precision-recall
    fig, axes = grid("AQ7 · Precision-Recall trên tập kiểm tra · tám thực nghiệm", "Recall", "Precision", (0, 1.02), (0.25, 1.02))
    for i, (_, wk) in enumerate(WEEKS):
        for j, (_, ds) in enumerate(DATASETS):
            ax, e = axes[i, j], data[(wk, ds)]
            for key, lab, col, ls in (("gb", "XGBoost", C_GB, (0, (4, 2))), ("lr", "LR", C_LR, "-")):
                c = e["pr"][e["pr"]["model"] == key]
                ax.plot(c["recall"], c["precision"], color=col, lw=1.3, ls=ls, label=lab)
            ax.axhline(float(e["m"].loc["Tỷ lệ nền", "pr_auc"]), color=MUTED, lw=0.9, ls=(0, (1, 2)), label="Tỷ lệ nền")
            ax.axvline(0.80, color=MUTED, lw=0.6, label="Recall = 0,80")
            ax.xaxis.set_major_formatter(comma(1)); ax.yaxis.set_major_formatter(comma(1))
            lr = e["m"].loc["Logistic regression"]
            ax.plot([lr["thr_recall"]], [lr["thr_precision"]], marker="D", ms=4.5, color=C_LR, mec="white", mew=0.8, ls="none",
                    label="Ngưỡng đã chọn của LR", zorder=5)
            if e["log"].get("rule_defined", True):
                r = e["m"].loc["Luật TMA1"]
                ax.plot([r["thr_recall"]], [r["thr_precision"]], marker="o", ms=4.5, color=INK, mec="white", mew=0.8, ls="none",
                        label="Luật TMA1", zorder=5)
            else:
                ax.text(1.0, 1.0, "Chưa có bài đánh giá\nđến hạn: không có\nluật TMA1", fontsize=6.3, color=INK, va="top", ha="right",
                        bbox={"facecolor": "white", "edgecolor": "none", "pad": 1.5})   # góc trên phải của ô này trống
    finish(fig, axes, out / "aq7_pr_tam_thuc_nghiem.png", ncol=6)

    # ---- AQ7: calibration
    fig, axes = grid("AQ7 · Calibration trên tập kiểm tra · tám thực nghiệm", "Xác suất dự báo", "Tỷ lệ y = 1 thực tế", (0, 1), (0, 1))
    for i, (_, wk) in enumerate(WEEKS):
        for j, (_, ds) in enumerate(DATASETS):
            ax, e = axes[i, j], data[(wk, ds)]
            ax.plot([0, 1], [0, 1], color=MUTED, lw=0.9, ls=(0, (1, 2)), label="Khớp hoàn toàn")
            for key, lab, col, ls, mk in (("gb", "XGBoost", C_GB, (0, (4, 2)), "s"), ("lr", "LR", C_LR, "-", "o")):
                c = e["cal"][e["cal"]["model"] == key]
                ax.plot(c["mean_pred"], c["observed"], color=col, lw=1.2, ls=ls, marker=mk, ms=3.6, mec="white", mew=0.6, label=lab)
            ax.set_xticks([0, 0.5, 1]); ax.xaxis.set_major_formatter(comma(1)); ax.yaxis.set_major_formatter(comma(1))
    finish(fig, axes, out / "aq7_calibration_tam_thuc_nghiem.png", ncol=3)

    # ---- AQ10: độ bao phủ theo K (mô hình được chọn ở cả tám thực nghiệm là LR)
    fig, axes = grid("AQ10 · Độ bao phủ theo K trên tập kiểm tra · tám thực nghiệm", "K (số sinh viên được liên hệ)",
                     "Độ bao phủ", (25, 360), (0, 0.75))
    for i, (_, wk) in enumerate(WEEKS):
        for j, (_, ds) in enumerate(DATASETS):
            ax, e = axes[i, j], data[(wk, ds)]
            assert e["log"]["decision"]["chosen"] == "logistic regression"
            c = e["cov"]
            ax.plot(c["K"], c["random"], color=MUTED, lw=0.9, ls=(0, (1, 2)), label="Chọn ngẫu nhiên")
            if e["log"].get("rule_defined", True):
                ax.plot(c["K"], c["rule"], color=INK, lw=1.0, ls=(0, (4, 2)), marker="s", ms=3.2, mec="white", mew=0.6, label="Luật TMA1")
            else:
                ax.text(0.96, 0.06, "Không có luật TMA1", transform=ax.transAxes, fontsize=6.3, color=INK, va="bottom", ha="right")
            ax.plot(c["K"], c["model"], color=C_LR, lw=1.3, marker="o", ms=3.6, mec="white", mew=0.6, label="LR")
            ax.axvline(70, color=MUTED, lw=0.6, label="K = 70 (năng lực giả định)")
            ax.set_xticks([70, 140, 210, 280, 350]); ax.yaxis.set_major_formatter(comma(1))
    finish(fig, axes, out / "aq10_coverage_tam_thuc_nghiem.png", ncol=4)


if __name__ == "__main__":
    main()
