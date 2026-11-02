"""Test dashboard (Streamlit AppTest): app chạy được ở mọi vai trò và PM/Lecturer không thấy dữ liệu cá nhân."""

from __future__ import annotations

from pathlib import Path

import pytest

pytest.importorskip("plotly")
from streamlit.testing.v1 import AppTest  # noqa: E402

APP = Path(__file__).resolve().parents[1] / "app" / "dashboard.py"
ROLES = ["Program Manager", "Lecturer", "Advisor"]


@pytest.fixture()
def app(pipeline_done, monkeypatch):
    monkeypatch.setenv("EDU_CONFIG", str(pipeline_done.root / "config.yaml"))
    at = AppTest.from_file(str(APP), default_timeout=60)
    at.run()
    return at


def _switch(at: AppTest, role: str) -> AppTest:
    at.sidebar.radio[0].set_value(role).run()
    return at


@pytest.mark.parametrize("role", ROLES)
def test_role_renders_without_error(app, role):
    at = _switch(app, role)
    assert not at.exception, at.exception


def test_program_manager_shows_interactive_charts(app):
    at = _switch(app, "Program Manager")
    charts = at.get("plotly_chart")
    assert len(charts) >= 5  # cohort, metrics, confusion, importance, threshold, fairness
    assert len(at.metric) >= 4


@pytest.mark.parametrize("role", ["Program Manager", "Lecturer"])
def test_aggregate_roles_hide_individuals(app, role):
    at = _switch(app, role)
    for df in at.dataframe:
        cols = {str(c).lower() for c in df.value.columns}
        assert not cols & {"pid", "id_student"}, f"{role} thấy cột cá nhân: {cols}"


def test_threshold_selector_updates_kpi(app, pipeline_done):
    import pandas as pd

    at = _switch(app, "Program Manager")
    shares = pd.read_csv(pipeline_done.path("reports_dir") / "aq12_threshold_scenarios.csv")["alert_share"]
    first = at.metric[4].value  # KPI "Số ca cảnh báo" của tab AQ12
    at.select_slider(key="alert_share").set_value(float(shares.iloc[-1])).run()
    assert not at.exception
    assert at.metric[4].value != first
