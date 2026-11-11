# Kết quả mô hình AQ7 (tự sinh)

- Quần thể: sinh viên còn theo học tại ngày 41. Train ['2013B', '2013J'] (n=3383), valid ['2014B'] (n=1283), test ['2014J'] (n=1834).
- Mô hình chính (chọn theo PR-AUC trên valid): **gboost**, ngưỡng 0.405 (chọn trên valid).
- Tiêu chí chấp nhận trên TEST: Recall 0.805 (≥ 0.8: ĐẠT), F1 0.661 (≥ 0.75: CHƯA ĐẠT).

| split   | model    |   threshold |   recall |   precision |     f1 |   roc_auc |   pr_auc |   alert_rate |
|:--------|:---------|------------:|---------:|------------:|-------:|----------:|---------:|-------------:|
| valid   | rule     |      0.5    |   0.2782 |      0.8413 | 0.4182 |    0.6139 |   0.5879 |       0.1621 |
| valid   | logistic |      0.3672 |   0.8315 |      0.6425 | 0.7249 |    0.7754 |   0.7756 |       0.6345 |
| valid   | gboost   |      0.4046 |   0.8013 |      0.6545 | 0.7205 |    0.7738 |   0.7768 |       0.6002 |
| test    | rule     |      0.5    |   0.2915 |      0.8601 | 0.4354 |    0.6305 |   0.5277 |       0.1325 |
| test    | logistic |      0.3672 |   0.8563 |      0.5487 | 0.6688 |    0.8012 |   0.7395 |       0.6101 |
| test    | gboost   |      0.4046 |   0.8047 |      0.5602 | 0.6606 |    0.7937 |   0.7447 |       0.5616 |

## False negative (bị bỏ sót) trên test

Số FN = 140; phân theo kết quả thực tế: {'Withdrawn': 75, 'Fail': 65}.

|                    |   median_false_negative |   median_true_positive |   n_fn |   n_tp |
|:-------------------|------------------------:|-----------------------:|-------:|-------:|
| clicks_total       |                  757    |                 206    |    140 |    577 |
| active_days_total  |                   29.5  |                  13    |    140 |    577 |
| engagement_change  |                   -0.01 |                  -0.42 |    140 |    577 |
| n_missing          |                    0    |                   0    |    140 |    577 |
| mean_score         |                   82    |                  73    |    140 |    577 |
| first_assess_score |                   82    |                  73    |    140 |    577 |

> Nếu chưa đạt tiêu chí: báo cáo trung thực, phân tích vì sao (FN là ai), KHÔNG chỉnh ngưỡng trên test để 'cho đạt'.