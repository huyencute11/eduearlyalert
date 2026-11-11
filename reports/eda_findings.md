# EDA Findings – Observation · Insight · Evidence · Limitation

> Observation do code tự sinh từ dữ liệu train+valid (tập test được giữ kín).
> **Insight phải do nhóm viết** trong `docs/eda_insights.md` (heading `## <tên file hình>`): nối observation với một quyết định của stakeholder.
> Không dùng từ 'gây ra', 'tác động', 'sinh viên yếu'.

Số biểu đồ: **11**

## 1. AQ1 – Tỷ lệ hoàn thành / Fail / Withdrawn theo lượt giảng dạy?

![aq1_outcomes_by_presentation.png](figures/aq1_outcomes_by_presentation.png)

| | |
|---|---|
| **Observation** | Completion rate theo lượt: 2013B 48.5%, 2013J 48.0%, 2014B 43.6%. Toàn bộ: 46.9% (n=5397). |
| **Insight** | [NHÁP] Chỉ khoảng 47% sinh viên hoàn thành môn, và tỷ lệ này khá ổn định qua 3 lượt (43,6–48,5%). Nhu cầu hỗ trợ là lớn và lặp lại mỗi lượt, không phải chuyện riêng của một lượt. Với Program Manager (D3), baseline thật là 46,9%, thay cho giả định 60%. Năng lực 70 ca/tuần (giả định K = 35 × 2) chỉ phủ được một phần nhỏ số sinh viên cần hỗ trợ, nên cần ưu tiên và phân tầng. |
| **Evidence** | `reports/figures/aq1_outcomes_by_presentation.png` |
| **Limitation** | Dữ liệu Anh 2013–2014; baseline 60% trong proposal là assumption, cần cập nhật theo số này. |

## 2. AQ1 – Rút môn diễn ra vào tuần nào? Còn bao nhiêu % rút sau Tuần 6?

![aq1_cumulative_withdrawal.png](figures/aq1_cumulative_withdrawal.png)

| | |
|---|---|
| **Observation** | Trong số sinh viên rút môn, tỷ lệ rút SAU mốc dự báo: 2013B 56%, 2013J 51%, 2014B 53% → đây là cửa sổ còn can thiệp được. |
| **Insight** | [NHÁP] 51–56% số sinh viên rút môn rút sau Tuần 6. Vì vậy cảnh báo ở cuối Tuần 6 vẫn còn thời gian để cố vấn (D1) liên hệ hơn một nửa số người sẽ rút. Phần còn lại rút trước mốc này, nên mô hình không thấy được họ. Nhóm này cần cách hỗ trợ khác ngay từ đầu môn (Lecturer, Program Manager), ví dụ hoạt động làm quen trong Tuần 0–2. |
| **Evidence** | `reports/figures/aq1_cumulative_withdrawal.png` |
| **Limitation** | Ngày rút môn có thể là ngày ghi nhận hành chính, không phải ngày thực sự ngừng học. |

## 3. AQ2 – Tương tác VLE phân bố thế nào theo tuần và loại tài nguyên?

![aq2_heatmap_week_activity.png](figures/aq2_heatmap_week_activity.png)

| | |
|---|---|
| **Observation** | 3 loại tài nguyên nhiều click nhất: oucontent (199 click/SV), forumng (168 click/SV), homepage (119 click/SV). |
| **Insight** | [NHÁP] Nội dung bài học (oucontent, 199 click/SV), diễn đàn (forumng, 168) và trang chủ (homepage, 119) là ba kênh sinh viên dùng nhiều nhất. Với Lecturer (D2), thay đổi hoạt động học nên ưu tiên hai kênh nội dung và diễn đàn. Diễn đàn cũng là nơi phù hợp để nhắc nhở chung, không cần chỉ đích danh ai. |
| **Evidence** | `reports/figures/aq2_heatmap_week_activity.png` |
| **Limitation** | Click là proxy của tương tác, không đo được chất lượng học (góp ý của Lecturer). |

## 4. AQ2 – Mức tương tác của lớp thay đổi thế nào qua từng tuần?

![aq2_clicks_by_week_box.png](figures/aq2_clicks_by_week_box.png)

