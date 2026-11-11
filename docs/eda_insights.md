# EDA insights (nhóm viết)

<!--
File này được ghép tự động vào cột Insight của reports/eda_findings.md mỗi lần chạy `pipeline eda`.
Mỗi insight nằm dưới heading `## <tên file hình>`. Hình chưa có insight thì report vẫn ghi TODO.
Insight = observation có ý nghĩa gì cho QUYẾT ĐỊNH của ai (Advisor D1, Lecturer D2, Program Manager D3).
Dùng "liên hệ/khác biệt", không dùng "gây ra/tác động"; không dùng "sinh viên yếu/kém".
Số liệu: module FFF, train + valid (2013B, 2013J, 2014B). Tập test không dùng trong EDA.
-->

> **BẢN NHÁP – P2 cần rà và sửa.** Claude soạn ngày 11/11/2026 từ `reports/eda_findings.md` (FFF).

## aq1_outcomes_by_presentation.png
[NHÁP] Chỉ khoảng 47% sinh viên hoàn thành môn, và tỷ lệ này khá ổn định qua 3 lượt (43,6–48,5%). Nhu cầu hỗ trợ là lớn và lặp lại mỗi lượt, không phải chuyện riêng của một lượt. Với Program Manager (D3), baseline thật là 46,9%, thay cho giả định 60%. Năng lực 70 ca/tuần (giả định K = 35 × 2) chỉ phủ được một phần nhỏ số sinh viên cần hỗ trợ, nên cần ưu tiên và phân tầng.

## aq1_cumulative_withdrawal.png
[NHÁP] 51–56% số sinh viên rút môn rút sau Tuần 6. Vì vậy cảnh báo ở cuối Tuần 6 vẫn còn thời gian để cố vấn (D1) liên hệ hơn một nửa số người sẽ rút. Phần còn lại rút trước mốc này, nên mô hình không thấy được họ. Nhóm này cần cách hỗ trợ khác ngay từ đầu môn (Lecturer, Program Manager), ví dụ hoạt động làm quen trong Tuần 0–2.

## aq2_heatmap_week_activity.png
[NHÁP] Nội dung bài học (oucontent, 199 click/SV), diễn đàn (forumng, 168) và trang chủ (homepage, 119) là ba kênh sinh viên dùng nhiều nhất. Với Lecturer (D2), thay đổi hoạt động học nên ưu tiên hai kênh nội dung và diễn đàn. Diễn đàn cũng là nơi phù hợp để nhắc nhở chung, không cần chỉ đích danh ai.

## aq2_clicks_by_week_box.png
[NHÁP] Tỷ lệ sinh viên không có click nào trong tuần tăng từ 19% (Tuần 1) lên 28% (Tuần 6). Nhóm "im lặng" lớn dần trước giữa kỳ. Với Lecturer và Advisor, "0 click hai tuần liên tiếp" là dấu hiệu đơn giản, có thể theo dõi ngay cả khi không có mô hình. Điều này nhất quán với baseline luật trong AQ7.

## aq3_submission_status.png
[NHÁP] 22% sinh viên chưa nộp TMA1 tại ngày 41. Với Advisor (D1), đây là lý do liên hệ cụ thể, dễ giải thích và không mang tính gán nhãn ("hỏi thăm khó khăn khi làm TMA1"). Với Lecturer (D2), nên nhắc nhở trước hạn nộp TMA1 (ngày 19 ở các lượt 2013, ngày 24 ở các lượt 2014).

## aq3_score_distribution.png
[NHÁP] Trong số sinh viên đã nộp TMA1, điểm trung vị là 82, tức phần lớn người nộp đạt điểm khá. Với nhiều sinh viên, việc có nộp hay không mang nhiều thông tin hơn chính điểm số. Lecturer có thể xem riêng nhóm nhỏ có điểm dưới 40 để hỗ trợ theo nội dung bài.

## aq4_engagement_by_outcome.png
[NHÁP] Số ngày hoạt động và tổng click khác biệt ở mức vừa giữa nhóm hoàn thành và không hoàn thành (Cliff's δ = 0,46); số tuần không hoạt động khác biệt ở mức δ = −0,35. Khác biệt là rõ, nhưng hai nhóm vẫn chồng lấn nhiều. Với Advisor, chỉ báo tương tác hữu ích để xếp thứ tự ưu tiên, nhưng không đủ để kết luận về từng cá nhân; cần đọc kèm thông tin bài đánh giá.

## aq4_weekly_median_clicks.png
[NHÁP] Tỷ số trung vị click giữa nhóm không hoàn thành và nhóm hoàn thành giữ quanh 0,4–0,5 ở Tuần 1–3, rồi giảm mạnh còn 0,21 (Tuần 5) và 0,18 (Tuần 6). Hai nhóm tách nhau rõ nhất từ Tuần 4–5. Với Program Manager (D3), mốc Tuần 6 nắm được giai đoạn tách nhau này. Một mốc sớm hơn (Tuần 4) có thể cảnh báo sớm hơn nhưng tín hiệu yếu hơn; đó là đánh đổi cần thử ở phân tích độ nhạy.

## aq5_completion_by_first_score.png
[NHÁP] Tỷ lệ hoàn thành chỉ 8% ở nhóm điểm TMA1 dưới 40 và 11% ở nhóm chưa nộp, so với 68% ở nhóm 80–100. Kết quả TMA1 là mốc kiểm tra sớm có liên hệ mạnh với khả năng hoàn thành. Với Advisor (D1), sinh viên chưa nộp hoặc dưới 40 điểm nên được ưu tiên trò chuyện. Với Lecturer (D2), cân nhắc hỗ trợ chuẩn bị cho bài đầu tiên.

## aq5_logit_coefficients.png
[NHÁP] Sau khi điều chỉnh theo tương tác, điểm TMA1 vẫn liên hệ rõ với khả năng không hoàn thành (OR = 0,37 cho mỗi SD điểm), số ngày hoạt động cũng vậy (OR = 0,54/SD). Hai nhóm tín hiệu (bài đánh giá và tương tác) bổ sung cho nhau. Pseudo R² = 0,18, nên phần lớn khác biệt vẫn chưa giải thích được. Với Program Manager, mô hình chắc chắn sẽ bỏ sót một phần sinh viên, nên phải giữ bước cố vấn duyệt và kênh để sinh viên tự tìm hỗ trợ.

## aq6_concept_gaps.png
[NHÁP] Ba concept C01, C03 và C05 có cùng tỷ lệ "cần hỗ trợ thêm" là 20%, vì ở FFF chỉ có TMA1 có hạn trước ngày 41 và cả ba concept đều được ánh xạ từ TMA1. Ở mốc Tuần 6, KG chưa phân biệt được concept nào cần hỗ trợ hơn; hình này chỉ minh hoạ cơ chế. Ánh xạ concept là DỮ LIỆU MÔ PHỎNG, nên Lecturer không nên dùng hình này để điều chỉnh nội dung thật.
