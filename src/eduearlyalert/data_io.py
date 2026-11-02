"""Nạp 7 file CSV của OULAD vào DuckDB và đọc dữ liệu theo phạm vi đã cấu hình.

OULAD mã hoá giá trị thiếu bằng ký tự '?', nên luôn đọc với nullstr='?'.
"""

from __future__ import annotations

import duckdb
import pandas as pd

from .config import Config

OULAD_TABLES = [
    "courses",
    "assessments",
    "vle",
    "studentInfo",
    "studentRegistration",
    "studentAssessment",
    "studentVle",
]


def connect(cfg: Config, read_only: bool = False) -> duckdb.DuckDBPyConnection:
    return duckdb.connect(str(cfg.path("db_path")), read_only=read_only)


def build_database(cfg: Config) -> dict[str, int]:
    """Tạo (hoặc tạo lại) DuckDB từ CSV. Trả về số dòng mỗi bảng."""
    raw_dir = cfg.path("raw_dir")
    missing = [t for t in OULAD_TABLES if not (raw_dir / f"{t}.csv").exists()]
    if missing:
        raise FileNotFoundError(
            f"Thiếu file trong {raw_dir}: {missing}. "
            "Tải OULAD tại https://analyse.kmi.open.ac.uk/open_dataset "
            "(xem docs/02_data.md) hoặc chạy scripts/make_fake_oulad.py để thử."
        )
    counts: dict[str, int] = {}
    with connect(cfg) as con:
        for t in OULAD_TABLES:
            csv = (raw_dir / f"{t}.csv").as_posix()
            con.execute(
                f"CREATE OR REPLACE TABLE {t} AS "
                f"SELECT * FROM read_csv('{csv}', header=true, nullstr='?', auto_detect=true)"
            )
            counts[t] = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    return counts


def query(cfg: Config, sql: str, params: list | None = None) -> pd.DataFrame:
    with connect(cfg, read_only=True) as con:
        return con.execute(sql, params or []).df()


def scope_filter(cfg: Config, alias: str = "") -> tuple[str, list]:
    """Mệnh đề WHERE giới hạn module + presentation theo config."""
    a = f"{alias}." if alias else ""
    pres = cfg.presentations()
    placeholders = ",".join(["?"] * len(pres))
    return f"{a}code_module = ? AND {a}code_presentation IN ({placeholders})", [cfg.module, *pres]
