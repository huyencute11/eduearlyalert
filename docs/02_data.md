# 02 · Dữ liệu: nguồn, schema, cohort, feature

## 1. Lấy dữ liệu OULAD

* Trang chính thức: <https://analyse.kmi.open.ac.uk/open_dataset> (CC-BY 4.0)
* Dự phòng: Figshare <https://figshare.com/articles/OULAD_Open_University_Learning_Analytics_Dataset/5081998>
  (cũng có trên UCI ML Repository; tránh bản sao Kaggle không rõ nguồn).
* Tải file zip (~45 MB), kiểm tra MD5 nếu trang có cung cấp, giải nén **7 file CSV** vào `data/raw/`:

```
data/raw/courses.csv            data/raw/studentInfo.csv
data/raw/assessments.csv        data/raw/studentRegistration.csv
data/raw/vle.csv                data/raw/studentAssessment.csv
data/raw/studentVle.csv         (file lớn nhất, ~10,6 triệu dòng)
```

Trích dẫn bắt buộc: Kuzilek J., Hlosta M., Zdrahal Z. *Open University Learning Analytics dataset.*
Sci. Data 4:170171 (2017). doi:10.1038/sdata.2017.171

**Lưu ý quan trọng**

* Giá trị thiếu trong CSV được ghi là `?` → `data_io.py` đọc với `nullstr='?'`.
* Cột `date` (VLE, assessments, registration) tính bằng **số ngày kể từ ngày bắt đầu môn** (ngày 0), có thể âm.
* `B` = bắt đầu tháng 2, `J` = tháng 10. Cấu trúc B và J có thể khác nhau.
* Module CCC, EEE, GGG thiếu lượt trước tương ứng → khó chia train/test theo thời gian.
  Ưu tiên BBB, DDD, FFF (đủ 2013B, 2013J, 2014B, 2014J).
* Bài thi cuối kỳ (`assessment_type = Exam`) có thể thiếu `date` – **không bao giờ** dùng làm feature.
* `is_banked = 1`: điểm chuyển từ lần học trước → loại khỏi feature.

## 2. Chọn module

Chạy `python -m eduearlyalert.pipeline audit`, mở `reports/module_presentation_counts.csv`
và chọn module thoả: đủ 4 presentation, đủ sinh viên, `n_assess_before_cutoff ≥ 1`.
Sửa `config.yaml › scope`, commit kèm lý do. **Chốt một lần cho cả nhóm.**

