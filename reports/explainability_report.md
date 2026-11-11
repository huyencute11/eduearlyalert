# Explainability Report (tự sinh)

Mô hình chính: **gboost**. SHAP chưa cài (`pip install shap`) – dùng permutation importance.

## Global – Permutation importance (valid, thước đo PR-AUC)

![](figures/aq7_feature_importance.png)

|                      |   importance |
|:---------------------|-------------:|
| mean_score           |       0.1047 |
| clicks_w6            |       0.0234 |
| mean_days_early      |       0.0109 |
| clicks_late          |       0.0084 |
| num_of_prev_attempts |       0.0048 |
| n_on_time            |       0.0047 |
| share_subpage        |       0.0041 |
| clicks_w5            |       0.003  |
| active_days_total    |       0.0027 |
| share_forumng        |       0.0019 |
| clicks_w2            |       0.0012 |
| share_oucontent      |       0.0007 |
| clicks_early         |       0.0007 |
| share_quiz           |       0.0006 |
| inactive_weeks       |       0.0006 |

## Local – Reason codes

Reason code là luật minh bạch (không phải SHAP), ngưỡng lấy từ tập train, xếp theo
độ quan trọng toàn cục của feature liên quan. Tất cả dùng ngôn ngữ hỗ trợ.

| Feature | Ví dụ câu giải thích |
|---|---|
| `first_assess_missing` | Chưa nộp bài đánh giá đầu tiên – nên hỏi thăm khó khăn |
| `n_missing` | Còn 1 bài đánh giá đầu kỳ chưa nộp |
| `engagement_change` | Hoạt động trên LMS giảm rõ ở Tuần 4–6 so với Tuần 1–3 |
| `active_days_total` | Số ngày học trên LMS (6 ngày) thuộc nhóm 25% thấp nhất lớp |
| `inactive_weeks` | 2 tuần không có hoạt động LMS |
| `mean_score` | Điểm trung bình bài đầu kỳ (38) chưa đạt ngưỡng 40 – cần hỗ trợ thêm |
| `n_late` | Có 1 bài nộp muộn |

> Giới hạn: reason code mô tả tín hiệu dữ liệu, KHÔNG phải nguyên nhân. Cố vấn cần trao đổi với sinh viên để hiểu bối cảnh thật.