| | |
|---|---|
| **Observation** | Tỷ lệ sinh viên 0 click: T1 19%, T2 21%, T3 19%, T4 23%, T5 26%, T6 28%. |
| **Insight** | [NHÁP] Tỷ lệ sinh viên không có click nào trong tuần tăng từ 19% (Tuần 1) lên 28% (Tuần 6). Nhóm "im lặng" lớn dần trước giữa kỳ. Với Lecturer và Advisor, "0 click hai tuần liên tiếp" là dấu hiệu đơn giản, có thể theo dõi ngay cả khi không có mô hình. Điều này nhất quán với baseline luật trong AQ7. |
| **Evidence** | `reports/figures/aq2_clicks_by_week_box.png` |
| **Limitation** | Tổng hợp theo tuần làm mất dao động trong tuần. |

## 5. AQ3 – Tỷ lệ nộp đúng hạn / muộn / không nộp từng bài đầu kỳ?

![aq3_submission_status.png](figures/aq3_submission_status.png)

| | |
|---|---|
| **Observation** | Tỷ lệ chưa nộp tại mốc: TMA1 22%. |
| **Insight** | [NHÁP] 22% sinh viên chưa nộp TMA1 tại ngày 41. Với Advisor (D1), đây là lý do liên hệ cụ thể, dễ giải thích và không mang tính gán nhãn ("hỏi thăm khó khăn khi làm TMA1"). Với Lecturer (D2), nên nhắc nhở trước hạn nộp TMA1 (ngày 19 ở các lượt 2013, ngày 24 ở các lượt 2014). |
| **Evidence** | `reports/figures/aq3_submission_status.png` |
| **Limitation** | Bài nộp sau ngày 41 bị tính là 'chưa nộp' vì chưa quan sát được tại mốc dự báo. |

## 6. AQ3 – Điểm trung vị và phân bố điểm của từng bài đầu kỳ?

![aq3_score_distribution.png](figures/aq3_score_distribution.png)

| | |
|---|---|
| **Observation** | Điểm trung vị: TMA1 82. |
| **Insight** | [NHÁP] Trong số sinh viên đã nộp TMA1, điểm trung vị là 82, tức phần lớn người nộp đạt điểm khá. Với nhiều sinh viên, việc có nộp hay không mang nhiều thông tin hơn chính điểm số. Lecturer có thể xem riêng nhóm nhỏ có điểm dưới 40 để hỗ trợ theo nội dung bài. |
| **Evidence** | `reports/figures/aq3_score_distribution.png` |
| **Limitation** | Chỉ tính bài đã nộp; sinh viên không nộp không xuất hiện trong histogram. |

## 7. AQ4 – Chỉ báo engagement Tuần 1–6 khác biệt đến mức nào giữa hai nhóm?

![aq4_engagement_by_outcome.png](figures/aq4_engagement_by_outcome.png)

