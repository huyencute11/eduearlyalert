"""AQ10–AQ12 – Ưu tiên liên hệ trong giới hạn năng lực cố vấn, gợi ý loại hỗ trợ, ngưỡng cảnh báo.

Chọn phương án (AQ10) và cung cấp bảng để nhóm chọn ngưỡng (AQ12) trên VALID. TEST chỉ dùng để
báo cáo kết quả cuối (`*_test.csv`), không bao giờ dùng để chọn – quy tắc 3 trong CLAUDE.md.
Risk List mô phỏng học kỳ hiện tại = lượt test, xếp theo phương án đã chọn trên valid. Đây là
DANH SÁCH ĐỀ XUẤT – mọi dòng ở trạng thái `pending_review`, cần cố vấn phê duyệt.

Output:
  reports/aq10_strategy_comparison.csv, reports/aq12_threshold_scenarios.csv   (valid – để chọn)
  reports/aq10_strategy_comparison_test.csv, reports/aq12_threshold_scenarios_test.csv   (test – chỉ báo cáo)
  reports/prioritization_report.md, reports/risk_list.csv
  reports/figures/aq10_coverage_at_k.png, reports/figures/aq12_tradeoff.png
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from . import features as feat_mod
from . import kg as kg_mod
from . import plotting
from .config import Config
from .governance import audit, check_language

plt = plotting.plt


def _pct(s: pd.Series) -> pd.Series:
    return s.rank(pct=True, method="average")


def strategy_scores(d: pd.DataFrame) -> dict[str, pd.Series]:
    """Ba phương án xếp hạng trong AQ10."""
    risk = _pct(d["score_main"])
    drop = _pct(-d["engagement_change"].fillna(0))
    missing = _pct(d["share_missing"].fillna(0))
    return {
        "A_risk_only": d["score_main"],
        "B_risk_plus_engagement_drop": 0.7 * risk + 0.3 * drop,
        "C_risk_plus_missing_work": 0.7 * risk + 0.3 * missing,
    }


def coverage_precision_at_k(y: pd.Series, score: pd.Series, k: int) -> tuple[float, float]:
    top = score.sort_values(ascending=False).index[:k]
    hit = y.loc[top].sum()
    return hit / max(y.sum(), 1), hit / max(len(top), 1)


def compare_strategies(d: pd.DataFrame, k: int) -> pd.DataFrame:
    """AQ10 – Coverage@K và Precision@K của từng phương án trên một tập."""
    rows = []
    for name, s in strategy_scores(d).items():
        cov, prec = coverage_precision_at_k(d["y"], s, k)
        rows.append({"strategy": name, "K": k, "coverage_at_K": round(cov, 3), "precision_at_K": round(prec, 3)})
    return pd.DataFrame(rows)


def select_strategy(valid_comp: pd.DataFrame) -> str:
    """Phương án có Coverage@K cao nhất trên VALID; hoà thì lấy Precision@K, rồi phương án đơn giản hơn (A trước)."""
    ranked = valid_comp.sort_values(["coverage_at_K", "precision_at_K"], ascending=False, kind="stable")
    return str(ranked.iloc[0]["strategy"])


def threshold_scenarios(d: pd.DataFrame, shares: list[float], k: int) -> pd.DataFrame:
    """AQ12 – kịch bản cảnh báo top x% theo điểm rủi ro trên một tập."""
    sc = []
    for share in shares:
        n_alert = int(round(share * len(d)))
        cov, prec = coverage_precision_at_k(d["y"], d["score_main"], n_alert)
        sc.append({"alert_share": share, "n_alerted": n_alert, "recall": round(cov, 3),
                   "precision": round(prec, 3), "false_alarms": int(round(n_alert * (1 - prec))),
                   "weeks_of_advisor_capacity": round(n_alert / k, 2), "fits_capacity": n_alert <= k})
    return pd.DataFrame(sc)


def support_type(row: dict, gaps: list[str]) -> str:
    """AQ11 – luật quyết định loại hỗ trợ (đề xuất, cố vấn quyết định cuối cùng)."""
    if row.get("tier") == "Rất cao" and row.get("engagement_change", 0) < -0.5:
        return "Mời tư vấn 1–1"
    if row.get("n_missing", 0) >= 1:
        return "Nhắc nhở có duyệt + hỏi thăm lý do chưa nộp bài"
    if gaps:
        return "Gợi ý tài nguyên ôn tập theo concept"
    return "Giới thiệu tutoring nhóm nhỏ"


def run(cfg: Config) -> dict:
    plotting.setup()
    processed, reports, figdir, interim = (cfg.path(k) for k in
                                           ("processed_dir", "reports_dir", "figures_dir", "interim_dir"))
    preds = pd.read_parquet(processed / "predictions.parquet")
    feats, _ = feat_mod.load(cfg)
    reasons = pd.read_parquet(processed / "reason_codes.parquet")
    keys = ["pid", "code_presentation"]

    def frame(split: str) -> pd.DataFrame:
        return (preds[preds["split"] == split]
                .merge(feats.drop(columns=["y", "split"]), on=keys)
                .merge(reasons, on=keys, how="left")
                .reset_index(drop=True))

    dv, d = frame("valid"), frame("test")   # dv: để chọn · d: học kỳ hiện tại (Risk List) + báo cáo
    if dv.empty:
        raise ValueError("Không có dự đoán cho tập valid – không thể chọn phương án/ngưỡng mà không dùng test.")

    adv = cfg["advisor"]
    K = adv["k_per_advisor"] * adv["n_advisors"]

    # ---- AQ10: chọn phương án trên VALID, báo cáo trên TEST ------------------
    comp = compare_strategies(dv, K)
    best = select_strategy(comp)
    comp.to_csv(reports / "aq10_strategy_comparison.csv", index=False)
    comp_test = compare_strategies(d, K)
    comp_test.to_csv(reports / "aq10_strategy_comparison_test.csv", index=False)
    strategies = strategy_scores(d)

    strategies_v = strategy_scores(dv)
    ks = np.unique(np.linspace(5, len(dv), 40).astype(int))
    fig, ax = plt.subplots(figsize=(7, 4))
    for name, s in strategies_v.items():
        ax.plot(ks, [coverage_precision_at_k(dv["y"], s, k)[0] for k in ks], label=name)
    ax.plot(ks, ks / len(dv), ls=":", color="#aaa", label="chọn ngẫu nhiên")
    ax.axvline(K, ls="--", color="#d73027")
    ax.text(K, 0.02, f" K={K}", color="#d73027", fontsize=8)
    ax.set(xlabel="Số sinh viên được liên hệ (K)", ylabel="Coverage@K",
           title="AQ10 · Tỷ lệ sinh viên cần hỗ trợ được tiếp cận theo K (valid)")
    ax.legend(frameon=False, fontsize=8)
    plotting.save(fig, figdir / "aq10_coverage_at_k.png")

    # ---- AQ12: kịch bản ngưỡng – bảng để CHỌN là valid -----------------------
    scen = threshold_scenarios(dv, adv["alert_shares"], K)
    scen.to_csv(reports / "aq12_threshold_scenarios.csv", index=False)
    scen_test = threshold_scenarios(d, adv["alert_shares"], K)
    scen_test.to_csv(reports / "aq12_threshold_scenarios_test.csv", index=False)

    shares = np.linspace(0.02, 0.6, 30)
    rec = [coverage_precision_at_k(dv["y"], dv["score_main"], int(s * len(dv)))[0] for s in shares]
    fig, ax1 = plt.subplots(figsize=(7, 4))
    ax1.plot(shares * 100, rec, color="#4575b4", label="Recall")
    ax1.axhline(cfg["acceptance"]["recall_min"], ls=":", color="#4575b4")
    ax1.set(xlabel="% sinh viên được cảnh báo", ylabel="Recall")
    ax2 = ax1.twinx()
    ax2.plot(shares * 100, shares * len(dv), color="#d73027", label="Số ca")
    ax2.axhline(K, ls="--", color="#d73027")
    ax2.set_ylabel("Số ca cần liên hệ (đỏ đứt = năng lực K/tuần)")
    ax1.set_title("AQ12 · Đánh đổi Recall – khối lượng công việc cố vấn (valid)")
    plotting.save(fig, figdir / "aq12_tradeoff.png")

    # ---- Risk List (AQ10 + AQ11) --------------------------------------------
    t = cfg["advisor"]["tiers"]
    pct = _pct(d["score_main"])
    d["tier"] = np.select([pct >= t["very_high"], pct >= t["high"]], ["Rất cao", "Cao"], default="Theo dõi")
    d["priority_score"] = strategies[best]
    top = d.sort_values("priority_score", ascending=False).head(K).copy()

    g = kg_mod.build_graph(cfg)
    gaps_path = interim / "concept_gaps.parquet"
    gaps = pd.read_parquet(gaps_path) if gaps_path.exists() else pd.DataFrame(columns=keys + ["concept_id", "needs_support"])
    # tối đa 3 concept có điểm hiệu dụng thấp nhất / sinh viên – danh sách ngắn để cố vấn dùng được
    gap_map = (gaps[gaps["needs_support"]].sort_values("concept_score")
               .groupby(keys)["concept_id"].apply(lambda s: list(s)[:3]).to_dict())

    recs = []
    for r in top.to_dict("records"):
        cg = gap_map.get((r["pid"], r["code_presentation"]), [])
        res_ids = sorted({x for c in cg for x in kg_mod.cq_resources_for_concept(g, c)})
        recs.append({
            "rank": len(recs) + 1, "pid": r["pid"], "code_presentation": r["code_presentation"],
            "risk_score": round(float(r["score_main"]), 3), "tier": r["tier"],
            "reasons": " | ".join(r["reasons"]) if isinstance(r["reasons"], (list, np.ndarray)) else "",
            "concepts_need_support": ", ".join(f"{c} ({g.nodes[c]['label']})" for c in cg),
            "suggested_resources": ", ".join(f"{x}: {g.nodes[x]['label']}" for x in res_ids),
            "suggested_support": support_type(r, cg),
            "status": "pending_review", "reviewed_by": "", "decision_note": "",
        })
    risk_list = pd.DataFrame(recs)
    bad = check_language(risk_list["reasons"].tolist() + risk_list["suggested_support"].tolist())
    if bad:
        raise ValueError(f"Risk List vi phạm quy tắc ngôn ngữ: {bad[:3]}")
    risk_list.to_csv(reports / "risk_list.csv", index=False)

    md = [
        "# Ưu tiên hỗ trợ – AQ10, AQ11, AQ12 (tự sinh)",
        "",
        f"Chọn trên **valid** {cfg.presentations('valid')} (n = {len(dv)}, cần hỗ trợ = {int(dv['y'].sum())}). "
        f"Test {cfg.presentations('test')} (n = {len(d)}, cần hỗ trợ = {int(d['y'].sum())}) chỉ để báo cáo và "
        f"mô phỏng Risk List của học kỳ hiện tại. Sinh viên còn theo học tại ngày {cfg.cutoff_day}. "
        f"Năng lực K = {adv['k_per_advisor']} × {adv['n_advisors']} cố vấn = **{K} ca/tuần** (ASSUMPTION).",
        "",
        "## AQ10 – So sánh phương án ưu tiên",
        "",
        "Valid (dùng để chọn):",
        "",
        comp.to_markdown(index=False),
        "",
        f"Phương án chọn trên valid (Coverage@K cao nhất; hoà thì Precision@K, rồi phương án đơn giản hơn): **{best}**.",
        "",
        "Test (chỉ báo cáo, không dùng để chọn):",
        "",
        comp_test.to_markdown(index=False),
        "",
        "![](figures/aq10_coverage_at_k.png)",
        "",
        "## AQ12 – Kịch bản ngưỡng cảnh báo",
        "",
        "Valid (nhóm chọn ngưỡng từ bảng này):",
        "",
        scen.to_markdown(index=False),
        "",
        "Test (chỉ báo cáo):",
        "",
        scen_test.to_markdown(index=False),
        "",
        "![](figures/aq12_tradeoff.png)",
        "",
        "## AQ11 – Phân bố loại hỗ trợ đề xuất trong Risk List",
        "",
        risk_list["suggested_support"].value_counts().to_frame().to_markdown() if len(risk_list) else "_trống_",
        "",
        "> Risk List (`reports/risk_list.csv`) chỉ là đề xuất. Mọi dòng ở trạng thái `pending_review`; "
        "cố vấn phê duyệt trên dashboard trước bất kỳ liên hệ nào. Đây là đánh giá trên dữ liệu lịch sử, "
        "không chứng minh hiệu quả can thiệp.",
    ]
    (reports / "prioritization_report.md").write_text("\n".join(md), encoding="utf-8")
    audit(cfg, "prioritize", K=K, best_strategy=best, n_risk_list=len(risk_list))
    return {"comparison": comp, "scenarios": scen, "risk_list": risk_list}
