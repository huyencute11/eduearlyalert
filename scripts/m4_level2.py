"""M4 Level 2 – prototype theo đúng quy trình đã cố định ở N03_Milestone4 (Mục 3.4, 4, 7).

Không sửa kế hoạch Level 1 sau khi thấy kết quả. Thứ tự:
  1. Nạp prepared dataset của M3 (features.parquet, quần thể còn theo học tại cutoff).
  2. Baseline: tỷ lệ nền; luật AQ7(b) = chưa nộp TMA1 hoặc điểm TMA1 < 40.
  3. Candidate: gradient boosting (XGBoost) và logistic regression (L2), không cân bằng lớp bằng trọng số.
  4. Biến đổi fit trên tập huấn luyện; tinh chỉnh, dừng sớm, calibration, ngưỡng trên tập kiểm định.
  5. Quy tắc giữ/đổi (Mục 3.4) được áp dụng và GHI LOG trước khi chạm vào tập kiểm tra.
  6. Tập kiểm tra dùng một lần cho báo cáo; không huấn luyện lại.

Chạy (mốc Tuần 6):
  python scripts/m4_level2.py --tag week6
Độ nhạy mốc Tuần 4 (cam kết M1; cửa sổ sớm/muộn = Tuần 1–2 / 3–4):
  EDU_ROOT=. python -m eduearlyalert.pipeline cohort features --config scripts/m4_level2_config_week4.yaml
  python scripts/m4_level2.py --features data/sensitivity_week4/processed/features.parquet --tag week4 --core-only
Output: reports/m4_level2/<tag>/ (csv, json, png). Cần thêm gói xgboost (requirements.txt).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import time
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import sklearn
import xgboost as xgb
from sklearn.calibration import calibration_curve
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, precision_recall_curve, roc_auc_score
from sklearn.pipeline import Pipeline, make_pipeline
from sklearn.preprocessing import FunctionTransformer, StandardScaler

matplotlib.use("Agg")
from eduearlyalert import cohort as cohort_mod  # noqa: E402
from eduearlyalert import plotting  # noqa: E402
from eduearlyalert.config import load_config  # noqa: E402
from eduearlyalert.governance import audit  # noqa: E402

plt = plotting.plt

ROOT = Path(__file__).resolve().parents[1]
SEED = 42
N_BOOT = 1000
K = 70  # 2 cố vấn × 35 (giả định M1)
RECALL_MIN = 0.80

# Nhóm feature dùng chung cho importance toàn cục và reason codes (M4 Mục 3.5)
GROUPS = {
    "Ít tương tác VLE": ["clicks_pre_start", "clicks_total", "active_days_total", "clicks_w"],
    "Tương tác giảm (Tuần cuối so với đầu)": ["engagement_change", "clicks_early", "clicks_late"],
    "Nhiều tuần không hoạt động": ["inactive_weeks"],
    "Chưa nộp TMA1": ["first_assess_missing", "n_missing", "share_missing", "n_on_time", "n_late", "n_assess_due"],
    "Điểm TMA1 thấp": ["first_assess_score", "mean_score", "min_score", "weighted_score_so_far"],
    "Nộp bài sát hạn": ["mean_days_early"],
    "Cách dùng loại tài nguyên": ["share_"],
    "Đăng ký muộn": ["reg_days_before_start", "date_registration"],
    "Học lại / khối lượng tín chỉ": ["num_of_prev_attempts", "studied_credits"],
}


def group_of(col: str) -> str:
    for g, keys in GROUPS.items():
        for k in keys:
            if col == k or (k.endswith("_") and col.startswith(k)) or (k == "clicks_w" and col.startswith("clicks_w")):
                return g
    raise KeyError(col)


# ----------------------------------------------------------------------------- metrics
def prauc(y, s):
    return float(average_precision_score(y, s))


def at_threshold(y, s, thr):
    pred = s >= thr
    tp = int((pred & (y == 1)).sum()); fp = int((pred & (y == 0)).sum()); fn = int((~pred & (y == 1)).sum())
    rec = tp / (tp + fn) if tp + fn else 0.0
    prec = tp / (tp + fp) if tp + fp else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"threshold": float(thr), "alerts": int(pred.sum()), "alert_rate": float(pred.mean()),
            "tp": tp, "fp": fp, "fn": fn, "recall": rec, "precision": prec, "f1": f1}


def choose_threshold(y, s, recall_min=None):
    """Ngưỡng có F1 cao nhất trong các ngưỡng đạt Recall ≥ recall_min (M1)."""
    recall_min = RECALL_MIN if recall_min is None else recall_min
    prec, rec, thr = precision_recall_curve(y, s)
    prec, rec = prec[:-1], rec[:-1]
    f1 = np.where(prec + rec > 0, 2 * prec * rec / (prec + rec), 0)
    ok = rec >= recall_min
    return float(thr[np.argmax(np.where(ok, f1, -1))])


def precision_at_recall(y, s, r):
    prec, rec, _ = precision_recall_curve(y, s)
    return float(prec[rec >= r].max())


def topk(y, s, k, rng=None):
    """Độ bao phủ@K và Precision@K; điểm bằng nhau được phá ngẫu nhiên (seed cố định)."""
    rng = rng or np.random.default_rng(SEED)
    order = np.lexsort((rng.random(len(s)), -s))[:k]
    tp = int(y[order].sum())
    return tp / y.sum(), tp / k


def calib_line(y, p):
    """Calibration-in-the-large và độ dốc: hồi quy y theo logit(p)."""
    lp = np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))
    m = LogisticRegression(C=1e6, max_iter=1000).fit(lp.reshape(-1, 1), y)
    return float(m.intercept_[0]), float(m.coef_[0, 0])


def boot_idx(n, rng):
    return rng.integers(0, n, n)


def ci(a):
    a = np.asarray(a, float)
    return [float(np.percentile(a, 2.5)), float(np.percentile(a, 97.5))]


# ----------------------------------------------------------------------------- models
def lr_pipeline(cols, binary, C):
    clicks = [c for c in cols if c.startswith("clicks_")]
    cont = [c for c in cols if c not in clicks and c not in binary]
    pre = ColumnTransformer([
        ("clicks", make_pipeline(FunctionTransformer(np.log1p, feature_names_out="one-to-one"),
                                 SimpleImputer(strategy="median"), StandardScaler()), clicks),
        ("cont", make_pipeline(SimpleImputer(strategy="median"), StandardScaler()), cont),
        ("bin", SimpleImputer(strategy="most_frequent"), binary),
    ], verbose_feature_names_out=False)
    return Pipeline([("pre", pre), ("lr", LogisticRegression(C=C, max_iter=5000))])


def fit_lr(Xtr, ytr, Xva, yva, cols, binary, log):
    rows = []
    for C in [0.001, 0.01, 0.1, 1.0, 10.0]:
        m = lr_pipeline(cols, binary, C).fit(Xtr, ytr)
        rows.append({"C": C, "valid_prauc": prauc(yva, m.predict_proba(Xva)[:, 1])})
    grid = pd.DataFrame(rows); best = grid.loc[grid.valid_prauc.idxmax()]
    log["lr_grid"] = grid.to_dict("records")
    return lr_pipeline(cols, binary, float(best.C)).fit(Xtr, ytr), {"C": float(best.C)}


def fit_gb(Xtr, ytr, Xva, yva, log):
    rows, best = [], None
    for depth in [2, 3, 4]:
        for lr in [0.03, 0.1]:
            for mcw in [1, 5]:
                params = dict(max_depth=depth, learning_rate=lr, min_child_weight=mcw, subsample=0.8,
                              colsample_bytree=0.8, n_estimators=2000, early_stopping_rounds=50,
                              eval_metric="aucpr", tree_method="hist", random_state=SEED, n_jobs=4)
                m = xgb.XGBClassifier(**params).fit(Xtr, ytr, eval_set=[(Xva, yva)], verbose=False)
                p = m.predict_proba(Xva, iteration_range=(0, m.best_iteration + 1))[:, 1]
                r = {"max_depth": depth, "learning_rate": lr, "min_child_weight": mcw,
                     "best_iteration": int(m.best_iteration), "valid_prauc": prauc(yva, p)}
                rows.append(r)
                if best is None or r["valid_prauc"] > best[0]["valid_prauc"]:
                    best = (r, m)
    log["gb_grid"] = rows
    return best[1], best[0]


class GB:
    """Gói XGBoost để dùng đúng số cây tốt nhất (dừng sớm)."""

    def __init__(self, m):
        self.m, self.n = m, m.best_iteration + 1

    def proba(self, X):
        return self.m.predict_proba(X, iteration_range=(0, self.n))[:, 1]

    def contribs(self, X):
        d = xgb.DMatrix(X, feature_names=list(X.columns))
        return self.m.get_booster().predict(d, pred_contribs=True, iteration_range=(0, self.n))


def platt(p_va, y_va):
    lp = np.log(np.clip(p_va, 1e-6, 1 - 1e-6) / (1 - np.clip(p_va, 1e-6, 1 - 1e-6)))
    m = LogisticRegression(C=1e6, max_iter=1000).fit(lp.reshape(-1, 1), y_va)

    def f(p):
        q = np.log(np.clip(p, 1e-6, 1 - 1e-6) / (1 - np.clip(p, 1e-6, 1 - 1e-6)))
        return m.predict_proba(q.reshape(-1, 1))[:, 1]
    return f


# ----------------------------------------------------------------------------- experiment
def run(features_path: Path, tag: str, core_only: bool):
    global SEED, K, RECALL_MIN
    cfg = load_config()
    SEED = cfg.seed  # tham số lấy từ config.yaml; lưới tinh chỉnh là chi tiết riêng của thí nghiệm này
    K = cfg["advisor"]["k_per_advisor"] * cfg["advisor"]["n_advisors"]
    RECALL_MIN = cfg["acceptance"]["recall_min"]
    plotting.setup()
    out = ROOT / "reports" / "m4_level2" / tag
    out.mkdir(parents=True, exist_ok=True)
    log = {"tag": tag, "started": time.strftime("%Y-%m-%d %H:%M:%S"), "seed": SEED,
           "python": platform.python_version(), "sklearn": sklearn.__version__, "xgboost": xgb.__version__,
           "numpy": np.__version__, "pandas": pd.__version__,
           "features_path": str(features_path.relative_to(ROOT)),
           "features_sha256": hashlib.sha256(features_path.read_bytes()).hexdigest()}
    meta = json.loads((features_path.parent / "feature_list.json").read_text())
    cols = meta["feature_columns"]
    log["cutoff_day"] = meta["cutoff_day"]; log["n_features"] = len(cols)

    f = pd.read_parquet(features_path)
    pop = f[f["in_prediction_population"].astype(bool)].reset_index(drop=True)
    parts = {s: pop[pop["split"] == s].reset_index(drop=True) for s in ("train", "valid", "test")}
    log["n"] = {s: int(len(d)) for s, d in parts.items()}
    log["n_pos"] = {s: int(d["y"].sum()) for s, d in parts.items()}
    X = {s: d[cols].astype(float) for s, d in parts.items()}
    y = {s: d["y"].to_numpy(int) for s, d in parts.items()}
    binary = [c for c in cols if set(X["train"][c].dropna().unique()) <= {0.0, 1.0}]
    log["binary_features"] = binary

    # ---- baselines
    prior = float(y["train"].mean())
    rule = {s: ((parts[s]["first_assess_missing"] == 1) | (parts[s]["first_assess_score"] < 40)).to_numpy(float)
            for s in parts}

    # ---- candidates (fit trên huấn luyện, chọn trên kiểm định)
    lr, lr_best = fit_lr(X["train"], y["train"], X["valid"], y["valid"], cols, binary, log)
    gbm, gb_best = fit_gb(X["train"], y["train"], X["valid"], y["valid"], log)
    gb = GB(gbm)
    log["lr_best"], log["gb_best"] = lr_best, gb_best
    raw = {"gb": {s: gb.proba(X[s]) for s in parts}, "lr": {s: lr.predict_proba(X[s])[:, 1] for s in parts}}

    # ---- calibration trên kiểm định: lệch nếu khoảng tin cậy của intercept không chứa 0 hoặc của slope không chứa 1
    rng = np.random.default_rng(SEED)
    calib = {}
    for name in ("gb", "lr"):
        p, yy = raw[name]["valid"], y["valid"]
        a0, b0 = calib_line(yy, p)
        bs = [calib_line(yy[i], p[i]) for i in (boot_idx(len(yy), rng) for _ in range(300))]
        ia, sb = ci([b[0] for b in bs]), ci([b[1] for b in bs])
        mis = not (ia[0] <= 0 <= ia[1]) or not (sb[0] <= 1 <= sb[1])
        calib[name] = {"intercept": a0, "intercept_ci": ia, "slope": b0, "slope_ci": sb, "miscalibrated": mis}
    log["calibration_valid"] = calib
    score = {}
    for name in ("gb", "lr"):
        if calib[name]["miscalibrated"]:
            g = platt(raw[name]["valid"], y["valid"])
            score[name] = {s: g(raw[name][s]) for s in parts}
        else:
            score[name] = raw[name]
    log["platt_applied"] = {n: calib[n]["miscalibrated"] for n in calib}

    # ---- ngưỡng trên kiểm định
    thr = {n: choose_threshold(y["valid"], score[n]["valid"]) for n in ("gb", "lr")}
    log["threshold_valid"] = thr
    log["mean_pred"] = {n: {sp: float(score[n][sp].mean()) for sp in parts} for n in ("gb", "lr")}

    # ---- so sánh trên kiểm định + quy tắc giữ/đổi (Mục 3.4) – TRƯỚC khi chạm tập kiểm tra
    yv = y["valid"]
    diff, auc_d = [], []
    for _ in range(N_BOOT):
        i = boot_idx(len(yv), rng)
        if yv[i].min() == yv[i].max():
            continue
        diff.append(prauc(yv[i], score["gb"]["valid"][i]) - prauc(yv[i], score["lr"]["valid"][i]))
    d_ci = ci(diff)
    decision = "gradient boosting" if d_ci[0] > 0 else "logistic regression"
    log["decision"] = {"prauc_gb_minus_lr_valid": prauc(yv, score["gb"]["valid"]) - prauc(yv, score["lr"]["valid"]),
                       "ci95": d_ci, "rule": "giữ gradient boosting chỉ khi khoảng tin cậy của chênh lệch nằm trên 0",
                       "chosen": decision, "decided_at": time.strftime("%Y-%m-%d %H:%M:%S")}
    chosen = "gb" if decision == "gradient boosting" else "lr"
    # bằng chứng bổ trợ cho quyết định: chênh lệch huấn luyện – kiểm định (overfitting) và độ phức tạp
    log["train_vs_valid"] = {n: {k: (prauc(y[k], score[n][k]) if k != "gap" else None) for k in ("train", "valid")}
                             for n in ("gb", "lr")}
    for n in ("gb", "lr"):
        tv = log["train_vs_valid"][n]
        tv["roc_train"] = float(roc_auc_score(y["train"], score[n]["train"]))
        tv["roc_valid"] = float(roc_auc_score(y["valid"], score[n]["valid"]))
        tv["gap_prauc"] = tv["train"] - tv["valid"]; tv["gap_roc"] = tv["roc_train"] - tv["roc_valid"]
    tdf = gbm.get_booster().trees_to_dataframe()
    tdf = tdf[tdf["Tree"] < gb.n]
    log["complexity"] = {"gb_trees": int(gb.n), "gb_splits": int((tdf["Feature"] != "Leaf").sum()),
                         "gb_leaves": int((tdf["Feature"] == "Leaf").sum()), "gb_grid_configs": len(log["gb_grid"]),
                         "lr_parameters": int(lr.named_steps["lr"].coef_.size + 1), "lr_grid_configs": len(log["lr_grid"])}
    (out / "decision.json").write_text(json.dumps(log["decision"], ensure_ascii=False, indent=2))

    # ---- bảng metric (kiểm định; kiểm tra sau khi đã chốt)
    rows = []
    for s in ("valid", "test"):
        yy = y[s]
        rows.append({"split": s, "model": "Tỷ lệ nền", "pr_auc": float(yy.mean()), "roc_auc": 0.5,
                     "brier": brier_score_loss(yy, np.full(len(yy), prior)),
                     **{f"thr_{k}": v for k, v in at_threshold(yy, np.full(len(yy), prior), prior).items()}})
        rr = at_threshold(yy, rule[s], 0.5)
        cov_r = min(K, rr["alerts"]) * rr["precision"] / yy.sum()
        rows.append({"split": s, "model": "Luật TMA1", "pr_auc": np.nan, "roc_auc": np.nan, "brier": np.nan,
                     **{f"thr_{k}": v for k, v in rr.items()}, "coverage@70": cov_r,
                     "precision@70": rr["precision"]})
        for n, label in (("gb", "Gradient boosting"), ("lr", "Logistic regression")):
            sc = score[n][s]
            cov, p70 = topk(yy, sc, K)
            rows.append({"split": s, "model": label, "pr_auc": prauc(yy, sc), "roc_auc": float(roc_auc_score(yy, sc)),
                         "brier": float(brier_score_loss(yy, sc)),
                         **{f"thr_{k}": v for k, v in at_threshold(yy, sc, thr[n]).items()},
                         "coverage@70": cov, "precision@70": p70,
                         "precision_at_rule_recall": precision_at_recall(yy, sc, at_threshold(yy, rule[s], 0.5)["recall"]),
                         "brier_raw": float(brier_score_loss(yy, raw[n][s]))})
        rows[-1].update({})
    met = pd.DataFrame(rows)
    met.to_csv(out / "aq7_metrics.csv", index=False)

    # khoảng tin cậy bootstrap cho PR-AUC và các metric tại ngưỡng (mô hình được chọn và đối chứng)
    cis = []
    for s in ("valid", "test"):
        yy = y[s]
        for n in ("gb", "lr"):
            sc = score[n][s]; acc = {"pr_auc": [], "recall": [], "precision": [], "f1": [], "coverage@70": []}
            for _ in range(N_BOOT):
                i = boot_idx(len(yy), rng)
                if yy[i].min() == yy[i].max():
                    continue
                acc["pr_auc"].append(prauc(yy[i], sc[i]))
                a = at_threshold(yy[i], sc[i], thr[n])
                for k in ("recall", "precision", "f1"):
                    acc[k].append(a[k])
                acc["coverage@70"].append(topk(yy[i], sc[i], K, np.random.default_rng(0))[0])
            cis.append({"split": s, "model": n, **{f"{k}_ci": ci(v) for k, v in acc.items()}})
    pd.DataFrame(cis).to_json(out / "aq7_metric_ci.json", orient="records", force_ascii=False, indent=2)

    log["finished_core"] = time.strftime("%Y-%m-%d %H:%M:%S")
    if core_only:
        (out / "experiment_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2))
        return

    # ---- hình: PR curve, calibration (kiểm định và kiểm tra)
    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for j, s in enumerate(("valid", "test")):
        for n, lab in (("gb", "Gradient boosting"), ("lr", "Logistic regression")):
            pr, rc, _ = precision_recall_curve(y[s], score[n][s])
            ax[j].plot(rc, pr, label=f"{lab} (PR-AUC {prauc(y[s], score[n][s]):.3f})")
        rr = at_threshold(y[s], rule[s], 0.5)
        ax[j].scatter([rr["recall"]], [rr["precision"]], color="k", zorder=5, label="Luật TMA1")
        ax[j].axhline(y[s].mean(), ls="--", color="grey", lw=1, label="Tỷ lệ nền")
        ax[j].axvline(RECALL_MIN, ls=":", color="grey", lw=1)
        ax[j].set_title(f"AQ7 · Precision–Recall · tập {'kiểm định 2014B' if s == 'valid' else 'kiểm tra 2014J'}")
        ax[j].set_xlabel("Recall"); ax[j].set_ylabel("Precision"); ax[j].legend(fontsize=7, loc="lower left")
    plotting.save(fig, out / "aq7_pr_curves.png")

    fig, ax = plt.subplots(1, 2, figsize=(10, 4))
    for j, s in enumerate(("valid", "test")):
        for n, lab in (("gb", "Gradient boosting"), ("lr", "Logistic regression")):
            fy, fx = calibration_curve(y[s], score[n][s], n_bins=10, strategy="quantile")
            ax[j].plot(fx, fy, marker="o", label=lab)
        ax[j].plot([0, 1], [0, 1], ls="--", color="grey", lw=1)
        ax[j].set_title(f"AQ7 · Calibration · tập {'kiểm định 2014B' if s == 'valid' else 'kiểm tra 2014J'}")
        ax[j].set_xlabel("Xác suất dự báo"); ax[j].set_ylabel("Tỷ lệ y = 1 thực tế"); ax[j].legend(fontsize=8)
    plotting.save(fig, out / "aq7_calibration.png")

    sc_c = score[chosen]
    # ---- AQ7 error analysis trên tập kiểm tra (mô hình được chọn)
    te = parts["test"].copy(); te["score"] = sc_c["test"]; te["alert"] = te["score"] >= thr[chosen]
    coh = pd.read_parquet(ROOT / "data/interim/cohort.parquet")[["pid", "code_presentation", "date_unregistration"]]
    te = te.merge(coh, on=["pid", "code_presentation"], how="left")
    te["group"] = np.select([(te.y == 1) & te.alert, (te.y == 1) & ~te.alert, (te.y == 0) & te.alert],
                            ["TP", "FN", "FP"], "TN")
    prof_cols = ["clicks_total", "active_days_total", "inactive_weeks", "engagement_change",
                 "first_assess_missing", "first_assess_score", "studied_credits", "num_of_prev_attempts"]
    prof = te.groupby("group")[prof_cols].median().T
    prof.loc["n"] = te.groupby("group").size()
    prof.to_csv(out / "aq7_error_profiles_test.csv")
    fn = te[te.group == "FN"]
    fn_split = {"FN_total": int(len(fn)), "FN_fail": int((fn.final_result == "Fail").sum()),
                "FN_withdrawn": int((fn.final_result == "Withdrawn").sum()),
                "FN_withdrawn_median_day": float(fn.loc[fn.final_result == "Withdrawn", "date_unregistration"].median()),
                "TP_withdrawn_median_day": float(te.loc[(te.group == "TP") & (te.final_result == "Withdrawn"),
                                                        "date_unregistration"].median()),
                "recall_fail": float(te.loc[te.final_result == "Fail", "alert"].mean()),
                "recall_withdrawn": float(te.loc[te.final_result == "Withdrawn", "alert"].mean())}
    log["error_test"] = fn_split

    # ---- AQ9 fairness (kiểm định = sơ bộ, kiểm tra = chính thức), mô hình được chọn + luật làm đối chiếu
    sens = cohort_mod.load_sensitive(cfg)  # chỉ để kiểm tra công bằng, không vào feature
    fair_rows, gap_rows = [], []
    for s in ("valid", "test"):
        d = parts[s][["pid", "code_presentation", "y"]].merge(sens, on=["pid", "code_presentation"], how="left")
        d["alert"] = sc_c[s] >= thr[chosen]; d["rule"] = rule[s] == 1
        for att in ["gender", "age_band", "region", "disability", "imd_band", "highest_education"]:
            g = d.groupby(att, dropna=False)
            for lev, dd in g:
                if len(dd) < 10:
                    continue
                pos = dd[dd.y == 1]
                fair_rows.append({"split": s, "attribute": att, "group": str(lev), "n": len(dd), "n_pos": len(pos),
                                  "recall": pos.alert.mean() if len(pos) else np.nan,
                                  "recall_rule": pos.rule.mean() if len(pos) else np.nan,
                                  "alert_rate": dd.alert.mean(),
                                  "precision": dd.loc[dd.alert, "y"].mean() if dd.alert.any() else np.nan})
            elig = [lev for lev, dd in g if (dd.y == 1).sum() >= 30]
            if len(elig) < 2:
                continue
            rec = {lev: d.loc[(d[att] == lev) & (d.y == 1), "alert"].mean() for lev in elig}
            hi, lo = max(rec, key=rec.get), min(rec, key=rec.get)
            gap = rec[hi] - rec[lo]
            bs = []
            for _ in range(N_BOOT):
                i = boot_idx(len(d), rng); db = d.iloc[i]
                a = db.loc[(db[att] == hi) & (db.y == 1), "alert"]; b = db.loc[(db[att] == lo) & (db.y == 1), "alert"]
                if len(a) and len(b):
                    bs.append(a.mean() - b.mean())
            c = ci(bs)
            gap_rows.append({"split": s, "attribute": att, "highest": str(hi), "lowest": str(lo), "gap": gap,
                             "ci_low": c[0], "ci_high": c[1], "level1_flag": gap > 0.10,
                             "level2_confirmed": gap > 0.10 and c[0] > 0})
    pd.DataFrame(fair_rows).to_csv(out / "aq9_groups.csv", index=False)
    pd.DataFrame(gap_rows).to_csv(out / "aq9_gaps.csv", index=False)
    log["roc_auc_by_run"] = {s: float(roc_auc_score(y[s], sc_c[s])) for s in ("valid", "test")}

    # ---- AQ10: độ bao phủ theo K, so với ngẫu nhiên và luật
    cov_rows = []
    for s in ("valid", "test"):
        yy = y[s]; rr = at_threshold(yy, rule[s], 0.5)
        for k in range(35, 351, 35):
            cm, pm = topk(yy, sc_c[s], k)
            cov_rows.append({"split": s, "K": k, "model": cm, "precision_model": pm,
                             "random": k / len(yy), "rule": min(k, rr["alerts"]) * rr["precision"] / yy.sum()
                             + max(0, k - rr["alerts"]) * ((yy.sum() - rr["tp"]) / max(1, len(yy) - rr["alerts"])) / yy.sum()})
    cov = pd.DataFrame(cov_rows); cov.to_csv(out / "aq10_coverage_by_k.csv", index=False)
    aq10 = {}
    for s in ("valid", "test"):
        yy = y[s]; rr = at_threshold(yy, rule[s], 0.5); dr, dl = [], []
        for _ in range(N_BOOT):
            i = boot_idx(len(yy), rng); yb = yy[i]; rb = rule[s][i]
            cm = topk(yb, sc_c[s][i], K, np.random.default_rng(1))[0]
            ar = at_threshold(yb, rb, 0.5)
            dr.append(cm - K / len(yb)); dl.append(cm - min(K, ar["alerts"]) * ar["precision"] / yb.sum())
        aq10[s] = {"coverage@70": topk(yy, sc_c[s], K)[0], "diff_vs_random_ci": ci(dr), "diff_vs_rule_ci": ci(dl)}
    # tỷ lệ nhóm trong top-70 so với trong số y = 1 (kiểm tra)
    d = parts["test"][["pid", "code_presentation", "y"]].merge(sens, on=["pid", "code_presentation"], how="left")
    order = np.lexsort((np.random.default_rng(SEED).random(len(d)), -sc_c["test"]))[:K]
    d["top"] = False; d.loc[order, "top"] = True
    share = []
    for att in ["gender", "age_band", "disability", "imd_band", "highest_education", "region"]:
        for lev, dd in d.groupby(att, dropna=False):
            if len(dd) < 10:
                continue
            share.append({"attribute": att, "group": str(lev), "share_top70": dd.top.sum() / K,
                          "share_positives": dd.y.sum() / d.y.sum()})
    pd.DataFrame(share).to_csv(out / "aq10_group_share_test.csv", index=False)
    log["aq10"] = aq10

    fig, ax = plt.subplots(figsize=(6, 4))
    cv = cov[cov.split == "test"]
    ax.plot(cv.K, cv.model, marker="o", label=f"Mô hình ({decision})")
    ax.plot(cv.K, cv.rule, marker="s", label="Luật TMA1")
    ax.plot(cv.K, cv.random, ls="--", label="Chọn ngẫu nhiên")
    ax.axvline(K, color="grey", ls=":", lw=1)
    ax.set_title("AQ10 · Độ bao phủ theo K · tập kiểm tra 2014J"); ax.set_xlabel("K (số sinh viên được liên hệ)")
    ax.set_ylabel("Độ bao phủ (phần SV y = 1 trong danh sách)"); ax.legend(fontsize=8)
    plotting.save(fig, out / "aq10_coverage.png")

    # ---- AQ12: bảng kịch bản
    sc_rows = []
    for s in ("valid", "test"):
        yy = y[s]; sc = sc_c[s]; n = len(yy)
        cases = [("Top 10%", np.sort(sc)[::-1][int(0.10 * n) - 1]), ("Top 20%", np.sort(sc)[::-1][int(0.20 * n) - 1]),
                 ("Top 30%", np.sort(sc)[::-1][int(0.30 * n) - 1]), ("Vừa năng lực 70", np.sort(sc)[::-1][K - 1]),
                 ("Ngưỡng 0,5", 0.5), ("Ngưỡng chọn (Recall ≥ 0,80 trên kiểm định)", thr[chosen])]
        for name, t in cases:
            a = at_threshold(yy, sc, t)
            sc_rows.append({"split": s, "scenario": name, **a, "weeks_of_capacity": a["alerts"] / K})
    pd.DataFrame(sc_rows).to_csv(out / "aq12_scenarios.csv", index=False)

    # ---- Explainability
    Xv = X["valid"]
    groups = {}
    for c in cols:
        groups.setdefault(group_of(c), []).append(c)
    base = prauc(y["valid"], gb.proba(Xv))
    imp = []
    prng = np.random.default_rng(SEED)
    for g, cs in groups.items():
        drops = []
        for _ in range(30):
            Xp = Xv.copy(); perm = prng.permutation(len(Xp))
            Xp[cs] = Xv[cs].to_numpy()[perm]
            drops.append(base - prauc(y["valid"], gb.proba(Xp)))
        imp.append({"group": g, "n_features": len(cs), "mean_drop_prauc": float(np.mean(drops)), "sd": float(np.std(drops))})
    pd.DataFrame(imp).sort_values("mean_drop_prauc", ascending=False).to_csv(out / "explain_gb_group_importance.csv", index=False)

    # logistic: hệ số chuẩn hoá + khoảng tin cậy bootstrap (1.000 lần lấy mẫu lại sinh viên huấn luyện)
    feat_names = list(lr.named_steps["pre"].get_feature_names_out())
    coef = lr.named_steps["lr"].coef_[0]
    bs = []
    for _ in range(N_BOOT):
        i = boot_idx(len(y["train"]), rng)
        m = lr_pipeline(cols, binary, lr_best["C"]).fit(X["train"].iloc[i], y["train"][i])
        bs.append(m.named_steps["lr"].coef_[0])
    bs = np.array(bs)
    pd.DataFrame({"feature": feat_names, "group": [group_of(c) for c in feat_names], "coef": coef,
                  "odds_ratio": np.exp(coef), "ci_low": np.percentile(bs, 2.5, axis=0),
                  "ci_high": np.percentile(bs, 97.5, axis=0)}).sort_values("coef", key=np.abs, ascending=False) \
        .to_csv(out / "explain_lr_coefficients.csv", index=False)

    # reason codes cho danh sách 70 SV đứng đầu (tập kiểm tra) – mô hình được chọn
    Xt = X["test"]
    if chosen == "gb":
        cb = gb.contribs(Xt); contrib = pd.DataFrame(cb[:, :-1], columns=cols); bias = cb[:, -1]
        logit = np.log(raw["gb"]["test"] / (1 - raw["gb"]["test"]))
        log["shap_fidelity_max_abs_err"] = float(np.max(np.abs(contrib.sum(axis=1).to_numpy() + bias - logit)))
    else:
        Z = lr.named_steps["pre"].transform(Xt); Zm = lr.named_steps["pre"].transform(X["train"]).mean(axis=0)
        contrib = pd.DataFrame((Z - Zm) * coef, columns=feat_names)
    gsum = pd.DataFrame({g: contrib[[c for c in cs if c in contrib.columns]].sum(axis=1) for g, cs in groups.items()})
    # v2: gán theo giá trị thật – với SV chưa nộp TMA1, phần "điểm" (điểm điền thay, điểm có trọng số = 0) và
    # "nộp sát hạn" thực chất là do chưa nộp; với SV 0 ngày hoạt động, tỷ trọng loại tài nguyên = 0 là do không truy cập
    g2 = gsum.copy()
    miss = (Xt["first_assess_missing"] == 1).to_numpy()
    for g in ("Điểm TMA1 thấp", "Nộp bài sát hạn"):
        g2.loc[miss, "Chưa nộp TMA1"] += g2.loc[miss, g]; g2.loc[miss, g] = 0
    idle = (Xt["active_days_total"].fillna(0) == 0).to_numpy()
    g2.loc[idle, "Ít tương tác VLE"] += g2.loc[idle, "Cách dùng loại tài nguyên"]; g2.loc[idle, "Cách dùng loại tài nguyên"] = 0
    order = np.lexsort((np.random.default_rng(SEED).random(len(sc_c["test"])), -sc_c["test"]))[:K]
    tabs = {}
    for ver, G in (("v1", gsum), ("v2", g2)):
        reasons = []
        for i in order:
            r = G.iloc[i]; r = r[r > 0].sort_values(ascending=False).head(3)
            reasons.append(list(r.index))
        first = pd.Series([r[0] if r else "–" for r in reasons]).value_counts()
        anyr = pd.Series([g for r in reasons for g in r]).value_counts()
        tabs[ver] = pd.DataFrame({f"{ver}_top_reason": first, f"{ver}_in_top3": anyr})
        ct = pd.crosstab(pd.Series([r[0] for r in reasons], name=f"{ver}_top_reason"),
                         pd.Series(miss[order], name="chua_nop_TMA1"))
        ct.to_csv(out / f"reason_codes_{ver}_by_tma1_missing.csv")
    pd.concat(tabs.values(), axis=1).fillna(0).astype(int).to_csv(out / "reason_codes_top70_test.csv")
    log["top70_test"] = {"tma1_missing_share": float(miss[order].mean()), "idle_share": float(idle[order].mean()),
                         "median_clicks_total": float(Xt["clicks_total"].iloc[order].median())}

    log["finished"] = time.strftime("%Y-%m-%d %H:%M:%S")
    (out / "experiment_log.json").write_text(json.dumps(log, ensure_ascii=False, indent=2, default=float))
    audit(cfg, "m4_level2", tag=tag, decision=log["decision"]["chosen"], features_sha256=log["features_sha256"])


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--features", default=str(ROOT / "data/processed/features.parquet"))
    ap.add_argument("--tag", default="week6")
    ap.add_argument("--core-only", action="store_true")
    a = ap.parse_args()
    run(Path(a.features).resolve(), a.tag, a.core_only)
