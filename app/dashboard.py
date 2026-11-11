"""EduEarlyAlert – Dashboard demo (Streamlit).

  streamlit run app/dashboard.py

Ba góc nhìn theo vai trò (phân quyền MÔ PHỎNG qua sidebar), mỗi màn hình phục vụ một quyết định
(docs/01_project_overview.md) và đi theo mạch Câu hỏi → Kết luận có số → Bằng chứng → Chi tiết kỹ thuật:
  * Program Manager – D3: phân bổ cố vấn, có nên dùng hệ thống. Chỉ số tổng hợp, KHÔNG thấy cá nhân.
  * Lecturer        – D2: điều chỉnh bài đánh giá / hoạt động / ôn tập. Chỉ số tổng hợp.
  * Advisor         – D1: tuần này liên hệ ai trước. Risk List có lý do + nút phê duyệt (human gate).
Dashboard chỉ đọc reports/; mọi quyết định của cố vấn được ghi vào reports/audit_log.jsonl.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eduearlyalert.config import load_config  # noqa: E402
from eduearlyalert.governance import audit  # noqa: E402

cfg = load_config()
REPORTS = cfg.path("reports_dir")
DECISIONS = REPORTS / "risk_list_decisions.csv"
ALL_PRES = "train+valid"
WEEK_LEN = cfg["timeline"]["week_length"]
CUTOFF_WEEK = cfg.cutoff_day // WEEK_LEN + 1  # ngày 41 → hết Tuần 6

st.set_page_config(page_title="EduEarlyAlert", page_icon="🎓", layout="wide")

# ---------------------------------------------------------------------------
# Màu & thuật ngữ
# ---------------------------------------------------------------------------
# Categorical cố định thứ tự (đã kiểm CVD); màu đi theo thực thể, không theo thứ hạng.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
GROUP_COLOR = {"Hoàn thành": SERIES[0], "Không hoàn thành": SERIES[1]}
# Kết quả cuối kỳ: hai sắc xanh = hoàn thành, hai sắc cam = không hoàn thành.
OUTCOME = {"Distinction": ("Giỏi (Distinction)", "#184f95"), "Pass": ("Đạt (Pass)", "#6da7ec"),
           "Fail": ("Không đạt (Fail)", "#f3a37f"), "Withdrawn": ("Rút môn (Withdrawn)", "#d95926")}
STATUS = {"on_time": ("Nộp đúng hạn", SERIES[0]), "late": ("Nộp muộn", SERIES[3]),
          "missing": ("Chưa nộp (tính đến Tuần 6)", SERIES[1])}
GRID = "rgba(128,128,128,0.18)"

GLOSSARY = f"""
**Mốc dự báo** – ngày {cfg.cutoff_day} của học kỳ (hết Tuần {CUTOFF_WEEK}). Hệ thống chỉ dùng dữ liệu đến mốc này.

**Học kỳ** – mã lượt giảng dạy trong OULAD: năm + `B` (bắt đầu tháng 2) hoặc `J` (tháng 10), ví dụ 2013J.

**Tập huấn luyện / kiểm định / kiểm tra** – chia theo học kỳ: mô hình học trên 2013B, 2013J; chọn ngưỡng
trên 2014B; **đánh giá cuối trên 2014J** (chưa từng nhìn thấy). Phân tích khám phá chỉ dùng 3 học kỳ đầu.

**Tỷ lệ phát hiện (Recall)** – trong số sinh viên thực sự không hoàn thành, bao nhiêu % được cảnh báo.

**Độ chính xác cảnh báo (Precision)** – trong số sinh viên được cảnh báo, bao nhiêu % thực sự cần hỗ trợ.

**F1** – trung bình điều hoà của hai chỉ số trên (0–1, càng cao càng tốt).

**Điểm rủi ro** – xác suất (0–1) mô hình ước lượng sinh viên không hoàn thành môn.

**Mã ẩn danh** – mã `S…` thay cho mã sinh viên thật; dashboard không hiển thị danh tính.

**KG mô phỏng** – ánh xạ Bài đánh giá → Concept → Tài nguyên do nhóm tự xây dựng, không phải dữ liệu thật.

