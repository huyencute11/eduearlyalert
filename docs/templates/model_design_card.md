# Model Design Card – AQ7 (GĐ5)

> Điền từ `reports/model_results.md`, `reports/model_metrics.json`, `config.yaml`.

| Mục | Nội dung |
|---|---|
| Câu hỏi | AQ7 – ước lượng xác suất không hoàn thành tại cuối Tuần 6 |
| Người dùng / quyết định | Advisor – D1 liên hệ ai trước |
| Target | `final_result ∈ {Fail, Withdrawn}` |
| Đơn vị dự báo | Sinh viên × presentation |
| Prediction time | Cuối ngày 41 (hết Tuần 6) |
| Observation window | Ngày ≤ 41 (gồm trước ngày 0: có/không) |
| Outcome window | Đến hết presentation |
| Quần thể | Còn theo học tại ngày 41 – n train / valid / test = … |
| Dữ liệu | OULAD, module …, presentations … |
| Feature | xem `feature_list.json` (… feature); không thuộc tính nhạy cảm |
| Kiểm soát leakage | `leakage.py` + test; bài nộp sau ngày 41 = chưa nộp |
| Baseline | Luật: chưa nộp bài đầu tiên hoặc 0 click Tuần 5–6 |
| Mô hình | logistic / gboost – chọn … theo PR-AUC valid |
| Ngưỡng | … (chọn trên valid: Recall ≥ 0.8, F1 max) |
| Kết quả test | Recall … · Precision … · F1 … · PR-AUC … · ROC-AUC … |
| Đạt tiêu chí? | Recall …, F1 … |
| Error analysis | FN = … (Withdrawn …, Fail …); đặc điểm: … |
| Explainability | Permutation importance + reason codes |
| Fairness | Chênh lệch Recall lớn nhất: … theo … |
| Giới hạn | OULAD Anh 2013–14; không nhân quả; … |
| Human oversight | Risk List `pending_review`, cố vấn duyệt từng ca |
