# Kết quả mô hình AQ7 (tự sinh)

- Quần thể: sinh viên còn theo học tại ngày 41. Train ['2013B', '2013J'] (n=725), valid ['2014B'] (n=360), test ['2014J'] (n=363).
- Mô hình chính (chọn theo PR-AUC trên valid): **logistic**, ngưỡng 0.467 (chọn trên valid).
- Tiêu chí chấp nhận trên TEST: Recall 0.824 (≥ 0.8: ĐẠT), F1 0.807 (≥ 0.75: ĐẠT).

| split   | model    |   threshold |   recall |   precision |     f1 |   roc_auc |   pr_auc |   alert_rate |
|:--------|:---------|------------:|---------:|------------:|-------:|----------:|---------:|-------------:|
| valid   | rule     |      0.5    |   0.5146 |      0.7097 | 0.5966 |    0.6621 |   0.5958 |       0.3444 |
| valid   | logistic |      0.4666 |   0.8187 |      0.8092 | 0.814  |    0.8883 |   0.8656 |       0.4806 |
| valid   | gboost   |      0.5412 |   0.8012 |      0.8107 | 0.8059 |    0.8671 |   0.8441 |       0.4694 |
| test    | rule     |      0.5    |   0.5211 |      0.6549 | 0.5804 |    0.6723 |   0.5286 |       0.3113 |
| test    | logistic |      0.4666 |   0.8239 |      0.7905 | 0.8069 |    0.8926 |   0.8643 |       0.4077 |
| test    | gboost   |      0.5412 |   0.7746 |      0.7432 | 0.7586 |    0.8843 |   0.8545 |       0.4077 |

## False negative (bị bỏ sót) trên test

Số FN = 25; phân theo kết quả thực tế: {'Withdrawn': 20, 'Fail': 5}.

|                    |   median_false_negative |   median_true_positive |   n_fn |   n_tp |
|:-------------------|------------------------:|-----------------------:|-------:|-------:|
| clicks_total       |                  184    |                  32    |     25 |    117 |
| active_days_total  |                   24    |                   7    |     25 |    117 |
| engagement_change  |                   -0.1  |                  -0.05 |     25 |    117 |
| n_missing          |                    0    |                   2    |     25 |    117 |
| mean_score         |                   70.17 |                  56.75 |     25 |    117 |
| first_assess_score |                   71    |                  60    |     25 |    117 |

> Nếu chưa đạt tiêu chí: báo cáo trung thực, phân tích vì sao (FN là ai), KHÔNG chỉnh ngưỡng trên test để 'cho đạt'.