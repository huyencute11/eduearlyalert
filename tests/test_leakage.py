import pytest

from eduearlyalert.leakage import LeakageError, assert_no_leakage


def test_forbidden_column_rejected(cfg):
    with pytest.raises(LeakageError):
        assert_no_leakage(cfg, ["clicks_total", "final_result"])


def test_sensitive_attribute_rejected(cfg):
    with pytest.raises(LeakageError, match="Fairness Gate"):
        assert_no_leakage(cfg, ["clicks_total", "gender"])


def test_date_after_cutoff_rejected(cfg):
    with pytest.raises(LeakageError):
        assert_no_leakage(cfg, ["clicks_total"], {"max_vle_date_used": cfg.cutoff_day + 1})


def test_clean_features_pass(cfg):
    assert_no_leakage(cfg, ["clicks_total", "n_missing"], {"max_vle_date_used": cfg.cutoff_day})


def test_built_features_respect_cutoff(pipeline_done):
    import json

    meta = json.loads((pipeline_done.path("processed_dir") / "feature_list.json").read_text())
    for k in ("max_vle_date_used", "max_due_date_used", "max_submission_date_used"):
        assert meta[k] is None or meta[k] <= pipeline_done.cutoff_day
    assert not set(meta["feature_columns"]) & set(pipeline_done.sensitive)
