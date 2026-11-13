"""GĐ3–GĐ5 – Feature engineering, CHỈ dùng dữ liệu có ngày ≤ cutoff_day.

Quy ước tuần: date < 0 → tuần 0 (trước khi môn bắt đầu); date 0..6 → tuần 1; ...
Một bài nộp SAU cutoff được coi là "chưa nộp" tại thời điểm dự báo, vì lúc đó
cố vấn chưa thể nhìn thấy nó.

Output:
  data/interim/vle_weekly.parquet    (pid × presentation × tuần × activity_type)
  data/interim/assess_long.parquet   (pid × bài đánh giá đầu kỳ: status, score)
  data/processed/features.parquet    (1 dòng/sinh viên×presentation, đã pseudonymize)
  data/processed/feature_list.json   (danh sách cột được phép vào mô hình + metadata leakage)
"""

from __future__ import annotations

import json

import numpy as np
import pandas as pd

from . import cohort as cohort_mod
from . import data_io
from .config import Config
from .governance import audit
from .leakage import assert_no_leakage

ACTIVITY_GROUPS = ["oucontent", "forumng", "quiz", "resource", "homepage", "subpage", "url"]


def _week_expr(col: str = "date", week_len: int = 7) -> str:
    return f"CASE WHEN {col} < 0 THEN 0 ELSE CAST(FLOOR({col} / {week_len}) AS INTEGER) + 1 END"


def vle_weekly(cfg: Config) -> pd.DataFrame:
    tl = cfg["timeline"]
    lo = -10_000 if tl["include_pre_start"] else 0
    where, params = data_io.scope_filter(cfg, "s")
    return data_io.query(
        cfg,
        f"""
        SELECT s.code_presentation, s.id_student,
               {_week_expr('s.date', tl['week_length'])} AS week,
               v.activity_type,
               SUM(s.sum_click) AS clicks,
               COUNT(DISTINCT s.date) AS active_days,
               MAX(s.date) AS max_date
        FROM studentVle s
        JOIN vle v USING (id_site, code_module, code_presentation)
        WHERE {where} AND s.date BETWEEN ? AND ?
        GROUP BY 1, 2, 3, 4
        """,
        [*params, lo, cfg.cutoff_day],
    )


def vle_features(cfg: Config, weekly: pd.DataFrame) -> pd.DataFrame:
    tl = cfg["timeline"]
    keys = ["code_presentation", "id_student"]
    lo = -10_000 if tl["include_pre_start"] else 0
    where, params = data_io.scope_filter(cfg)
    days = data_io.query(
        cfg,
        f"""SELECT code_presentation, id_student, COUNT(DISTINCT date) AS active_days_total
            FROM studentVle WHERE {where} AND date BETWEEN ? AND ? GROUP BY 1, 2""",
        [*params, lo, cfg.cutoff_day],
    )

    by_week = weekly.pivot_table(index=keys, columns="week", values="clicks", aggfunc="sum", fill_value=0)
    n_weeks = (cfg.cutoff_day + 1) // tl["week_length"]
    for w in range(0, n_weeks + 1):
        if w not in by_week.columns:
            by_week[w] = 0
    by_week = by_week[sorted(by_week.columns)]
    feat = pd.DataFrame(index=by_week.index)
    feat["clicks_pre_start"] = by_week[0]
    for w in range(1, n_weeks + 1):
        feat[f"clicks_w{w}"] = by_week[w]
    weeks = [f"clicks_w{w}" for w in range(1, n_weeks + 1)]
    feat["clicks_total"] = feat[weeks].sum(axis=1)
    feat["inactive_weeks"] = (feat[weeks] == 0).sum(axis=1)

    e0, e1 = tl["early_window"]
    l0, l1 = tl["late_window"]
    early = feat[[f"clicks_w{w}" for w in range(e0, e1 + 1)]].sum(axis=1)
    late = feat[[f"clicks_w{w}" for w in range(l0, l1 + 1)]].sum(axis=1)
    feat["clicks_early"] = early
    feat["clicks_late"] = late
    # >0: tăng tương tác, <0: giảm. Dùng log để không bị chi phối bởi người click rất nhiều.
    feat["engagement_change"] = np.log1p(late) - np.log1p(early)

    w_main = weekly[weekly["week"] >= 1]
    by_type = w_main.pivot_table(index=keys, columns="activity_type", values="clicks", aggfunc="sum", fill_value=0)
    total = by_type.sum(axis=1).replace(0, np.nan)
    for a in ACTIVITY_GROUPS:
        feat[f"share_{a}"] = (by_type[a] / total) if a in by_type.columns else 0.0
    feat = feat.reset_index().merge(days, on=keys, how="left")
    return feat


def assessment_long(cfg: Config) -> pd.DataFrame:
    """Mọi bài (không phải Exam) có hạn ≤ cutoff, ghép với bài nộp của từng sinh viên."""
    cutoff = cfg.cutoff_day
    where, params = data_io.scope_filter(cfg, "a")
    where_i, params_i = data_io.scope_filter(cfg, "i")
    df = data_io.query(
        cfg,
        f"""
        WITH due AS (
            SELECT a.code_presentation, a.id_assessment, a.assessment_type, a.date AS due_date, a.weight
            FROM assessments a
            WHERE {where} AND a.assessment_type <> 'Exam' AND a.date IS NOT NULL AND a.date <= ?
        ),
        students AS (
            SELECT i.code_presentation, i.id_student FROM studentInfo i WHERE {where_i}
        )
        SELECT s.code_presentation, s.id_student, d.id_assessment, d.assessment_type,
               d.due_date, d.weight,
               sa.date_submitted, sa.score
        FROM students s
        JOIN due d USING (code_presentation)
        LEFT JOIN studentAssessment sa
               ON sa.id_assessment = d.id_assessment AND sa.id_student = s.id_student
              AND COALESCE(sa.is_banked, 0) = 0
              AND sa.date_submitted <= ?
        """,
        [*params, cutoff, *params_i, cutoff],
    )
    for c in ("due_date", "weight", "date_submitted", "score"):
        df[c] = pd.to_numeric(df[c], errors="coerce").astype(float)
    df["status"] = np.select(
        [df["date_submitted"].isna().to_numpy(), (df["date_submitted"] <= df["due_date"]).to_numpy()],
        ["missing", "on_time"],
        default="late",
    )
    df["days_early"] = df["due_date"] - df["date_submitted"]
    return df