**Liên hệ ≠ nguyên nhân** – các tín hiệu cho thấy sự khác biệt giữa hai nhóm, không chứng minh nguyên nhân.
"""


# ---------------------------------------------------------------------------
# Tiện ích đọc dữ liệu & bố cục
# ---------------------------------------------------------------------------
def need(path: Path) -> bool:
    if not path.exists():
        st.warning(f"Chưa có `{path.relative_to(cfg.root)}`. Chạy `python -m eduearlyalert.pipeline all` trước.")
        return False
    return True


def read_csv(name: str) -> pd.DataFrame | None:
    """Đọc một CSV trong reports/; None nếu bước pipeline tương ứng chưa chạy."""
    p = REPORTS / name
    return pd.read_csv(p) if p.exists() else None


def visible(df: pd.DataFrame) -> pd.DataFrame:
    """Bỏ các dòng đã bị ẩn vì nhóm < min_group_size."""
    return df[~df["suppressed"].astype(bool)] if "suppressed" in df.columns else df


def pct(x: float, digits: int = 0) -> str:
    return f"{x:.{digits}%}"


def week_label(w: int) -> str:
    return "Trước khai giảng" if w <= 0 else f"Tuần {w}"


def question_box(question: str, decision: str, findings: list[str]) -> None:
    """Khối mở đầu mỗi vai trò: câu hỏi của người dùng + kết luận chính (số tự sinh từ reports/)."""
    with st.container(border=True):
        st.markdown(f"#### ❓ {question}")
        st.caption(f"Quyết định được hỗ trợ: {decision}")
        if findings:
            st.markdown("**Kết luận chính**")
            st.markdown("\n".join(f"{i}. {f}" for i, f in enumerate(findings, 1)))


def evidence(title: str, takeaway: str, fig: go.Figure, source: str) -> None:
    """Một biểu đồ làm bằng chứng: tiêu đề + câu kết luận phía trên, nguồn (AQ, file) phía dưới."""
    st.markdown(f"**{title}**")
    if takeaway:
        st.markdown(takeaway)
    st.plotly_chart(fig, width="stretch",
                    config={"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})
    st.caption(f"Nguồn: {source}")


def style(fig: go.Figure, height: int = 340, y_pct: bool = False, hover: str = "x unified") -> go.Figure:
    """Giao diện chung: không tiêu đề trong hình (tiêu đề ở markdown), legend phía trên, lưới mờ."""
    fig.update_layout(
        height=height, margin={"l": 8, "r": 8, "t": 36, "b": 8}, hovermode=hover,
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.0, "xanchor": "left", "x": 0, "title": None},
        bargap=0.3, bargroupgap=0.08, font={"size": 13},
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor=GRID, zeroline=False)
    if y_pct:
        fig.update_yaxes(tickformat=".0%", range=[0, 1.05])
    return fig


# ---------------------------------------------------------------------------
# Biểu đồ – Program Manager
# ---------------------------------------------------------------------------
def outcome_chart(d: pd.DataFrame) -> go.Figure:
    """AQ1 · Kết quả cuối kỳ theo học kỳ (cột chồng 100%)."""
    d = visible(d[d["code_presentation"] != ALL_PRES])
    fig = go.Figure()
    for res, (label, color) in OUTCOME.items():
        s = d[d["final_result"] == res]
        if len(s):
            fig.add_bar(name=label, x=s["code_presentation"], y=s["share"], customdata=s["n"],
                        marker={"color": color, "line": {"width": 2, "color": "white"}},
                        hovertemplate="%{y:.1%} (%{customdata:.0f} SV)<extra>" + label + "</extra>")
    fig.update_layout(barmode="stack", legend={"traceorder": "normal"})
    fig = style(fig, y_pct=True)
    fig.update_xaxes(title="Học kỳ")
    return fig


def withdrawal_chart(d: pd.DataFrame) -> go.Figure:
    """AQ1 · Rút môn tích luỹ theo tuần, có vạch mốc dự báo."""
    d = visible(d[d["code_presentation"] != ALL_PRES])
    fig = go.Figure()
    for i, (p, s) in enumerate(d.groupby("code_presentation")):
        fig.add_scatter(x=s["week"], y=s["cum_share"], name=p, mode="lines",
                        line={"width": 2, "color": SERIES[i % len(SERIES)]}, hovertemplate="%{y:.1%}")
    fig.add_vrect(x0=0, x1=CUTOFF_WEEK, fillcolor="rgba(128,128,128,0.08)", line_width=0)
    fig.add_vline(x=CUTOFF_WEEK, line={"dash": "dot", "width": 1, "color": "gray"},
                  annotation_text=f"Mốc dự báo (hết Tuần {CUTOFF_WEEK})", annotation_position="top right")
    fig = style(fig)
    fig.update_yaxes(tickformat=".0%", title="% sinh viên đã rút môn")
    fig.update_xaxes(title="Tuần học")
    return fig


def detection_chart(test: dict, main: str, recall_min: float) -> go.Figure:
    """AQ7 · Mô hình chính so với luật đơn giản (baseline) trên học kỳ kiểm tra."""
    keys = [("recall", "Tỷ lệ phát hiện"), ("precision", "Độ chính xác cảnh báo"), ("f1", "F1")]
    fig = go.Figure()
    for i, (name, label) in enumerate([("rule", "Luật đơn giản (so sánh)"), (main, "Mô hình được chọn")]):
        m = test[name]
        fig.add_bar(name=label, x=[k[1] for k in keys], y=[m[k[0]] for k in keys], marker_color=SERIES[i],
                    text=[pct(m[k[0]]) if k[0] != "f1" else f"{m['f1']:.2f}" for k in keys], textposition="outside",
                    hovertemplate="%{y:.2f}<extra>" + label + "</extra>")
    # Mục tiêu chỉ áp dụng cho tỷ lệ phát hiện → vạch ngắn trên nhóm cột đầu tiên.
    fig.add_shape(type="line", xref="x", yref="y", x0=-0.45, x1=0.45, y0=recall_min, y1=recall_min,
                  line={"dash": "dot", "width": 2, "color": "gray"})
    fig.add_annotation(x=0, y=1.0, xref="x", yref="y", text=f"Mục tiêu ≥ {pct(recall_min)}",
                       showarrow=False, font={"size": 12, "color": "gray"})
    fig.update_layout(barmode="group")
    fig = style(fig, y_pct=True)
    fig.update_yaxes(range=[0, 1.08])
    return fig


def outcome_split_chart(m: dict) -> go.Figure:
    """AQ7 · Kết quả cảnh báo trên học kỳ kiểm tra, diễn giải bằng lời."""
    cats = [("Phát hiện đúng", m["tp"], SERIES[0]), ("Bỏ sót", m["fn"], SERIES[1]),
            ("Báo nhầm", m["fp"], SERIES[3]), ("Không cảnh báo, đúng", m["tn"], "#b9c4d0")]
    fig = go.Figure(go.Bar(
        y=[c[0] for c in cats][::-1], x=[c[1] for c in cats][::-1], orientation="h",
        marker_color=[c[2] for c in cats][::-1], text=[c[1] for c in cats][::-1], textposition="outside",
        hovertemplate="%{y}: %{x} sinh viên<extra></extra>"))
    fig = style(fig, height=260, hover="closest")
    fig.update_xaxes(showgrid=True, gridcolor=GRID, title="Số sinh viên (học kỳ kiểm tra)",
                     range=[0, max(c[1] for c in cats) * 1.18])
    return fig


def threshold_chart(sc: pd.DataFrame, selected: float) -> go.Figure:
    """AQ12 · Phát hiện vs độ chính xác theo tỷ lệ sinh viên được cảnh báo."""
    fig = go.Figure()
    for i, (k, label) in enumerate([("recall", "Tỷ lệ phát hiện"), ("precision", "Độ chính xác cảnh báo")]):
        fig.add_scatter(x=sc["alert_share"], y=sc[k], name=label, mode="lines+markers",
                        line={"width": 2, "color": SERIES[i]}, marker={"size": 9, "line": {"width": 2, "color": "white"}},
                        hovertemplate="%{y:.1%}")
    fig.add_vline(x=selected, line={"dash": "dot", "width": 1, "color": "gray"})
    fig = style(fig, y_pct=True)
    fig.update_xaxes(tickformat=".0%", title="Tỷ lệ sinh viên được cảnh báo", tickvals=sc["alert_share"])
    return fig


def fairness_chart(fb: pd.DataFrame, attribute: str, overall: float) -> go.Figure:
    """AQ9 · Tỷ lệ phát hiện theo nhóm của một thuộc tính (nhóm nhỏ đã ẩn)."""
    d = visible(fb[fb["attribute"] == attribute]).sort_values("recall")
    fig = go.Figure(go.Bar(x=d["recall"], y=d["group"], orientation="h", marker_color=SERIES[0],
                           customdata=d[["n"]], text=[pct(v) for v in d["recall"]], textposition="outside",
                           hovertemplate="%{y}: phát hiện %{x:.1%} (n = %{customdata[0]})<extra></extra>"))
    fig.add_vline(x=overall, line={"dash": "dot", "width": 1, "color": "gray"},
                  annotation_text=f"Chung: {pct(overall)}", annotation_position="top")
    fig = style(fig, height=max(240, 36 * len(d) + 80), hover="closest")
    fig.update_xaxes(tickformat=".0%", range=[0, 1.1], showgrid=True, gridcolor=GRID)
    return fig


def importance_chart(imp: pd.DataFrame, top: int = 10) -> go.Figure:
    """AQ7 · Permutation importance (mức giảm PR-AUC khi xáo trộn feature)."""
    imp = imp.rename(columns={imp.columns[0]: "feature"}).nlargest(top, "perm_importance_pr_auc").iloc[::-1]
    fig = go.Figure(go.Bar(x=imp["perm_importance_pr_auc"], y=imp["feature"], orientation="h",
                           marker_color=SERIES[0], hovertemplate="%{y}: %{x:.4f}<extra></extra>"))
    fig = style(fig, height=26 * top + 80, hover="closest")
    fig.update_xaxes(showgrid=True, gridcolor=GRID, title="Mức giảm PR-AUC")
    return fig


# ---------------------------------------------------------------------------
# Biểu đồ – Lecturer
# ---------------------------------------------------------------------------
def submission_chart(d: pd.DataFrame) -> go.Figure:
    """AQ3 · Tình trạng nộp bài đánh giá đầu kỳ."""
    d = visible(d)
    fig = go.Figure()
    for status, (label, color) in STATUS.items():
        s = d[d["status"] == status]
        fig.add_bar(name=label, y=s["assessment_key"], x=s["share"], orientation="h", customdata=s["n"],
                    marker={"color": color, "line": {"width": 2, "color": "white"}},
                    hovertemplate="%{x:.1%} (%{customdata:.0f} SV)<extra>" + label + "</extra>")
    fig.update_layout(barmode="stack", legend={"traceorder": "normal"})
    fig = style(fig, height=max(240, 56 * d["assessment_key"].nunique() + 100), hover="y unified")
    fig.update_xaxes(tickformat=".0%", range=[0, 1], showgrid=True, gridcolor=GRID)
    fig.update_yaxes(categoryorder="category descending", title="Bài đánh giá")
    return fig


def first_score_chart(d: pd.DataFrame) -> go.Figure:
    """AQ5 · Tỷ lệ hoàn thành theo điểm bài đánh giá đầu tiên."""
    d = visible(d)
    fig = go.Figure(go.Bar(x=d["bin"], y=d["completion"], customdata=d["n"], marker_color=SERIES[0],
                           text=[pct(v) for v in d["completion"]], textposition="outside",
                           hovertemplate="%{x}: %{y:.1%} hoàn thành (%{customdata} SV)<extra></extra>"))
    fig = style(fig, y_pct=True, hover="closest")
    fig.update_xaxes(title="Điểm bài đánh giá đầu tiên")
    fig.update_yaxes(title="Tỷ lệ hoàn thành môn")
    return fig


def weekly_groups_chart(d: pd.DataFrame) -> go.Figure:
    """AQ4 · Trung vị click/tuần của hai nhóm."""
    d = visible(d)
    fig = go.Figure()
    for grp, s in d.groupby("group"):
        fig.add_scatter(x=[week_label(int(w)) for w in s["week"]], y=s["median"], name=grp, mode="lines+markers",
                        line={"width": 2, "color": GROUP_COLOR.get(grp, SERIES[2])},
                        marker={"size": 9, "line": {"width": 2, "color": "white"}}, hovertemplate="%{y:.0f} click")
    fig = style(fig)
    fig.update_yaxes(rangemode="tozero", title="Số click trung vị / tuần")
    return fig


def heatmap_chart(d: pd.DataFrame) -> go.Figure:
    """AQ2 · Click trung bình/sinh viên theo tuần × loại tài nguyên."""
    t = d.pivot_table(index="activity_type", columns="week", values="clicks_per_student", aggfunc="sum").fillna(0)
    t = t.loc[t.sum(axis=1).sort_values().index]
    fig = go.Figure(go.Heatmap(
        z=t.values, x=[week_label(int(w)) for w in t.columns], y=t.index, xgap=2, ygap=2,
        colorscale=[[0, "#eef4fc"], [0.5, "#3987e5"], [1, "#104281"]], colorbar={"title": "Click/SV"},
        texttemplate="%{z:.0f}", hovertemplate="%{y} · %{x}: %{z:.1f} click/SV<extra></extra>"))
    return style(fig, height=max(300, 30 * len(t) + 80), hover="closest")


def concept_chart(d: pd.DataFrame) -> go.Figure:
    """AQ6 · Tỷ lệ cần hỗ trợ thêm theo concept, theo nhóm kết quả."""
    d = visible(d)
    fig = go.Figure()
    for grp in ["Hoàn thành", "Không hoàn thành"]:
        s = d[d["group"] == grp].sort_values("concept_id", ascending=False)
        fig.add_bar(name=grp, y=s["concept_id"], x=s["share_needs_support"], orientation="h", customdata=s["n"],
                    marker_color=GROUP_COLOR[grp], hovertemplate="%{x:.1%} (n=%{customdata})<extra>" + grp + "</extra>")
    fig.update_layout(barmode="group")
    fig = style(fig, height=max(300, 44 * d["concept_id"].nunique() + 100), hover="y unified")
    fig.update_xaxes(tickformat=".0%", range=[0, 1], showgrid=True, gridcolor=GRID,
                     title="% sinh viên cần hỗ trợ thêm ở concept")
    return fig


def effect_chart(d: pd.DataFrame) -> go.Figure:
    """AQ4 · Effect size Cliff's δ."""
    d = d.sort_values("cliffs_delta")
    fig = go.Figure(go.Bar(x=d["cliffs_delta"], y=d["indicator"], orientation="h", marker_color=SERIES[0],
                           customdata=d[["magnitude", "p_holm"]],
                           hovertemplate="%{y}<br>δ = %{x:.2f} (%{customdata[0]})<br>p Holm = %{customdata[1]:.1e}"
                                         "<extra></extra>"))
    fig.add_vline(x=0, line={"width": 1, "color": "gray"})
    fig = style(fig, height=300, hover="closest")
    fig.update_xaxes(range=[-1, 1], showgrid=True, gridcolor=GRID, title="Cliff's δ (hoàn thành vs không)")
    return fig


