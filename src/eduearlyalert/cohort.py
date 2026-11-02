"""Định nghĩa cohort và nhãn.

Đơn vị phân tích: 1 dòng = 1 sinh viên × 1 presentation của module đã chọn.

Hai quần thể (xem docs/concepts.md):
  * descriptive  – mọi sinh viên đăng ký (AQ1–AQ3).
  * prediction   – sinh viên CÒN THEO HỌC tại cutoff_day (AQ7+). Ai đã rút trước
                   mốc dự báo thì không còn gì để "cảnh báo sớm"; đưa vào sẽ làm
                   Recall đẹp giả tạo.

Output:
  data/interim/cohort.parquet     (có id_student – nội bộ, không chia sẻ)
  data/interim/sensitive.parquet  (pid + thuộc tính nhạy cảm – chỉ cho AQ9)
  reports/cohort_flow.csv         (số dòng bị loại ở từng bước lọc)
"""

from __future__ import annotations

import pandas as pd

from . import data_io
from .config import Config
from .governance import audit, pseudonymize


def build(cfg: Config) -> pd.DataFrame:
    where, params = data_io.scope_filter(cfg, "i")
    df = data_io.query(
        cfg,
        f"""
        SELECT i.code_module, i.code_presentation, i.id_student, i.final_result,
               i.num_of_prev_attempts, i.studied_credits,
               {", ".join("i." + c for c in cfg.sensitive)},
               r.date_registration, r.date_unregistration,
               c.module_presentation_length
        FROM studentInfo i
        LEFT JOIN studentRegistration r USING (code_module, code_presentation, id_student)
        LEFT JOIN courses c USING (code_module, code_presentation)
        WHERE {where}
        """,
        params,
    )
    if df.empty:
        raise ValueError(
            f"Không có sinh viên cho module={cfg.module}, presentations={cfg.presentations()}. "
            "Kiểm tra reports/module_presentation_counts.csv."
        )

    cutoff = cfg.cutoff_day
    pos = set(cfg["label"]["positive_results"])
    df["y"] = df["final_result"].isin(pos).astype(int)
    df["split"] = df["code_presentation"].map(cfg.split_of)
    df["pid"] = pseudonymize(df["id_student"])

    df["withdrawn_by_cutoff"] = df["date_unregistration"].notna() & (df["date_unregistration"] <= cutoff)
    df["registered_after_cutoff"] = df["date_registration"].notna() & (df["date_registration"] > cutoff)
    df["in_prediction_population"] = ~(df["withdrawn_by_cutoff"] | df["registered_after_cutoff"])

    # Luồng lọc – bằng chứng cho Data Quality & Limitations
    flow = []
    for (pres, split), g in df.groupby(["code_presentation", "split"]):
        flow.append(
            {
                "code_presentation": pres,
                "split": split,
                "registered": len(g),
                "withdrawn_by_cutoff": int(g["withdrawn_by_cutoff"].sum()),
                "registered_after_cutoff": int(g["registered_after_cutoff"].sum()),
                "prediction_population": int(g["in_prediction_population"].sum()),
                "positive_rate_all": round(g["y"].mean(), 3),
                "positive_rate_prediction_pop": round(g.loc[g["in_prediction_population"], "y"].mean(), 3),
            }
        )
    pd.DataFrame(flow).to_csv(cfg.path("reports_dir") / "cohort_flow.csv", index=False)

    interim = cfg.path("interim_dir")
    df[["pid", "code_presentation", *cfg.sensitive]].to_parquet(interim / "sensitive.parquet", index=False)
    df.drop(columns=cfg.sensitive).to_parquet(interim / "cohort.parquet", index=False)

    audit(cfg, "cohort", n_rows=len(df), n_prediction=int(df["in_prediction_population"].sum()))
    return df


def load(cfg: Config) -> pd.DataFrame:
    return pd.read_parquet(cfg.path("interim_dir") / "cohort.parquet")


def load_sensitive(cfg: Config) -> pd.DataFrame:
    return pd.read_parquet(cfg.path("interim_dir") / "sensitive.parquet")
