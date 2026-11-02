import pandas as pd

from eduearlyalert import cohort, features
from eduearlyalert.governance import pseudonymize


def test_label_definition(pipeline_done):
    c = cohort.load(pipeline_done)
    pos = c["final_result"].isin(["Fail", "Withdrawn"])
    assert (c["y"] == pos.astype(int)).all()


def test_prediction_population_excludes_early_withdrawals(pipeline_done):
    c = cohort.load(pipeline_done)
    pop = c[c["in_prediction_population"]]
    early = pop["date_unregistration"].notna() & (pop["date_unregistration"] <= pipeline_done.cutoff_day)
    assert not early.any()


def test_processed_data_is_pseudonymized(pipeline_done):
    df, _ = features.load(pipeline_done)
    assert "id_student" not in df.columns
    assert df["pid"].str.startswith("S").all()
    assert not set(pipeline_done.sensitive) & set(df.columns)


def test_pseudonymize_is_deterministic():
    s = pd.Series([123, 456])
    assert pseudonymize(s, "x").tolist() == pseudonymize(s, "x").tolist()
    assert pseudonymize(s, "x").tolist() != pseudonymize(s, "y").tolist()
