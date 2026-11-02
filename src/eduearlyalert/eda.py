"""GĐ4 – EDA theo Analytical Question (AQ1–AQ6), ≥ 8 biểu đồ có mục tiêu.

Mỗi hàm `aqX_*` = 1 biểu đồ, trả về một dict "finding" gồm câu hỏi, observation
(tự sinh từ số liệu) và đường dẫn hình. `run()` gom lại thành
reports/eda_findings.md – bảng Observation–Insight–Evidence–Limitation.
Cột Insight để TRỐNG (TODO) có chủ đích: insight là việc của con người.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

from . import plotting
from .config import Config
from .governance import audit
from .kg import add_assessment_key

plt = plotting.plt
OUTCOME_ORDER = ["Distinction", "Pass", "Fail", "Withdrawn"]


# ---------------------------------------------------------------------------
# Tiện ích thống kê
# ---------------------------------------------------------------------------
def cliffs_delta(a: np.ndarray, b: np.ndarray) -> float:
    """Effect size phi tham số: P(a>b) − P(a<b). |d|<.147 nhỏ, <.33 vừa, <.474 khá, còn lại lớn."""
    a, b = np.asarray(a), np.asarray(b)
    if len(a) == 0 or len(b) == 0:
        return float("nan")
    b_sorted = np.sort(b)
    gt = np.searchsorted(b_sorted, a, side="left").sum()
    lt = (len(b) - np.searchsorted(b_sorted, a, side="right")).sum()
    return float((gt - lt) / (len(a) * len(b)))


def holm(pvals: list[float]) -> list[float]:
    p = np.asarray(pvals, dtype=float)
    order = np.argsort(p)
    m = len(p)
    adj = np.empty(m)
    running = 0.0
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx])
        adj[idx] = min(1.0, running)
    return adj.tolist()


def _finding(aq, question, observation, fig, limitation):
    return {"aq": aq, "question": question, "observation": observation,
            "figure": fig.name if fig is not None else "", "limitation": limitation}


# ---------------------------------------------------------------------------
# AQ1 – Hiện trạng hoàn thành
# ---------------------------------------------------------------------------
def aq1_outcomes(df: pd.DataFrame, figdir) -> dict:
    tab = pd.crosstab(df["code_presentation"], df["final_result"], normalize="index")
    tab = tab.reindex(columns=[c for c in OUTCOME_ORDER if c in tab.columns])
    fig, ax = plt.subplots(figsize=(7, 4))
    bottom = np.zeros(len(tab))
    for c in tab.columns:
        ax.bar(tab.index, tab[c], bottom=bottom, label=c, color=plotting.OUTCOME_COLORS[c])
        bottom += tab[c].values
    ax.set_ylabel("Tỷ lệ sinh viên")
    ax.set_title("AQ1 · Kết quả cuối kỳ theo lượt giảng dạy")
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.12), frameon=False)
    path = plotting.save(fig, figdir / "aq1_outcomes_by_presentation.png")
    comp = df.groupby("code_presentation")["final_result"].apply(lambda s: s.isin(["Pass", "Distinction"]).mean())
    obs = "Completion rate theo lượt: " + ", ".join(f"{k} {v:.1%}" for k, v in comp.items()) + \
          f". Toàn bộ: {df['final_result'].isin(['Pass','Distinction']).mean():.1%} (n={len(df)})."
    return _finding("AQ1", "Tỷ lệ hoàn thành / Fail / Withdrawn theo lượt giảng dạy?", obs, path,
                    "Dữ liệu Anh 2013–2014; baseline 60% trong proposal là assumption, cần cập nhật theo số này.")


def aq1_cumulative_withdrawal(df: pd.DataFrame, figdir, cfg: Config) -> dict:
    wl = cfg["timeline"]["week_length"]
    max_week = int(np.ceil(df["module_presentation_length"].max() / wl))
    fig, ax = plt.subplots(figsize=(7, 4))
    after_share = []
    for pres, g in df.groupby("code_presentation"):
        wk = np.floor(g["date_unregistration"].dropna() / wl) + 1
        weeks = np.arange(0, max_week + 1)
        cum = [(wk <= w).sum() / len(g) for w in weeks]
        ax.plot(weeks, cum, label=pres)
        n_w = g["date_unregistration"].notna().sum()
        if n_w:
            after_share.append((pres, (g["date_unregistration"] > cfg.cutoff_day).sum() / n_w))
    cut_week = (cfg.cutoff_day + 1) / wl
    ax.axvline(cut_week, ls="--", color="#555")
    ax.text(cut_week + 0.3, ax.get_ylim()[1] * 0.92, "mốc dự báo\n(hết Tuần 6)", fontsize=8)
    ax.set_xlabel("Tuần học")
    ax.set_ylabel("Tỷ lệ rút môn tích luỹ")
    ax.set_title("AQ1 · Rút môn tích luỹ theo tuần")
    ax.legend(frameon=False)
    path = plotting.save(fig, figdir / "aq1_cumulative_withdrawal.png")
    obs = "Trong số sinh viên rút môn, tỷ lệ rút SAU mốc dự báo: " + \
          ", ".join(f"{p} {s:.0%}" for p, s in after_share) + " → đây là cửa sổ còn can thiệp được."
    return _finding("AQ1", "Rút môn diễn ra vào tuần nào? Còn bao nhiêu % rút sau Tuần 6?", obs, path,
                    "Ngày rút môn có thể là ngày ghi nhận hành chính, không phải ngày thực sự ngừng học.")


# ---------------------------------------------------------------------------
# AQ2 – Tương tác VLE 6 tuần đầu
# ---------------------------------------------------------------------------
def aq2_heatmap(weekly: pd.DataFrame, n_students: int, figdir) -> dict:
    t = weekly.groupby(["activity_type", "week"])["clicks"].sum().unstack(fill_value=0) / max(n_students, 1)
    t = t.loc[t.sum(axis=1).sort_values(ascending=False).index[:12]]
    fig, ax = plt.subplots(figsize=(7, 5))
    im = ax.imshow(np.log1p(t.values), aspect="auto", cmap="Blues")
    ax.set_xticks(range(t.shape[1]), [f"T{w}" if w > 0 else "Trước" for w in t.columns])
    ax.set_yticks(range(t.shape[0]), t.index)
    for i in range(t.shape[0]):
        for j in range(t.shape[1]):
            ax.text(j, i, f"{t.values[i, j]:.0f}", ha="center", va="center", fontsize=7)
    fig.colorbar(im, ax=ax, label="log(1 + click TB/sinh viên)")
    ax.set_title("AQ2 · Click trung bình/sinh viên theo tuần × loại tài nguyên")
    path = plotting.save(fig, figdir / "aq2_heatmap_week_activity.png")
    top = t.sum(axis=1).head(3)
    obs = "3 loại tài nguyên nhiều click nhất: " + ", ".join(f"{k} ({v:.0f} click/SV)" for k, v in top.items()) + "."
    return _finding("AQ2", "Tương tác VLE phân bố thế nào theo tuần và loại tài nguyên?", obs, path,
                    "Click là proxy của tương tác, không đo được chất lượng học (góp ý của Lecturer).")


def aq2_weekly_box(feat: pd.DataFrame, figdir) -> dict:
    cols = sorted([c for c in feat.columns if c.startswith("clicks_w")], key=lambda c: int(c[8:]))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.boxplot([np.log1p(feat[c]) for c in cols], showfliers=False)
    ax.set_xticks(range(1, len(cols) + 1), [c.replace("clicks_w", "T") for c in cols])
    ax.set_ylabel("log(1 + click/tuần)")
    ax.set_title("AQ2 · Phân bố click theo tuần (6 tuần đầu)")
    path = plotting.save(fig, figdir / "aq2_clicks_by_week_box.png")
    zero = {c: (feat[c] == 0).mean() for c in cols}
    obs = "Tỷ lệ sinh viên 0 click: " + ", ".join(f"{c.replace('clicks_w','T')} {v:.0%}" for c, v in zero.items()) + "."
    return _finding("AQ2", "Mức tương tác của lớp thay đổi thế nào qua từng tuần?", obs, path,
                    "Tổng hợp theo tuần làm mất dao động trong tuần.")


# ---------------------------------------------------------------------------
# AQ3 – Nộp bài và điểm đầu kỳ
# ---------------------------------------------------------------------------
def aq3_submission(long: pd.DataFrame, figdir) -> dict:
    lk = add_assessment_key(long)
    t = pd.crosstab(lk["assessment_key"], lk["status"], normalize="index").reindex(
        columns=["on_time", "late", "missing"], fill_value=0)
    fig, ax = plt.subplots(figsize=(7, 4))
    left = np.zeros(len(t))
    colors = {"on_time": "#4575b4", "late": "#fdae61", "missing": "#d73027"}
    labels = {"on_time": "Đúng hạn", "late": "Muộn", "missing": "Chưa nộp (tại mốc)"}
    for c in t.columns:
        ax.barh(t.index, t[c], left=left, color=colors[c], label=labels[c])
        left += t[c].values
    ax.set_xlabel("Tỷ lệ sinh viên")
    ax.set_title("AQ3 · Tình trạng nộp bài đánh giá đầu kỳ")
    ax.legend(ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.15), frameon=False)
    path = plotting.save(fig, figdir / "aq3_submission_status.png")
    obs = "Tỷ lệ chưa nộp tại mốc: " + ", ".join(f"{k} {v:.0%}" for k, v in t["missing"].items()) + "."
    return _finding("AQ3", "Tỷ lệ nộp đúng hạn / muộn / không nộp từng bài đầu kỳ?", obs, path,
                    "Bài nộp sau ngày 41 bị tính là 'chưa nộp' vì chưa quan sát được tại mốc dự báo.")


def aq3_scores(long: pd.DataFrame, figdir) -> dict:
    lk = add_assessment_key(long).dropna(subset=["score"])
    keys = sorted(lk["assessment_key"].unique())
    fig, ax = plt.subplots(figsize=(7, 4))
    for k in keys:
        ax.hist(lk.loc[lk["assessment_key"] == k, "score"], bins=20, range=(0, 100), alpha=0.5, label=k)
    ax.axvline(40, ls="--", color="#555")
    ax.set_xlabel("Điểm")
    ax.set_ylabel("Số sinh viên")
    ax.set_title("AQ3 · Phân bố điểm các bài đầu kỳ (ngưỡng đạt 40)")
    ax.legend(frameon=False)
    path = plotting.save(fig, figdir / "aq3_score_distribution.png")
    med = lk.groupby("assessment_key")["score"].median()
    obs = "Điểm trung vị: " + ", ".join(f"{k} {v:.0f}" for k, v in med.items()) + "."
    return _finding("AQ3", "Điểm trung vị và phân bố điểm của từng bài đầu kỳ?", obs, path,
                    "Chỉ tính bài đã nộp; sinh viên không nộp không xuất hiện trong histogram.")


# ---------------------------------------------------------------------------
# AQ4 – Chỉ báo engagement khác biệt giữa hai nhóm
# ---------------------------------------------------------------------------
AQ4_INDICATORS = ["clicks_total", "active_days_total", "inactive_weeks", "engagement_change", "clicks_pre_start"]


def aq4_group_comparison(pop: pd.DataFrame, figdir, reports) -> dict:
    rows = []
    for c in AQ4_INDICATORS:
        a, b = pop.loc[pop["y"] == 0, c].dropna(), pop.loc[pop["y"] == 1, c].dropna()
        if len(a) < 2 or len(b) < 2:
            continue
        p = stats.mannwhitneyu(a, b, alternative="two-sided").pvalue
        rows.append({"indicator": c, "median_completed": a.median(), "median_not_completed": b.median(),
                     "cliffs_delta": cliffs_delta(a.values, b.values), "p_value": p})
    res = pd.DataFrame(rows)
    res["p_holm"] = holm(res["p_value"].tolist())
    res["magnitude"] = pd.cut(res["cliffs_delta"].abs(), [-1, .147, .33, .474, 2],
                              labels=["không đáng kể", "nhỏ", "vừa", "lớn"])
    res.round(4).to_csv(reports / "aq4_group_comparison.csv", index=False)

    fig, axes = plt.subplots(1, 2, figsize=(9, 4))
    data = [pop.loc[pop["y"] == k, "active_days_total"] for k in (0, 1)]
    parts = axes[0].violinplot(data, showmedians=True)
    for body, k in zip(parts["bodies"], (0, 1)):
        body.set_facecolor(plotting.GROUP_COLORS[k])
    axes[0].set_xticks([1, 2], [plotting.GROUP_LABELS[0], plotting.GROUP_LABELS[1]])
    axes[0].set_ylabel("Số ngày hoạt động (ngày ≤ 41)")
    axes[0].set_title("Số ngày hoạt động theo nhóm")
    r = res.sort_values("cliffs_delta")
    axes[1].barh(r["indicator"], r["cliffs_delta"], color="#777")
    axes[1].axvline(0, color="k", lw=0.8)
    axes[1].set_xlabel("Cliff's delta (hoàn thành vs không)")
    axes[1].set_title("Effect size các chỉ báo")
    fig.suptitle("AQ4 · Chỉ báo engagement: nhóm hoàn thành vs không hoàn thành", fontweight="bold")
    path = plotting.save(fig, figdir / "aq4_engagement_by_outcome.png")
    top = res.reindex(res["cliffs_delta"].abs().sort_values(ascending=False).index).head(3)
    obs = "Chỉ báo khác biệt lớn nhất (Cliff's δ, p Holm): " + "; ".join(
        f"{r.indicator} δ={r.cliffs_delta:.2f} ({r.magnitude}), p={r.p_holm:.1e}" for r in top.itertuples()) + "."
    return _finding("AQ4", "Chỉ báo engagement Tuần 1–6 khác biệt đến mức nào giữa hai nhóm?", obs, path,
                    "Khác biệt/liên hệ, KHÔNG phải nhân quả. Với n lớn, p nhỏ là dễ – đọc effect size.")


def aq4_weekly_lines(pop: pd.DataFrame, figdir) -> dict:
    cols = sorted([c for c in pop.columns if c.startswith("clicks_w")], key=lambda c: int(c[8:]))
    fig, ax = plt.subplots(figsize=(7, 4))
    med = {}
    for k in (0, 1):
        m = pop.loc[pop["y"] == k, cols].median()
        med[k] = m
        ax.plot(range(1, len(cols) + 1), m.values, marker="o", color=plotting.GROUP_COLORS[k],
                label=plotting.GROUP_LABELS[k])
    ax.set_xticks(range(1, len(cols) + 1), [c.replace("clicks_w", "T") for c in cols])
    ax.set_ylabel("Trung vị click/tuần")
    ax.set_title("AQ4 · Hai nhóm tách nhau từ tuần nào?")
    ax.legend(frameon=False)
    path = plotting.save(fig, figdir / "aq4_weekly_median_clicks.png")
    ratio = (med[1] + 1) / (med[0] + 1)
    obs = "Tỷ số trung vị click (không hoàn thành / hoàn thành): " + \
          ", ".join(f"{c.replace('clicks_w','T')} {v:.2f}" for c, v in ratio.items()) + "."
    return _finding("AQ4", "Đường tương tác của hai nhóm tách nhau từ tuần nào?", obs, path,
                    "Trung vị che khuất sự đa dạng trong từng nhóm.")


# ---------------------------------------------------------------------------
# AQ5 – Điểm & hành vi nộp bài liên hệ với hoàn thành
# ---------------------------------------------------------------------------
def aq5_first_score(pop: pd.DataFrame, figdir) -> dict:
    s = pop.copy()
    s["bin"] = pd.cut(s["first_assess_score"], [-0.1, 40, 60, 80, 100], labels=["<40", "40–60", "60–80", "80–100"])
    s["bin"] = s["bin"].cat.add_categories(["Chưa nộp"])
    s.loc[s["first_assess_missing"] == 1, "bin"] = "Chưa nộp"
    t = s.groupby("bin", observed=False).agg(n=("y", "size"), completion=("y", lambda v: 1 - v.mean()))
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.bar(t.index.astype(str), t["completion"], color="#4575b4")
    for i, (c, n) in enumerate(zip(t["completion"], t["n"])):
        if n:
            ax.text(i, c + 0.01, f"{c:.0%}\n(n={n})", ha="center", fontsize=8)
    ax.set_ylim(0, 1.1)
    ax.set_xlabel("Điểm bài đánh giá đầu tiên")
    ax.set_ylabel("Tỷ lệ hoàn thành")
    ax.set_title("AQ5 · Tỷ lệ hoàn thành theo điểm bài đầu tiên")
    path = plotting.save(fig, figdir / "aq5_completion_by_first_score.png")
    obs = "Tỷ lệ hoàn thành: " + ", ".join(f"{k} {v:.0%}" for k, v in t["completion"].dropna().items()) + "."
    return _finding("AQ5", "Điểm bài đầu tiên liên hệ thế nào với khả năng hoàn thành?", obs, path,
                    "Liên hệ, không nhân quả; nhóm 'chưa nộp' gộp nhiều lý do khác nhau.")


def aq5_explanatory_regression(pop: pd.DataFrame, figdir, reports) -> dict:
    cols = ["first_assess_score", "share_missing", "n_late", "active_days_total", "engagement_change"]
    d = pop[cols + ["y"]].copy()
    d["first_assess_score"] = d["first_assess_score"].fillna(0)  # chưa nộp ~ 0 điểm, đã có cờ share_missing
    d = d.dropna()
    X = (d[cols] - d[cols].mean()) / d[cols].std(ddof=0).replace(0, 1)
    model = sm.Logit(d["y"], sm.add_constant(X)).fit(disp=False)
    ci = model.conf_int()
    res = pd.DataFrame({"odds_ratio_per_SD": np.exp(model.params), "ci_low": np.exp(ci[0]),
                        "ci_high": np.exp(ci[1]), "p_value": model.pvalues}).drop(index="const")
    res.round(4).to_csv(reports / "aq5_logit_odds_ratios.csv")
    fig, ax = plt.subplots(figsize=(7, 4))
    y = np.arange(len(res))
    ax.errorbar(res["odds_ratio_per_SD"], y, xerr=[res["odds_ratio_per_SD"] - res["ci_low"],
                res["ci_high"] - res["odds_ratio_per_SD"]], fmt="o", color="#333")
    ax.axvline(1, ls="--", color="#999")
    ax.set_yticks(y, res.index)
    ax.set_xscale("log")
    ax.set_xlabel("Odds ratio của KHÔNG hoàn thành / +1 SD (thang log, CI 95%)")
    ax.set_title("AQ5 · Hồi quy logistic giải thích (đã điều chỉnh lẫn nhau)")
    path = plotting.save(fig, figdir / "aq5_logit_coefficients.png")
    obs = "OR/SD: " + ", ".join(f"{k} {v:.2f}" for k, v in res["odds_ratio_per_SD"].items()) + \
          f". Pseudo R² = {model.prsquared:.3f}."
    return _finding("AQ5", "Sau khi điều chỉnh theo engagement, yếu tố bài đánh giá nào còn liên hệ mạnh?", obs, path,
                    "Mô hình giải thích, không phải dự báo; các biến tương quan nhau nên hệ số có thể không ổn định.")


# ---------------------------------------------------------------------------
# AQ6 – Concept/CLO hụt nhiều nhất (qua KG mô phỏng)
# ---------------------------------------------------------------------------
def aq6_concept_gaps(gaps: pd.DataFrame, pop: pd.DataFrame, figdir) -> dict | None:
    if gaps.empty:
        return None
    g = gaps.merge(pop[["pid", "code_presentation", "y"]], on=["pid", "code_presentation"])
    t = g.groupby(["concept_id", "y"])["needs_support"].mean().unstack().rename(columns=plotting.GROUP_LABELS)
    t = t.sort_values(t.columns[-1], ascending=True)
    fig, ax = plt.subplots(figsize=(7, 4))
    h = 0.4
    yy = np.arange(len(t))
    for i, (k, col) in enumerate(zip((0, 1), t.columns)):
        ax.barh(yy + (i - 0.5) * h, t[col], height=h, color=plotting.GROUP_COLORS[k], label=col)
    ax.set_yticks(yy, t.index)
    ax.set_xlabel("Tỷ lệ sinh viên cần hỗ trợ thêm ở concept (điểm hiệu dụng < 40)")
    ax.set_title("AQ6 · Concept cần hỗ trợ thêm, theo nhóm kết quả (KG MÔ PHỎNG)")
    ax.legend(frameon=False)
    path = plotting.save(fig, figdir / "aq6_concept_gaps.png",
                         "Nguồn: OULAD + ánh xạ Concept–CLO mô phỏng do Nhóm 3 xây dựng")
    top = t[t.columns[-1]].sort_values(ascending=False).head(3)
    obs = "Concept có tỷ lệ cần hỗ trợ cao nhất ở nhóm không hoàn thành: " + \
          ", ".join(f"{k} {v:.0%}" for k, v in top.items()) + "."
    return _finding("AQ6", "Concept/CLO nào nhiều sinh viên cần hỗ trợ thêm nhất?", obs, path,
                    "Ánh xạ concept là DỮ LIỆU MÔ PHỎNG và ở mức bài, không phải mức câu hỏi.")


# ---------------------------------------------------------------------------
def run(cfg: Config) -> list[dict]:
    plotting.setup()
    figdir, reports, interim, processed = (cfg.path(k) for k in
                                           ("figures_dir", "reports_dir", "interim_dir", "processed_dir"))
    feat = pd.read_parquet(processed / "features.parquet")
    coh = pd.read_parquet(interim / "cohort.parquet")
    weekly = pd.read_parquet(interim / "vle_weekly.parquet")
    long = pd.read_parquet(interim / "assess_long.parquet")
    gaps_path = interim / "concept_gaps.parquet"
    gaps = pd.read_parquet(gaps_path) if gaps_path.exists() else pd.DataFrame()

    # EDA chỉ trên train+valid để không "nhìn trộm" tập test
    eda_df = feat[feat["split"].isin(["train", "valid"])]
    eda_coh = coh[coh["split"].isin(["train", "valid"])]
    pop = eda_df[eda_df["in_prediction_population"]]
    pids = set(eda_df["pid"])

    findings = [
        aq1_outcomes(eda_coh, figdir),
        aq1_cumulative_withdrawal(eda_coh, figdir, cfg),
        aq2_heatmap(weekly[weekly["pid"].isin(pids)], len(eda_df), figdir),
        aq2_weekly_box(eda_df, figdir),
    ]
    long_e = long[long["pid"].isin(pids)]
    if not long_e.empty:
        findings += [aq3_submission(long_e, figdir), aq3_scores(long_e, figdir)]
    findings += [aq4_group_comparison(pop, figdir, reports), aq4_weekly_lines(pop, figdir)]
    if pop["first_assess_score"].notna().any():
        findings += [aq5_first_score(pop, figdir), aq5_explanatory_regression(pop, figdir, reports)]
    f6 = aq6_concept_gaps(gaps[gaps["pid"].isin(pids)] if not gaps.empty else gaps, pop, figdir)
    if f6:
        findings.append(f6)

    lines = [
        "# EDA Findings – Observation · Insight · Evidence · Limitation",
        "",
        "> Observation do code tự sinh từ dữ liệu train+valid (tập test được giữ kín).",
        "> **Insight phải do nhóm viết**: nối observation với một quyết định của stakeholder.",
        "> Không dùng từ 'gây ra', 'tác động', 'sinh viên yếu'.",
        "",
        f"Số biểu đồ: **{len(findings)}**",
        "",
    ]
    for i, f in enumerate(findings, 1):
        lines += [
            f"## {i}. {f['aq']} – {f['question']}",
            "",
            f"![{f['figure']}](figures/{f['figure']})",
            "",
            "| | |",
            "|---|---|",
            f"| **Observation** | {f['observation']} |",
            "| **Insight** | TODO (nhóm viết: điều này có nghĩa gì cho quyết định của ai?) |",
            f"| **Evidence** | `reports/figures/{f['figure']}` |",
            f"| **Limitation** | {f['limitation']} |",
            "",
        ]
    (reports / "eda_findings.md").write_text("\n".join(lines), encoding="utf-8")
    audit(cfg, "eda", n_figures=len(findings))
    return findings
