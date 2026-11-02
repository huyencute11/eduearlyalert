"""Kiểm soát leakage – chạy tự động mỗi khi build feature và trước khi train.

Pipeline DỪNG (raise) nếu vi phạm. Không được tắt kiểm tra này để "cho chạy được".
"""

from __future__ import annotations

from .config import Config

# Cột chứa (hoặc suy ra được) kết quả cuối kỳ, hoặc thông tin sau mốc dự báo
FORBIDDEN_COLUMNS = {
    "final_result", "y", "date_unregistration", "withdrawn_by_cutoff",
    "module_presentation_length", "id_student", "pid", "split",
}


class LeakageError(RuntimeError):
    pass


def assert_no_leakage(cfg: Config, feature_cols: list[str], meta: dict | None = None) -> None:
    problems: list[str] = []

    bad = sorted(set(feature_cols) & FORBIDDEN_COLUMNS)
    if bad:
        problems.append(f"Cột bị cấm nằm trong feature: {bad}")

    sens = sorted(set(feature_cols) & set(cfg.sensitive))
    if sens:
        problems.append(f"Fairness Gate: thuộc tính nhạy cảm nằm trong feature: {sens}")

    if meta:
        for k in ("max_vle_date_used", "max_due_date_used", "max_submission_date_used"):
            v = meta.get(k)
            if v is not None and v > cfg.cutoff_day:
                problems.append(f"{k}={v} > cutoff_day={cfg.cutoff_day}")

    if problems:
        raise LeakageError("LEAKAGE CHECK FAILED:\n  - " + "\n  - ".join(problems))
