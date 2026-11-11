# Data Quality Report (tự sinh)

> Sinh bởi `python -m eduearlyalert.pipeline audit`. Không sửa tay – sửa code rồi chạy lại.
> Phần **Nhận định & xử lý** ở cuối do nhóm viết trong `docs/data_quality_notes.md`.

## 1. Kích thước bảng và khoá trùng

| table               |   n_rows |   duplicate_keys |
|:--------------------|---------:|-----------------:|
| courses             |       22 |                0 |
| assessments         |      206 |                0 |
| vle                 |     6364 |                0 |
| studentInfo         |    32593 |                0 |
| studentRegistration |    32593 |                0 |
| studentAssessment   |   173912 |                0 |
| studentVle          | 10655280 |              nan |

## 2. Giá trị thiếu (chỉ cột có thiếu)

| table               | column              |   missing |   missing_pct |
|:--------------------|:--------------------|----------:|--------------:|
| assessments         | date                |        11 |          5.34 |
| vle                 | week_from           |      5243 |         82.39 |
| vle                 | week_to             |      5243 |         82.39 |
| studentInfo         | imd_band            |      1111 |          3.41 |
| studentRegistration | date_registration   |        45 |          0.14 |
| studentRegistration | date_unregistration |     22521 |         69.1  |
| studentAssessment   | score               |       173 |          0.1  |

## 3. Toàn vẹn tham chiếu (orphan rows)

| child               | parent      | keys                                     |   orphans |
|:--------------------|:------------|:-----------------------------------------|----------:|
| studentAssessment   | assessments | id_assessment                            |         0 |
| studentVle          | vle         | id_site                                  |         0 |
| studentVle          | studentInfo | code_module,code_presentation,id_student |         0 |
| studentRegistration | studentInfo | code_module,code_presentation,id_student |         0 |

## 4. Phân bố các trường số chính

| field                   |   mn |   p50 |   p99 |   mx |
|:------------------------|-----:|------:|------:|-----:|
| studentVle.sum_click    |    1 |     2 |    34 | 6977 |
| studentAssessment.score |    0 |    80 |   100 |  100 |
| studentVle.date         |  -25 |    86 |   240 |  269 |

## 5. Module × presentation (để chọn phạm vi)

Module đang cấu hình: **FFF**, presentations: ['2013B', '2013J', '2014B', '2014J']. `n_assess_before_cutoff` = số bài đánh giá (không tính Exam) có hạn ≤ ngày 41; nếu = 0 thì AQ3, AQ5, AQ6 sẽ không có dữ liệu.

| code_module   | code_presentation   |   n_students |   completion_rate |   withdrawn_rate |   n_assess_before_cutoff |
|:--------------|:--------------------|-------------:|------------------:|-----------------:|-------------------------:|
| AAA           | 2013J               |          383 |             0.726 |            0.157 |                        1 |
| AAA           | 2014J               |          365 |             0.693 |            0.181 |                        1 |
| BBB           | 2013B               |         1767 |             0.454 |            0.286 |                        1 |
| BBB           | 2013J               |         2237 |             0.479 |            0.288 |                        1 |
| BBB           | 2014B               |         1613 |             0.451 |            0.304 |                        2 |
| BBB           | 2014J               |         2292 |             0.503 |            0.327 |                        1 |
| CCC           | 2014B               |         1936 |             0.342 |            0.464 |                        2 |
| CCC           | 2014J               |         2498 |             0.406 |            0.431 |                        2 |
| DDD           | 2013B               |         1303 |             0.391 |            0.332 |                        2 |
| DDD           | 2013J               |         1938 |             0.428 |            0.351 |                        1 |
| DDD           | 2014B               |         1228 |             0.39  |            0.399 |                        1 |
| DDD           | 2014J               |         1803 |             0.439 |            0.359 |                        2 |
| EEE           | 2013J               |         1052 |             0.579 |            0.231 |                        1 |
| EEE           | 2014B               |          694 |             0.514 |            0.249 |                        1 |
| EEE           | 2014J               |         1188 |             0.576 |            0.258 |                        1 |
| FFF           | 2013B               |         1614 |             0.485 |            0.255 |                        1 |
| FFF           | 2013J               |         2283 |             0.48  |            0.296 |                        1 |
| FFF           | 2014B               |         1500 |             0.436 |            0.308 |                        1 |
| FFF           | 2014J               |         2365 |             0.472 |            0.362 |                        1 |
| GGG           | 2013J               |          952 |             0.622 |            0.069 |                        0 |
| GGG           | 2014B               |          833 |             0.574 |            0.12  |                        0 |
| GGG           | 2014J               |          749 |             0.593 |            0.168 |                        0 |