def odds_chart(d: pd.DataFrame) -> go.Figure:
    """AQ5 · Odds ratio / +1 SD (CI 95%)."""
    d = d.rename(columns={d.columns[0]: "term"}).sort_values("odds_ratio_per_SD")
    fig = go.Figure(go.Scatter(
        x=d["odds_ratio_per_SD"], y=d["term"], mode="markers", marker={"size": 10, "color": SERIES[0]},
        error_x={"type": "data", "symmetric": False, "array": d["ci_high"] - d["odds_ratio_per_SD"],
                 "arrayminus": d["odds_ratio_per_SD"] - d["ci_low"], "thickness": 2, "width": 0, "color": SERIES[0]},
        customdata=d[["ci_low", "ci_high"]],
        hovertemplate="%{y}<br>OR = %{x:.2f} [%{customdata[0]:.2f}–%{customdata[1]:.2f}]<extra></extra>"))
    fig.add_vline(x=1, line={"dash": "dot", "width": 1, "color": "gray"})
    fig = style(fig, height=300, hover="closest")
    fig.update_xaxes(type="log", showgrid=True, gridcolor=GRID, title="OR của không hoàn thành / +1 SD (log)")
    return fig


def strategy_chart(d: pd.DataFrame) -> go.Figure:
    """AQ10 · Coverage@K và Precision@K của các phương án ưu tiên."""
    names = {"A_risk_only": "A · Chỉ theo điểm rủi ro", "B_risk_plus_engagement_drop": "B · Rủi ro + giảm tương tác",
             "C_risk_plus_missing_work": "C · Rủi ro + chưa nộp bài"}
    fig = go.Figure()
    for i, (col, label) in enumerate([("coverage_at_K", "Bao phủ: % SV cần hỗ trợ lọt vào danh sách"),
                                      ("precision_at_K", "Độ chính xác: % ca trong danh sách thực sự cần hỗ trợ")]):
        fig.add_bar(name=label, x=[names.get(s, s) for s in d["strategy"]], y=d[col], marker_color=SERIES[i],
                    text=[pct(v) for v in d[col]], textposition="outside", hovertemplate="%{y:.1%}<extra></extra>")
    fig.update_layout(barmode="group")
    return style(fig, y_pct=True)


