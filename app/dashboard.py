"""EduEarlyAlert – Dashboard demo (Streamlit).

  streamlit run app/dashboard.py

Ba góc nhìn theo vai trò (phân quyền MÔ PHỎNG qua sidebar):
  * Program Manager – chỉ số tổng hợp, KHÔNG thấy danh sách cá nhân.
  * Lecturer        – concept/bài đánh giá cần hỗ trợ thêm (tổng hợp).
  * Advisor         – Risk List có lý do + nút phê duyệt (human validation gate).
Mọi quyết định của cố vấn được ghi vào reports/audit_log.jsonl.
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
FIG = cfg.path("figures_dir")
DECISIONS = REPORTS / "risk_list_decisions.csv"

st.set_page_config(page_title="EduEarlyAlert", page_icon="🎓", layout="wide")


def need(path: Path) -> bool:
    if not path.exists():
        st.warning(f"Chưa có `{path.relative_to(cfg.root)}`. Chạy `python -m eduearlyalert.pipeline all` trước.")
        return False
    return True


def show_fig(name: str, caption: str = "") -> None:
    p = FIG / name
    if p.exists():
        st.image(str(p), caption=caption, width="stretch")


# ---- biểu đồ tương tác (Plotly) -------------------------------------------
# Bảng màu categorical cố định thứ tự (đã kiểm CVD); màu đi theo thực thể, không theo thứ hạng.
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]
MODEL_LABEL = {"rule": "Rule (baseline)", "logistic": "Logistic", "gboost": "Gradient Boosting"}
METRIC_LABEL = {"recall": "Recall", "precision": "Precision", "f1": "F1", "pr_auc": "PR-AUC", "roc_auc": "ROC-AUC"}


def read_csv(name: str) -> pd.DataFrame | None:
    """Đọc một CSV trong reports/; None nếu chưa có (bước pipeline chưa chạy)."""
    p = REPORTS / name
    return pd.read_csv(p) if p.exists() else None


def style(fig: go.Figure, height: int = 360, y_pct: bool = False) -> go.Figure:
    """Giao diện chung: lưới mờ, legend phía trên, hover gom theo trục x."""
    fig.update_layout(
        height=height, margin={"l": 8, "r": 8, "t": 40, "b": 8}, hovermode="x unified",
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "xanchor": "left", "x": 0, "title": None},
        bargap=0.25, bargroupgap=0.08, font={"size": 13},
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(128,128,128,0.18)", zeroline=False)
    if y_pct:
        fig.update_yaxes(tickformat=".0%", range=[0, 1.05])
    return fig


def chart(fig: go.Figure) -> None:
    st.plotly_chart(fig, width="stretch", config={"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})


def cohort_chart(flow: pd.DataFrame) -> go.Figure:
    """AQ1 · Quần thể dự báo và số rút môn trước mốc, theo presentation."""
    x = flow["code_presentation"] + " (" + flow["split"] + ")"
    fig = go.Figure([
        go.Bar(name="Còn theo học tại mốc (quần thể dự báo)", x=x, y=flow["prediction_population"],
               marker={"color": SERIES[0], "line": {"width": 2, "color": "white"}},
               hovertemplate="%{y} sinh viên<extra></extra>"),
        go.Bar(name="Rút môn trước mốc", x=x, y=flow["withdrawn_by_cutoff"],
               marker={"color": SERIES[1], "line": {"width": 2, "color": "white"}},
               hovertemplate="%{y} sinh viên<extra></extra>"),
    ])
    fig.update_layout(barmode="stack", title="AQ1 · Quy mô cohort theo presentation")
    return style(fig)


def metrics_chart(metrics: dict, split: str) -> go.Figure:
    """AQ7 · So sánh các mô hình trên một tập (valid/test)."""
    keys = ["recall", "precision", "f1", "pr_auc"]
    fig = go.Figure()
    for i, (name, m) in enumerate(metrics[split].items()):
        fig.add_bar(name=MODEL_LABEL.get(name, name), x=[METRIC_LABEL[k] for k in keys], y=[m[k] for k in keys],
                    marker_color=SERIES[i % len(SERIES)], hovertemplate="%{y:.2f}<extra>" + MODEL_LABEL.get(name, name) + "</extra>")
    acc = metrics["acceptance"]
    fig.add_hline(y=acc["recall_min"], line={"dash": "dot", "width": 1, "color": "gray"},
                  annotation_text=f"Tiêu chí Recall ≥ {acc['recall_min']:.0%}", annotation_position="top left")
    fig.update_layout(barmode="group", title=f"AQ7 · Chất lượng mô hình trên tập {split}")
    return style(fig, y_pct=True)


def confusion_chart(m: dict) -> go.Figure:
    """AQ7 · Ma trận nhầm lẫn của mô hình chính."""
    z = [[m["tn"], m["fp"]], [m["fn"], m["tp"]]]
    labels = [["Đúng: không cảnh báo", "Báo nhầm"], ["Bỏ sót", "Đúng: cảnh báo"]]
    fig = go.Figure(go.Heatmap(
        z=z, x=["Dự báo: không", "Dự báo: có nguy cơ"], y=["Thực tế: hoàn thành", "Thực tế: không hoàn thành"],
        colorscale=[[0, "#cde2fb"], [1, "#1c5cab"]], showscale=False, text=labels, xgap=2, ygap=2,
        texttemplate="<b>%{z}</b><br>%{text}", hovertemplate="%{y} · %{x}: %{z}<extra></extra>"))
    fig.update_layout(title="AQ7 · Ma trận nhầm lẫn (mô hình chính, test)")
    fig = style(fig, height=340)
    fig.update_layout(hovermode="closest")
    fig.update_yaxes(autorange="reversed", gridcolor=None)
    return fig


def importance_chart(imp: pd.DataFrame, top: int) -> go.Figure:
    """AQ7 · Permutation importance (giảm PR-AUC khi xáo trộn feature)."""
    imp = imp.rename(columns={imp.columns[0]: "feature"}).nlargest(top, "perm_importance_pr_auc").iloc[::-1]
    fig = go.Figure(go.Bar(x=imp["perm_importance_pr_auc"], y=imp["feature"], orientation="h",
                           marker_color=SERIES[0], hovertemplate="%{y}: %{x:.4f}<extra></extra>"))
    fig.update_layout(title=f"AQ7 · Top {top} feature theo permutation importance")
    fig = style(fig, height=max(300, 26 * top + 80))
    fig.update_layout(hovermode="closest")
    fig.update_xaxes(showgrid=True, gridcolor="rgba(128,128,128,0.18)", title="Mức giảm PR-AUC")
    return fig


def threshold_chart(sc: pd.DataFrame, selected: float) -> go.Figure:
    """AQ12 · Recall/Precision theo tỷ lệ sinh viên được cảnh báo."""
    fig = go.Figure()
    for i, k in enumerate(["recall", "precision"]):
        fig.add_scatter(x=sc["alert_share"], y=sc[k], name=METRIC_LABEL[k], mode="lines+markers",
                        line={"width": 2, "color": SERIES[i]}, marker={"size": 9, "line": {"width": 2, "color": "white"}},
                        hovertemplate="%{y:.1%}")
    fig.add_vline(x=selected, line={"dash": "dot", "width": 1, "color": "gray"})
    fig.update_layout(title="AQ12 · Đánh đổi Recall – Precision theo tỷ lệ cảnh báo")
    fig = style(fig, y_pct=True)
    fig.update_xaxes(tickformat=".0%", title="Tỷ lệ sinh viên được cảnh báo", tickvals=sc["alert_share"])
    return fig


def fairness_chart(fb: pd.DataFrame, attribute: str, overall_recall: float) -> go.Figure:
    """AQ9 · Recall theo nhóm của một thuộc tính nhạy cảm (nhóm nhỏ đã bị ẩn)."""
    d = fb[(fb["attribute"] == attribute) & (~fb["suppressed"].astype(bool))].sort_values("recall")
    fig = go.Figure(go.Bar(x=d["recall"], y=d["group"], orientation="h", marker_color=SERIES[0],
                           customdata=d[["n", "fnr"]], hovertemplate="%{y}<br>Recall %{x:.1%} · FNR %{customdata[1]:.1%}"
                           "<br>n = %{customdata[0]}<extra></extra>"))
    fig.add_vline(x=overall_recall, line={"dash": "dot", "width": 1, "color": "gray"},
                  annotation_text=f"Toàn bộ test: {overall_recall:.0%}", annotation_position="top")
    fig.update_layout(title=f"AQ9 · Recall theo nhóm – {attribute}")
    fig = style(fig, height=max(280, 34 * len(d) + 100))
    fig.update_layout(hovermode="closest")
    fig.update_xaxes(tickformat=".0%", range=[0, 1.05], showgrid=True, gridcolor="rgba(128,128,128,0.18)")
    return fig


def program_manager_view() -> None:
    """Program Manager: chỉ số tổng hợp, không có dữ liệu cá nhân."""
    st.header("Tổng quan chương trình")
    st.caption(f"Module {cfg.module} · mốc dự báo ngày {cfg.cutoff_day} · chỉ số tổng hợp, không hiển thị cá nhân.")
    if not need(REPORTS / "model_metrics.json"):
        return
    m = json.loads((REPORTS / "model_metrics.json").read_text(encoding="utf-8"))
    main = m["main_model"]
    t = m["test"][main]
    acc = m["acceptance"]
    flow = read_csv("cohort_flow.csv")

    c1, c2, c3, c4 = st.columns(4, border=True)
    if flow is not None:
        completion = 1 - (flow["positive_rate_all"] * flow["registered"]).sum() / flow["registered"].sum()
        c1.metric("Tỷ lệ hoàn thành (mọi lượt)", f"{completion:.1%}", help="Tính trên toàn bộ lượt đăng ký, gồm cả rút sớm.")
    c2.metric("Early Detection Recall (test)", f"{t['recall']:.0%}", f"{t['recall'] - acc['recall_min']:+.0%} so với tiêu chí",
              help=f"Tiêu chí ≥ {acc['recall_min']:.0%}")
    c3.metric("F1 (test)", f"{t['f1']:.2f}", f"{t['f1'] - acc['f1_min']:+.2f} so với tiêu chí", help=f"Tiêu chí ≥ {acc['f1_min']}")
    c4.metric("Tỷ lệ được cảnh báo (test)", f"{t['alert_rate']:.0%}", help=f"Mô hình chính: {MODEL_LABEL.get(main, main)}")

    tab_cohort, tab_model, tab_thr, tab_fair, tab_eda = st.tabs(
        ["Cohort", "Mô hình (AQ7)", "Ngưỡng & năng lực (AQ12)", "Công bằng (AQ9)", "Khám phá dữ liệu (AQ1–AQ6)"])

    with tab_cohort:
        if flow is not None:
            chart(cohort_chart(flow))
            with st.expander("Bảng số liệu cohort"):
                st.dataframe(flow, width="stretch", hide_index=True)

    with tab_model:
        split = st.segmented_control("Tập đánh giá", ["test", "valid"], default="test", key="metric_split",
                                     help="Ngưỡng và mô hình chính được chọn trên valid; test chỉ để báo cáo.")
        split = split or "test"
        chart(metrics_chart(m, split))
        left, right = st.columns(2)
        with left:
            chart(confusion_chart(t))
        with right:
            imp = read_csv("feature_importance.csv")
            if imp is not None:
                top = st.slider("Số feature hiển thị", 5, min(25, len(imp)), min(10, len(imp)), key="imp_top")
                chart(importance_chart(imp, top))
                st.caption("Importance phản ánh mức mô hình dựa vào feature – là liên hệ, không phải nguyên nhân.")
        with st.expander("Bảng chỉ số đầy đủ"):
            st.dataframe(pd.DataFrame(m[split]).T.rename(index=MODEL_LABEL), width="stretch")

    with tab_thr:
        sc = read_csv("aq12_threshold_scenarios.csv")
        if sc is not None and len(sc):
            shares = sc["alert_share"].tolist()
            pick = st.select_slider("Cảnh báo top bao nhiêu % sinh viên?", options=shares, value=shares[0],
                                    format_func=lambda v: f"{v:.0%}", key="alert_share")
            row = sc[sc["alert_share"] == pick].iloc[0]
            k1, k2, k3, k4 = st.columns(4, border=True)
            k1.metric("Số ca cảnh báo", int(row["n_alerted"]))
            k2.metric("Recall", f"{row['recall']:.0%}")
            k3.metric("Báo nhầm", int(row["false_alarms"]))
            k4.metric("Tuần năng lực cố vấn", f"{row['weeks_of_advisor_capacity']:.2f}",
                      help=f"Giả định {cfg['advisor']['n_advisors']} cố vấn × {cfg['advisor']['k_per_advisor']} ca/tuần "
                           "(assumption của proposal, không phải dữ kiện).")
            if bool(row["fits_capacity"]):
                st.success("✅ Vừa năng lực xử lý trong 1 tuần.", icon=None)
            else:
                st.warning("⚠️ Vượt năng lực 1 tuần – cần ưu tiên (xem Risk List) hoặc tăng nguồn lực.")
            chart(threshold_chart(sc, pick))
            with st.expander("Bảng kịch bản"):
                st.dataframe(sc, width="stretch", hide_index=True)

    with tab_fair:
        fb = read_csv("fairness_by_group.csv")
        if fb is not None and len(fb):
            attr = st.selectbox("Thuộc tính", sorted(fb["attribute"].unique()), key="fair_attr")
            chart(fairness_chart(fb, attr, t["recall"]))
            hidden = fb[(fb["attribute"] == attr) & fb["suppressed"].astype(bool)]
            if len(hidden):
                st.caption(f"{len(hidden)} nhóm có n < {cfg['fairness']['min_group_size']} đã được ẩn số liệu.")
            st.caption("Thuộc tính nhạy cảm chỉ dùng để kiểm định công bằng, không đưa vào mô hình.")

    with tab_eda:
        eda_view()


# ---- EDA tương tác (AQ1–AQ6) – đọc reports/aqX_*.csv do eda.export_dashboard_data sinh ----
ALL_PRES = "train+valid"
GROUP_COLOR = {"Hoàn thành": SERIES[0], "Không hoàn thành": SERIES[1]}
STATUS = {"on_time": ("Đúng hạn", SERIES[0]), "late": ("Muộn", SERIES[2]), "missing": ("Chưa nộp (tại mốc)", SERIES[1])}


def visible(df: pd.DataFrame) -> pd.DataFrame:
    """Bỏ các dòng đã bị ẩn vì nhóm < min_group_size."""
    return df[~df["suppressed"].astype(bool)] if "suppressed" in df.columns else df


def week_label(w: int) -> str:
    return "Trước" if w <= 0 else f"T{w}"


def aq1_outcome_chart(d: pd.DataFrame) -> go.Figure:
    d = visible(d[d["code_presentation"] != ALL_PRES])
    order = ["Distinction", "Pass", "Fail", "Withdrawn"]
    fig = go.Figure()
    for i, res in enumerate([r for r in order if r in set(d["final_result"])]):
        s = d[d["final_result"] == res]
        fig.add_bar(name=res, x=s["code_presentation"], y=s["share"], customdata=s["n"],
                    marker={"color": SERIES[i], "line": {"width": 2, "color": "white"}},
                    hovertemplate="%{y:.1%} (n=%{customdata:.0f})<extra>" + res + "</extra>")
    fig.update_layout(barmode="stack", title="AQ1 · Kết quả cuối kỳ theo lượt giảng dạy")
    return style(fig, y_pct=True)


def aq1_withdrawal_chart(d: pd.DataFrame) -> go.Figure:
    d = visible(d[d["code_presentation"] != ALL_PRES])
    fig = go.Figure()
    for i, (p, s) in enumerate(d.groupby("code_presentation")):
        fig.add_scatter(x=s["week"], y=s["cum_share"], name=p, mode="lines",
                        line={"width": 2, "color": SERIES[i % len(SERIES)]}, hovertemplate="%{y:.1%}")
    cut_week = (cfg.cutoff_day + 1) / cfg["timeline"]["week_length"]
    fig.add_vline(x=cut_week, line={"dash": "dot", "width": 1, "color": "gray"},
                  annotation_text="Mốc dự báo", annotation_position="top right")
    fig.update_layout(title="AQ1 · Rút môn tích luỹ theo tuần")
    fig = style(fig)
    fig.update_yaxes(tickformat=".0%")
    fig.update_xaxes(title="Tuần học")
    return fig


def aq2_heatmap_chart(d: pd.DataFrame) -> go.Figure:
    t = d.pivot_table(index="activity_type", columns="week", values="clicks_per_student", aggfunc="sum").fillna(0)
    t = t.loc[t.sum(axis=1).sort_values().index]
    fig = go.Figure(go.Heatmap(
        z=t.values, x=[week_label(int(w)) for w in t.columns], y=t.index, xgap=2, ygap=2,
        colorscale=[[0, "#cde2fb"], [0.5, "#3987e5"], [1, "#104281"]], colorbar={"title": "Click/SV"},
        texttemplate="%{z:.0f}", hovertemplate="%{y} · %{x}: %{z:.1f} click/SV<extra></extra>"))
    fig.update_layout(title="AQ2 · Click trung bình/sinh viên theo tuần × loại tài nguyên")
    fig = style(fig, height=max(320, 30 * len(t) + 100))
    fig.update_layout(hovermode="closest")
    return fig


def aq2_box_chart(d: pd.DataFrame) -> go.Figure:
    d = visible(d)
    fig = go.Figure(go.Box(
        x=[week_label(int(w)) for w in d["week"]], q1=d["q1"], median=d["median"], q3=d["q3"],
        lowerfence=[0] * len(d), upperfence=d["p90"], marker_color=SERIES[0], name="Click/tuần",
        customdata=d["zero_share"], hoverinfo="x+y"))
    fig.update_layout(title="AQ2 · Phân bố click theo tuần (hộp = Q1–Q3, râu = 0–P90)", showlegend=False)
    fig = style(fig)
    fig.update_layout(hovermode="closest")
    return fig


def aq2_zero_chart(d: pd.DataFrame) -> go.Figure:
    d = visible(d)
    fig = go.Figure(go.Scatter(x=[week_label(int(w)) for w in d["week"]], y=d["zero_share"], mode="lines+markers",
                               line={"width": 2, "color": SERIES[1]}, marker={"size": 9},
                               hovertemplate="%{y:.1%} sinh viên 0 click<extra></extra>"))
    fig.update_layout(title="AQ2 · Tỷ lệ sinh viên không có click trong tuần")
    fig = style(fig)
    fig.update_yaxes(tickformat=".0%", rangemode="tozero")
    return fig


def aq3_submission_chart(d: pd.DataFrame) -> go.Figure:
    d = visible(d)
    fig = go.Figure()
    for status, (label, color) in STATUS.items():
        s = d[d["status"] == status]
        fig.add_bar(name=label, y=s["assessment_key"], x=s["share"], orientation="h", customdata=s["n"],
                    marker={"color": color, "line": {"width": 2, "color": "white"}},
                    hovertemplate="%{x:.1%} (n=%{customdata:.0f})<extra>" + label + "</extra>")
    fig.update_layout(barmode="stack", title="AQ3 · Tình trạng nộp bài đánh giá đầu kỳ")
    fig = style(fig, height=max(260, 50 * d["assessment_key"].nunique() + 120))
    fig.update_layout(hovermode="y unified")
    fig.update_xaxes(tickformat=".0%", range=[0, 1], showgrid=True, gridcolor="rgba(128,128,128,0.18)")
    fig.update_yaxes(categoryorder="category descending")
    return fig


def aq3_score_chart(d: pd.DataFrame, keys: list[str]) -> go.Figure:
    d = visible(d)
    fig = go.Figure()
    for i, k in enumerate(keys):
        s = d[d["assessment_key"] == k]
        fig.add_bar(name=k, x=s["bin_left"] + 2.5, y=s["n"], width=5, opacity=0.75 if len(keys) > 1 else 1,
                    marker={"color": SERIES[i % len(SERIES)], "line": {"width": 1, "color": "white"}},
                    hovertemplate="Điểm %{x:.0f}±2.5: %{y:.0f} SV<extra>" + k + "</extra>")
    fig.add_vline(x=40, line={"dash": "dot", "width": 1, "color": "gray"}, annotation_text="Ngưỡng đạt 40")
    fig.update_layout(barmode="overlay", title="AQ3 · Phân bố điểm các bài đầu kỳ")
    fig = style(fig)
    fig.update_xaxes(range=[0, 100], title="Điểm", dtick=10)
    fig.update_yaxes(title="Số sinh viên")
    return fig


def aq4_weekly_chart(d: pd.DataFrame) -> go.Figure:
    d = visible(d)
    fig = go.Figure()
    for grp, s in d.groupby("group"):
        fig.add_scatter(x=[week_label(int(w)) for w in s["week"]], y=s["median"], name=grp, mode="lines+markers",
                        line={"width": 2, "color": GROUP_COLOR.get(grp, SERIES[2])},
                        marker={"size": 9, "line": {"width": 2, "color": "white"}}, hovertemplate="%{y:.0f} click")
    fig.update_layout(title="AQ4 · Trung vị click/tuần: hai nhóm tách nhau từ tuần nào?")
    fig = style(fig)
    fig.update_yaxes(rangemode="tozero", title="Trung vị click/tuần")
    return fig


def aq4_effect_chart(d: pd.DataFrame) -> go.Figure:
    d = d.sort_values("cliffs_delta")
    fig = go.Figure(go.Bar(x=d["cliffs_delta"], y=d["indicator"], orientation="h", marker_color=SERIES[0],
                           customdata=d[["magnitude", "p_holm"]],
                           hovertemplate="%{y}<br>δ = %{x:.2f} (%{customdata[0]})<br>p Holm = %{customdata[1]:.1e}"
                                         "<extra></extra>"))
    fig.add_vline(x=0, line={"width": 1, "color": "gray"})
    fig.update_layout(title="AQ4 · Effect size (Cliff's δ: hoàn thành vs không)")
    fig = style(fig, height=320)
    fig.update_layout(hovermode="closest")
    fig.update_xaxes(range=[-1, 1], showgrid=True, gridcolor="rgba(128,128,128,0.18)")
    return fig


def aq5_score_chart(d: pd.DataFrame) -> go.Figure:
    d = visible(d)
    fig = go.Figure(go.Bar(x=d["bin"], y=d["completion"], customdata=d["n"], marker_color=SERIES[0],
                           text=[f"{v:.0%}" for v in d["completion"]], textposition="outside",
                           hovertemplate="%{x}: %{y:.1%} hoàn thành (n=%{customdata})<extra></extra>"))
    fig.update_layout(title="AQ5 · Tỷ lệ hoàn thành theo điểm bài đánh giá đầu tiên")
    fig = style(fig, y_pct=True)
    fig.update_layout(hovermode="closest")
    fig.update_xaxes(title="Điểm bài đầu tiên")
    return fig


def aq5_or_chart(d: pd.DataFrame) -> go.Figure:
    d = d.rename(columns={d.columns[0]: "term"}).sort_values("odds_ratio_per_SD")
    fig = go.Figure(go.Scatter(
        x=d["odds_ratio_per_SD"], y=d["term"], mode="markers", marker={"size": 10, "color": SERIES[0]},
        error_x={"type": "data", "symmetric": False, "array": d["ci_high"] - d["odds_ratio_per_SD"],
                     "arrayminus": d["odds_ratio_per_SD"] - d["ci_low"], "thickness": 2, "width": 0, "color": SERIES[0]},
        customdata=d[["ci_low", "ci_high", "p_value"]],
        hovertemplate="%{y}<br>OR = %{x:.2f} [%{customdata[0]:.2f}–%{customdata[1]:.2f}]"
                      "<br>p = %{customdata[2]:.1e}<extra></extra>"))
    fig.add_vline(x=1, line={"dash": "dot", "width": 1, "color": "gray"})
    fig.update_layout(title="AQ5 · OR của không hoàn thành / +1 SD (CI 95%, đã điều chỉnh)")
    fig = style(fig, height=320)
    fig.update_layout(hovermode="closest")
    fig.update_xaxes(type="log", showgrid=True, gridcolor="rgba(128,128,128,0.18)")
    return fig


def aq6_concept_chart(d: pd.DataFrame) -> go.Figure:
    d = visible(d)
    fig = go.Figure()
    for grp in ["Hoàn thành", "Không hoàn thành"]:
        s = d[d["group"] == grp].sort_values("concept_id", ascending=False)
        fig.add_bar(name=grp, y=s["concept_id"], x=s["share_needs_support"], orientation="h", customdata=s["n"],
                    marker_color=GROUP_COLOR[grp], hovertemplate="%{x:.1%} (n=%{customdata})<extra>" + grp + "</extra>")
    fig.update_layout(barmode="group", title="AQ6 · Tỷ lệ cần hỗ trợ thêm theo concept (KG MÔ PHỎNG)")
    fig = style(fig, height=max(320, 44 * d["concept_id"].nunique() + 120))
    fig.update_layout(hovermode="y unified")
    fig.update_xaxes(tickformat=".0%", range=[0, 1], showgrid=True, gridcolor="rgba(128,128,128,0.18)")
    return fig


def eda_view() -> None:
    """EDA AQ1–AQ6: chỉ train + valid (tập test giữ kín), số liệu tổng hợp, nhóm < min_group_size bị ẩn."""
    out = read_csv("aq1_outcomes.csv")
    if out is None:
        st.warning("Chưa có dữ liệu EDA cho dashboard. Chạy `python -m eduearlyalert.pipeline eda` trước.")
        return
    pres_options = [ALL_PRES] + sorted(p for p in out["code_presentation"].unique() if p != ALL_PRES)
    pres = st.selectbox("Lượt giảng dạy", pres_options, key="eda_pres",
                        format_func=lambda p: "Tất cả (train + valid)" if p == ALL_PRES else p,
                        help="EDA chỉ dùng train + valid; tập test được giữ kín cho đánh giá cuối.")

    def sel(name: str) -> pd.DataFrame | None:
        d = read_csv(name)
        return None if d is None else d[d["code_presentation"] == pres]

    t1, t2, t3, t4, t5, t6 = st.tabs(["AQ1 Hoàn thành", "AQ2 Tương tác LMS", "AQ3 Nộp bài & điểm",
                                      "AQ4 Engagement theo nhóm", "AQ5 Điểm & hoàn thành", "AQ6 Concept"])
    with t1:
        st.caption("So sánh giữa các lượt giảng dạy nên không áp dụng bộ lọc lượt.")
        c1, c2 = st.columns(2)
        with c1:
            chart(aq1_outcome_chart(out))
        wd = read_csv("aq1_withdrawal.csv")
        if wd is not None:
            with c2:
                chart(aq1_withdrawal_chart(wd))
    with t2:
        act, wk = sel("aq2_activity_week.csv"), sel("aq2_weekly_clicks.csv")
        if act is not None and len(act):
            weeks = sorted(int(w) for w in act["week"].unique())
            lo, hi = st.select_slider("Khoảng tuần", options=weeks, value=(weeks[0], weeks[-1]),
                                      format_func=week_label, key="eda_weeks")
            chart(aq2_heatmap_chart(visible(act[act["week"].between(lo, hi)])))
        if wk is not None and len(wk):
            c1, c2 = st.columns(2)
            with c1:
                chart(aq2_box_chart(wk))
            with c2:
                chart(aq2_zero_chart(wk))
        st.caption("Click là proxy của tương tác, không đo được chất lượng học.")
    with t3:
        sub, sc = sel("aq3_submission.csv"), sel("aq3_scores.csv")
        if sub is None or not len(sub):
            st.info("Chưa có bài đánh giá nào trước mốc dự báo.")
        else:
            chart(aq3_submission_chart(sub))
            if sc is not None and len(sc):
                keys = sorted(sc["assessment_key"].unique())
                pick = st.multiselect("Bài đánh giá", keys, default=keys[:2], key="eda_assess", max_selections=4)
                if pick:
                    chart(aq3_score_chart(sc, pick))
            st.caption("Bài nộp sau ngày mốc được tính là 'chưa nộp' vì chưa quan sát được tại mốc dự báo.")
    with t4:
        wm = sel("aq4_weekly_median.csv")
        if wm is not None:
            chart(aq4_weekly_chart(wm))
        gc = read_csv("aq4_group_comparison.csv")
        if gc is not None and len(gc):
            chart(aq4_effect_chart(gc))
            st.caption("Effect size tính trên toàn bộ train + valid. Khác biệt/liên hệ, không phải quan hệ nhân quả.")
    with t5:
        fs = sel("aq5_first_score.csv")
        c1, c2 = st.columns(2)
        if fs is not None:
            with c1:
                chart(aq5_score_chart(fs))
        orr = read_csv("aq5_logit_odds_ratios.csv")
        if orr is not None and len(orr):
            with c2:
                chart(aq5_or_chart(orr))
        st.caption("Mô hình giải thích, không phải dự báo; liên hệ, không phải nhân quả.")
    with t6:
        cg = sel("aq6_concept_gaps.csv")
        if cg is None or not len(cg):
            st.info("Chưa có ánh xạ concept cho module này (kg/concept_map.csv).")
        else:
            chart(aq6_concept_chart(cg))
            st.caption("⚠️ Ánh xạ concept là DỮ LIỆU MÔ PHỎNG (kg/), ở mức bài đánh giá, không phải mức câu hỏi.")


# ---------------------------------------------------------------------------
st.sidebar.title("🎓 EduEarlyAlert")
role = st.sidebar.radio("Vai trò (mô phỏng phân quyền)", ["Program Manager", "Lecturer", "Advisor"])
reviewer = st.sidebar.text_input("Tên người duyệt (ghi audit log)", value="advisor_demo")
st.sidebar.caption(
    "Dữ liệu: OULAD (đã ẩn danh) + Knowledge Graph MÔ PHỎNG. "
    "Hệ thống chỉ đề xuất; mọi liên hệ với sinh viên cần con người phê duyệt."
)

# ---------------------------------------------------------------------------
if role == "Program Manager":
    program_manager_view()

# ---------------------------------------------------------------------------
elif role == "Lecturer":
    st.header("Thông tin cho giảng viên")
    st.caption("Chỉ số tổng hợp theo bài đánh giá và concept – không hiển thị cá nhân.")
    eda_view()
    kgmd = REPORTS / "kg_competency_questions.md"
    if kgmd.exists():
        with st.expander("Đường giải thích Assessment → Concept → CLO → Resource"):
            st.markdown(kgmd.read_text(encoding="utf-8"))

# ---------------------------------------------------------------------------
else:
    st.header("Danh sách đề xuất hỗ trợ (Risk List)")
    st.info(
        "Đây là **đề xuất**, không phải kết luận về sinh viên. Hãy đọc lý do, cân nhắc bối cảnh "
        "và chọn Phê duyệt / Bỏ qua cho từng ca. Không có tin nhắn nào được gửi tự động."
    )
    if need(REPORTS / "risk_list.csv"):
        rl = pd.read_csv(REPORTS / "risk_list.csv").fillna("")
        if DECISIONS.exists():
            dec = pd.read_csv(DECISIONS).fillna("")
            rl = rl.drop(columns=["status", "reviewed_by", "decision_note"]).merge(
                dec[["pid", "status", "reviewed_by", "decision_note"]], on="pid", how="left")
            rl["status"] = rl["status"].replace("", pd.NA).fillna("pending_review")

        tiers = st.multiselect("Mức ưu tiên", ["Rất cao", "Cao", "Theo dõi"], default=["Rất cao", "Cao", "Theo dõi"])
        status = st.multiselect("Trạng thái", ["pending_review", "approved", "dismissed", "contacted"],
                                default=["pending_review", "approved"])
        view = rl[rl["tier"].isin(tiers) & rl["status"].isin(status)]
        st.caption(f"{len(view)} / {len(rl)} ca hiển thị · năng lực giả định "
                   f"{cfg['advisor']['k_per_advisor']} ca/cố vấn/tuần")

        for r in view.itertuples(index=False):
            with st.expander(f"#{r.rank} · {r.pid} · {r.tier} · risk {r.risk_score:.2f} · [{r.status}]"):
                st.markdown("**Lý do (tín hiệu dữ liệu, không phải nguyên nhân):**")
                for reason in str(r.reasons).split(" | "):
                    st.markdown(f"- {reason}")
                if r.concepts_need_support:
                    st.markdown(f"**Concept cần hỗ trợ thêm:** {r.concepts_need_support}")
                if r.suggested_resources:
                    st.markdown(f"**Tài nguyên gợi ý:** {r.suggested_resources}")
                st.markdown(f"**Loại hỗ trợ đề xuất:** {r.suggested_support}")
                note = st.text_input("Ghi chú quyết định", key=f"note_{r.pid}", value=str(r.decision_note))
                b1, b2, b3 = st.columns(3)
                action = None
                if b1.button("✅ Phê duyệt liên hệ", key=f"ok_{r.pid}"):
                    action = "approved"
                if b2.button("⏭️ Bỏ qua", key=f"skip_{r.pid}"):
                    action = "dismissed"
                if b3.button("📞 Đã liên hệ", key=f"done_{r.pid}"):
                    action = "contacted"
                if action:
                    if not reviewer.strip():
                        st.error("Cần nhập tên người duyệt ở sidebar.")
                    else:
                        row = pd.DataFrame([{"pid": r.pid, "status": action, "reviewed_by": reviewer,
                                             "decision_note": note}])
                        old = pd.read_csv(DECISIONS) if DECISIONS.exists() else pd.DataFrame(columns=row.columns)
                        pd.concat([old[old["pid"] != r.pid], row]).to_csv(DECISIONS, index=False)
                        audit(cfg, f"risk_list_{action}", pid=r.pid, reviewer=reviewer, note=note)
                        st.success(f"Đã ghi: {action}")
                        st.rerun()

        st.subheader("So sánh phương án ưu tiên (AQ10)")
        show_fig("aq10_coverage_at_k.png")
