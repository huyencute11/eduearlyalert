# Fairness Audit – AQ9 (tự sinh)

Tập test, n = 363. Recall chung = 0.824. Nhóm < 10 sinh viên bị ẩn.

![](figures/aq9_recall_by_group.png)

## Chênh lệch Recall lớn nhất theo thuộc tính

| attribute         |   recall_min |   recall_max |   recall_gap |
|:------------------|-------------:|-------------:|-------------:|
| age_band          |        0.778 |        0.9   |        0.122 |
| disability        |        0.803 |        1     |        0.197 |
| gender            |        0.794 |        0.851 |        0.057 |
| highest_education |        0.81  |        0.836 |        0.027 |
| imd_band          |        0.75  |        0.9   |        0.15  |
| region            |        0.792 |        0.905 |        0.113 |

## Chi tiết

| attribute         | group                 |   n |   prevalence |   selection_rate |   recall |     fnr |   precision | suppressed   |
|:------------------|:----------------------|----:|-------------:|-----------------:|---------:|--------:|------------:|:-------------|
| gender            | F                     | 191 |        0.356 |            0.398 |    0.794 |   0.206 |       0.711 | False        |
| gender            | M                     | 172 |        0.43  |            0.419 |    0.851 |   0.149 |       0.875 | False        |
| region            | London Region         |  75 |        0.4   |            0.387 |    0.8   |   0.2   |       0.828 | False        |
| region            | North Region          |  80 |        0.45  |            0.475 |    0.833 |   0.167 |       0.789 | False        |
| region            | Scotland              |  67 |        0.358 |            0.343 |    0.792 |   0.208 |       0.826 | False        |
| region            | South East Region     |  62 |        0.339 |            0.371 |    0.905 |   0.095 |       0.826 | False        |
| region            | Wales                 |  79 |        0.392 |            0.443 |    0.806 |   0.194 |       0.714 | False        |
| disability        | N                     | 325 |        0.391 |            0.4   |    0.803 |   0.197 |       0.785 | False        |
| disability        | Y                     |  38 |        0.395 |            0.474 |    1     |   0     |       0.833 | False        |
| age_band          | 0-35                  | 258 |        0.349 |            0.357 |    0.778 |   0.222 |       0.761 | False        |
| age_band          | 35-55                 | 100 |        0.5   |            0.53  |    0.9   |   0.1   |       0.849 | False        |
| age_band          | 55<=                  |   5 |      nan     |          nan     |  nan     | nan     |     nan     | True         |
| imd_band          | 0-10%                 |  51 |        0.392 |            0.412 |    0.75  |   0.25  |       0.714 | False        |
| imd_band          | 10-20                 |  42 |        0.381 |            0.357 |    0.75  |   0.25  |       0.8   | False        |
| imd_band          | 20-30%                |  51 |        0.392 |            0.373 |    0.8   |   0.2   |       0.842 | False        |
| imd_band          | 30-40%                |  71 |        0.324 |            0.31  |    0.826 |   0.174 |       0.864 | False        |
| imd_band          | 40-50%                |  61 |        0.328 |            0.459 |    0.9   |   0.1   |       0.643 | False        |
| imd_band          | 50-60%                |  38 |        0.447 |            0.447 |    0.824 |   0.176 |       0.824 | False        |
| imd_band          | Không rõ              |  49 |        0.531 |            0.531 |    0.885 |   0.115 |       0.885 | False        |
| highest_education | A Level or Equivalent | 131 |        0.42  |            0.458 |    0.836 |   0.164 |       0.767 | False        |
| highest_education | HE Qualification      | 117 |        0.359 |            0.359 |    0.81  |   0.19  |       0.81  | False        |
| highest_education | Lower Than A Level    | 115 |        0.391 |            0.4   |    0.822 |   0.178 |       0.804 | False        |

## Nhận định & hành động (nhóm điền)

- Ngưỡng chênh lệch chấp nhận được (thống nhất với stakeholder): TODO
- Nhóm bị bỏ sót nhiều hơn và hành động đề xuất (chấp nhận / điều chỉnh / dừng): TODO