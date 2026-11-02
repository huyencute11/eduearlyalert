"""Test dashboard (Streamlit AppTest): app chạy được ở mọi vai trò và PM/Lecturer không thấy dữ liệu cá nhân."""

from __future__ import annotations

import json
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
def test_eda_view_has_interactive_charts(app, role):
    at = _switch(app, role)
    assert at.selectbox(key="eda_pres") is not None
    titles = " ".join(json.loads(c.proto.spec)["layout"].get("title", {}).get("text", "")
                      for c in at.get("plotly_chart"))
    for aq in ["AQ1", "AQ2", "AQ3", "AQ4", "AQ5", "AQ6"]:
        assert f"{aq} ·" in titles, f"{role} thiếu biểu đồ {aq}"


def test_eda_presentation_filter_reruns(app):
    at = _switch(app, "Lecturer")
    box = at.selectbox(key="eda_pres")
    box.set_value(box.options[-1]).run()
    assert not at.exception


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


# ---- Advisor: Risk List + human validation gate ----------------------------
def _audit_lines(cfg) -> list[dict]:
    log = cfg.path("audit_log")
    return [json.loads(x) for x in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []


def test_advisor_shows_risk_list_table_and_detail(app):
    at = _switch(app, "Advisor")
    assert not at.exception
    assert len(at.dataframe) >= 1
    assert at.selectbox(key="case_pid").value is not None
    assert len(at.get("plotly_chart")) >= 1  # AQ10


def test_advisor_approval_writes_audit_log_and_decision(app, pipeline_done):
    import pandas as pd

    at = _switch(app, "Advisor")
    pid = at.selectbox(key="case_pid").value
    before = len(_audit_lines(pipeline_done))
    at.text_area(key=f"note_{pid}").input("Đã trao đổi với GV").run()
    at.button(key=f"ok_{pid}").click().run()
    assert not at.exception
    logs = _audit_lines(pipeline_done)
    assert len(logs) == before + 1
    assert logs[-1]["action"] == "risk_list_approved" and logs[-1]["pid"] == pid
    dec = pd.read_csv(pipeline_done.path("reports_dir") / "risk_list_decisions.csv", dtype=str)
    row = dec[dec["pid"] == pid].iloc[0]
    assert row["status"] == "approved" and row["decision_note"] == "Đã trao đổi với GV"
    # Risk List gốc do pipeline sinh vẫn luôn pending_review
    rl = pd.read_csv(pipeline_done.path("reports_dir") / "risk_list.csv")
    assert (rl["status"] == "pending_review").all()


def test_advisor_requires_reviewer_name(app, pipeline_done):
    at = _switch(app, "Advisor")
    at.sidebar.text_input[0].input("   ").run()
    pid = at.selectbox(key="case_pid").value
    before = len(_audit_lines(pipeline_done))
    at.button(key=f"skip_{pid}").click().run()
    assert len(_audit_lines(pipeline_done)) == before
    assert any("Cần nhập tên người duyệt" in e.value for e in at.error)


def test_advisor_search_filter(app):
    at = _switch(app, "Advisor")
    at.text_input(key="rl_query").input("không-tồn-tại-xyz").run()
    assert not at.exception
    assert any("Không có ca nào" in i.value for i in at.info)
