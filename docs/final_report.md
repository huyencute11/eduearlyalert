# Final Project Report – EduEarlyAlert

<!--
Khung theo "Milestone P5 – Final Integration & Project Report" (MTH045). Cấu trúc: Abstract, mục 1–14,
Traceability Matrix (bắt buộc), AQ Revision Log, bảng trả lời theo AQ, AI Decision Log, phụ lục.
Độ dài phần chính: 15–25 trang. Xuất DOCX/PDF: pandoc docs/final_report.md -o final_report.docx

QUY TẮC VIẾT (từ P5 + CLAUDE.md):
- Viết lại thành MỘT câu chuyện; không dán nguyên 4 milestone.
- Mọi con số lấy từ reports/ (ghi file nguồn). Không gõ tay số không có nguồn.
- Thiếu evidence thì ghi GAP / N.A. và giải thích; không bịa cho đủ bảng.
- Diagnostic = liên hệ/khác biệt, không nhân quả. Prescriptive = phương án cần kiểm chứng.
- KG là dữ liệu MÔ PHỎNG; 60%, 68%, K = 35 là giả định.
- Không "sinh viên yếu/kém/lười".
-->

> **BẢN NHÁP – P2 gom và chịu trách nhiệm cuối.** Claude dựng khung và điền nháp các bảng bắt buộc
> ngày 11/11/2026 từ `reports/` (OULAD thật, module FFF). Mỗi mục ghi người viết đề xuất; nhóm có thể đổi.

| Thông tin nhóm | Nội dung |
|---|---|
| Tên nhóm | Nhóm 3 |
| Thành viên | _[P1, P2, P3, P4 – điền tên]_ |
| Project title cuối cùng | EduEarlyAlert – Cảnh báo sớm và ưu tiên hỗ trợ sinh viên có nguy cơ không hoàn thành môn học |
| Dataset / version cuối cùng | OULAD (Kuzilek et al., 2017), bản UCI ML Repository #349, CC-BY 4.0; module FFF, 4 lượt 2013B–2014J |
| Milestone 4 status | ☑ Level 1 bắt buộc · ☑ Level 2 có thử nghiệm (pipeline chạy được, có kết quả thật) |
| Ngày nộp | _[__/__/____]_ |

---

## Abstract / Executive Summary

<!-- P2 · viết SAU CÙNG · 150–250 từ · không đưa chi tiết không có trong report.
Phải có: problem; data; final AQ; analysis đã làm; key result; educational value; limitations.
Key result nên dùng: Recall test 0.805 (đạt), F1 0.661 (chưa đạt), baseline completion 46.9%. -->

_[Chưa viết]_

## 1. Introduction & Educational Context

<!-- P2 · nguồn M1 · bối cảnh blended learning; motivation; stakeholders; phạm vi; objective.
Evidence: docs/01_project_overview.md (Problem statement, Stakeholders). Không kể lại transcript stakeholder. -->

_[Chưa viết]_

## 2. Business Understanding & Success Criteria

<!-- P2 · nguồn M1 · Business Goal; SMART; Primary/Secondary KPI; decision needs (D1–D3).
Evidence: docs/01_project_overview.md. CẦN CHỐT: baseline thật 46.9% thay cho giả định 60% → mục tiêu 68% phải sửa
(vẫn ghi là assumption). Phân biệt KPI tổ chức với tiêu chí chấp nhận mô hình (Recall ≥ 0.80, F1 ≥ 0.75). -->

_[Chưa viết]_

## 3. Analytical Questions & Analytics Levels

<!-- P2 + P3 · nguồn M1 + M3 · danh sách AQ cuối + level + decision. Dùng bảng Traceability (cuối report)
và AQ Revision Log; ở đây chỉ trình bày ladder và AQ quality check (Clear, Specific, Scoped, Data-oriented, Answerable). -->

_[Chưa viết]_

## 4. Data Requirements & Dataset Selection

> **BẢN NHÁP – P1 cần rà và sửa.** Claude viết ngày 11/11/2026 từ `docs/02_data.md`, `docs/data_quality_notes.md`,
> `reports/` và truy vấn trên OULAD thật (FFF).

Để trả lời các AQ ở mục 3 cho quyết định D1–D3, dữ liệu cần thoả bốn yêu cầu (Bảng 4.1). Thứ nhất, có **kết quả cuối
môn** của từng sinh viên để làm nhãn. Thứ hai, có **dấu vết hành vi theo thời gian** (tương tác, nộp bài, điểm),
đủ chi tiết để chỉ lấy phần xảy ra trước mốc dự báo. Thứ ba, có **nhiều lượt giảng dạy** để chia train/valid/test theo
thời gian. Thứ tư, có thuộc tính nhân khẩu học **chỉ để kiểm tra công bằng**.

**Bảng 4.1 – Data Requirement Matrix (rút gọn).**

| Yêu cầu | Phục vụ AQ | Đơn vị / độ chi tiết | Trường dữ liệu OULAD | Mức đáp ứng |
|---|---|---|---|---|
| Kết quả cuối môn | AQ1, AQ4–AQ7, AQ9–AQ12 | Sinh viên × lượt | `studentInfo.final_result` | Đủ |
| Thời điểm rút môn | AQ1, AQ8, lọc quần thể | Ngày | `studentRegistration.date_unregistration` | Đủ (chỉ dùng để lọc, không làm feature) |
| Tương tác học tập theo thời gian | AQ2, AQ4, AQ7 | Ngày × tài nguyên | `studentVle.sum_click`, `vle.activity_type` | Đủ |
| Nộp bài và điểm các bài đầu kỳ | AQ3, AQ5, AQ7 | Bài đánh giá | `assessments`, `studentAssessment` | Một phần: FFF chỉ có 1 bài trước ngày 41 |
| Nội dung/kiến thức của bài đánh giá | AQ6, AQ11 | Concept, CLO | Không có | **GAP** → dùng KG mô phỏng |
| Nhiều lượt giảng dạy | Chia theo thời gian | Lượt | `code_presentation` | Đủ (4 lượt) |
| Thuộc tính nhạy cảm (chỉ audit) | AQ9 | Sinh viên | `gender, region, disability, age_band, imd_band, highest_education` | Đủ |
| Hiệu quả của can thiệp | AQ10–AQ12 (kiểm chứng) | Liên hệ × kết quả | Không có | **GAP**: chỉ đánh giá được trên dữ liệu lịch sử |