# ---------------------------------------------------------------------------
# Program Manager – D3
# ---------------------------------------------------------------------------
def program_manager_view() -> None:
    st.title("Quản lý chương trình")
    if not need(REPORTS / "model_metrics.json"):
        return
    m = json.loads((REPORTS / "model_metrics.json").read_text(encoding="utf-8"))
    main, acc = m["main_model"], m["acceptance"]
    t = m["test"][main]
    flow, wd = read_csv("cohort_flow.csv"), read_csv("aq1_withdrawal.csv")
    sc, fb, out = read_csv("aq12_threshold_scenarios.csv"), read_csv("fairness_by_group.csv"), read_csv("aq1_outcomes.csv")
    adv = cfg["advisor"]
    capacity = adv["k_per_advisor"] * adv["n_advisors"]

    findings = []
    if flow is not None:
        comp = 1 - (flow["positive_rate_all"] * flow["registered"]).sum() / flow["registered"].sum()
        findings.append(f"Chỉ **{pct(comp, 1)}** sinh viên hoàn thành môn ({flow['registered'].sum():,} lượt đăng ký, "
                        "4 học kỳ). Mốc 60% trong proposal là giả định, cần so lại với con số này.")
    if wd is not None:
        a = wd[wd["code_presentation"] == ALL_PRES]
        final, before = a["cum_share"].max(), a.loc[a["week"] <= CUTOFF_WEEK, "cum_share"].max()
        if final > 0:
            findings.append(f"**{pct(1 - before / final)}** số ca rút môn xảy ra **sau Tuần {CUTOFF_WEEK}** → "
                            "cảnh báo ở cuối Tuần 6 vẫn còn thời gian để hỗ trợ.")
    ok = "đạt" if t["recall"] >= acc["recall_min"] else "**chưa đạt**"
    findings.append(f"Trên học kỳ kiểm tra (chưa từng dùng để huấn luyện), mô hình phát hiện **{t['tp']}/{t['positives']}"
                    f" ({pct(t['recall'])})** sinh viên không hoàn thành – {ok} mục tiêu {pct(acc['recall_min'])}; "
                    f"cứ 100 cảnh báo thì **{t['precision'] * 100:.0f}** đúng.")
    if sc is not None and len(sc):
        fits = sc[sc["fits_capacity"].astype(bool)]
        cap_txt = (f"chỉ đủ cảnh báo **top {pct(fits['alert_share'].max())}** sinh viên mỗi tuần"
                   if len(fits) else "chưa đủ cho kịch bản cảnh báo nhỏ nhất")
        findings.append(f"Với {adv['n_advisors']} cố vấn × {adv['k_per_advisor']} ca/tuần = {capacity} ca "
                        f"(giả định), năng lực hiện tại {cap_txt} – xem mục ③ để cân nhắc tăng nguồn lực.")
    if fb is not None and len(fb):
        v = visible(fb).dropna(subset=["recall"])
        gaps = v.groupby("attribute")["recall"].agg(lambda s: s.max() - s.min())
        if len(gaps):
            findings.append(f"Chênh lệch tỷ lệ phát hiện lớn nhất giữa các nhóm là **{gaps.max() * 100:.0f} điểm %** "
                            f"(theo {gaps.idxmax()}) – cần theo dõi trước khi mở rộng.")
    question_box("Có nên dùng hệ thống cảnh báo sớm, và cần bao nhiêu năng lực cố vấn?",
                 "D3 – phân bổ cố vấn, quyết định mở rộng mô hình (khó đảo ngược, cần cân nhắc kỹ).", findings)

    c1, c2, c3, c4 = st.columns(4, border=True)
    if flow is not None:
        c1.metric("Tỷ lệ hoàn thành môn", pct(comp, 1))
    c2.metric("Tỷ lệ phát hiện", pct(t["recall"]), f"{(t['recall'] - acc['recall_min']) * 100:+.0f} điểm % so với mục tiêu",
              help="Recall trên học kỳ kiểm tra: % sinh viên không hoàn thành được cảnh báo.")
    c3.metric("Độ chính xác cảnh báo", pct(t["precision"]), help="Precision: % cảnh báo là đúng.")
    c4.metric("Năng lực cố vấn / tuần", f"{capacity} ca", help="Giả định của proposal, chưa phải dữ kiện.")

    tab1, tab2, tab3, tab4 = st.tabs(["① Hiện trạng hoàn thành", "② Mô hình phát hiện được bao nhiêu",
                                      "③ Năng lực cố vấn & ngưỡng cảnh báo", "④ Công bằng giữa các nhóm"])
    with tab1:
        l, r = st.columns(2)
        if out is not None:
            with l:
                evidence("Kết quả cuối kỳ theo học kỳ", "Phần màu cam là sinh viên không hoàn thành (trượt hoặc rút môn).",
                         outcome_chart(out), "AQ1 · reports/aq1_outcomes.csv (3 học kỳ khám phá)")
        if wd is not None:
            with r:
                evidence("Sinh viên rút môn vào tuần nào?",
                         f"Vùng xám là 6 tuần đầu; đường còn đi lên rõ sau Tuần {CUTOFF_WEEK} → còn cửa sổ can thiệp.",
                         withdrawal_chart(wd), "AQ1 · reports/aq1_withdrawal.csv")
    with tab2:
        l, r = st.columns([3, 2])
        with l:
            evidence("Mô hình so với một luật đơn giản",
                     "Luật đơn giản = cảnh báo khi có dấu hiệu rõ (vd. chưa nộp bài). Mô hình cần tốt hơn mới đáng dùng.",
                     detection_chart(m["test"], main, acc["recall_min"]), "AQ7 · reports/model_metrics.json (học kỳ kiểm tra)")
        with r:
            evidence(f"{t['n']} sinh viên của học kỳ kiểm tra được xếp thế nào",
                     f"**Bỏ sót {t['fn']}** sinh viên – đây là nhóm cần cơ chế khác (giảng viên, tự đăng ký hỗ trợ).",
                     outcome_split_chart(t), "AQ7 · reports/model_metrics.json")
        with st.expander("Chi tiết kỹ thuật: mọi mô hình, cả tập kiểm định, feature quan trọng"):
            st.dataframe(pd.concat({"Kiểm định (valid)": pd.DataFrame(m["valid"]).T,
                                    "Kiểm tra (test)": pd.DataFrame(m["test"]).T}), width="stretch")
            imp = read_csv("feature_importance.csv")
            if imp is not None:
                evidence("Feature mô hình dựa vào nhiều nhất", "Mức độ mô hình dựa vào – là liên hệ, không phải nguyên nhân.",
                         importance_chart(imp), "AQ7 · reports/feature_importance.csv")
    with tab3:
        if sc is not None and len(sc):
            shares = sc["alert_share"].tolist()
            pick = st.select_slider("Thử: cảnh báo bao nhiêu % sinh viên mỗi tuần?", options=shares, value=shares[0],
                                    format_func=lambda v: f"Top {v:.0%}", key="alert_share")
            row = sc[sc["alert_share"] == pick].iloc[0]
            k1, k2, k3 = st.columns(3, border=True)
            k1.metric("Số sinh viên được cảnh báo", int(row["n_alerted"]))
            k2.metric("Phát hiện được", pct(row["recall"]), help="% sinh viên không hoàn thành được đưa vào cảnh báo.")
            k3.metric("Số tuần làm việc của cố vấn", f"{row['weeks_of_advisor_capacity']:.2f}",
                      help=f"So với năng lực {capacity} ca/tuần (giả định).")
            if bool(row["fits_capacity"]):
                st.success(f"Đủ năng lực: {int(row['n_alerted'])} ca ≤ {capacity} ca/tuần.")
            else:
                st.warning(f"Vượt năng lực: {int(row['n_alerted'])} ca > {capacity} ca/tuần → cần thêm cố vấn "
                           "hoặc chỉ liên hệ những ca ưu tiên cao nhất.")
            evidence("Cảnh báo nhiều hơn thì phát hiện nhiều hơn, nhưng tốn năng lực hơn",
                     "Đường xanh: % sinh viên cần hỗ trợ được phát hiện. Đường cam: % cảnh báo là đúng.",
                     threshold_chart(sc, pick), "AQ12 · reports/aq12_threshold_scenarios.csv")
    with tab4:
        if fb is not None and len(fb):
            names = {"gender": "Giới tính", "region": "Vùng", "disability": "Khuyết tật", "age_band": "Nhóm tuổi",
                     "imd_band": "Mức thu nhập khu vực (IMD)", "highest_education": "Trình độ học vấn"}
            attr = st.selectbox("Xem theo thuộc tính", sorted(fb["attribute"].unique()), key="fair_attr",
                                format_func=lambda a: names.get(a, a))
            evidence(f"Tỷ lệ phát hiện theo {names.get(attr, attr).lower()}",
                     "Thanh ngắn hơn vạch chung = nhóm đó dễ bị bỏ sót hơn.",
                     fairness_chart(fb, attr, t["recall"]), "AQ9 · reports/fairness_by_group.csv (học kỳ kiểm tra)")
            hidden = fb[(fb["attribute"] == attr) & fb["suppressed"].astype(bool)]
            if len(hidden):
                st.caption(f"{len(hidden)} nhóm có dưới {cfg['fairness']['min_group_size']} sinh viên đã được ẩn.")
            st.info("Các thuộc tính này **không** được đưa vào mô hình; chỉ dùng để kiểm tra công bằng.")


