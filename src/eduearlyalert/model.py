"""GĐ5 – AQ7: dự báo nguy cơ không hoàn thành tại cuối Tuần 6.

Thiết kế (xem docs/03_pipeline.md và Model Design Card):
  * Target: final_result ∈ {Fail, Withdrawn}; đơn vị: sinh viên × presentation.
  * Quần thể: sinh viên còn theo học tại cutoff_day.
  * Chia theo thời gian: train (presentation cũ) → valid (chọn ngưỡng/mô hình) → test (1 lần).
  * So sánh theo bậc: rule baseline → logistic regression → gradient boosting.
  * Ngưỡng: chọn trên VALID sao cho Recall ≥ recall_min và F1 lớn nhất.

Output:
  data/processed/models/*.joblib
  data/processed/predictions.parquet
  reports/model_metrics.json, reports/model_results.md, reports/false_negative_analysis.csv
  reports/figures/aq7_*.png
"""

from __future__ import annotations

import json

import joblib
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score, brier_score_loss, confusion_matrix, f1_score,
    precision_recall_curve, precision_score, recall_score, roc_auc_score, roc_curve,
)
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from . import features as feat_mod
from . import plotting
from .config import Config
from .governance import audit
from .leakage import assert_no_leakage

plt = plotting.plt


def rule_baseline_score(df: pd.DataFrame) -> np.ndarray:
    """Baseline 0 – luật mà cố vấn có thể tự áp dụng không cần mô hình."""
    no_first = df.get("first_assess_missing", pd.Series(0, index=df.index)).fillna(0) == 1
    late_cols = [c for c in ("clicks_w5", "clicks_w6") if c in df.columns]
    inactive_late = df[late_cols].sum(axis=1) == 0 if late_cols else False
    return (no_first | inactive_late).astype(float).to_numpy()


def make_models(seed: int) -> dict:
    return {
        "logistic": make_pipeline(
            SimpleImputer(strategy="median", add_indicator=True),
            StandardScaler(),
            LogisticRegression(class_weight="balanced", max_iter=5000),
        ),
        "gboost": HistGradientBoostingClassifier(
            class_weight="balanced", learning_rate=0.05, max_iter=300, max_leaf_nodes=15,
            l2_regularization=1.0, early_stopping=True, random_state=seed,
        ),
    }


def choose_threshold(y: np.ndarray, score: np.ndarray, recall_min: float) -> float:
    """Ngưỡng có F1 cao nhất trong các ngưỡng đạt Recall ≥ recall_min (nếu không có: Recall cao nhất)."""
    if len(np.unique(score)) <= 2:  # điểm nhị phân (rule)
        return 0.5
    prec, rec, thr = precision_recall_curve(y, score)
    prec, rec = prec[:-1], rec[:-1]
    f1 = np.where(prec + rec > 0, 2 * prec * rec / (prec + rec), 0)
    ok = rec >= recall_min
    idx = np.argmax(np.where(ok, f1, -1)) if ok.any() else np.argmax(rec)
    return float(thr[idx])


def evaluate(y: np.ndarray, score: np.ndarray, thr: float) -> dict:
    pred = (score >= thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    out = {
        "threshold": thr, "n": int(len(y)), "positives": int(y.sum()),
        "recall": recall_score(y, pred, zero_division=0),
        "precision": precision_score(y, pred, zero_division=0),
        "f1": f1_score(y, pred, zero_division=0),
        "alert_rate": float(pred.mean()),
        "tp": int(tp), "fp": int(fp), "fn": int(fn), "tn": int(tn),
    }
    if len(np.unique(y)) == 2:
        out["roc_auc"] = roc_auc_score(y, score)
        out["pr_auc"] = average_precision_score(y, score)
        out["brier"] = brier_score_loss(y, np.clip(score, 0, 1))
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in out.items()}


