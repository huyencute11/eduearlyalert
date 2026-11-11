# Ưu tiên hỗ trợ – AQ10, AQ11, AQ12 (tự sinh)

Tập test, n = 1834 sinh viên còn theo học tại ngày 41; số cần hỗ trợ thực tế = 717. Năng lực K = 35 × 2 cố vấn = **70 ca/tuần** (ASSUMPTION).

## AQ10 – So sánh phương án ưu tiên

| strategy                    |   K |   coverage_at_K |   precision_at_K |
|:----------------------------|----:|----------------:|-----------------:|
| A_risk_only                 |  70 |           0.093 |            0.957 |
| B_risk_plus_engagement_drop |  70 |           0.093 |            0.957 |
| C_risk_plus_missing_work    |  70 |           0.093 |            0.957 |

Phương án có Coverage@K cao nhất: **A_risk_only**.

![](figures/aq10_coverage_at_k.png)

## AQ12 – Kịch bản ngưỡng cảnh báo

|   alert_share |   n_alerted |   recall |   precision |   false_alarms |   weeks_of_advisor_capacity | fits_capacity   |
|--------------:|------------:|---------:|------------:|---------------:|----------------------------:|:----------------|
|           0.1 |         183 |    0.237 |       0.929 |             13 |                        2.61 | False           |
|           0.2 |         367 |    0.418 |       0.817 |             67 |                        5.24 | False           |
|           0.3 |         550 |    0.545 |       0.711 |            159 |                        7.86 | False           |

![](figures/aq12_tradeoff.png)

## AQ11 – Phân bố loại hỗ trợ đề xuất trong Risk List

| suggested_support                               |   count |
|:------------------------------------------------|--------:|
| Nhắc nhở có duyệt + hỏi thăm lý do chưa nộp bài |      37 |
| Mời tư vấn 1–1                                  |      29 |
| Gợi ý tài nguyên ôn tập theo concept            |       2 |
| Giới thiệu tutoring nhóm nhỏ                    |       2 |

> Risk List (`reports/risk_list.csv`) chỉ là đề xuất. Mọi dòng ở trạng thái `pending_review`; cố vấn phê duyệt trên dashboard trước bất kỳ liên hệ nào. Đây là đánh giá trên dữ liệu lịch sử, không chứng minh hiệu quả can thiệp.