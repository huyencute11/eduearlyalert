# 03 · Pipeline: từng bước làm gì, ra gì, ai phụ trách

```
data/raw ─► audit ─► cohort ─► features ─► kg ─► eda
                                   │                 
                                   └─► model ─► explain ─► fairness ─► prioritize ─► dashboard
```

Chạy tất cả: `python -m eduearlyalert.pipeline all`. Chạy lẻ: `... pipeline model explain`.
Mỗi bước đọc output của bước trước từ đĩa, nên có thể chạy lại riêng một bước.

| # | Bước | GĐ | AQ | Input | Output chính | Lead |
|---|---|---|---|---|---|---|
| 1 | `audit` | GĐ3 | – | `data/raw/*.csv` | `data_quality_report.md`, `data_dictionary_auto.csv`, `module_presentation_counts.csv` | Problem & Data |
| 2 | `cohort` | GĐ3 | – | DuckDB | `interim/cohort.parquet`, `interim/sensitive.parquet`, `cohort_flow.csv` | Problem & Data |
| 3 | `features` | GĐ3–5 | – | cohort + DuckDB | `processed/features.parquet`, `feature_list.json` (+ leakage check) | Problem & Data / Modeling |
| 4 | `kg` | GĐ6 | AQ6 | `kg/`, `assess_long` | `kg_triples.csv`, `kg_competency_questions.md`, `concept_gaps.parquet` | Modeling/KG |
| 5 | `eda` | GĐ4 | AQ1–6 | features, weekly, gaps | `figures/aq1..6_*.png`, `eda_findings.md` | Analytics/EDA |
| 6 | `model` | GĐ5 | AQ7 | features | `model_results.md`, `model_metrics.json`, `predictions.parquet` | Modeling |
| 7 | `explain` | GĐ6 | AQ7, AQ11 | model + features | `explainability_report.md`, `reason_codes.parquet` | Modeling |
| 8 | `fairness` | GĐ8 | AQ9 | predictions + sensitive | `fairness_report.md`, `fairness_by_group.csv` | Eval & Governance |
| 9 | `prioritize` | GĐ8 | AQ10–12 | predictions + reasons + KG | `prioritization_report.md`, `risk_list.csv` | Eval & Governance |
| 10 | dashboard | GĐ10 | demo | `reports/` | `app/dashboard.py` | Report & Presentation |

## Chi tiết các quyết định thiết kế

**Chia dữ liệu theo thời gian.** Train trên presentation cũ, valid để chọn ngưỡng và chọn
mô hình, test chỉ dùng một lần ở cuối. EDA cũng chỉ chạy trên train + valid để không
"nhìn trộm" test. Không random split.

**Mô hình theo bậc.** `rule` (chưa nộp bài đầu tiên hoặc 0 click Tuần 5–6) → `logistic`
(impute median + chuẩn hoá + class_weight balanced) → `gboost` (HistGradientBoosting).
Mô hình chính được chọn theo PR-AUC trên valid. Ngưỡng: F1 cao nhất trong các ngưỡng có
Recall valid ≥ 0.80.

**Nếu không đạt tiêu chí chấp nhận**: báo cáo trung thực, đọc `false_negative_analysis.csv`
(ai bị bỏ sót – thường là người rút muộn nhưng tích cực đến Tuần 6). Không chỉnh ngưỡng trên test.

**Reason codes** là luật minh bạch, ngưỡng lấy từ phân vị tập train, sắp theo permutation
importance. Đây là tín hiệu dữ liệu, không phải nguyên nhân.

**Ưu tiên (AQ10)**: ba phương án A (chỉ risk), B (risk 70% + sụt tương tác 30%),
C (risk 70% + tỷ lệ bài chưa nộp 30%), so sánh bằng Coverage@K và Precision@K với
K = `k_per_advisor × n_advisors`.

## Thêm một bước / feature mới

1. Viết hàm trong module phù hợp (hoặc module mới) với hàm `run(cfg)`.
2. Đăng ký trong `pipeline.STEPS` nếu là bước mới.
3. Feature mới → thêm vào `features.model_feature_columns` **và** bảng ở `docs/02_data.md`.
4. Thêm test trong `tests/`. Chạy `pytest` trước khi mở PR.

## Mở rộng (nếu còn thời gian)

* AQ8: dự báo rút môn Tuần 7–12 (nhãn từ `date_unregistration ∈ (41, 83]`).
* Độ nhạy theo mốc dự báo: chạy lại với `cutoff_day = 27` (Tuần 4) theo đề nghị của Advisor.
* SHAP beeswarm trong notebook; clustering hành vi (Exploratory).
* LLM soạn giải thích từ `reason_codes` – read-only, có duyệt, không sinh số liệu.