> **BẢN NHÁP – P1 cần rà.** **Đã chốt: FFF**, train 2013B và 2013J, valid 2014B, test 2014J (PR #2).
> Ban đầu nhóm dự định chọn BBB, nhưng ở BBB 2014J bài TMA đầu kỳ có trọng số 0 và điểm gần như chỉ 1/100,
> khác với ba lượt còn lại. FFF có thiết kế giống nhau ở cả 4 lượt: 1 bài TMA trọng số 12.5,
> hạn ngày 19 (2013) hoặc ngày 24 (2014). Lý do chọn đến từ metadata `assessments.csv`, không dựa trên kết quả test.

## 3. Cohort và nhãn (`cohort.py`)

| Khái niệm | Định nghĩa |
|---|---|
| Đơn vị | 1 dòng = sinh viên × presentation |
| `y = 1` | `final_result ∈ {Fail, Withdrawn}` (không hoàn thành) |
| Quần thể mô tả | Mọi sinh viên đăng ký (AQ1–AQ3) |
| Quần thể dự báo | Còn theo học tại `cutoff_day = 41`: loại người có `date_unregistration ≤ 41` hoặc đăng ký sau ngày 41 |
| `split` | train / valid / test theo presentation (`config.yaml › scope.presentations`) |
| `pid` | SHA-256(salt + id_student), 10 ký tự hex, tiền tố `S` |

`reports/cohort_flow.csv` ghi số dòng bị loại ở từng bước – đưa vào phần Data Quality của report.

**Cohort FFF** (số liệu chép từ `reports/cohort_flow.csv` ngày 11/11/2026; chạy lại pipeline thì đối chiếu lại):

| Lượt | Split | Đăng ký | Rút trước ngày 41 | Đăng ký sau ngày 41 | Quần thể dự báo | Tỷ lệ y=1 (toàn bộ) | Tỷ lệ y=1 (quần thể dự báo) |
|---|---|---:|---:|---:|---:|---:|---:|
| 2013B | train | 1.614 | 181 | 0 | 1.433 | 51,5% | 45,4% |
| 2013J | train | 2.283 | 333 | 0 | 1.950 | 52,0% | 43,8% |
| 2014B | valid | 1.500 | 217 | 0 | 1.283 | 56,4% | 49,0% |
| 2014J | test | 2.365 | 530 | 1 | 1.834 | 52,8% | 39,1% |

Tập test (2014J) có nhiều người rút trước ngày 41 nhất (22%). Vì vậy tỷ lệ y=1 trong quần thể dự báo
của test thấp hơn các tập khác. Điều này ảnh hưởng tới precision và F1 trên test (xem rủi ro R11).

## 4. Data dictionary – feature (`features.py`)

Mọi feature chỉ dùng dữ liệu có ngày ≤ 41. Tuần: `date < 0 → 0`, `0..6 → 1`, …, `35..41 → 6`.

| Feature | Ý nghĩa | Nguồn | AQ |
|---|---|---|---|
| `clicks_pre_start` | Tổng click trước ngày 0 | studentVle | AQ2, AQ4 |
| `clicks_w1` … `clicks_w6` | Click từng tuần | studentVle | AQ2, AQ4 |
| `clicks_total` | Tổng click Tuần 1–6 | studentVle | AQ4 |
| `active_days_total` | Số ngày có hoạt động (gồm trước ngày 0 nếu `include_pre_start`) | studentVle | AQ4 |
| `inactive_weeks` | Số tuần (1–6) không có click | studentVle | AQ4 |
| `clicks_early`, `clicks_late` | Click Tuần 1–3, Tuần 4–6 | studentVle | AQ4 |
| `engagement_change` | log(1+late) − log(1+early); âm = giảm | studentVle | AQ4, AQ10 |
| `share_<activity>` | Tỷ trọng click theo loại tài nguyên | studentVle + vle | AQ2 |
| `n_assess_due` | Số bài (không tính Exam) có hạn ≤ 41 | assessments | AQ3 |
| `n_on_time`, `n_late`, `n_missing` | Đếm theo trạng thái tại ngày 41 | studentAssessment | AQ3, AQ5 |
| `share_missing` | `n_missing / n_assess_due` | – | AQ5, AQ10 |
| `mean_score`, `min_score` | Điểm các bài đã nộp | studentAssessment | AQ5 |
| `weighted_score_so_far` | Điểm có trọng số, bài thiếu = 0 | studentAssessment | AQ5 |
| `first_assess_score`, `first_assess_missing` | Bài có hạn sớm nhất | studentAssessment | AQ5 |
| `mean_days_early` | Hạn nộp − ngày nộp (TB) | studentAssessment | AQ5 |
| `reg_days_before_start` | Đăng ký trước bao nhiêu ngày | studentRegistration | – |
| `num_of_prev_attempts`, `studied_credits` | Số lần học lại, tín chỉ đang học | studentInfo | – |

**Không bao giờ là feature** (kiểm tra tự động trong `leakage.py`): `final_result`, `y`,
`date_unregistration`, `module_presentation_length`, `id_student`, và thuộc tính nhạy cảm
`gender, region, disability, age_band, imd_band, highest_education`.

## 5. Dữ liệu mô phỏng

`kg/concepts.yaml` và `kg/concept_map.csv` do nhóm tự xây dựng. Khoá ánh xạ là
`assessment_key` (TMA1, CMA2… theo thứ tự hạn nộp), nên một bảng dùng cho mọi presentation.
Sau khi chọn module, mở `reports/kg_competency_questions.md` để xem bài nào chưa được ánh xạ.

## 6. Data Inventory

> **BẢN NHÁP – P1 cần rà.**

| Nguồn | Nội dung | Format · kích thước | Owner | Thời gian | Truy cập | Rủi ro |
|---|---|---|---|---|---|---|
| OULAD `studentInfo` | Nhân khẩu, kết quả cuối kỳ (`final_result`) | CSV · 32.593 dòng | Open University (KMi); trong nhóm: P1 | 2013–2014 (4 lượt FFF) | Công khai, CC-BY 4.0 | Thuộc tính nhạy cảm (chỉ cho AQ9); `final_result` là nhãn, không phải feature |
| OULAD `studentRegistration` | Ngày đăng ký và ngày rút môn | CSV · 32.593 dòng | như trên | như trên | như trên | `date_unregistration` gây leakage nếu dùng làm feature |
| OULAD `courses` | Module × lượt, độ dài lượt | CSV · 22 dòng | như trên | như trên | như trên | `module_presentation_length` là thông tin tương lai |
| OULAD `assessments` | Bài đánh giá, hạn nộp, trọng số | CSV · 206 dòng | như trên | như trên | như trên | Thiết kế bài khác nhau giữa các lượt (Q1); Exam không có `date` |
| OULAD `studentAssessment` | Ngày nộp, điểm, `is_banked` | CSV · 173.912 dòng | như trên | như trên | như trên | Bài banked; điểm thiếu |
| OULAD `vle` | Tài nguyên VLE và loại hoạt động | CSV · 6.364 dòng | như trên | như trên | như trên | `week_from/to` phần lớn bị thiếu |
| OULAD `studentVle` | Click theo ngày × tài nguyên | CSV · 10.655.280 dòng (~430 MB) | như trên | như trên | như trên | Không có khoá duy nhất; đuôi click rất dài |
| `kg/concepts.yaml`, `kg/concept_map.csv` | Concept, CLO, ánh xạ bài → concept | YAML/CSV · vài chục dòng | Nhóm 3 (P3) | 11/2026 | Trong repo | **MÔ PHỎNG**, không phải chương trình thật; concept thiên về KHXH trong khi FFF là môn STEM |
| `data/raw/_fake_backup/`, `scripts/make_fake_oulad.py` | Dữ liệu giả cùng schema để test | CSV | Nhóm 3 | – | Trong repo (script) | Không dùng cho báo cáo |

Dữ liệu thô (`data/`) không bao giờ được commit. `id_student` được thay bằng `pid` (SHA-256 + `EDU_SALT`)
trước khi ghi ra `data/processed/` và `reports/`.
