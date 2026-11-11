<!--
File này được ghép tự động vào mục 6 của reports/data_quality_report.md mỗi lần chạy `pipeline audit`.
Viết ở đây, KHÔNG sửa trong reports/. Comment HTML như thế này bị bỏ qua khi ghép.
Số liệu lấy từ OULAD thật, phạm vi module FFF (4 lượt), trừ khi ghi "toàn bộ OULAD".
-->
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