# ---------------------------------------------------------------------------
# Lecturer – D2
# ---------------------------------------------------------------------------
def lecturer_view() -> None:
    st.title("Giảng viên")
    out = read_csv("aq1_outcomes.csv")
    if out is None:
        st.warning("Chưa có dữ liệu. Chạy `python -m eduearlyalert.pipeline eda` trước.")
        return
    pres_options = [ALL_PRES] + sorted(p for p in out["code_presentation"].unique() if p != ALL_PRES)
    pres = st.selectbox("Học kỳ", pres_options, key="eda_pres",
                        format_func=lambda p: "Tất cả 3 học kỳ khám phá" if p == ALL_PRES else p,
                        help="Học kỳ kiểm tra (2014J) được giữ riêng để đánh giá mô hình nên không có ở đây.")

    def sel(name: str) -> pd.DataFrame | None:
        d = read_csv(name)
        return None if d is None else d[d["code_presentation"] == pres]

    sub, fs, wm = sel("aq3_submission.csv"), sel("aq5_first_score.csv"), sel("aq4_weekly_median.csv")
    cg, act = sel("aq6_concept_gaps.csv"), sel("aq2_activity_week.csv")
    gc = read_csv("aq4_group_comparison.csv")

    findings = []
    if sub is not None and len(visible(sub)):
        miss = visible(sub)[visible(sub)["status"] == "missing"].sort_values("share", ascending=False)
        if len(miss):
            r = miss.iloc[0]
            findings.append(f"Bài **{r['assessment_key']}** có tỷ lệ chưa nộp cao nhất tại Tuần {CUTOFF_WEEK}: "
                            f"**{pct(r['share'])}** sinh viên.")
    if gc is not None and "active_days_total" in set(gc["indicator"]):
        r = gc.set_index("indicator").loc["active_days_total"]
        findings.append(f"Sinh viên không hoàn thành học trên LMS ít ngày hơn rõ rệt: trung vị **{r['median_not_completed']:.0f}"
                        f" ngày** so với **{r['median_completed']:.0f} ngày** trong 6 tuần đầu.")
    if wm is not None and len(visible(wm)):
        w1 = visible(wm)[visible(wm)["week"] == 1].set_index("group")["median"]
        if {"Hoàn thành", "Không hoàn thành"} <= set(w1.index) and w1["Hoàn thành"] > 0:
            findings.append(f"Hai nhóm tách nhau **ngay từ Tuần 1**: nhóm không hoàn thành chỉ có số click bằng "
                            f"**{pct(w1['Không hoàn thành'] / w1['Hoàn thành'])}** nhóm hoàn thành.")
    if fs is not None and len(visible(fs)):
        f = visible(fs).set_index("bin")["completion"]
        if "<40" in f and "80–100" in f:
            findings.append(f"Điểm bài đầu tiên liên hệ với kết quả: dưới 40 điểm chỉ **{pct(f['<40'])}** hoàn thành, "
                            f"từ 80 điểm là **{pct(f['80–100'])}**.")
    if cg is not None and len(visible(cg)):
        c = visible(cg)[visible(cg)["group"] == "Không hoàn thành"].sort_values("share_needs_support", ascending=False)
        if len(c):
            findings.append(f"Concept cần ôn nhiều nhất: **{c.iloc[0]['concept_id']}** – {pct(c.iloc[0]['share_needs_support'])}"
                            " sinh viên nhóm không hoàn thành cần hỗ trợ thêm (KG mô phỏng).")
    question_box("Nên điều chỉnh bài đánh giá, hoạt động hay buổi ôn tập ở đâu?",
                 "D2 – điều chỉnh hoạt động học, nhắc nộp bài, tổ chức ôn tập theo concept.", findings)
    st.caption("Mọi số liệu là tổng hợp, không hiển thị sinh viên cụ thể. Đây là liên hệ, không phải nguyên nhân.")

    tab1, tab2, tab3 = st.tabs(["① Nộp bài & điểm", "② Mức tương tác trên LMS", "③ Concept cần ôn tập"])
    with tab1:
        if sub is None or not len(sub):
            st.info("Chưa có bài đánh giá nào trước mốc dự báo.")
        else:
            l, r = st.columns(2)
            with l:
                evidence("Tình trạng nộp các bài đầu kỳ", "Bài nộp sau Tuần 6 được tính là *chưa nộp* vì chưa thấy tại mốc.",
                         submission_chart(sub), "AQ3 · reports/aq3_submission.csv")
            if fs is not None and len(fs):
                with r:
                    evidence("Điểm bài đầu tiên và khả năng hoàn thành môn",
                             "Nhóm chưa nộp và nhóm dưới 40 điểm là nơi nên nhắc nhở / hỗ trợ sớm.",
                             first_score_chart(fs), "AQ5 · reports/aq5_first_score.csv")
    with tab2:
        if wm is not None and len(wm):
            evidence("Số click mỗi tuần của hai nhóm", "Khoảng cách xuất hiện từ Tuần 1 và giữ nguyên đến Tuần 6.",
                     weekly_groups_chart(wm), "AQ4 · reports/aq4_weekly_median.csv")
        if act is not None and len(act):
            evidence("Sinh viên dùng loại tài nguyên nào, vào tuần nào", "Ô càng đậm = càng nhiều click trung bình/sinh viên.",
                     heatmap_chart(visible(act)), "AQ2 · reports/aq2_activity_week.csv")
        st.caption("Click chỉ là thước đo gián tiếp của việc học, không đo được chất lượng học.")
    with tab3:
        if cg is None or not len(cg):
            st.info("Chưa có ánh xạ concept cho module này (kg/concept_map.csv).")
        else:
            st.warning("Ánh xạ Bài đánh giá → Concept là **DỮ LIỆU MÔ PHỎNG** do nhóm xây dựng (thư mục kg/).")
            evidence("Tỷ lệ sinh viên cần hỗ trợ thêm theo concept", "Concept có thanh cam dài = nên ưu tiên buổi ôn tập.",
                     concept_chart(cg), "AQ6 · reports/aq6_concept_gaps.csv")
            kgmd = REPORTS / "kg_competency_questions.md"
            if kgmd.exists():
                with st.expander("Concept nối với CLO và tài nguyên nào? (Knowledge Graph)"):
                    st.markdown(kgmd.read_text(encoding="utf-8"))

    with st.expander("Chi tiết kỹ thuật: effect size, hồi quy giải thích"):
        if gc is not None and len(gc):
            evidence("Mức khác biệt giữa hai nhóm (Cliff's δ)", "|δ| > 0.47 là khác biệt lớn. Tính trên 3 học kỳ khám phá.",
                     effect_chart(gc), "AQ4 · reports/aq4_group_comparison.csv")
        orr = read_csv("aq5_logit_odds_ratios.csv")
        if orr is not None and len(orr):
            evidence("Hồi quy logistic giải thích (đã điều chỉnh lẫn nhau)",
                     "OR < 1: giá trị cao hơn đi kèm khả năng không hoàn thành thấp hơn. Mô hình giải thích, không dự báo.",
                     odds_chart(orr), "AQ5 · reports/aq5_logit_odds_ratios.csv")