def _plots(y_test, scores: dict, main: str, thr: float, figdir) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for name, s in scores.items():
        if len(np.unique(s)) > 2:
            fpr, tpr, _ = roc_curve(y_test, s)
            axes[0].plot(fpr, tpr, label=f"{name} (AUC {roc_auc_score(y_test, s):.2f})")
            p, r, _ = precision_recall_curve(y_test, s)
            axes[1].plot(r, p, label=f"{name} (AP {average_precision_score(y_test, s):.2f})")
    axes[0].plot([0, 1], [0, 1], ls="--", color="#aaa")
    axes[0].set(xlabel="False positive rate", ylabel="Recall", title="ROC")
    axes[1].axhline(y_test.mean(), ls="--", color="#aaa", label="tỷ lệ nền")
    axes[1].set(xlabel="Recall", ylabel="Precision", title="Precision–Recall")
    for a in axes:
        a.legend(frameon=False, fontsize=8)
    fig.suptitle("AQ7 · Hiệu năng trên tập TEST (presentation giữ lại)", fontweight="bold")
    plotting.save(fig, figdir / "aq7_roc_pr.png")

    s = scores[main]
    cm = confusion_matrix(y_test, (s >= thr).astype(int), labels=[0, 1])
    fig, ax = plt.subplots(figsize=(4.5, 4))
    ax.imshow(cm, cmap="Blues")
    for i in range(2):
        for j in range(2):
            ax.text(j, i, cm[i, j], ha="center", va="center", fontsize=12)
    ax.set_xticks([0, 1], ["Dự báo: ổn", "Dự báo: cần hỗ trợ"])
    ax.set_yticks([0, 1], ["Thực tế: hoàn thành", "Thực tế: không HT"])
    ax.set_title(f"AQ7 · Confusion matrix ({main}, ngưỡng {thr:.2f})")
    plotting.save(fig, figdir / "aq7_confusion_matrix.png")

    frac_pos, mean_pred = calibration_curve(y_test, s, n_bins=10, strategy="quantile")
    fig, ax = plt.subplots(figsize=(4.5, 4))
    ax.plot(mean_pred, frac_pos, marker="o")
    ax.plot([0, 1], [0, 1], ls="--", color="#aaa")
    ax.set(xlabel="Xác suất dự báo", ylabel="Tỷ lệ thực tế", title=f"AQ7 · Calibration ({main})")
    plotting.save(fig, figdir / "aq7_calibration.png")


