"""GĐ6 – Explainability: global importance + reason codes cho từng sinh viên.

* Global: permutation importance trên VALID (độc lập loại mô hình); SHAP nếu đã cài.
* Local: reason codes theo LUẬT minh bạch, viết bằng ngôn ngữ hỗ trợ.
  Ngưỡng của luật lấy từ phân vị của tập TRAIN (không nhìn test).

Output:
  reports/explainability_report.md, reports/feature_importance.csv
  reports/figures/aq7_feature_importance.png
  data/processed/reason_codes.parquet
"""

from __future__ import annotations

import pandas as pd
from sklearn.inspection import permutation_importance

from . import features as feat_mod
from . import plotting
from .config import Config
from .governance import audit, check_language
from .model import load_main

plt = plotting.plt


def reason_rules(train: pd.DataFrame) -> list[dict]:
    """Mỗi luật: feature liên quan, điều kiện, câu giải thích (ngôn ngữ hỗ trợ)."""
    q = train.quantile(0.25, numeric_only=True)
    return [
        {"feature": "first_assess_missing", "when": lambda r: r.get("first_assess_missing", 0) == 1,
         "text": lambda r: "Chưa nộp bài đánh giá đầu tiên – nên hỏi thăm khó khăn"},
        {"feature": "n_missing", "when": lambda r: r.get("n_missing", 0) >= 1,
         "text": lambda r: f"Còn {int(r['n_missing'])} bài đánh giá đầu kỳ chưa nộp"},
        {"feature": "engagement_change", "when": lambda r: r.get("engagement_change", 0) <= min(q.get("engagement_change", -1), -0.3),
         "text": lambda r: "Hoạt động trên LMS giảm rõ ở Tuần 4–6 so với Tuần 1–3"},
        {"feature": "active_days_total", "when": lambda r: r.get("active_days_total", 99) <= q.get("active_days_total", 0),
         "text": lambda r: f"Số ngày học trên LMS ({int(r['active_days_total'])} ngày) thuộc nhóm 25% thấp nhất lớp"},
        {"feature": "inactive_weeks", "when": lambda r: r.get("inactive_weeks", 0) >= 2,
         "text": lambda r: f"{int(r['inactive_weeks'])} tuần không có hoạt động LMS"},
        {"feature": "mean_score", "when": lambda r: pd.notna(r.get("mean_score")) and r["mean_score"] < 40,
         "text": lambda r: f"Điểm trung bình bài đầu kỳ ({r['mean_score']:.0f}) chưa đạt ngưỡng 40 – cần hỗ trợ thêm"},
        {"feature": "n_late", "when": lambda r: r.get("n_late", 0) >= 1,
         "text": lambda r: f"Có {int(r['n_late'])} bài nộp muộn"},
    ]


def reason_codes(df: pd.DataFrame, rules: list[dict], importance: pd.Series, top: int = 3) -> pd.Series:
    order = sorted(rules, key=lambda rl: -importance.get(rl["feature"], 0))
    out = []
    for _, r in df.iterrows():
        rd = r.to_dict()
        hits = [rl["text"](rd) for rl in order if rl["when"](rd)]
        out.append(hits[:top] if hits else ["Không có tín hiệu nổi bật – xem chi tiết điểm/hoạt động"])
    return pd.Series(out, index=df.index)


def run(cfg: Config) -> dict:
    plotting.setup()
    df, feature_cols = feat_mod.load(cfg)
    pop = df[df["in_prediction_population"]]
    train, valid = pop[pop["split"] == "train"], pop[pop["split"] == "valid"]
    model, main, thr, _ = load_main(cfg)

    pi = permutation_importance(model, valid[feature_cols], valid["y"], scoring="average_precision",
                                n_repeats=5, random_state=cfg.seed)
    imp = pd.Series(pi.importances_mean, index=feature_cols).sort_values(ascending=False)
    reports = cfg.path("reports_dir")
    imp.rename("perm_importance_pr_auc").to_csv(reports / "feature_importance.csv")

    top = imp.head(12)[::-1]
    fig, ax = plt.subplots(figsize=(7, 4.5))
    ax.barh(top.index, top.values, color="#4575b4")
    ax.set_xlabel("Mức giảm PR-AUC khi xáo trộn feature (valid)")
    ax.set_title(f"AQ7 · Feature quan trọng nhất ({main})")
    plotting.save(fig, cfg.path("figures_dir") / "aq7_feature_importance.png")

    shap_note = "SHAP chưa cài (`pip install shap`) – dùng permutation importance."
    try:  # tuỳ chọn
        import shap  # noqa: F401

        shap_note = "Đã cài SHAP – có thể bổ sung beeswarm trong notebook (notebooks/)."
    except ImportError:
        pass

    rules = reason_rules(train[feature_cols])
    scored = df[df["split"].isin(["valid", "test"]) & df["in_prediction_population"]].copy()
    scored["reasons"] = reason_codes(scored, rules, imp)
    bad = check_language([t for rs in scored["reasons"] for t in rs])
    if bad:
        raise ValueError(f"Reason code vi phạm quy tắc ngôn ngữ: {bad[:3]}")
    scored[["pid", "code_presentation", "reasons"]].to_parquet(
        cfg.path("processed_dir") / "reason_codes.parquet", index=False)

    md = [
        "# Explainability Report (tự sinh)",
        "",
        f"Mô hình chính: **{main}**. {shap_note}",
        "",
        "## Global – Permutation importance (valid, thước đo PR-AUC)",
        "",
        "![](figures/aq7_feature_importance.png)",
        "",
        imp.head(15).round(4).rename("importance").to_frame().to_markdown(),
        "",
        "## Local – Reason codes",
        "",
        "Reason code là luật minh bạch (không phải SHAP), ngưỡng lấy từ tập train, xếp theo",
        "độ quan trọng toàn cục của feature liên quan. Tất cả dùng ngôn ngữ hỗ trợ.",
        "",
        "| Feature | Ví dụ câu giải thích |",
        "|---|---|",
    ]
    for rl in rules:
        ex = scored[[rl["when"](r) for r in scored.to_dict("records")]]
        sample = rl["text"](ex.iloc[0].to_dict()) if len(ex) else "(không có ca nào)"
        md.append(f"| `{rl['feature']}` | {sample} |")
    md += ["", "> Giới hạn: reason code mô tả tín hiệu dữ liệu, KHÔNG phải nguyên nhân. "
           "Cố vấn cần trao đổi với sinh viên để hiểu bối cảnh thật."]
    (reports / "explainability_report.md").write_text("\n".join(md), encoding="utf-8")
    audit(cfg, "explain", main=main)
    return {"importance": imp}
