# Model Design Card – AQ7 (GĐ5)

> Điền từ `reports/model_results.md`, `reports/model_metrics.json`, `config.yaml`.
>
> **BẢN NHÁP – P3 cần rà và sửa.** Claude điền ngày 11/11/2026 từ lần chạy trên OULAD thật, module FFF.
> Chạy lại pipeline thì phải đối chiếu lại toàn bộ số liệu.

| Mục | Nội dung |
|---|---|
| Câu hỏi | AQ7 – ước lượng xác suất không hoàn thành tại cuối Tuần 6 |
| Người dùng / quyết định | Advisor – D1 liên hệ ai trước |
| Target | `final_result ∈ {Fail, Withdrawn}` |
| Đơn vị dự báo | Sinh viên × presentation |
| Prediction time | Cuối ngày 41 (hết Tuần 6) |
| Observation window | Ngày ≤ 41, có tính hoạt động trước ngày 0 (`include_pre_start: true`) |
| Outcome window | Đến hết presentation |
| Quần thể | Còn theo học tại ngày 41: n train / valid / test = 3.383 / 1.283 / 1.834 |
| Dữ liệu | OULAD, module FFF; train 2013B + 2013J, valid 2014B, test 2014J |
| Feature | 34 feature (`data/processed/feature_list.json`); không có thuộc tính nhạy cảm |
| Kiểm soát leakage | `leakage.py` + test; dữ liệu dùng muộn nhất: VLE ngày 41, hạn nộp ngày 24, ngày nộp 41; bài nộp sau ngày 41 = chưa nộp; loại bài `is_banked` |
| Baseline | Luật: chưa nộp bài đầu tiên hoặc 0 click Tuần 5–6 |
| Mô hình | logistic / gboost; chọn **gboost** theo PR-AUC trên valid (0,777 so với 0,776 của logistic, gần như ngang nhau) |
| Ngưỡng | 0,405 (chọn trên valid: Recall ≥ 0,8, F1 lớn nhất) |
| Kết quả valid | Recall 0,801 · Precision 0,655 · F1 0,721 · PR-AUC 0,777 · ROC-AUC 0,774 |
| Kết quả test | Recall 0,805 · Precision 0,560 · F1 0,661 · PR-AUC 0,745 · ROC-AUC 0,794 |
| Baseline luật (test) | Recall 0,292 · Precision 0,860 · F1 0,435 · PR-AUC 0,528 |
| Đạt tiêu chí? | Recall **đạt** (0,805 ≥ 0,80); F1 **chưa đạt** (0,661 < 0,75) |
| Error analysis | FN = 140 (Withdrawn 75, Fail 65); FN có mức tương tác và điểm cao hơn TP (xem bên dưới) |
| Explainability | Permutation importance (theo PR-AUC) + reason codes. Quan trọng nhất: `mean_score` (0,105), `clicks_w6` (0,023), `mean_days_early` (0,011) |
| Fairness | Chênh lệch Recall lớn nhất: 0,33 theo `highest_education`, nhưng do các nhóm rất nhỏ (xem `docs/04_governance.md`) |
| Giới hạn | OULAD Anh 2013–14, một module STEM; không nhân quả; chỉ 1 bài đánh giá trước mốc; tập test có tỷ lệ rút sớm cao hơn; KG mô phỏng |
| Human oversight | Risk List `pending_review`, cố vấn duyệt từng ca |

## Error analysis (bản nháp)

Nguồn: `reports/false_negative_analysis.csv`, tập test.

| Chỉ báo (trung vị) | Bị bỏ sót (FN, n = 140) | Phát hiện đúng (TP, n = 577) |
|---|---:|---:|
| Tổng click Tuần 1–6 | 757 | 206 |
| Số ngày hoạt động | 29,5 | 13 |
| Thay đổi tương tác (âm = giảm) | −0,01 | −0,42 |
| Số bài chưa nộp | 0 | 0 |
| Điểm TMA1 | 82 | 73 |

**Nhận định:**

1. Đa số sinh viên bị bỏ sót **trông giống nhóm hoàn thành ở Tuần 1–6**: tương tác cao gấp khoảng 3,7 lần nhóm TP, không có dấu hiệu giảm tương tác, đã nộp TMA1 với điểm trung vị 82. Với dữ liệu đến ngày 41, mô hình khó phân biệt nhóm này. Đây là giới hạn của mốc dự báo, không chỉ của thuật toán.
2. 75/140 FN là Withdrawn. Theo AQ1, hơn một nửa số người rút môn rút sau Tuần 6, nên tín hiệu của họ có thể chỉ xuất hiện muộn hơn. Đây là lý do cho AQ8 (rút môn Tuần 7–12) hoặc một mốc kiểm tra thứ hai (ví dụ sau TMA2, ngày 47–52); hiện đang ghi ở phần Limitations.
3. 65/140 FN là Fail, phần lớn đã nộp TMA1 với điểm khá. Khó khăn của họ có thể nằm ở các bài sau hoặc ở Exam, mà dữ liệu Tuần 6 chưa quan sát được.
4. Precision trên test (0,56) thấp hơn trên valid (0,65), một phần vì tỷ lệ y=1 trong quần thể dự báo của test thấp hơn (39% so với 49%; xem `docs/02_data.md`). Ngưỡng **không** được chỉnh lại trên test.

**Hệ quả cho triển khai:** không nên hiểu "không có trong Risk List" là "không cần hỗ trợ". Cần giữ kênh để sinh viên tự tìm hỗ trợ và một tầng "Theo dõi" ở các mốc sau (rủi ro R2).