def run(cfg: Config) -> dict:
    plotting.setup()
    df, feature_cols = feat_mod.load(cfg)
    assert_no_leakage(cfg, feature_cols)
    pop = df[df["in_prediction_population"]].reset_index(drop=True)
    parts = {s: pop[pop["split"] == s] for s in ("train", "valid", "test")}
    for s, d in parts.items():
        if d.empty or d["y"].nunique() < 2:
            raise ValueError(f"Tập {s} rỗng hoặc chỉ có 1 lớp – kiểm tra scope.presentations trong config.yaml")

    recall_min = cfg["acceptance"]["recall_min"]
    models = make_models(cfg.seed)
    scores_valid, scores_test, thresholds = {}, {}, {}

    scores_valid["rule"] = rule_baseline_score(parts["valid"])
    scores_test["rule"] = rule_baseline_score(parts["test"])
    thresholds["rule"] = 0.5

    model_dir = cfg.path("processed_dir") / "models"
    model_dir.mkdir(exist_ok=True)
    Xtr, ytr = parts["train"][feature_cols], parts["train"]["y"].to_numpy()
    for name, m in models.items():
        m.fit(Xtr, ytr)
        joblib.dump(m, model_dir / f"{name}.joblib")
        scores_valid[name] = m.predict_proba(parts["valid"][feature_cols])[:, 1]
        scores_test[name] = m.predict_proba(parts["test"][feature_cols])[:, 1]
        thresholds[name] = choose_threshold(parts["valid"]["y"].to_numpy(), scores_valid[name], recall_min)

    yv, yt = parts["valid"]["y"].to_numpy(), parts["test"]["y"].to_numpy()
    metrics = {"valid": {}, "test": {}}
    for name in scores_valid:
        metrics["valid"][name] = evaluate(yv, scores_valid[name], thresholds[name])
        metrics["test"][name] = evaluate(yt, scores_test[name], thresholds[name])

    # Chọn mô hình chính trên VALID (PR-AUC), không nhìn test
    main = max(models, key=lambda n: metrics["valid"][n].get("pr_auc", 0))
    acc = cfg["acceptance"]
    t = metrics["test"][main]
    metrics["main_model"] = main
    metrics["acceptance"] = {
        "recall_min": acc["recall_min"], "f1_min": acc["f1_min"],
        "recall_ok": t["recall"] >= acc["recall_min"], "f1_ok": t["f1"] >= acc["f1_min"],
    }
    metrics["feature_columns"] = feature_cols

    reports = cfg.path("reports_dir")
    (reports / "model_metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    preds = []
    for s, sc in (("valid", scores_valid), ("test", scores_test)):
        d = parts[s][["pid", "code_presentation", "split", "y"]].copy()
        for name, v in sc.items():
            d[f"score_{name}"] = v
        preds.append(d)
    pred_df = pd.concat(preds, ignore_index=True)
    pred_df["score_main"] = pred_df[f"score_{main}"]
    pred_df["alert"] = (pred_df["score_main"] >= thresholds[main]).astype(int)
    pred_df.to_parquet(cfg.path("processed_dir") / "predictions.parquet", index=False)

    # Phân tích false negative trên test: ai bị bỏ sót?
    test = parts["test"].assign(score=scores_test[main], alert=(scores_test[main] >= thresholds[main]).astype(int))
    fn = test[(test["y"] == 1) & (test["alert"] == 0)]
    tp = test[(test["y"] == 1) & (test["alert"] == 1)]
    key = ["clicks_total", "active_days_total", "engagement_change", "n_missing", "mean_score", "first_assess_score"]
    key = [k for k in key if k in test.columns]
    fna = pd.DataFrame({"median_false_negative": fn[key].median(), "median_true_positive": tp[key].median()})
    fna["n_fn"], fna["n_tp"] = len(fn), len(tp)
    fna.round(3).to_csv(reports / "false_negative_analysis.csv")
    fn_withdrawn = None
    if len(fn):
        fr = df.set_index(["pid", "code_presentation"]).loc[list(zip(fn["pid"], fn["code_presentation"])), "final_result"]
        fn_withdrawn = fr.value_counts().to_dict()

    _plots(yt, scores_test, main, thresholds[main], cfg.path("figures_dir"))

    rows = []
    for split in ("valid", "test"):
        for name, m in metrics[split].items():
            rows.append({"split": split, "model": name, **{k: m.get(k) for k in
                         ("threshold", "recall", "precision", "f1", "roc_auc", "pr_auc", "alert_rate")}})
    md = [
        "# Kết quả mô hình AQ7 (tự sinh)",
        "",
        f"- Quần thể: sinh viên còn theo học tại ngày {cfg.cutoff_day}. "
        f"Train {cfg.presentations('train')} (n={len(parts['train'])}), "
        f"valid {cfg.presentations('valid')} (n={len(parts['valid'])}), test {cfg.presentations('test')} (n={len(parts['test'])}).",
        f"- Mô hình chính (chọn theo PR-AUC trên valid): **{main}**, ngưỡng {thresholds[main]:.3f} (chọn trên valid).",
        f"- Tiêu chí chấp nhận trên TEST: Recall {t['recall']:.3f} (≥ {acc['recall_min']}: "
        f"{'ĐẠT' if metrics['acceptance']['recall_ok'] else 'CHƯA ĐẠT'}), "
        f"F1 {t['f1']:.3f} (≥ {acc['f1_min']}: {'ĐẠT' if metrics['acceptance']['f1_ok'] else 'CHƯA ĐẠT'}).",
        "",
        pd.DataFrame(rows).to_markdown(index=False),
        "",
        "## False negative (bị bỏ sót) trên test",
        "",
        f"Số FN = {len(fn)}; phân theo kết quả thực tế: {fn_withdrawn}.",
        "",
        fna.round(2).to_markdown(),
        "",
        "> Nếu chưa đạt tiêu chí: báo cáo trung thực, phân tích vì sao (FN là ai), "
        "KHÔNG chỉnh ngưỡng trên test để 'cho đạt'.",
    ]
    (reports / "model_results.md").write_text("\n".join(md), encoding="utf-8")
    audit(cfg, "model", main=main, test_recall=t["recall"], test_f1=t["f1"])
    return metrics


def load_main(cfg: Config):
    metrics = json.loads((cfg.path("reports_dir") / "model_metrics.json").read_text(encoding="utf-8"))
    main = metrics["main_model"]
    model = joblib.load(cfg.path("processed_dir") / "models" / f"{main}.joblib")
    thr = metrics["test"][main]["threshold"]
    return model, main, thr, metrics
