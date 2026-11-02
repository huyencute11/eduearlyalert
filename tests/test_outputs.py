import json

import pandas as pd

from eduearlyalert.governance import check_language


def test_reports_exist(pipeline_done):
    r = pipeline_done.path("reports_dir")
    for f in ["data_quality_report.md", "eda_findings.md", "model_results.md", "explainability_report.md",
              "fairness_report.md", "prioritization_report.md", "risk_list.csv", "kg_triples.csv"]:
        assert (r / f).exists(), f


def test_at_least_8_eda_figures(pipeline_done):
    figs = list(pipeline_done.path("figures_dir").glob("aq[1-6]_*.png"))
    assert len(figs) >= 8


def test_model_beats_rule_baseline(pipeline_done):
    m = json.loads((pipeline_done.path("reports_dir") / "model_metrics.json").read_text())
    main = m["main_model"]
    assert m["test"][main]["pr_auc"] >= m["test"]["rule"]["pr_auc"]


def test_risk_list_requires_human_review(pipeline_done):
    rl = pd.read_csv(pipeline_done.path("reports_dir") / "risk_list.csv")
    k = pipeline_done["advisor"]["k_per_advisor"] * pipeline_done["advisor"]["n_advisors"]
    assert len(rl) <= k
    assert (rl["status"] == "pending_review").all()
    assert not check_language(rl["reasons"].fillna("").tolist())


def test_kg_triples_have_provenance(pipeline_done):
    t = pd.read_csv(pipeline_done.path("reports_dir") / "kg_triples.csv")
    assert t["provenance"].str.len().gt(0).all()