# ---------------------------------------------------------------------------
# Advisor – D1: Risk List + human validation gate
# ---------------------------------------------------------------------------
STATUS_LABEL = {"pending_review": "⏳ Chờ duyệt", "approved": "✅ Đã duyệt liên hệ",
                "dismissed": "⏭️ Bỏ qua", "contacted": "📞 Đã liên hệ"}
TIERS = ["Rất cao", "Cao", "Theo dõi"]
TEXT_COLS = ["reasons", "concepts_need_support", "suggested_resources", "suggested_support",
             "status", "reviewed_by", "decision_note"]
DECISION_COLS = ["status", "reviewed_by", "decision_note"]


def load_risk_list() -> pd.DataFrame:
    """Risk List (reports/risk_list.csv) gộp với quyết định đã ghi (risk_list_decisions.csv)."""
    rl = pd.read_csv(REPORTS / "risk_list.csv", dtype=dict.fromkeys(TEXT_COLS, str))
    rl[TEXT_COLS] = rl[TEXT_COLS].fillna("")
    if DECISIONS.exists():
        dec = pd.read_csv(DECISIONS, dtype=str).fillna("")
        rl = rl.drop(columns=DECISION_COLS).merge(dec[["pid", *DECISION_COLS]], on="pid", how="left")
        rl[DECISION_COLS] = rl[DECISION_COLS].fillna("")
    rl["status"] = rl["status"].replace("", "pending_review")
    return rl


