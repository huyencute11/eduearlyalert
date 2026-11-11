"""AQ10/AQ12: phương án và ngưỡng được chọn trên VALID; test chỉ để báo cáo (quy tắc 3)."""

from __future__ import annotations

import json

import pandas as pd

from eduearlyalert.prioritize import select_strategy


def _comp(rows):
    return pd.DataFrame(rows, columns=["strategy", "K", "coverage_at_K", "precision_at_K"])


def test_select_strategy_uses_highest_coverage():
    comp = _comp([("A_risk_only", 70, 0.10, 0.90),
                  ("B_risk_plus_engagement_drop", 70, 0.12, 0.85),
                  ("C_risk_plus_missing_work", 70, 0.11, 0.95)])
    assert select_strategy(comp) == "B_risk_plus_engagement_drop"


def test_select_strategy_tie_breaks_on_precision_then_simplest():
    comp = _comp([("A_risk_only", 70, 0.10, 0.90),
                  ("B_risk_plus_engagement_drop", 70, 0.10, 0.95),
                  ("C_risk_plus_missing_work", 70, 0.10, 0.95)])
    assert select_strategy(comp) == "B_risk_plus_engagement_drop"
    full_tie = _comp([(s, 70, 0.10, 0.90) for s in
                      ("A_risk_only", "B_risk_plus_engagement_drop", "C_risk_plus_missing_work")])
    assert select_strategy(full_tie) == "A_risk_only"


def _n_split(cfg, split: str) -> int:
    preds = pd.read_parquet(cfg.path("processed_dir") / "predictions.parquet")
    return int((preds["split"] == split).sum())


def test_selection_tables_are_built_on_valid(pipeline_done):
    reports = pipeline_done.path("reports_dir")
    n_valid, n_test = _n_split(pipeline_done, "valid"), _n_split(pipeline_done, "test")
    assert n_valid != n_test  # nếu bằng nhau, phép kiểm tra bên dưới không phân biệt được hai tập

    scen = pd.read_csv(reports / "aq12_threshold_scenarios.csv")
    scen_test = pd.read_csv(reports / "aq12_threshold_scenarios_test.csv")
    shares = pipeline_done["advisor"]["alert_shares"]
    assert scen["n_alerted"].tolist() == [round(s * n_valid) for s in shares]
    assert scen_test["n_alerted"].tolist() == [round(s * n_test) for s in shares]


def test_logged_strategy_matches_valid_selection(pipeline_done):
    reports = pipeline_done.path("reports_dir")
    comp_valid = pd.read_csv(reports / "aq10_strategy_comparison.csv")
    assert (reports / "aq10_strategy_comparison_test.csv").exists()
    events = [json.loads(line) for line in pipeline_done.path("audit_log").read_text(encoding="utf-8").splitlines()]
    last = [e for e in events if e.get("action") == "prioritize"][-1]
    assert last["best_strategy"] == select_strategy(comp_valid)
