# OULAD – schema và bẫy dữ liệu

Nguồn: https://analyse.kmi.open.ac.uk/open_dataset · Kuzilek et al. (2017), Sci. Data 4:170171.
Giá trị thiếu ghi bằng `?`. Mọi cột `date` = số ngày tính từ ngày bắt đầu presentation (ngày 0).

| Bảng | Khoá | Cột chính | Ghi chú |
|---|---|---|---|
| courses | code_module, code_presentation | module_presentation_length | độ dài (ngày) |
| assessments | id_assessment | code_module, code_presentation, assessment_type (TMA/CMA/Exam), date (hạn nộp), weight | Exam có thể thiếu date; Exam weight = 100 riêng |
| vle | id_site | code_module, code_presentation, activity_type, week_from, week_to | week_from/to thường thiếu |
| studentInfo | code_module, code_presentation, id_student | gender, region, highest_education, imd_band, age_band, num_of_prev_attempts, studied_credits, disability, final_result | final_result ∈ {Pass, Distinction, Fail, Withdrawn} |
| studentRegistration | code_module, code_presentation, id_student | date_registration, date_unregistration | unregistration rỗng = không rút |
| studentAssessment | id_assessment, id_student | date_submitted, is_banked, score | score có thể thiếu; is_banked=1 là điểm chuyển |
| studentVle | (không khoá) | code_module, code_presentation, id_student, id_site, date, sum_click | ~10,6 triệu dòng – dùng DuckDB |

## Bẫy

* `B` (tháng 2) và `J` (tháng 10) có thể khác cấu trúc; nên so sánh cùng loại khi có thể.
* CCC, EEE, GGG thiếu lượt trước tương ứng – khó chia theo thời gian.
* Một sinh viên có thể học nhiều module/presentation → đơn vị phân tích là sinh viên × presentation.
* Bài nộp **sau** ngày 41 không được thấy tại mốc dự báo → coi là chưa nộp.
* `date_unregistration` ≤ 41 → loại khỏi quần thể dự báo (đã rút).
* `highest_education`, `imd_band` là thông tin kinh tế–xã hội → coi là nhạy cảm (chỉ audit).
* Lớp không cân bằng; tỷ lệ hoàn thành khác nhau nhiều giữa module → baseline 60% trong proposal
  phải cập nhật theo AQ1.
