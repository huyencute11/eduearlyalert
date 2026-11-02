"""GĐ3 – Data audit: data quality report + data dictionary tự sinh.

Output:
  reports/data_quality_report.md
  reports/data_dictionary_auto.csv     (đối chiếu với docs/02_data.md)
  reports/module_presentation_counts.csv  (để chọn module)
"""

from __future__ import annotations

import pandas as pd

from . import data_io
from .config import Config
from .governance import audit

# Khoá chính dự kiến của từng bảng (theo tài liệu OULAD)
PRIMARY_KEYS = {
    "courses": ["code_module", "code_presentation"],
    "assessments": ["id_assessment"],
    "vle": ["id_site"],
    "studentInfo": ["code_module", "code_presentation", "id_student"],
    "studentRegistration": ["code_module", "code_presentation", "id_student"],
    "studentAssessment": ["id_assessment", "id_student"],
}

# Kiểm tra toàn vẹn tham chiếu: (bảng con, bảng cha, cột nối)
FOREIGN_KEYS = [
    ("studentAssessment", "assessments", ["id_assessment"]),
    ("studentVle", "vle", ["id_site"]),
    ("studentVle", "studentInfo", ["code_module", "code_presentation", "id_student"]),
    ("studentRegistration", "studentInfo", ["code_module", "code_presentation", "id_student"]),
]


def _profile_table(con, table: str) -> tuple[pd.DataFrame, dict]:
    cols = con.execute(f"DESCRIBE {table}").df()[["column_name", "column_type"]]
    n = con.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    rows = []
    for c, typ in cols.itertuples(index=False):
        nulls, distinct = con.execute(
            f'SELECT COUNT(*) - COUNT("{c}"), APPROX_COUNT_DISTINCT("{c}") FROM {table}'
        ).fetchone()
        rows.append(
            {
                "table": table,
                "column": c,
                "dtype": typ,
                "n_rows": n,
                "missing": nulls,
                "missing_pct": round(100 * nulls / n, 2) if n else 0.0,
                "approx_distinct": distinct,
            }
        )
    meta = {"table": table, "n_rows": n}
    if table in PRIMARY_KEYS:
        k = ", ".join(PRIMARY_KEYS[table])
        dup = con.execute(
            f"SELECT COALESCE(SUM(c - 1), 0) FROM (SELECT COUNT(*) c FROM {table} GROUP BY {k} HAVING c > 1)"
        ).fetchone()[0]
        meta["duplicate_keys"] = int(dup)
    return pd.DataFrame(rows), meta


def _numeric_outliers(con) -> pd.DataFrame:
    sql = """
        SELECT 'studentVle.sum_click' AS field, MIN(sum_click) mn,
               QUANTILE_CONT(sum_click, 0.5) p50, QUANTILE_CONT(sum_click, 0.99) p99, MAX(sum_click) mx
        FROM studentVle
        UNION ALL
        SELECT 'studentAssessment.score', MIN(score), QUANTILE_CONT(score, 0.5),
               QUANTILE_CONT(score, 0.99), MAX(score) FROM studentAssessment
        UNION ALL
        SELECT 'studentVle.date', MIN(date), QUANTILE_CONT(date, 0.5),
               QUANTILE_CONT(date, 0.99), MAX(date) FROM studentVle
    """
    return con.execute(sql).df()


def run(cfg: Config) -> dict:
    counts = data_io.build_database(cfg)
    reports = cfg.path("reports_dir")

    with data_io.connect(cfg, read_only=True) as con:
        profiles, metas = [], []
        for t in data_io.OULAD_TABLES:
            p, m = _profile_table(con, t)
            profiles.append(p)
            metas.append(m)
        profile = pd.concat(profiles, ignore_index=True)
        meta = pd.DataFrame(metas)

        fk_rows = []
        for child, parent, keys in FOREIGN_KEYS:
            on = " AND ".join(f"c.{k} = p.{k}" for k in keys)
            orphans = con.execute(
                f"SELECT COUNT(*) FROM {child} c WHERE NOT EXISTS "
                f"(SELECT 1 FROM {parent} p WHERE {on})"
            ).fetchone()[0]
            fk_rows.append({"child": child, "parent": parent, "keys": ",".join(keys), "orphans": orphans})
        fk = pd.DataFrame(fk_rows)

        outliers = _numeric_outliers(con)

        mp = con.execute(
            """
            SELECT code_module, code_presentation, COUNT(*) AS n_students,
                   ROUND(AVG(CASE WHEN final_result IN ('Pass','Distinction') THEN 1 ELSE 0 END), 3) AS completion_rate,
                   ROUND(AVG(CASE WHEN final_result = 'Withdrawn' THEN 1 ELSE 0 END), 3) AS withdrawn_rate
            FROM studentInfo GROUP BY 1, 2 ORDER BY 1, 2
            """
        ).df()
        early_assess = con.execute(
            f"""
            SELECT code_module, code_presentation, COUNT(*) AS n_assess_before_cutoff
            FROM assessments
            WHERE assessment_type <> 'Exam' AND date <= {cfg.cutoff_day}
            GROUP BY 1, 2
            """
        ).df()

    mp = mp.merge(early_assess, how="left", on=["code_module", "code_presentation"])
    mp["n_assess_before_cutoff"] = mp["n_assess_before_cutoff"].fillna(0).astype(int)

    profile.to_csv(reports / "data_dictionary_auto.csv", index=False)
    mp.to_csv(reports / "module_presentation_counts.csv", index=False)

    lines = [
        "# Data Quality Report (tự sinh)",
        "",
        "> Sinh bởi `python -m eduearlyalert.pipeline audit`. Không sửa tay – sửa code rồi chạy lại.",
        "> Phần **Nhận định & xử lý** ở cuối do nhóm viết.",
        "",
        "## 1. Kích thước bảng và khoá trùng",
        "",
        meta.to_markdown(index=False),
        "",
        "## 2. Giá trị thiếu (chỉ cột có thiếu)",
        "",
        profile[profile["missing"] > 0][["table", "column", "missing", "missing_pct"]].to_markdown(index=False)
        or "_Không có giá trị thiếu._",
        "",
        "## 3. Toàn vẹn tham chiếu (orphan rows)",
        "",
        fk.to_markdown(index=False),
        "",
        "## 4. Phân bố các trường số chính",
        "",
        outliers.round(2).to_markdown(index=False),
        "",
        "## 5. Module × presentation (để chọn phạm vi)",
        "",
        f"Module đang cấu hình: **{cfg.module}**, presentations: {cfg.presentations()}. "
        f"`n_assess_before_cutoff` = số bài đánh giá (không tính Exam) có hạn ≤ ngày {cfg.cutoff_day}; "
        "nếu = 0 thì AQ3, AQ5, AQ6 sẽ không có dữ liệu.",
        "",
        mp.to_markdown(index=False),
        "",
        "## 6. Nhận định & xử lý (nhóm điền)",
        "",
        "| Vấn đề | Bằng chứng (mục nào ở trên) | Quyết định xử lý | Ảnh hưởng tới AQ |",
        "|---|---|---|---|",
        "| TODO | | | |",
        "",
    ]
    (reports / "data_quality_report.md").write_text("\n".join(lines), encoding="utf-8")
    audit(cfg, "audit", row_counts=counts)
    return {"row_counts": counts, "module_presentations": mp}