def record_decision(pid: str, action: str, reviewer: str, note: str) -> None:
    """Ghi quyết định của cố vấn (một dòng/pid) và audit log. Không gửi gì cho sinh viên."""
    if action not in STATUS_LABEL or action == "pending_review":
        raise ValueError(f"Hành động không hợp lệ: {action}")
    row = pd.DataFrame([{"pid": pid, "status": action, "reviewed_by": reviewer.strip(), "decision_note": note.strip()}])
    old = pd.read_csv(DECISIONS, dtype=str) if DECISIONS.exists() else pd.DataFrame(columns=row.columns)
    pd.concat([old[old["pid"] != pid], row], ignore_index=True).to_csv(DECISIONS, index=False)
    audit(cfg, f"risk_list_{action}", pid=pid, reviewer=reviewer.strip(), note=note.strip())


def decision_history(pid: str) -> list[dict]:
    """Các lần duyệt của một ca, đọc từ audit_log.jsonl (mới nhất trước)."""
    log = cfg.path("audit_log")
    if not log.exists():
        return []
    rows = []
    for line in log.read_text(encoding="utf-8").splitlines():
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue  # bỏ qua dòng hỏng để dashboard không sập; file log giữ nguyên
        if r.get("pid") == pid and str(r.get("action", "")).startswith("risk_list_"):
            rows.append(r)
    return rows[::-1]


def bullets(items: list[str]) -> str:
    return "\n".join(f"- {x.strip()}" for x in items if x.strip())


def case_detail(r: pd.Series, reviewer: str) -> None:
    """Bước 2–3: đọc lý do, ghi chú và quyết định cho một ca."""
    pid = r["pid"]
    with st.container(border=True):
        st.markdown(f"### Ca #{r['rank']} · `{pid}`")
        st.caption(f"Mức ưu tiên **{r['tier']}** · điểm rủi ro **{r['risk_score']:.2f}** · "
                   f"{STATUS_LABEL.get(r['status'], r['status'])}")
        st.markdown("**② Vì sao ca này được đề xuất?** *(tín hiệu dữ liệu đến Tuần 6, không phải nguyên nhân)*")
        st.markdown(bullets(r["reasons"].split(" | ")))
        st.markdown(f"**Gợi ý cách hỗ trợ:** {r['suggested_support']}")
        if r["concepts_need_support"]:
            st.markdown("**Concept cần hỗ trợ thêm** *(KG mô phỏng)*:")
            st.markdown(bullets(r["concepts_need_support"].replace("), ", ")|").split("|")))
        if r["suggested_resources"]:
            with st.expander("Tài nguyên có thể gửi kèm"):
                st.markdown(bullets(r["suggested_resources"].replace(", R", "|R").split("|")))

        st.markdown("**③ Quyết định của bạn**")
        note = st.text_area("Ghi chú (bối cảnh, lý do chọn, việc cần làm tiếp)", key=f"note_{pid}",
                            value=r["decision_note"], height=80)
        b1, b2, b3 = st.columns(3)
        action = None
        if b1.button("✅ Duyệt", key=f"ok_{pid}", type="primary", width="stretch",
                     help="Duyệt để liên hệ sinh viên này"):
            action = "approved"
        if b2.button("⏭️ Bỏ qua", key=f"skip_{pid}", width="stretch"):
            action = "dismissed"
        if b3.button("📞 Đã liên hệ", key=f"done_{pid}", width="stretch"):
            action = "contacted"
        if action:
            if not reviewer.strip():
                st.error("Cần nhập tên người duyệt ở thanh bên trái trước khi ghi quyết định.")
            else:
                record_decision(pid, action, reviewer, note)
                st.session_state["_rl_flash"] = (f"Đã ghi **{STATUS_LABEL[action]}** cho `{pid}` "
                                                 f"(người duyệt: {reviewer.strip()}) vào nhật ký audit_log.jsonl.")
                st.rerun()
        st.caption("Hệ thống không tự gửi tin nhắn. Việc liên hệ do cố vấn thực hiện sau khi duyệt.")

    hist = decision_history(pid)
    if hist:
        with st.expander(f"④ Nhật ký quyết định của ca này ({len(hist)})"):
            h = pd.DataFrame(hist).reindex(columns=["ts", "reviewer", "action", "note"])
            h.columns = ["Thời điểm (UTC)", "Người duyệt", "Hành động", "Ghi chú"]
            st.dataframe(h, hide_index=True, width="stretch")