## 6. Nhận định & xử lý (nhóm điền)

> Ghép từ `docs/data_quality_notes.md` (nhóm viết).

> **BẢN NHÁP – P1 cần rà và sửa.** Claude soạn ngày 11/11/2026 từ `reports/` và truy vấn DuckDB trên module FFF.

| # | Vấn đề | Bằng chứng | Quyết định xử lý | Ảnh hưởng tới AQ |
|---|---|---|---|---|
| Q1 | Thiết kế bài đánh giá khác nhau giữa các lượt: ở BBB 2014J, bài TMA đầu kỳ có trọng số 0 và điểm gần như chỉ 1 hoặc 100; ba lượt còn lại có trọng số 5 và điểm 0–100 | Mục 5; `assessments.csv` | Chọn FFF: cả 4 lượt có 1 bài TMA trọng số 12.5 trước ngày 41. Quyết định dựa trên metadata, không dựa trên kết quả test | Mọi AQ; xem rủi ro R10 |
| Q2 | `studentVle` không có khoá duy nhất: FFF có 540.673 tổ hợp (sinh viên × tài nguyên × ngày) xuất hiện nhiều hơn 1 dòng | Mục 1 (`duplicate_keys = nan`) | Giữ nguyên, không xoá trùng; mọi feature đều cộng `sum_click`, nên nhiều dòng tương ứng nhiều lần truy cập | AQ2, AQ4, feature VLE |
| Q3 | Click trước ngày bắt đầu: FFF có 256.062 dòng `date < 0` | Mục 4 (`studentVle.date` min −25) | Gán vào tuần 0, tính trong `clicks_pre_start`; `include_pre_start: true` | AQ2, AQ4 |
| Q4 | `sum_click` có đuôi rất dài: lớn nhất 4.098 ở FFF (6.977 trên toàn bộ OULAD), trong khi phân vị 99,9% là 102 | Mục 4 | Giữ nguyên, không cắt ngưỡng. Mô hình gboost ít nhạy với outlier; với logistic, nên thử log-transform (việc tiếp theo) | AQ4, AQ7 |
| Q5 | `imd_band` thiếu 367/7.762 dòng FFF (4,7%) | Mục 2 | Chỉ dùng trong audit fairness; giá trị thiếu thành nhóm "Không rõ" | AQ9 |
| Q6 | `date_registration` thiếu 11 dòng FFF | Mục 2 | Không bị coi là "đăng ký sau ngày 41". Ở mô hình, `reg_days_before_start` được điền bằng trung vị kèm cột chỉ báo thiếu | AQ7 |
| Q7 | `date_unregistration` thiếu 69% (toàn bộ OULAD) | Mục 2 | Thiếu nghĩa là chưa rút môn. Chỉ dùng để lọc quần thể dự báo (rút trước ngày 41), không bao giờ là feature (leakage) | AQ1, AQ7 |
| Q8 | `score` thiếu 46 bài đã nộp (FFF) | Mục 2 | `mean_score` bỏ qua giá trị thiếu; `weighted_score_so_far` tính bài thiếu là 0 | AQ3, AQ5 |
| Q9 | Bài chuyển điểm từ lần học trước (`is_banked = 1`): 620 dòng FFF | `studentAssessment` | Loại khỏi mọi feature | AQ3, AQ5 |
| Q10 | `vle.week_from/week_to` thiếu 1.141/1.967 tài nguyên FFF (58%) | Mục 2 | Không dùng; tuần được tính từ `studentVle.date` | AQ2 |
| Q11 | Bài Exam không có `date` | Mục 2 (`assessments.date` thiếu 11) | Không bao giờ dùng Exam làm feature | – |
| Q12 | 1 sinh viên lượt 2014J đăng ký sau ngày 41 | `reports/cohort_flow.csv` | Loại khỏi quần thể dự báo | AQ7 |
