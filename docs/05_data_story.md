# 05 · Data Story – từ biểu đồ đến quyết định

Data story **không phải** chạy thêm phân tích mới; nó sắp các bằng chứng đã có thành một
mạch kể dẫn tới quyết định. Mạch dưới đây đi theo đường lõi AQ1 → AQ4 → AQ7 → AQ10.

| Chương | Thông điệp cần chứng minh | Hình (reports/figures) | Bảng/số liệu | Ai cần nghe |
|---|---|---|---|---|
| 1. Hiện trạng | Bao nhiêu % không hoàn thành; phần lớn rút môn diễn ra **sau** Tuần 6 → còn cửa sổ can thiệp | `aq1_outcomes_by_presentation`, `aq1_cumulative_withdrawal` | `cohort_flow.csv` | PM |
| 2. Tín hiệu sớm | Hai nhóm tách nhau từ rất sớm, rõ nhất ở số ngày hoạt động và bài chưa nộp – không chỉ số click | `aq4_engagement_by_outcome`, `aq4_weekly_median_clicks`, `aq3_submission_status` | `aq4_group_comparison.csv` | Lecturer, Advisor |
| 3. Ở đâu | Bài/concept nào nhiều sinh viên cần hỗ trợ thêm | `aq5_completion_by_first_score`, `aq6_concept_gaps` | `aq5_logit_odds_ratios.csv` | Lecturer |
| 4. Ai | Mô hình tại cuối Tuần 6 bắt được bao nhiêu %, bỏ sót ai, có công bằng không | `aq7_roc_pr`, `aq7_confusion_matrix`, `aq9_recall_by_group` | `model_results.md`, `fairness_report.md` | PM, Advisor |
| 5. Làm gì | Với 70 ca/tuần, phương án nào tiếp cận nhiều người cần hỗ trợ nhất; ngưỡng nào khả thi | `aq10_coverage_at_k`, `aq12_tradeoff` | `aq12_threshold_scenarios.csv` | Advisor, PM |
| 6. Giới hạn | OULAD Anh 2013–14; KG mô phỏng; không nhân quả; cần pilot có nhóm so sánh | – | – | Tất cả |

## Công thức viết mỗi chương

1. **Câu chủ đề** (1 câu, có số): "Chỉ X% sinh viên lượt 2013J hoàn thành môn." (thay X bằng số thật)
2. **Bằng chứng**: 1 hình + 1 con số từ file trong `reports/`.
3. **Insight**: điều đó có nghĩa gì cho *quyết định của ai*.
4. **Giới hạn**: một câu, trung thực.

Observation ≠ Insight. Observation là cái thấy trên hình (ví dụ minh hoạ: "nhóm không hoàn thành có trung
vị A ngày hoạt động so với B"). Insight nối với hành động ("số ngày hoạt động Tuần 1–3
là chỉ báo cố vấn có thể theo dõi mà không cần mô hình").

## Từ data story sang slide (10–15 slide)

Title/team → Problem → Stakeholders → Data → Analytics questions → Chương 1 → Chương 2–3 (EDA)
→ Methodology → Chương 4 (Results + Evaluation) → Governance → Demo (dashboard Advisor) →
Chương 5 → Limitations → Conclusion → Q&A.

## Kịch bản demo

User question ("Tuần này tôi nên liên hệ ai trước?") → hệ thống đọc dữ liệu đến cuối Tuần 6 →
mô hình + luật ưu tiên → Risk List top-K kèm lý do và concept → cố vấn mở một ca, đọc lý do,
**phê duyệt** → audit log ghi lại → hành động: liên hệ, chọn tài nguyên từ KG.
