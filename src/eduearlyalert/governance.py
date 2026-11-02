"""Tiện ích governance: pseudonymize, audit log, ngôn ngữ hỗ trợ, ẩn nhóm nhỏ."""

from __future__ import annotations

import getpass
import hashlib
import json
import os
from datetime import datetime, timezone

import pandas as pd

from .config import Config

# Muối (salt) để hash lại id_student. Mỗi nhóm đặt EDU_SALT riêng trong .env,
# KHÔNG commit giá trị thật lên git.
_DEFAULT_SALT = "change-me-in-.env"

# Từ ngữ không được xuất hiện trong output hướng tới người dùng (Mục 10 đề cương).
BANNED_TERMS = ["sinh viên yếu", "sinh viên kém", "học dốt", "lười", "weak student", "lazy"]


def pseudonymize(ids: pd.Series, salt: str | None = None) -> pd.Series:
    salt = salt or os.environ.get("EDU_SALT", _DEFAULT_SALT)
    return ids.astype(str).map(
        lambda x: "S" + hashlib.sha256(f"{salt}:{x}".encode()).hexdigest()[:10]
    )


def check_language(texts: list[str] | pd.Series) -> list[str]:
    """Trả về các câu vi phạm quy tắc 'không gán nhãn tiêu cực'."""
    bad = []
    for t in texts:
        low = str(t).lower()
        if any(term in low for term in BANNED_TERMS):
            bad.append(str(t))
    return bad


def suppress_small_groups(df: pd.DataFrame, count_col: str, min_size: int) -> pd.DataFrame:
    """Ẩn số liệu của nhóm có cỡ < min_size (privacy cho báo cáo tổng hợp)."""
    out = df.copy()
    small = out[count_col] < min_size
    num_cols = [c for c in out.select_dtypes("number").columns if c != count_col]
    out[num_cols] = out[num_cols].astype(float)
    out.loc[small, num_cols] = float("nan")
    out["suppressed"] = small
    return out


def audit(cfg: Config, action: str, **details) -> None:
    """Ghi một dòng JSON vào audit log (ai, lúc nào, làm gì)."""
    record = {
        "ts": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "user": os.environ.get("EDU_USER") or getpass.getuser(),
        "action": action,
        **details,
    }
    with open(cfg.path("audit_log"), "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
