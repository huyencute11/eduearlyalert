# Data Quality Report (tự sinh)

> Sinh bởi `python -m eduearlyalert.pipeline audit`. Không sửa tay – sửa code rồi chạy lại.
> Phần **Nhận định & xử lý** ở cuối do nhóm viết.

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

| Vấn đề | Bằng chứng (mục nào ở trên) | Quyết định xử lý | Ảnh hưởng tới AQ |
|---|---|---|---|
| TODO | | | |
