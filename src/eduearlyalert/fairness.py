"""AQ9 – Fairness audit. Thuộc tính nhạy cảm CHỈ được nối vào ở đây, sau khi đã dự báo.

Đo trên tập TEST với mô hình chính tại ngưỡng đã chọn:
  selection rate, recall, FNR (tỷ lệ bỏ sót), precision theo từng nhóm.
Nhóm < min_group_size bị ẩn số liệu.

Output: reports/fairness_report.md, reports/fairness_by_group.csv, reports/figures/aq9_*.png
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import cohort as cohort_mod
from . import plotting
from .config import Config
from .governance import audit, suppress_small_groups

plt = plotting.plt


def group_metrics(d: pd.DataFrame, attr: str) -> pd.DataFrame:
    rows = []
    for grp, g in d.groupby(attr, dropna=False):
        pos = g["y"] == 1
        tp = ((g["alert"] == 1) & pos).sum()
        rows.append({
            "attribute": attr, "group": "Không rõ" if pd.isna(grp) else str(grp), "n": len(g),
            "prevalence": pos.mean(), "selection_rate": g["alert"].mean(),
            "recall": tp / pos.sum() if pos.sum() else np.nan,
            "fnr": 1 - tp / pos.sum() if pos.sum() else np.nan,
            "precision": tp / g["alert"].sum() if g["alert"].sum() else np.nan,
        })
    return pd.DataFrame(rows)


def run(cfg: Config) -> pd.DataFrame:
    plotting.setup()
    preds = pd.read_parquet(cfg.path("processed_dir") / "predictions.parquet")
    test = preds[preds["split"] == "test"].merge(cohort_mod.load_sensitive(cfg), on=["pid", "code_presentation"])
    min_n = cfg["fairness"]["min_group_size"]

    tabs = [group_metrics(test, a) for a in cfg.sensitive if a in test.columns]
    res = suppress_small_groups(pd.concat(tabs, ignore_index=True), "n", min_n)
    reports = cfg.path("reports_dir")
    res.round(3).to_csv(reports / "fairness_by_group.csv", index=False)

    disp = (res.dropna(subset=["recall"]).groupby("attribute")
            .agg(recall_min=("recall", "min"), recall_max=("recall", "max")))
    disp["recall_gap"] = disp["recall_max"] - disp["recall_min"]

    attrs = list(res["attribute"].unique())
    fig, axes = plt.subplots(len(attrs), 1, figsize=(7, 2.0 * len(attrs)))
    axes = np.atleast_1d(axes)
    overall = test.loc[test["y"] == 1, "alert"].mean()
    for ax, a in zip(axes, attrs):
        r = res[(res["attribute"] == a) & ~res["suppressed"]]
        ax.barh(r["group"], r["recall"], color="#4575b4")
        ax.axvline(overall, ls="--", color="#d73027")
        ax.set_xlim(0, 1)
        ax.set_title(a, fontsize=9, loc="left")
    axes[-1].set_xlabel("Recall theo nhóm (đường đỏ = Recall chung)")
    fig.suptitle("AQ9 · Recall của mô hình theo nhóm (chỉ audit, không dùng làm feature)", fontweight="bold")
    plotting.save(fig, cfg.path("figures_dir") / "aq9_recall_by_group.png")

    md = [
        "# Fairness Audit – AQ9 (tự sinh)",
        "",
        f"Tập test, n = {len(test)}. Recall chung = {overall:.3f}. Nhóm < {min_n} sinh viên bị ẩn.",
        "",
        "![](figures/aq9_recall_by_group.png)",
        "",
        "## Chênh lệch Recall lớn nhất theo thuộc tính",
        "",
        disp.round(3).to_markdown(),
        "",
        "## Chi tiết",
        "",
        res.round(3).to_markdown(index=False),
        "",
        "## Nhận định & hành động (nhóm điền)",
        "",
        "- Ngưỡng chênh lệch chấp nhận được (thống nhất với stakeholder): TODO",
        "- Nhóm bị bỏ sót nhiều hơn và hành động đề xuất (chấp nhận / điều chỉnh / dừng): TODO",
    ]
    (reports / "fairness_report.md").write_text("\n".join(md), encoding="utf-8")
    audit(cfg, "fairness", max_recall_gap=float(disp["recall_gap"].max()) if len(disp) else None)
    return res
