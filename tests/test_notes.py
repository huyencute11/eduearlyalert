"""Nội dung nhóm viết (docs/*.md) được ghép vào report tự sinh và không mất khi chạy lại."""

from __future__ import annotations

import pytest

from eduearlyalert import audit, eda
from eduearlyalert.notes import LanguageRuleError, load_insights, load_section

INSIGHTS_MD = """# EDA insights (nhóm viết)

<!-- hướng dẫn: comment này bị bỏ qua -->

## aq1_outcomes_by_presentation.png
Tỷ lệ hoàn thành ổn định giữa các lượt,
nên cố vấn có thể dùng một ngưỡng chung.

## aq2_heatmap_week_activity.png

## Ghi chú chung
Đoạn này không thuộc hình nào.
"""


def test_load_insights_parses_by_figure_name(tmp_path):
    p = tmp_path / "eda_insights.md"
    p.write_text(INSIGHTS_MD, encoding="utf-8")
    out = load_insights(p)
    assert out == {
        "aq1_outcomes_by_presentation.png":
            "Tỷ lệ hoàn thành ổn định giữa các lượt, nên cố vấn có thể dùng một ngưỡng chung.",
    }


def test_load_insights_escapes_table_pipes(tmp_path):
    p = tmp_path / "eda_insights.md"
    p.write_text("## aq1_x.png\nA | B\n", encoding="utf-8")
    assert load_insights(p) == {"aq1_x.png": "A \\| B"}


def test_missing_files_return_empty(tmp_path):
    assert load_insights(tmp_path / "none.md") == {}
    assert load_section(tmp_path / "none.md") is None
    (tmp_path / "blank.md").write_text("<!-- chỉ có hướng dẫn -->\n", encoding="utf-8")
    assert load_section(tmp_path / "blank.md") is None


def test_duplicate_figure_heading_is_rejected(tmp_path):
    p = tmp_path / "eda_insights.md"
    p.write_text("## aq1_x.png\nA\n## aq1_x.png\nB\n", encoding="utf-8")
    with pytest.raises(ValueError, match="hai lần"):
        load_insights(p)


@pytest.mark.parametrize("loader", [load_insights, load_section])
def test_banned_language_is_rejected(tmp_path, loader):
    p = tmp_path / "notes.md"
    p.write_text("## aq1_x.png\nNhóm sinh viên yếu nộp bài muộn.\n", encoding="utf-8")
    with pytest.raises(LanguageRuleError):
        loader(p)


def test_team_notes_survive_pipeline_rerun(pipeline_done):
    cfg = pipeline_done
    dq_path, ins_path = cfg.path("dq_notes"), cfg.path("eda_insights")
    dq_path.write_text("| Vấn đề | Quyết định |\n|---|---|\n| imd_band thiếu | giữ NaN |\n", encoding="utf-8")
    ins_path.write_text("## aq1_outcomes_by_presentation.png\nInsight thử nghiệm.\n", encoding="utf-8")
    try:
        audit.run(cfg)
        eda.run(cfg)
        reports = cfg.path("reports_dir")
        dq = (reports / "data_quality_report.md").read_text(encoding="utf-8")
        findings = (reports / "eda_findings.md").read_text(encoding="utf-8")
        assert "| imd_band thiếu | giữ NaN |" in dq
        assert "| TODO | | | |" not in dq
        assert "| **Insight** | Insight thử nghiệm. |" in findings
        assert eda.INSIGHT_TODO in findings  # các hình chưa có insight vẫn giữ TODO
    finally:
        dq_path.unlink()
        ins_path.unlink()
        audit.run(cfg)
        eda.run(cfg)


def test_reports_keep_todo_without_team_notes(pipeline_done):
    reports = pipeline_done.path("reports_dir")
    assert "| TODO | | | |" in (reports / "data_quality_report.md").read_text(encoding="utf-8")
    assert eda.INSIGHT_TODO in (reports / "eda_findings.md").read_text(encoding="utf-8")
