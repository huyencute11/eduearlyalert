# Data Quality Report (tự sinh)

> Sinh bởi `python -m eduearlyalert.pipeline audit`. Không sửa tay – sửa code rồi chạy lại.
> Phần **Nhận định & xử lý** ở cuối do nhóm viết.

## 1. Kích thước bảng và khoá trùng

| table               |   n_rows |   duplicate_keys |
|:--------------------|---------:|-----------------:|
| courses             |        6 |                0 |
| assessments         |       48 |                0 |
| vle                 |      170 |                0 |
| studentInfo         |     1800 |                0 |
| studentRegistration |     1800 |                0 |
| studentAssessment   |     7918 |                0 |
| studentVle          |   328208 |              nan |

## 2. Giá trị thiếu (chỉ cột có thiếu)

| table               | column              |   missing |   missing_pct |
|:--------------------|:--------------------|----------:|--------------:|
| assessments         | date                |         6 |         12.5  |
| vle                 | week_from           |       170 |        100    |
| vle                 | week_to             |       170 |        100    |
| studentInfo         | imd_band            |       245 |         13.61 |
| studentRegistration | date_unregistration |      1328 |         73.78 |
| studentAssessment   | score               |        67 |          0.85 |

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
| studentVle.sum_click    |    1 |     5 |    13 |   23 |
| studentAssessment.score |    0 |    72 |   100 |  100 |
| studentVle.date         |  -10 |   121 |   262 |  268 |

## 5. Module × presentation (để chọn phạm vi)

Module đang cấu hình: **BBB**, presentations: ['2013B', '2013J', '2014B', '2014J']. `n_assess_before_cutoff` = số bài đánh giá (không tính Exam) có hạn ≤ ngày 41; nếu = 0 thì AQ3, AQ5, AQ6 sẽ không có dữ liệu.

| code_module   | code_presentation   |   n_students |   completion_rate |   withdrawn_rate |   n_assess_before_cutoff |
|:--------------|:--------------------|-------------:|------------------:|-----------------:|-------------------------:|
| BBB           | 2013B               |          400 |             0.493 |            0.288 |                        3 |
| BBB           | 2013J               |          400 |             0.545 |            0.22  |                        3 |
| BBB           | 2014B               |          400 |             0.473 |            0.275 |                        3 |
| BBB           | 2014J               |          400 |             0.553 |            0.253 |                        3 |
| DDD           | 2013J               |          100 |             0.45  |            0.31  |                        3 |
| DDD           | 2014J               |          100 |             0.51  |            0.27  |                        3 |

## 6. Nhận định & xử lý (nhóm điền)

| Vấn đề | Bằng chứng (mục nào ở trên) | Quyết định xử lý | Ảnh hưởng tới AQ |
|---|---|---|---|
| TODO | | | |
