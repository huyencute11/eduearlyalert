# 01 · Tổng quan dự án

> Nguồn: Project Charter V1 và Milestone 1 (Nhóm 3, MTH045). File này là bản tóm tắt để
> code bám theo; khi proposal thay đổi, cập nhật file này trước rồi mới sửa code.

## Problem statement

Trong các môn blended learning, sinh viên giảm tương tác hoặc hụt bài đánh giá đầu kỳ
thường chỉ được nhận diện sau giữa kỳ, khi hỗ trợ đã kém hiệu quả. Cố vấn có năng lực
giới hạn nên cần **nhận diện sớm, xếp thứ tự ưu tiên và hiểu lý do** sinh viên cần hỗ trợ.

## Mức độ project

Mức 3 (Predictive/Explanatory) + Mức 4 nhẹ (Knowledge Graph quy mô nhỏ, dữ liệu mô phỏng).
Không có LLM/Agent trong lõi; LLM chỉ là tuỳ chọn read-only để soạn giải thích.

## Stakeholders và quyết định

| Stakeholder | Quyết định được hỗ trợ | Màn hình dashboard |
|---|---|---|
| Program Manager | D3 – phân bổ cố vấn, mở rộng mô hình (gần one-way door) | Program Manager |
| Lecturer | D2 – điều chỉnh hoạt động/bài đánh giá/ôn tập | Lecturer |
| Advisor | D1 – liên hệ ai trước trong tuần (two-way door) | Advisor (Risk List) |
| Sinh viên (gián tiếp) | Nhận hỗ trợ sớm, không bị gán nhãn | – |

## Business Goal · SMART · KPI

* **Business Goal:** cải thiện khả năng hoàn thành môn học trong các môn blended thông qua
  nhận diện sớm và hỗ trợ kịp thời.
* **Primary KPI:** Course Completion Rate = (Pass + Distinction) / đăng ký Tuần 1.
  Baseline 60% → 68% là **assumption**; cập nhật theo `reports/figures/aq1_*` sau khi chạy dữ liệu thật.
* **Secondary:** Early Detection Recall ≥ 80%; Timely Support Contact Rate ≥ 80%.
* **Tiêu chí chấp nhận mô hình** (không phải KPI): Recall ≥ 0.80, F1 ≥ 0.75 trên hold-out
  theo presentation → `config.yaml › acceptance`.

## Analytical Question Ladder ↔ code

★ = đường lõi. Nếu thiếu thời gian, giữ đường lõi AQ1 → AQ4 → AQ7 → AQ10.

| AQ | Loại | Câu hỏi (rút gọn) | Hàm / file | Output chính |
|---|---|---|---|---|
| AQ1 ★ | Descriptive | Tỷ lệ hoàn thành/Fail/Withdrawn; rút môn theo tuần | `eda.aq1_outcomes`, `eda.aq1_cumulative_withdrawal` | `aq1_*.png` |
| AQ2 | Descriptive | Tương tác VLE theo tuần × loại tài nguyên | `eda.aq2_heatmap`, `eda.aq2_weekly_box` | `aq2_*.png` |
| AQ3 | Descriptive | Nộp đúng hạn/muộn/không nộp; điểm từng bài | `eda.aq3_submission`, `eda.aq3_scores` | `aq3_*.png` |
| AQ4 ★ | Diagnostic | Chỉ báo engagement khác biệt giữa hai nhóm (effect size) | `eda.aq4_group_comparison`, `eda.aq4_weekly_lines` | `aq4_group_comparison.csv` |
| AQ5 | Diagnostic | Điểm/nộp bài liên hệ với hoàn thành (đã điều chỉnh) | `eda.aq5_first_score`, `eda.aq5_explanatory_regression` | `aq5_logit_odds_ratios.csv` |
| AQ6 | Diagnostic | Concept/CLO nhiều sinh viên cần hỗ trợ (KG mô phỏng) | `kg.concept_gaps`, `eda.aq6_concept_gaps` | `aq6_concept_gaps.png` |
| AQ7 ★ | Predictive | Xác suất không hoàn thành tại cuối Tuần 6 | `model.run` | `model_results.md` |
| AQ8 | Predictive | Rút môn Tuần 7–12 | *mở rộng – chưa làm* | – |
| AQ9 | Predictive | Hiệu năng nhất quán giữa nhóm/presentation? | `fairness.run` | `fairness_report.md` |
| AQ10 ★ | Prescriptive | Ai liên hệ trước với năng lực K? | `prioritize.run` | `risk_list.csv`, `aq10_*.png` |
| AQ11 | Prescriptive | Loại hỗ trợ nào cho từng sinh viên? | `prioritize.support_type` + KG | cột `suggested_support` |
| AQ12 | Prescriptive | Ngưỡng cảnh báo 10/20/30% – đánh đổi | `prioritize.run` | `aq12_threshold_scenarios.csv` |

## Ngoài phạm vi

Triển khai thật / tự động nhắn sinh viên; dữ liệu cá nhân thật; chứng minh nhân quả;
so sánh giảng viên; dự báo tuyển sinh/dropout cấp trường.