def advisor_view(reviewer: str) -> None:
    st.title("Cố vấn học tập")
    if not need(REPORTS / "risk_list.csv"):
        return
    rl = load_risk_list()
    adv = cfg["advisor"]
    capacity = adv["k_per_advisor"] * adv["n_advisors"]
    sc = read_csv("aq10_strategy_comparison.csv")
    counts = rl["status"].value_counts()
    pending = int(counts.get("pending_review", 0))

    findings = [(f"Hệ thống đề xuất **{len(rl)} sinh viên** cần liên hệ tuần này, bằng năng lực {adv['n_advisors']} "
                 f"cố vấn × {adv['k_per_advisor']} ca (giả định). Danh sách xếp theo điểm rủi ro, cao nhất trước.")]
    if sc is not None and len(sc):
        best = sc.sort_values("coverage_at_K", ascending=False).iloc[0]
        findings.append(f"Kiểm tra trên dữ liệu lịch sử: **{pct(best['precision_at_K'])}** ca trong danh sách kiểu này "
                        f"thực sự cần hỗ trợ; danh sách bao phủ **{pct(best['coverage_at_K'])}** số sinh viên cần hỗ trợ "
                        "– phần còn lại cần thêm năng lực hoặc kênh khác.")
    findings.append(f"Còn **{pending}/{len(rl)}** ca chờ bạn duyệt. Mỗi ca chỉ là **đề xuất** – hãy đọc lý do và "
                    "bối cảnh trước khi quyết định.")
    question_box("Tuần này tôi nên liên hệ sinh viên nào trước?",
                 "D1 – chọn ai để liên hệ trong tuần (dễ đảo ngược; mọi liên hệ cần cố vấn duyệt).", findings)

    flash = st.session_state.pop("_rl_flash", None)
    if flash:
        st.success(flash)

    k1, k2, k3, k4 = st.columns(4, border=True)
    k1.metric("Ca đề xuất", len(rl), help=f"Năng lực giả định {capacity} ca/tuần.")
    k2.metric("Chờ duyệt", pending)
    k3.metric("Đã duyệt liên hệ", int(counts.get("approved", 0)))
    k4.metric("Đã liên hệ / bỏ qua", f"{int(counts.get('contacted', 0))} / {int(counts.get('dismissed', 0))}")

    st.markdown("**① Chọn một ca trong danh sách** (bấm vào ô đầu dòng)")
    f1, f2, f3 = st.columns([1, 1, 1])
    present = [t for t in TIERS if t in set(rl["tier"])]
    tiers = f1.multiselect("Mức ưu tiên", present, default=present, key="rl_tier")
    status = f2.multiselect("Trạng thái", list(STATUS_LABEL), default=["pending_review", "approved"],
                            format_func=STATUS_LABEL.get, key="rl_status")
    query = f3.text_input("Tìm mã / concept / lý do", key="rl_query", placeholder="vd: C02, chưa nộp")

    view = rl[rl["tier"].isin(tiers) & rl["status"].isin(status)]
    if query.strip():
        hay = (view["pid"] + " " + view["reasons"] + " " + view["concepts_need_support"]).str.lower()
        view = view[hay.str.contains(query.strip().lower(), regex=False)]
    view = view.sort_values("rank").reset_index(drop=True)

    left, right = st.columns([11, 9], gap="medium")
    with left:
        st.caption(f"Đang hiện {len(view)} / {len(rl)} ca")
        table = view.assign(status_label=view["status"].map(STATUS_LABEL))
        event = st.dataframe(
            table[["rank", "pid", "tier", "risk_score", "status_label"]],
            hide_index=True, width="stretch", height=460, key="rl_table",
            on_select="rerun", selection_mode="single-row",
            column_config={
                "rank": st.column_config.NumberColumn("#", width=40),
                "pid": st.column_config.TextColumn("Mã ẩn danh", width=110),
                "tier": st.column_config.TextColumn("Ưu tiên", width=70),
                "risk_score": st.column_config.ProgressColumn("Điểm rủi ro", min_value=0, max_value=1, format="%.2f",
                                                              width=110),
                "status_label": st.column_config.TextColumn("Trạng thái", width=150),
            })
        st.download_button("⬇️ Tải danh sách đang lọc (CSV)", view.to_csv(index=False).encode("utf-8"),
                           file_name="risk_list_filtered.csv", mime="text/csv", key="rl_download")

    with right:
        if view.empty:
            st.info("Không có ca nào khớp bộ lọc.")
        else:
            options = view["pid"].tolist()
            rows = event.selection.rows if event is not None else []
            picked = options[rows[0]] if rows and rows[0] < len(options) else None
            if picked and st.session_state.get("_rl_last_pick") != picked:
                st.session_state["case_pid"] = picked  # đồng bộ dòng được bấm trên bảng → ô chọn ca
                st.session_state["_rl_last_pick"] = picked
            if st.session_state.get("case_pid") not in options:
                st.session_state["case_pid"] = options[0]
            label = dict(zip(view["pid"], "#" + view["rank"].astype(str) + " · " + view["pid"] + " · " + view["tier"]))
            pid = st.selectbox("Ca đang xem", options, key="case_pid", format_func=label.get)
            case_detail(view[view["pid"] == pid].iloc[0], reviewer)

    if sc is not None and len(sc):
        with st.expander("Vì sao xếp theo điểm rủi ro? So sánh 3 cách xếp ưu tiên"):
            evidence(f"Với {int(sc['K'].iloc[0])} ca/tuần, cách nào tiếp cận được nhiều người cần hỗ trợ nhất?",
                     "Cách A (chỉ theo điểm rủi ro) bao phủ nhiều nhất và chính xác nhất nên được dùng cho danh sách trên.",
                     strategy_chart(sc), "AQ10 · reports/aq10_strategy_comparison.csv (tập valid – dùng để chọn)")


# ---------------------------------------------------------------------------
# Khung trang
# ---------------------------------------------------------------------------
ROLES = {
    "Program Manager": "Quản lý chương trình · D3 phân bổ cố vấn",
    "Lecturer": "Giảng viên · D2 điều chỉnh bài, ôn tập",
    "Advisor": "Cố vấn học tập · D1 liên hệ ai trước",
}
st.sidebar.title("🎓 EduEarlyAlert")
st.sidebar.caption(f"Cảnh báo sớm sinh viên có nguy cơ không hoàn thành môn · module {cfg.module} · "
                   f"dữ liệu đến hết Tuần {CUTOFF_WEEK}")
role = st.sidebar.radio("Bạn là ai? (phân quyền mô phỏng)", list(ROLES), format_func=ROLES.get)
reviewer = st.sidebar.text_input("Tên người duyệt (ghi vào nhật ký)", value="advisor_demo")
with st.sidebar.expander("📖 Giải thích thuật ngữ"):
    st.markdown(GLOSSARY)
st.sidebar.caption("Dữ liệu: OULAD (Anh, 2013–2014, đã ẩn danh) + Knowledge Graph MÔ PHỎNG. "
                   "Hệ thống chỉ đề xuất; mọi liên hệ với sinh viên cần con người phê duyệt.")

if role == "Program Manager":
    program_manager_view()
elif role == "Lecturer":
    lecturer_view()
else:
    advisor_view(reviewer)
