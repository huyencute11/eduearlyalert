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
    st.header("Tổng quan chương trình")
    if need(REPORTS / "model_metrics.json"):
        m = json.loads((REPORTS / "model_metrics.json").read_text(encoding="utf-8"))
        t = m["test"][m["main_model"]]
        flow = pd.read_csv(REPORTS / "cohort_flow.csv")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Completion rate (toàn bộ lượt)", f"{1 - (flow['positive_rate_all'] * flow['registered']).sum() / flow['registered'].sum():.1%}")
        c2.metric("Early Detection Recall (test)", f"{t['recall']:.0%}", help=f"Tiêu chí ≥ {m['acceptance']['recall_min']:.0%}")
        c3.metric("F1 (test)", f"{t['f1']:.2f}", help=f"Tiêu chí ≥ {m['acceptance']['f1_min']}")
        c4.metric("Tỷ lệ được cảnh báo", f"{t['alert_rate']:.0%}")
        st.dataframe(flow, width="stretch", hide_index=True)
    c1, c2 = st.columns(2)
    with c1:
        show_fig("aq1_outcomes_by_presentation.png")
    with c2:
        show_fig("aq1_cumulative_withdrawal.png")
    st.subheader("Năng lực cố vấn và ngưỡng cảnh báo (AQ12)")
    if (REPORTS / "aq12_threshold_scenarios.csv").exists():
        st.dataframe(pd.read_csv(REPORTS / "aq12_threshold_scenarios.csv"), hide_index=True, width="stretch")
    show_fig("aq12_tradeoff.png")
    st.subheader("Công bằng (AQ9)")
    show_fig("aq9_recall_by_group.png")

# ---------------------------------------------------------------------------
elif role == "Lecturer":
    st.header("Thông tin cho giảng viên")
    st.caption("Chỉ số tổng hợp theo bài đánh giá và concept – không hiển thị cá nhân.")
    c1, c2 = st.columns(2)
    with c1:
        show_fig("aq3_submission_status.png")
    with c2:
        show_fig("aq3_score_distribution.png")
    show_fig("aq6_concept_gaps.png", "Concept dựa trên ánh xạ MÔ PHỎNG (kg/)")
    show_fig("aq4_weekly_median_clicks.png")
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