def assessment_features(long: pd.DataFrame) -> pd.DataFrame:
    keys = ["code_presentation", "id_student"]
    if long.empty:
        return pd.DataFrame(columns=keys)
    g = long.groupby(keys)
    feat = pd.DataFrame(
        {
            "n_assess_due": g.size(),
            "n_on_time": g["status"].apply(lambda s: (s == "on_time").sum()),
            "n_late": g["status"].apply(lambda s: (s == "late").sum()),
            "n_missing": g["status"].apply(lambda s: (s == "missing").sum()),
            "mean_score": g["score"].mean(),
            "min_score": g["score"].min(),
            "mean_days_early": g["days_early"].mean(),
        }
    )
    feat["share_missing"] = feat["n_missing"] / feat["n_assess_due"]
    w = long.assign(ws=long["score"].fillna(0) * long["weight"])
    wsum = w.groupby(keys)["weight"].sum()
    feat["weighted_score_so_far"] = np.where(wsum > 0, w.groupby(keys)["ws"].sum() / wsum.replace(0, np.nan), np.nan)

    first = long.sort_values(["due_date", "id_assessment"]).groupby(keys).head(1).set_index(keys)
    feat["first_assess_score"] = first["score"]
    feat["first_assess_missing"] = (first["status"] == "missing").astype(int)
    return feat.reset_index()


# Danh sách cột được phép vào mô hình. Thêm feature mới = thêm vào đây + docs/02_data.md
def model_feature_columns(df: pd.DataFrame) -> list[str]:
    base = [
        "clicks_pre_start", "clicks_total", "active_days_total", "inactive_weeks",
        "clicks_early", "clicks_late", "engagement_change",
        "n_assess_due", "n_on_time", "n_late", "n_missing", "share_missing",
        "mean_score", "min_score", "mean_days_early", "weighted_score_so_far",
        "first_assess_score", "first_assess_missing",
        "reg_days_before_start", "num_of_prev_attempts", "studied_credits",
    ]
    weekly = sorted(c for c in df.columns if c.startswith("clicks_w"))
    shares = [f"share_{a}" for a in ACTIVITY_GROUPS]
    return [c for c in [*base, *weekly, *shares] if c in df.columns]


def build(cfg: Config) -> pd.DataFrame:
    coh = cohort_mod.load(cfg)
    keys = ["code_presentation", "id_student"]
    interim, processed = cfg.path("interim_dir"), cfg.path("processed_dir")

    weekly = vle_weekly(cfg)
    vfeat = vle_features(cfg, weekly)
    long = assessment_long(cfg)
    afeat = assessment_features(long)

    pid_map = coh[keys + ["pid"]]
    weekly.merge(pid_map, on=keys).drop(columns="id_student").to_parquet(interim / "vle_weekly.parquet", index=False)
    long.merge(pid_map, on=keys).drop(columns="id_student").to_parquet(interim / "assess_long.parquet", index=False)

    df = coh.merge(vfeat, on=keys, how="left").merge(afeat, on=keys, how="left")
    df["reg_days_before_start"] = -df["date_registration"]

    zero_fill = [c for c in df.columns if c.startswith(("clicks_", "share_"))] + [
        c for c in ("active_days_total", "n_on_time", "n_late", "n_missing") if c in df.columns
    ]  # không có bài đánh giá nào hạn <= cutoff (ví dụ EEE ở ngày 27) thì không có cột bài đánh giá
    df[zero_fill] = df[zero_fill].fillna(0)
    df["inactive_weeks"] = df["inactive_weeks"].fillna((cfg.cutoff_day + 1) // cfg["timeline"]["week_length"])
    df["engagement_change"] = df["engagement_change"].fillna(0.0)

    feature_cols = model_feature_columns(df)
    meta = {
        "cutoff_day": cfg.cutoff_day,
        "max_vle_date_used": None if weekly.empty else int(weekly["max_date"].max()),
        "max_due_date_used": None if long.empty else int(long["due_date"].max()),
        "max_submission_date_used": None if long["date_submitted"].dropna().empty else int(long["date_submitted"].max()),
        "feature_columns": feature_cols,
    }
    assert_no_leakage(cfg, feature_cols, meta)

    out = df.drop(columns=["id_student", "date_unregistration"])
    out.to_parquet(processed / "features.parquet", index=False)
    (processed / "feature_list.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    audit(cfg, "features", n_rows=len(out), n_features=len(feature_cols))
    return out


def load(cfg: Config) -> tuple[pd.DataFrame, list[str]]:
    processed = cfg.path("processed_dir")
    df = pd.read_parquet(processed / "features.parquet")
    meta = json.loads((processed / "feature_list.json").read_text(encoding="utf-8"))
    return df, meta["feature_columns"]