**Lựa chọn dataset.** Nhóm chọn **Open University Learning Analytics Dataset (OULAD)** (Kuzilek et al., 2017). Đây là
dataset công khai, giấy phép CC-BY 4.0, và đã ẩn danh. OULAD là một trong số ít dataset mở có đồng thời ba thứ:
click VLE theo ngày, lịch sử nộp bài kèm điểm, và kết quả cuối môn cho nhiều lượt của cùng một môn. Nhờ đó dữ liệu
đáp ứng cả bốn yêu cầu trên. Phiên bản dùng trong report là bản trên UCI Machine Learning Repository (#349),
tải ngày 11/11/2026: một file zip 46,7 MB gồm 7 file CSV.

> **GAP – lấy từ báo cáo M2:** Dataset Selection Matrix so sánh các dataset ứng viên, kèm search log.
> Không có trong repo, nên nhóm cần chép lại từ M2 (không viết lại theo trí nhớ).

## 5. Dataset Description & Requirement–Data Fit

> **BẢN NHÁP – P1 cần rà và sửa.**

**Cấu trúc.** OULAD gồm 7 bảng, nối với nhau qua khoá `(code_module, code_presentation, id_student)`,
`id_assessment` và `id_site` (Bảng 5.1). Mô tả đầy đủ từng cột nằm ở Data Dictionary (Phụ lục A).

**Bảng 5.1 – Các bảng OULAD** (nguồn: `reports/data_quality_report.md` mục 1).

| Bảng | Số dòng (toàn bộ OULAD) | Khoá | Nội dung |
|---|---:|---|---|
| `courses` | 22 | module, lượt | Độ dài từng lượt |
| `assessments` | 206 | `id_assessment` | Loại bài (TMA, CMA, Exam), hạn nộp, trọng số |
| `vle` | 6.364 | `id_site` | Tài nguyên VLE, loại hoạt động |
| `studentInfo` | 32.593 | module, lượt, `id_student` | Nhân khẩu học, `final_result` |
| `studentRegistration` | 32.593 | module, lượt, `id_student` | Ngày đăng ký, ngày rút |
| `studentAssessment` | 173.912 | `id_assessment`, `id_student` | Ngày nộp, điểm, `is_banked` |
| `studentVle` | 10.655.280 | không có khoá duy nhất | Click theo ngày × tài nguyên |

**Phạm vi cuối: module FFF, 4 lượt.** Ban đầu nhóm định dùng BBB. Khi chạy bước audit trên dữ liệu thật, nhóm thấy
ở BBB 2014J (lượt dự định làm test) bài TMA đầu kỳ có trọng số 0 và điểm gần như chỉ 1 hoặc 100, trong khi ba lượt còn
lại có trọng số 5 và điểm 0–100. Nếu giữ BBB, mô hình sẽ được đánh giá trên một lượt có cách chấm bài khác. FFF có thiết
kế giống nhau ở cả 4 lượt: một bài TMA trọng số 12,5, hạn ngày 19 (2013) hoặc ngày 24 (2014). Quyết định này dựa trên
metadata `assessments.csv` (xem Q1, mục 6). FFF có 7.762 lượt đăng ký của 7.397 sinh viên (Bảng 5.2).

**Bảng 5.2 – Lượt giảng dạy của FFF** (nguồn: `reports/module_presentation_counts.csv`, `reports/cohort_flow.csv`).

| Lượt | Vai trò | Sinh viên đăng ký | Tỷ lệ hoàn thành | Tỷ lệ rút môn |
|---|---|---:|---:|---:|
| 2013B | train | 1.614 | 48,5% | 25,5% |
| 2013J | train | 2.283 | 48,0% | 29,6% |
| 2014B | valid | 1.500 | 43,6% | 30,8% |
| 2014J | test | 2.365 | 47,2% | 36,2% |

**Bảng 5.3 – AQ–Data Fit Matrix.**

| AQ | Dữ liệu thực tế | Độ phù hợp | Trạng thái |
|---|---|---|---|
| AQ1 | `final_result`, `date_unregistration` | Đầy đủ | Keep |
| AQ2 | `studentVle`, `vle` | Đầy đủ; click chỉ là proxy của việc học | Keep |
| AQ3 | `assessments`, `studentAssessment` | Chỉ 1 bài (TMA1) trước ngày 41 | Modify (chỉ TMA1) |
| AQ4, AQ5 | Feature tương tác + bài đánh giá | Đầy đủ cho phân tích liên hệ | Keep |
| AQ6 | Không có dữ liệu concept | Thiếu → KG mô phỏng | Modify (minh hoạ) |
| AQ7 | 34 feature ≤ ngày 41 | Đầy đủ | Keep |
| AQ8 | `date_unregistration` | Có dữ liệu, thiếu thời gian | Defer |
| AQ9 | 6 thuộc tính nhạy cảm | Đầy đủ; một số nhóm rất nhỏ | Keep |
| AQ10–AQ12 | Dự đoán AQ7 + năng lực K (giả định) | Không có dữ liệu về can thiệp thật | Keep (chỉ đánh giá trên dữ liệu lịch sử) |

## 6. Data Understanding & Data Quality

> **BẢN NHÁP – P1 cần rà và sửa.** Chi tiết 12 vấn đề (Q1–Q12) ở `reports/data_quality_report.md` mục 6.

**Tính toàn vẹn.** Các bảng có khoá đều không trùng khoá. Không có dòng con nào thiếu bảng cha: kiểm tra 4 quan hệ
khoá ngoại đều cho 0 dòng mồ côi. Riêng `studentVle` không có khoá duy nhất: ở FFF có 540.673 tổ hợp
(sinh viên × tài nguyên × ngày) xuất hiện nhiều hơn một dòng. Nhóm coi đây là nhiều lần truy cập, nên cộng dồn
`sum_click` thay vì xoá trùng (Q2).

**Giá trị thiếu.** Phần lớn giá trị thiếu là thiếu có nghĩa, không phải lỗi:
- `date_unregistration` thiếu nghĩa là sinh viên chưa rút môn (Q7).
- Bài Exam không có ngày (Q11).
- `vle.week_from/week_to` thiếu ở 58% tài nguyên FFF. Nhóm không dùng hai cột này mà tính tuần từ ngày truy cập (Q10).

Các giá trị thiếu ảnh hưởng tới phân tích đều nhỏ:
- `imd_band` thiếu 4,7%. Chỉ dùng trong audit fairness, giữ thành nhóm "Không rõ" (Q5).
- `date_registration` thiếu 11 dòng (Q6).
- `score` thiếu 46 bài đã nộp (Q8).

**Phân bố và outlier.**
- `sum_click` có đuôi rất dài: giá trị lớn nhất ở FFF là 4.098, trong khi phân vị 99,9% là 102. Nhóm giữ nguyên
  vì đây có thể là hành vi thật (Q4).
- 256.062 dòng click có ngày âm, tức là hoạt động trước khi môn bắt đầu (Q3).
- Điểm TMA1 lệch về phía cao, trung vị 82 (`reports/eda_findings.md`, hình AQ3).

**Mất cân bằng nhãn.** Tỷ lệ không hoàn thành (y = 1) là 51–56% trên toàn bộ đăng ký. Trong quần thể dự báo (sinh viên
còn theo học tại ngày 41), tỷ lệ này là 39–49%, nên nhãn khá cân bằng. Nhóm vẫn ưu tiên PR-AUC và Recall thay cho
accuracy (mục 9).

**Độ phủ thời gian.** Bốn lượt từ 2/2013 đến 10/2014, hai lượt bắt đầu tháng 2 (B) và hai lượt bắt đầu tháng 10 (J).
Lượt test (2014J) có **tỷ lệ rút trước ngày 41 cao nhất (22%)**, so với 11–15% ở ba lượt kia. Vì vậy tỷ lệ y = 1 trong
quần thể dự báo của test chỉ 39%, thấp hơn các tập khác. Sự khác biệt này có ảnh hưởng tới precision trên test (mục 10).

**Tính đại diện.** FFF là một môn STEM của Open University (Anh), với sinh viên chủ yếu học từ xa:
- 81,8% là nam, 74% dưới 35 tuổi, 9,5% khai báo khuyết tật.
- Kết luận không tự động áp dụng cho bối cảnh đại học Việt Nam hay cho các môn khác (rủi ro R6).
- Có 365 lượt đăng ký là của sinh viên học lại hoặc học nhiều lượt (7.762 lượt / 7.397 sinh viên). Thông tin này
  được phản ánh qua `num_of_prev_attempts`.

**Trường nhạy cảm.** Có 6 thuộc tính nhạy cảm, được tách vào `sensitive.parquet`. Chỉ bước kiểm tra công bằng
(`fairness.py`) được đọc file này (Fairness Gate). `id_student` được thay bằng `pid` (SHA-256 kèm salt) trước khi
ghi ra bất kỳ output nào.

**Vấn đề dữ liệu nào có thể thay đổi kết luận?** Có hai vấn đề:
1. **Thiết kế bài đánh giá khác nhau giữa các lượt (Q1).** Lỗi này đã làm Recall rơi từ 0,80 xuống 0,53 với BBB,
   và đã được xử lý bằng cách đổi module.
2. **Tỷ lệ rút sớm khác nhau giữa các lượt.** Điều này làm precision trên test thấp hơn valid. Đây là giới hạn
   cần nêu, không thể sửa bằng cách chỉnh ngưỡng.

## 7. Data Preparation & Analytic-ready Data

> **BẢN NHÁP – P1 cần rà và sửa.**

Toàn bộ quá trình chuẩn bị dữ liệu là một pipeline Python tái lập được:
`audit → cohort → features → kg → eda → model → explain → fairness → prioritize`.
Pipeline chạy bằng lệnh `python -m eduearlyalert.pipeline all`. Mọi tham số (module, lượt, `cutoff_day = 41`,
ngưỡng chấp nhận, K) nằm ở `config.yaml`. CSV được đọc bằng DuckDB với `nullstr='?'`, vì OULAD ghi giá trị thiếu
bằng dấu `?`.

**Bảng 7.1 – Preparation Decision Matrix.**

| Bước | Quyết định | Lý do | Kiểm soát leakage / rủi ro |
|---|---|---|---|
| Đơn vị phân tích | 1 dòng = sinh viên × lượt | Một sinh viên có thể học nhiều lượt | – |
| Nhãn | y = 1 nếu Fail hoặc Withdrawn | Cả hai đều là "không hoàn thành", là điều cố vấn muốn ngăn | `final_result` chỉ dùng làm nhãn |
| Quần thể dự báo | Loại người rút ≤ ngày 41 và người đăng ký sau ngày 41 | Chỉ dự báo cho người còn có thể hỗ trợ được | `date_unregistration` chỉ dùng để lọc |
| Chia dữ liệu | Theo lượt: train 2013B+2013J, valid 2014B, test 2014J | Mô phỏng dùng dữ liệu cũ để dự báo lượt mới | Không chia ngẫu nhiên; chọn mô hình/ngưỡng trên valid |
| Tuần | `date < 0` → tuần 0; 0–6 → tuần 1; …; 35–41 → tuần 6 | Khớp lịch học | Chỉ dùng ngày ≤ 41 |
| Feature tương tác | Click theo tuần, ngày hoạt động, tuần không hoạt động, thay đổi tương tác, tỷ trọng theo loại tài nguyên | AQ2, AQ4 | Click sau ngày 41 bị loại |
| Feature bài đánh giá | Số bài đến hạn/đúng hạn/muộn/chưa nộp, điểm, điểm có trọng số | AQ3, AQ5 | Chỉ bài hạn ≤ 41; bài nộp sau 41 = chưa nộp; loại `is_banked`; không dùng Exam |
| Giá trị thiếu | Click thiếu = 0; điểm thiếu → bỏ qua (TB) hoặc 0 (có trọng số); còn lại điền trung vị kèm cột chỉ báo | Không có click nghĩa là không hoạt động | Trung vị học trên train (trong pipeline mô hình) |
| Thuộc tính nhạy cảm | Tách riêng, không vào feature | Fairness Gate | `leakage.py` báo lỗi nếu lọt vào |
| Định danh | `id_student` → `pid` | Bảo vệ quyền riêng tư | Không có `id_student` trong output |

**Kiểm soát leakage tự động.** Mỗi lần tạo feature và trước khi huấn luyện, `leakage.assert_no_leakage` sẽ dừng
pipeline nếu xảy ra một trong ba trường hợp:
1. Có cột bị cấm trong feature, gồm `final_result`, `date_unregistration`, `module_presentation_length`, các định danh,
   hoặc thuộc tính nhạy cảm.
2. Ngày lớn nhất được dùng vượt ngày 41. Lần chạy cuối: VLE dùng đến ngày 41, hạn nộp đến ngày 24, ngày nộp đến
   ngày 41.
3. Kiểm tra này có test tự động trong `tests/test_leakage.py`.

**Dữ liệu cuối (analytic-ready).** `data/processed/features.parquet` gồm 7.762 dòng (sinh viên × lượt) và
**34 feature** (danh sách trong `feature_list.json`; định nghĩa ở Phụ lục A). Quần thể dự báo có 6.500 dòng:
train 3.383, valid 1.283, test 1.834. Mỗi lần chạy, pipeline tự sinh lại `reports/cohort_flow.csv` và ghi vào audit log
(`reports/audit_log.jsonl`).

**Tái lập.** Theo license, OULAD được phép chia sẻ lại. Tuy vậy, repo không commit dữ liệu (cả bản gốc lẫn bản đã xử lý)
vì dung lượng và theo nguyên tắc governance. Cách tái tạo:
1. Tải zip từ UCI #349 vào `data/raw/`.
2. Chạy `pip install -r requirements.txt && pip install -e .`
3. Đặt `EDU_SALT` trong `.env`.
4. Chạy `python -m eduearlyalert.pipeline all`.

`pytest` (44 test) kiểm tra pipeline trên dữ liệu giả cùng schema.

## 8. Modeling / Analysis Strategy

> **BẢN NHÁP – P3 cần rà và sửa.** Claude viết ngày 11/11/2026 từ `docs/03_pipeline.md`, `src/eduearlyalert/` và
> `docs/templates/model_design_card.md`.

Mỗi AQ được gắn với một loại phân tích và một phương pháp phù hợp với dữ liệu, với mức diễn giải cần có và với người
dùng kết quả (Bảng 8.1). Nhóm chọn theo ba nguyên tắc:
1. **Bắt đầu từ baseline đơn giản** mà người dùng có thể tự áp dụng.
2. **Ưu tiên phương pháp diễn giải được** cho các AQ diagnostic.
3. **Chỉ dùng mô hình phức tạp hơn khi nó tốt hơn baseline trên tập valid.**

**Bảng 8.1 – Model/Method Selection Matrix.**

| AQ | Loại | Technical task | Baseline | Phương pháp ứng viên | Phương án chính và lý do |
|---|---|---|---|---|---|
| AQ1–AQ3 | Descriptive | Tổng hợp theo lượt/tuần/bài | – | Bảng tỷ lệ, đường tích luỹ, heatmap, histogram | Mô tả trực tiếp. Chỉ dùng train + valid để không nhìn trước tập test |
| AQ4 | Diagnostic | So sánh hai nhóm | So sánh trung bình | t-test; Mann-Whitney + Cliff's δ | **Mann-Whitney + Cliff's δ, hiệu chỉnh Holm.** Click lệch phải mạnh, không giả định phân phối chuẩn được. Với n lớn, p-value gần như luôn nhỏ, nên đọc effect size |
| AQ5 | Diagnostic | Liên hệ có điều chỉnh | Tỷ lệ hoàn thành theo nhóm điểm | Hồi quy logistic giải thích | **Logistic giải thích, OR trên mỗi SD.** Đọc được chiều và độ lớn của liên hệ sau khi điều chỉnh theo tương tác. Không diễn giải nhân quả |
| AQ6 | Diagnostic | Truy vấn đồ thị | – | Truy vấn KG | **Truy vấn KG (NetworkX)** trên ánh xạ mô phỏng. Chỉ minh hoạ cơ chế giải thích |
| AQ7 | Predictive | Phân loại nhị phân tại ngày 41 | **Luật**: chưa nộp bài đầu tiên hoặc 0 click Tuần 5–6 | Logistic (điền trung vị, chuẩn hoá, cân bằng lớp); Gradient boosting (HistGradientBoosting, cân bằng lớp) | **Chọn theo PR-AUC trên valid.** Logistic dễ giải thích; boosting xử lý được quan hệ phi tuyến và giá trị thiếu. Kết quả: gboost (PR-AUC valid 0,777) gần như ngang logistic (0,776) |
| AQ9 | Predictive (audit) | Đánh giá theo nhóm | Recall chung | Recall/FNR/precision theo nhóm | **Recall theo nhóm**, ẩn nhóm < 10. Bỏ sót sinh viên cần hỗ trợ là lỗi có hại nhất |
| AQ10 | Prescriptive | Xếp hạng trong giới hạn năng lực | Chọn ngẫu nhiên | A: chỉ điểm rủi ro; B: rủi ro + giảm tương tác; C: rủi ro + chưa nộp bài | **Coverage@K trên valid**, K = 70 (giả định). Hoà thì chọn phương án đơn giản hơn |
| AQ11 | Prescriptive | Gợi ý loại hỗ trợ | – | Luật dựa trên reason codes + KG | **Luật minh bạch**, cố vấn quyết định cuối cùng |
| AQ12 | Prescriptive | Phân tích kịch bản | – | Cảnh báo top 10/20/30% | **Bảng đánh đổi** Recall, precision và số ca so với năng lực. Nhóm chọn ngưỡng trên valid |

**Vì sao không dùng mô hình phức tạp hơn.** Dữ liệu chỉ có 3.383 dòng train và 34 feature dạng bảng. Mục tiêu là cố
vấn hiểu được vì sao một sinh viên được đề xuất. Vì vậy nhóm dừng ở logistic và gradient boosting, giải thích bằng
permutation importance và reason codes. SHAP, deep learning và clustering được cắt vì thời gian (AQ Revision Log).

**Không dùng LLM trong lõi.** Proposal có tuỳ chọn dùng LLM để soạn câu giải thích. Nhóm không làm, vì reason codes
dạng luật đã đủ minh bạch, và LLM có thể tạo nội dung không có trong dữ liệu (rủi ro "thêm claim không có thật" mà P5
nêu).

## 9. Evaluation Design

> **BẢN NHÁP – P4 cần rà và sửa.** Nguồn: `config.yaml`, `docs/03_pipeline.md`, `docs/04_governance.md`.

**Chia dữ liệu theo thời gian.** Train trên hai lượt 2013 (2013B, 2013J), valid trên 2014B, test trên 2014J. Cách
chia này mô phỏng việc dùng dữ liệu các lượt trước để dự báo một lượt mới, và tránh việc cùng một lượt xuất hiện ở cả
train và test. Có ba quy tắc:
- **Valid** dùng để chọn mô hình, chọn ngưỡng, chọn phương án ưu tiên và cung cấp bảng để chọn ngưỡng cảnh báo.
- **Test** chỉ được dùng một lần, để báo cáo.
- EDA chỉ chạy trên train + valid.

**Bảng 9.1 – Evaluation Plan theo thành phần.**

| Thành phần | Metric | Baseline / so sánh | Tiêu chí thành công | Kiểm tra bổ sung |
|---|---|---|---|---|
| EDA (AQ1–AQ6) | Effect size (Cliff's δ), OR, tỷ lệ | – | Mỗi hình có Observation–Insight–Evidence–Limitation; ≥ 8 hình | Ngôn ngữ "liên hệ", không nhân quả; ẩn nhóm < 10 |
| Mô hình (AQ7) | **Recall** (chính), F1, PR-AUC, ROC-AUC, Brier | Luật (baseline 0) | **Recall ≥ 0,80 và F1 ≥ 0,75 trên test** (tiêu chí chấp nhận, không phải KPI) | Leakage check tự động; FN analysis; calibration |
| Giải thích | Permutation importance theo PR-AUC (trên valid) | – | Mỗi cảnh báo có ≥ 1 lý do bằng ngôn ngữ hỗ trợ | `check_language` chặn từ cấm |
| Fairness (AQ9) | Recall và FNR theo nhóm | Recall chung | Đề xuất: chênh lệch ≤ 0,10 giữa các nhóm có ≥ 30 sinh viên y = 1 (P4 chốt) | Ẩn nhóm < 10; không đưa thuộc tính nhạy cảm vào mô hình |
| Ưu tiên (AQ10, AQ12) | Coverage@K, Precision@K; Recall/precision theo % cảnh báo | Chọn ngẫu nhiên; phương án A | Chọn trên valid | K là giả định |
| KG (AQ6) | Competency questions trả lời được | – | Mỗi bài trước mốc có ánh xạ concept | Nhãn "MÔ PHỎNG" trên mọi output |
| Toàn hệ thống | Human gates G1–G4 | – | Mọi Risk List ở `pending_review`; quyết định ghi vào `audit_log.jsonl` | Không có chức năng tự liên hệ sinh viên |

**Vì sao chọn các metric này.**
- Lỗi tốn kém nhất là **bỏ sót** sinh viên cần hỗ trợ (false negative). Vì vậy Recall là metric chính.
- PR-AUC dùng để chọn mô hình vì nó không phụ thuộc ngưỡng và tập trung vào lớp dương.
- F1 giữ cho số cảnh báo sai không quá lớn, để cố vấn không mất thời gian vào ca không cần.
- Accuracy không được dùng.

**Ngưỡng của mô hình.** Ngưỡng được chọn trên valid: F1 cao nhất trong các ngưỡng đạt Recall ≥ 0,80.
Ngưỡng **không** được chỉnh lại sau khi xem test.

## 10. Experimental Implementation & Results

> **BẢN NHÁP – P3 cần rà và sửa.** Mọi số liệu từ `reports/model_metrics.json`, `reports/model_results.md`,
> `reports/explainability_report.md`, `reports/fairness_report.md`, `reports/prioritization_report.md`
> (OULAD thật, FFF, lần chạy ngày 11/11/2026).

**Triển khai.**
- Python 3; pandas và DuckDB (cho `studentVle` 10,6 triệu dòng); scikit-learn; NetworkX (KG); Streamlit (dashboard).
- Pipeline 9 bước, mỗi bước có `run(cfg)`. Mọi tham số nằm ở `config.yaml`, seed = 42.
- 44 test tự động, chạy trên dữ liệu giả cùng schema. Có CI (`.github/workflows/ci.yml`).
- Mã nguồn: _[link repo]_.

**Kết quả AQ7.** Quần thể dự báo: train 3.383, valid 1.283 (629 y = 1), test 1.834 (717 y = 1).

**Bảng 10.1 – So sánh mô hình** (ngưỡng chọn trên valid).

| Tập | Mô hình | Ngưỡng | Recall | Precision | F1 | PR-AUC | ROC-AUC | Brier | % được cảnh báo |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Valid | Luật | – | 0,278 | 0,841 | 0,418 | 0,588 | 0,614 | – | 16% |
| Valid | Logistic | 0,367 | 0,832 | 0,643 | 0,725 | 0,776 | 0,775 | 0,193 | 63% |
| Valid | **Gboost** | 0,405 | 0,801 | 0,655 | 0,721 | **0,777** | 0,774 | 0,193 | 60% |
| Test | Luật | – | 0,292 | 0,860 | 0,435 | 0,528 | 0,631 | – | 13% |
| Test | Logistic | 0,367 | 0,856 | 0,549 | 0,669 | 0,740 | 0,801 | 0,181 | 61% |
| Test | **Gboost** | 0,405 | **0,805** | 0,560 | **0,661** | 0,745 | 0,794 | 0,185 | 56% |

**Diễn giải kết quả:**
1. Hai mô hình học máy tốt hơn rõ rệt so với luật: PR-AUC trên test 0,745 so với 0,528. Luật có precision cao
   nhưng chỉ phát hiện 29% số sinh viên cần hỗ trợ.
2. Mô hình chính (gboost) **đạt tiêu chí Recall** (0,805 ≥ 0,80) nhưng **chưa đạt tiêu chí F1** (0,661 < 0,75).
3. Logistic và gboost gần như ngang nhau. Trên test, logistic có F1 nhỉnh hơn một chút (0,669), nhưng nhóm **không
   đổi** mô hình chính, vì lựa chọn đã được chốt trên valid.
4. Precision trên test thấp hơn valid (0,56 so với 0,65), một phần vì tỷ lệ y = 1 trong quần thể dự báo của test
   thấp hơn (39% so với 49%; mục 6).
5. Hình `aq7_roc_pr.png`, `aq7_confusion_matrix.png` và `aq7_calibration.png` ở Phụ lục.

**Một mâu thuẫn quan trọng cho triển khai.** Để đạt Recall 0,80, mô hình phải cảnh báo **56% sinh viên** của lượt test,
tức 1.030 người. Năng lực giả định là 70 ca/tuần. Vì vậy, ở dạng "cảnh báo khi vượt ngưỡng", hệ thống không dùng được.
Cách dùng thực tế là **xếp hạng rồi liên hệ Top-K** (AQ10). Trên valid, Top-70 đạt Precision@K 0,957 nhưng chỉ bao phủ
10,7% số sinh viên cần hỗ trợ. Tiêu chí Recall ≥ 0,80 đo khả năng phân biệt của mô hình, không phải độ bao phủ thực tế
khi năng lực có hạn. Cả hai con số cần được trình bày cạnh nhau.

**Error analysis.** Có 140 false negative trên test: 75 Withdrawn và 65 Fail.
- So với nhóm được phát hiện đúng, nhóm bị bỏ sót có tổng click trung vị cao gấp khoảng 3,7 lần (757 so với 206).
- Số ngày hoạt động gấp đôi (29,5 so với 13), gần như không giảm tương tác, và điểm TMA1 trung vị 82 so với 73.
- Nói cách khác, ở Tuần 1–6 họ trông giống nhóm hoàn thành. Đây là giới hạn của mốc dự báo: hơn một nửa số người rút
  môn rút sau Tuần 6 (AQ1), và khó khăn của nhóm Fail có thể chỉ xuất hiện ở các bài sau.
- Chi tiết ở Model Design Card (Phụ lục D).

**Giải thích (explainability).**
- Theo permutation importance trên valid, `mean_score` (điểm TMA1) quan trọng nhất: PR-AUC giảm 0,105 khi xáo trộn
  feature này. Tiếp theo là `clicks_w6` (0,023) và `mean_days_early` (0,011).
- Ở mức cá nhân, mỗi cảnh báo kèm reason codes dạng luật, ngưỡng lấy từ phân vị trên train. Ví dụ: "Chưa nộp bài đánh
  giá đầu tiên – nên hỏi thăm khó khăn".
- Reason code cho biết **dấu hiệu trong dữ liệu**, không phải nguyên nhân sinh viên gặp khó khăn.

**Fairness (AQ9).**
- Recall chung trên test là 0,805.
- Chênh lệch đáng chú ý nhất theo giới tính: nữ 0,736 (n = 345), nam 0,819 (n = 1.489).
- Chênh lệch lớn hơn theo trình độ học vấn (0,33) đến từ hai nhóm chỉ có 3–4 sinh viên y = 1, nên không đủ tin cậy.
- Theo ngưỡng đề xuất ở mục 9, chưa thuộc tính nào vượt ngưỡng. Nhận định chi tiết ở `docs/04_governance.md`.

**Ưu tiên (AQ10–AQ12).** Ba phương án AQ10 gần như như nhau ở K = 70. Trên valid, A và C hoà (Coverage@K 0,107), B
thấp hơn một chút (0,103), nên nhóm chọn phương án đơn giản nhất là A. Theo bảng AQ12 trên valid:
- Cảnh báo top 10% tương đương 128 ca, cần 1,8 tuần năng lực, Recall 0,18 và precision 0,90.
- Top 30% tương đương 385 ca, cần 5,5 tuần năng lực, Recall 0,50.

Ngưỡng cuối cùng do P4 chọn: _[điền sau khi chọn]_. Mọi đánh giá ưu tiên chỉ dựa trên dữ liệu lịch sử, **không**
chứng minh rằng liên hệ sẽ giúp sinh viên hoàn thành môn.

**Khả năng tái lập.** Cùng dữ liệu, cùng `config.yaml` và cùng seed thì cho cùng kết quả. Mỗi bước ghi vào
`reports/audit_log.jsonl`. Chạy lại `pipeline all` trên các commit đã merge không làm thay đổi `reports/` (đã kiểm tra
khi tích hợp PR #5).

## 11. Findings, Discussion & Decision Support

<!-- P2 (cả nhóm góp) · trả lời TỪNG AQ ở đúng mức evidence → dùng bảng "Câu trả lời theo AQ" bên dưới
làm xương sống, viết thêm phần thảo luận. Evidence: docs/eda_insights.md, reports/eda_findings.md. -->

_[Chưa viết]_

## 12. Limitations & Future Work

<!-- P4 · dataset gaps; khả năng khái quát; giới hạn quan sát/nhân quả; giới hạn mô hình; AQ hoãn; dữ liệu cần thêm.
Phân biệt "không thấy bằng chứng" với "không có dữ liệu để kiểm tra".
Gợi ý nội dung: OULAD Anh 2013–14, 1 module STEM; KG mô phỏng (concept thiên về KHXH); chỉ 1 bài đánh giá trước mốc;
FN trông giống nhóm hoàn thành ở Tuần 1–6; F1 chưa đạt; AQ8 hoãn; mốc Tuần 4, SHAP, LLM, clustering bị cắt;
AQ10/AQ12 từng tính trên test (đã sửa, PR #6); chênh lệch Recall theo gender. Nguồn: docs/04_governance.md (Risk Register R1–R11). -->

_[Chưa viết]_

## 13. Generative AI Use & Reflection

<!-- P4 (cả nhóm khai) · AI dùng vào việc gì; gợi ý gì; kiểm chứng ra sao; chấp nhận/bác bỏ; quyết định cuối của người.
Dùng bảng "AI Decision Log" bên dưới. AI không thay evidence. -->

_[Chưa viết]_

## 14. Conclusion

<!-- P2 · đã hỏi gì; dữ liệu hỗ trợ đến đâu; phân tích nào phù hợp; kết luận được/không được; bước tiếp theo.
Không thêm kết luận mới. -->

_[Chưa viết]_

---

## Final Project Traceability Matrix (bắt buộc)

> **BẢN NHÁP – cả nhóm rà.** Một hàng = một AQ cuối. Ô thiếu evidence ghi GAP.
> KPI: Completion Rate (baseline thật 46,9%, `reports/aq1_outcomes.csv`; mục tiêu là assumption).
> Goal chung: cải thiện hoàn thành môn nhờ nhận diện sớm và hỗ trợ kịp thời (`docs/01_project_overview.md`).

| AQ-ID | Goal / KPI | Final Analytical Question | Level | Required Data / Unit | Actual Dataset & Variables | Preparation / Feature Logic | Method + Rationale | Evaluation / Result | Decision Supported | Final Status |
|---|---|---|---|---|---|---|---|---|---|---|
| AQ1 | Completion Rate (baseline) | Tỷ lệ Pass/Distinction/Fail/Withdrawn theo lượt; rút môn diễn ra tuần nào? | Descriptive | Kết quả + ngày rút; SV × lượt | `studentInfo.final_result`, `studentRegistration.date_unregistration` | Train + valid; ẩn nhóm < 10 | Tỷ lệ, đường tích luỹ – mô tả | Completion 46,9%; 51–56% số người rút, rút sau Tuần 6 | D3 lập kế hoạch nguồn lực; xác nhận cửa sổ can thiệp | Answered |
| AQ2 | Early Detection | Tương tác VLE theo tuần × loại tài nguyên? | Descriptive | Click theo ngày; SV × tuần | `studentVle`, `vle.activity_type` | Tuần = ngày/7, ngày âm → tuần 0; cộng `sum_click` | Heatmap, boxplot – mô tả | Tỷ lệ 0 click tăng 19% → 28% (T1 → T6) | D2 điều chỉnh hoạt động học | Answered |
| AQ3 | Early Detection | Nộp đúng hạn/muộn/chưa nộp và điểm các bài đầu kỳ? | Descriptive | Hạn nộp, ngày nộp, điểm | `assessments`, `studentAssessment` | Chỉ bài hạn ≤ ngày 41; nộp sau 41 = chưa nộp; bỏ `is_banked` | Tỷ lệ, histogram | Chỉ 1 bài (TMA1): 22% chưa nộp, điểm trung vị 82 | D1 lý do liên hệ; D2 nhắc trước hạn | Answered (chỉ TMA1) |
| AQ4 | Early Detection | Chỉ báo tương tác Tuần 1–6 khác biệt bao nhiêu giữa hai nhóm? | Diagnostic | Feature tương tác; nhãn | Feature VLE (`active_days_total`, `clicks_total`, `inactive_weeks`…) | Feature ≤ ngày 41 | Cliff's δ + Mann-Whitney, Holm – không giả định phân phối, đọc effect size | δ = 0,46 (vừa) cho số ngày hoạt động và tổng click | D1 xếp ưu tiên (không gán nhãn cá nhân) | Answered |
| AQ5 | Early Detection | Điểm/nộp bài liên hệ với hoàn thành ra sao khi đã điều chỉnh theo tương tác? | Diagnostic | Điểm, nộp bài, tương tác | Feature bài đánh giá + tương tác | Chuẩn hoá theo SD | Logistic giải thích (OR/SD) | OR điểm TMA1 = 0,37; pseudo R² = 0,18 | D1, D2 mốc kiểm tra TMA1 | Answered (liên hệ, không nhân quả) |
| AQ6 | Support quality | Concept/CLO nào nhiều SV cần hỗ trợ thêm? | Diagnostic | Ánh xạ bài → concept | **KG MÔ PHỎNG** (`kg/`) + điểm TMA1 | Điểm hiệu dụng theo concept | Truy vấn KG | C01, C03, C05 cùng 20%: chưa phân biệt được ở Tuần 6 | D2 (chỉ minh hoạ cơ chế) | Partial – dữ liệu mô phỏng |
| AQ7 | Early Detection Recall ≥ 80% | Xác suất không hoàn thành tại cuối Tuần 6? | Predictive | Feature ≤ ngày 41; SV còn theo học | 34 feature, không thuộc tính nhạy cảm | Quần thể dự báo; chia theo lượt; leakage check | Rule vs logistic vs gboost; chọn theo PR-AUC valid | Test: Recall 0,805 ✔, F1 0,661 ✘, PR-AUC 0,745 (rule 0,528) | D1 liên hệ ai trước | Answered (F1 chưa đạt) |
| AQ8 | Early Detection | Rút môn Tuần 7–12? | Predictive | Ngày rút | `date_unregistration` | – | – | GAP – chưa làm | – | Deferred (thiếu thời gian) |
| AQ9 | Trách nhiệm/công bằng | Hiệu năng có nhất quán giữa các nhóm? | Predictive (audit) | Thuộc tính nhạy cảm (chỉ audit) | `gender, region, disability, age_band, imd_band, highest_education` | Không vào mô hình (Fairness Gate) | Recall/FNR theo nhóm | Chênh lệch đáng chú ý: gender 0,08 (F 0,74 / M 0,82); các chênh lệch lớn hơn đến từ nhóm nhỏ | G3 – duyệt fairness | Partial – thiếu khoảng tin cậy |
| AQ10 | Timely Support Contact ≥ 80% | Ai liên hệ trước khi năng lực có hạn (K)? | Prescriptive | Risk score + năng lực | Dự đoán AQ7, K = 70 (assumption) | Top-K, phân tầng | So sánh 3 phương án theo Coverage@K; chọn trên valid | Valid: chọn A (A = C: Coverage@K 0,107, Precision@K 0,957; B 0,103). Test: cả 3 như nhau (0,093) | D1 | Answered (trên dữ liệu lịch sử) |
| AQ11 | Support quality | Loại hỗ trợ nào cho từng SV? | Prescriptive | Reason codes + concept gap | Reason codes, KG mô phỏng | Luật gán loại hỗ trợ | Luật (có người duyệt) | Phân bố đề xuất trong Risk List; chưa đánh giá hiệu quả | D1 (cố vấn duyệt) | Partial – chưa kiểm chứng |
| AQ12 | Timely Support Contact | Ngưỡng cảnh báo 10/20/30% – đánh đổi? | Prescriptive | Risk score + năng lực | Dự đoán AQ7 | Kịch bản ngưỡng | Recall/precision/tải công việc; bảng chọn trên valid | Valid: 10% = 128 ca (1,8 tuần năng lực), Recall 0,18, Precision 0,90; cả 3 ngưỡng vượt 70 ca/tuần | D3 | Partial – P4 chưa chọn ngưỡng |

## AQ Revision Log

> **BẢN NHÁP.** GAP: câu chữ AQ đúng như ở M1 không có trong repo; cột "AQ ở M1" lấy theo `docs/01_project_overview.md`
> (tóm tắt Project Charter V1 + M1). Nhóm đối chiếu lại với báo cáo M1.

| AQ-ID | AQ ở M1 | Finding từ M2/M3 (và lúc chạy) | AQ cuối cùng | Action | Lý do | Ảnh hưởng tới phương pháp |
|---|---|---|---|---|---|---|
| Phạm vi | Module BBB | BBB 2014J: TMA đầu kỳ trọng số 0, điểm gần nhị phân | Module FFF | Modify | Thiết kế bài đánh giá ổn định ở 4 lượt | Mọi AQ chạy lại trên FFF |
| AQ3 | Các bài đánh giá đầu kỳ | FFF chỉ có 1 bài hạn ≤ ngày 41 | Chỉ TMA1 | Modify | Giới hạn của dữ liệu | Feature bài đánh giá ít thông tin |
| AQ6 | Concept/CLO cần hỗ trợ | Không có dữ liệu concept thật | Giữ, dùng KG mô phỏng | Modify | OULAD không có ánh xạ concept | Chỉ minh hoạ cơ chế, không kết luận |
| AQ8 | Rút môn Tuần 7–12 | – | – | Defer | Thiếu thời gian | Ghi vào Future Work |
| AQ10, AQ12 | Ưu tiên, ngưỡng | Bảng chọn từng được tính trên tập test | Chọn trên valid, test chỉ báo cáo | Modify | Không chọn tham số bằng test | Đã sửa `prioritize.py` (PR #6) |
| Khác | Mốc Tuần 4, SHAP, LLM, clustering | – | – | Drop | Thiếu thời gian (checklist) | Dùng permutation importance thay SHAP |

## Câu trả lời cuối cùng theo Analytical Question

> **BẢN NHÁP.** Diễn giải đúng mức: Descriptive mô tả; Diagnostic là liên hệ; Predictive là khả năng dự báo trên
> hold-out; Prescriptive là phương án cần kiểm chứng.

| AQ-ID | Evidence/Data Used | Method / Analysis | Main Finding | Confidence / Limitation | Implication for Decision |
|---|---|---|---|---|---|
| AQ1 | `reports/aq1_outcomes.csv`, `aq1_withdrawal.csv` | Mô tả | Hoàn thành 46,9%; hơn nửa số người rút, rút sau Tuần 6 | Ngày rút là ngày hành chính | Cảnh báo Tuần 6 còn thời gian; cần hỗ trợ đầu môn cho nhóm rút sớm |
| AQ2 | `reports/aq2_*.csv` | Mô tả | Nhóm 0 click tăng 19% → 28% | Click là proxy | Theo dõi "0 click 2 tuần" |
| AQ3 | `reports/aq3_*.csv` | Mô tả | 22% chưa nộp TMA1; điểm trung vị 82 | Chỉ 1 bài | Lý do liên hệ cụ thể |
| AQ4 | `reports/aq4_group_comparison.csv` | Cliff's δ | Khác biệt mức vừa (δ = 0,46) | Liên hệ; hai nhóm chồng lấn | Dùng để xếp ưu tiên, không gán nhãn |
| AQ5 | `reports/aq5_*.csv` | Logistic giải thích | Điểm TMA1 vẫn liên hệ sau điều chỉnh (OR = 0,37/SD) | Pseudo R² 0,18 | TMA1 là mốc kiểm tra sớm |
| AQ6 | `reports/aq6_concept_gaps.csv` | Truy vấn KG | Chưa phân biệt concept ở Tuần 6 | **Mô phỏng** | Chỉ minh hoạ |
| AQ7 | `reports/model_results.md` | gboost, ngưỡng từ valid | Recall 0,805, F1 0,661 | FN trông giống nhóm hoàn thành | Hỗ trợ D1, luôn có người duyệt |
| AQ8 | – | – | GAP | Hoãn | Future Work |
| AQ9 | `reports/fairness_report.md` | Recall theo nhóm | Gender chênh 0,08 | Nhóm nhỏ dao động lớn | Ghi vào Limitations; theo dõi tầng gần ngưỡng |
| AQ10 | `reports/prioritization_report.md` | Coverage@K, chọn trên valid | Chọn A (chỉ theo điểm rủi ro); ở K = 70 các phương án gần như như nhau | Đánh giá trên dữ liệu lịch sử; K là giả định | Dùng phương án đơn giản nhất (A) |
| AQ11 | `reports/risk_list.csv` | Luật | Phân bố loại hỗ trợ | Chưa đánh giá hiệu quả | Là gợi ý, cố vấn quyết định |
| AQ12 | `reports/aq12_threshold_scenarios.csv` (valid) | Kịch bản | Mọi ngưỡng vượt năng lực (10% = 128 ca trên valid) | K là giả định; P4 chưa chọn | Cần thêm năng lực hoặc chỉ liên hệ Top-K |

## AI Decision Log

> **BẢN NHÁP – mỗi thành viên khai phần mình.** Hàng M3/M5 ghi lại việc dùng Claude Code ngày 11/11/2026 (có thật).
> Các hàng khác: GAP, nhóm tự khai.

| Stage | AI used for | AI suggestion/output | Student verification / modification | Final human decision |
|---|---|---|---|---|
| M1 / M5 | _[nhóm khai]_ | | | |
| M2 / M5 | _[nhóm khai]_ | | | |
| M3 / M5 | Claude Code: tải OULAD, chạy pipeline, kiểm tra dữ liệu | Phát hiện BBB 2014J có TMA đầu kỳ trọng số 0, điểm gần nhị phân; đề xuất đổi sang FFF | _[P1 đối chiếu `assessments.csv`]_ | Nhóm chọn FFF (PR #2) |
| M3 / M5 | Claude Code: soạn nháp data quality notes, data inventory | 12 vấn đề Q1–Q12, bảng inventory | _[P1 rà]_ | _[P1]_ |
| M4 / M5 | Claude Code: soạn nháp insight EDA, model card, nhận định fairness | Bản nháp có nhãn; chỉ ra AQ10/AQ12 đang tính trên test | _[P2, P3, P4 rà]_ | _[nhóm]_ |
| M4 / M5 | Claude Code: sửa `prioritize.py` để chọn trên valid | Code + 4 test (PR #6) | Nhóm duyệt PR, chạy lại pipeline | Merge PR #6 |
| M5 | Claude Code: viết nháp mục 4–7 | Văn bản từ `docs/` và `reports/` | _[P1 rà, đối chiếu số liệu]_ | _[P1]_ |
| M5 | Claude Code: viết nháp mục 8–10 | Văn bản từ `reports/model_metrics.json` và các report khác | _[P3, P4 rà, đối chiếu số liệu]_ | _[P3, P4]_ |
| M5 | Claude Code: dựng khung Final Report theo P5 | Khung + 4 bảng bắt buộc | _[P2 rà]_ | _[nhóm]_ |

## Phụ lục

<!-- A. Data dictionary (docs/02_data.md mục 4 + reports/data_dictionary_auto.csv)
     B. Data Quality Report (reports/data_quality_report.md)
     C. EDA findings đủ 11 hình (reports/eda_findings.md)
     D. Model Design Card (docs/templates/model_design_card.md)
     E. Risk Register + Governance (docs/04_governance.md)
     F. README + link repo; hướng dẫn tái tạo (make setup → pipeline)
     G. Search log M2 – GAP, lấy từ báo cáo M2 -->

_[Chưa gom]_

## Tài liệu tham khảo

- Kuzilek J., Hlosta M., Zdrahal Z. (2017). Open University Learning Analytics dataset. *Scientific Data* 4:170171. doi:10.1038/sdata.2017.171
- _[Nhóm bổ sung; không thêm citation chưa kiểm chứng]_
