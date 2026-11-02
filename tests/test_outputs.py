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


EDA_DASHBOARD_TABLES = ["aq1_outcomes", "aq1_withdrawal", "aq2_activity_week", "aq2_weekly_clicks",
                        "aq3_submission", "aq3_scores", "aq4_weekly_median", "aq5_first_score", "aq6_concept_gaps"]


def test_eda_dashboard_tables_are_aggregate_and_train_valid_only(pipeline_done):
    r = pipeline_done.path("reports_dir")
    allowed = set(pipeline_done.presentations("train") + pipeline_done.presentations("valid")) | {"train+valid"}
    for name in EDA_DASHBOARD_TABLES:
        t = pd.read_csv(r / f"{name}.csv")
        assert len(t), name
        assert not {"pid", "id_student"} & set(t.columns), name
        assert set(t["code_presentation"]) <= allowed, f"{name} chứa presentation test"
        assert "train+valid" in set(t["code_presentation"]), name


def test_eda_dashboard_tables_suppress_small_groups():
    from eduearlyalert.eda import _suppress

    df = pd.DataFrame({"week": [1, 2], "n_group": [5, 50], "share": [0.2, 0.4]})
    out = _suppress(df, "n_group", ["share"], 10)
    assert out["suppressed"].tolist() == [True, False]
    assert pd.isna(out.loc[0, "share"]) and out.loc[1, "share"] == 0.4
    assert out["week"].tolist() == [1, 2]  # khoá trục không bị ẩn