| | |
|---|---|
| **Observation** | Chỉ báo khác biệt lớn nhất (Cliff's δ, p Holm): active_days_total δ=0.46 (vừa), p=1.1e-160; clicks_total δ=0.46 (vừa), p=6.7e-158; inactive_weeks δ=-0.35 (vừa), p=4.4e-132. |
| **Insight** | [NHÁP] Số ngày hoạt động và tổng click khác biệt ở mức vừa giữa nhóm hoàn thành và không hoàn thành (Cliff's δ = 0,46); số tuần không hoạt động khác biệt ở mức δ = −0,35. Khác biệt là rõ, nhưng hai nhóm vẫn chồng lấn nhiều. Với Advisor, chỉ báo tương tác hữu ích để xếp thứ tự ưu tiên, nhưng không đủ để kết luận về từng cá nhân; cần đọc kèm thông tin bài đánh giá. |
| **Evidence** | `reports/figures/aq4_engagement_by_outcome.png` |
| **Limitation** | Khác biệt/liên hệ, KHÔNG phải nhân quả. Với n lớn, p nhỏ là dễ – đọc effect size. |

## 8. AQ4 – Đường tương tác của hai nhóm tách nhau từ tuần nào?

![aq4_weekly_median_clicks.png](figures/aq4_weekly_median_clicks.png)

| | |
|---|---|
| **Observation** | Tỷ số trung vị click (không hoàn thành / hoàn thành): T1 0.49, T2 0.43, T3 0.51, T4 0.38, T5 0.21, T6 0.18. |
| **Insight** | [NHÁP] Tỷ số trung vị click giữa nhóm không hoàn thành và nhóm hoàn thành giữ quanh 0,4–0,5 ở Tuần 1–3, rồi giảm mạnh còn 0,21 (Tuần 5) và 0,18 (Tuần 6). Hai nhóm tách nhau rõ nhất từ Tuần 4–5. Với Program Manager (D3), mốc Tuần 6 nắm được giai đoạn tách nhau này. Một mốc sớm hơn (Tuần 4) có thể cảnh báo sớm hơn nhưng tín hiệu yếu hơn; đó là đánh đổi cần thử ở phân tích độ nhạy. |
| **Evidence** | `reports/figures/aq4_weekly_median_clicks.png` |
| **Limitation** | Trung vị che khuất sự đa dạng trong từng nhóm. |

## 9. AQ5 – Điểm bài đầu tiên liên hệ thế nào với khả năng hoàn thành?

![aq5_completion_by_first_score.png](figures/aq5_completion_by_first_score.png)

| | |
|---|---|
| **Observation** | Tỷ lệ hoàn thành: <40 8%, 40–60 29%, 60–80 53%, 80–100 68%, Chưa nộp 11%. |
| **Insight** | [NHÁP] Tỷ lệ hoàn thành chỉ 8% ở nhóm điểm TMA1 dưới 40 và 11% ở nhóm chưa nộp, so với 68% ở nhóm 80–100. Kết quả TMA1 là mốc kiểm tra sớm có liên hệ mạnh với khả năng hoàn thành. Với Advisor (D1), sinh viên chưa nộp hoặc dưới 40 điểm nên được ưu tiên trò chuyện. Với Lecturer (D2), cân nhắc hỗ trợ chuẩn bị cho bài đầu tiên. |
| **Evidence** | `reports/figures/aq5_completion_by_first_score.png` |
| **Limitation** | Liên hệ, không nhân quả; nhóm 'chưa nộp' gộp nhiều lý do khác nhau. |

## 10. AQ5 – Sau khi điều chỉnh theo engagement, yếu tố bài đánh giá nào còn liên hệ mạnh?

![aq5_logit_coefficients.png](figures/aq5_logit_coefficients.png)

| | |
|---|---|
| **Observation** | OR/SD: first_assess_score 0.37, share_missing 0.69, n_late 1.31, active_days_total 0.54, engagement_change 0.76. Pseudo R² = 0.184. |
| **Insight** | [NHÁP] Sau khi điều chỉnh theo tương tác, điểm TMA1 vẫn liên hệ rõ với khả năng không hoàn thành (OR = 0,37 cho mỗi SD điểm), số ngày hoạt động cũng vậy (OR = 0,54/SD). Hai nhóm tín hiệu (bài đánh giá và tương tác) bổ sung cho nhau. Pseudo R² = 0,18, nên phần lớn khác biệt vẫn chưa giải thích được. Với Program Manager, mô hình chắc chắn sẽ bỏ sót một phần sinh viên, nên phải giữ bước cố vấn duyệt và kênh để sinh viên tự tìm hỗ trợ. |
| **Evidence** | `reports/figures/aq5_logit_coefficients.png` |
| **Limitation** | Mô hình giải thích, không phải dự báo; các biến tương quan nhau nên hệ số có thể không ổn định. |

## 11. AQ6 – Concept/CLO nào nhiều sinh viên cần hỗ trợ thêm nhất?

![aq6_concept_gaps.png](figures/aq6_concept_gaps.png)

| | |
|---|---|
| **Observation** | Concept có tỷ lệ cần hỗ trợ cao nhất ở nhóm không hoàn thành: C01 20%, C03 20%, C05 20%. |
| **Insight** | [NHÁP] Ba concept C01, C03 và C05 có cùng tỷ lệ "cần hỗ trợ thêm" là 20%, vì ở FFF chỉ có TMA1 có hạn trước ngày 41 và cả ba concept đều được ánh xạ từ TMA1. Ở mốc Tuần 6, KG chưa phân biệt được concept nào cần hỗ trợ hơn; hình này chỉ minh hoạ cơ chế. Ánh xạ concept là DỮ LIỆU MÔ PHỎNG, nên Lecturer không nên dùng hình này để điều chỉnh nội dung thật. |
| **Evidence** | `reports/figures/aq6_concept_gaps.png` |
| **Limitation** | Ánh xạ concept là DỮ LIỆU MÔ PHỎNG và ở mức bài, không phải mức câu hỏi. |
