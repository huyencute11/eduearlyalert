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

<!-- P1 · nguồn M2 · unit of analysis; target; variables; time; population; candidate datasets; lý do chọn; license.
Evidence: docs/02_data.md mục 1, 3, 6. GAP: Data Requirement Matrix và Dataset Selection Matrix (các dataset ứng viên
đã so sánh ở M2) KHÔNG có trong repo → lấy từ báo cáo M2. -->

_[Chưa viết]_

## 5. Dataset Description & Requirement–Data Fit

<!-- P1 · nguồn M2 + M3 · 7 bảng, khoá, kích thước, coverage, gaps, AQ status keep/modify/defer/drop.
Evidence: docs/02_data.md (Data Inventory, Data Dictionary), reports/data_dictionary_auto.csv,
reports/module_presentation_counts.csv. Nêu lý do chọn FFF (BBB 2014J lệch thiết kế bài đánh giá). -->

_[Chưa viết]_

## 6. Data Understanding & Data Quality

<!-- P1 · nguồn M3 · phân bố; missing; duplicates; outliers; imbalance; temporal coverage; representativeness; sensitive fields.
Evidence: reports/data_quality_report.md (mục 6 = docs/data_quality_notes.md, Q1–Q12), reports/figures/aq1_*, aq2_*.
Trả lời câu tự kiểm tra: vấn đề dữ liệu nào có thể thay đổi kết luận? (Q1 thiết kế bài đánh giá; tỷ lệ rút sớm ở test). -->

_[Chưa viết]_

## 7. Data Preparation & Analytic-ready Data

<!-- P1 · nguồn M3 · cleaning, join, feature, xử lý missing, KIỂM SOÁT LEAKAGE, version.
Evidence: docs/03_pipeline.md, docs/02_data.md mục 3–4, reports/cohort_flow.csv, src/eduearlyalert/leakage.py.
Cần Preparation Decision Matrix (bước | quyết định | lý do | rủi ro leakage). -->

_[Chưa viết]_

## 8. Modeling / Analysis Strategy

<!-- P3 · M4 Level 1 · AQ → loại phân tích → task → baseline → candidate methods → phương án chính → rationale.
Evidence: docs/templates/model_design_card.md, docs/01 (AQ ladder ↔ code). Cần Model/Method Selection Matrix
cho MỌI AQ (không chỉ AQ7): ví dụ AQ4 = Cliff's δ + Holm; AQ5 = logistic giải thích; AQ7 = rule vs logistic vs gboost. -->

_[Chưa viết]_

## 9. Evaluation Design

<!-- P4 · M4 Level 1 · metric; baseline; split theo presentation; tiêu chí; leakage/fairness/interpretability checks.
Evidence: config.yaml (acceptance, scope), docs/04_governance.md (human gates, fairness), reports/model_metrics.json.
Viết rõ: ngưỡng chọn trên valid; test chạm 1 lần. ⚠️ AQ10/AQ12 hiện tính trên test – xem mục 12 / việc mở. -->

_[Chưa viết]_

## 10. Experimental Implementation & Results

<!-- P3 · M4 Level 2 · tools; setup; kết quả; so sánh baseline; error analysis; diễn giải.
Evidence: reports/model_results.md, reports/figures/aq7_*, docs/templates/model_design_card.md (error analysis),
reports/explainability_report.md, reports/fairness_report.md, reports/prioritization_report.md.
Không chỉ báo "best model": giải thích metric và ý nghĩa với AQ7. -->

_[Chưa viết]_

## 11. Findings, Discussion & Decision Support

<!-- P2 (cả nhóm góp) · trả lời TỪNG AQ ở đúng mức evidence → dùng bảng "Câu trả lời theo AQ" bên dưới
làm xương sống, viết thêm phần thảo luận. Evidence: docs/eda_insights.md, reports/eda_findings.md. -->

_[Chưa viết]_

## 12. Limitations & Future Work

<!-- P4 · dataset gaps; khả năng khái quát; giới hạn quan sát/nhân quả; giới hạn mô hình; AQ hoãn; dữ liệu cần thêm.
Phân biệt "không thấy bằng chứng" với "không có dữ liệu để kiểm tra".
Gợi ý nội dung: OULAD Anh 2013–14, 1 module STEM; KG mô phỏng (concept thiên về KHXH); chỉ 1 bài đánh giá trước mốc;
FN trông giống nhóm hoàn thành ở Tuần 1–6; F1 chưa đạt; AQ8 hoãn; mốc Tuần 4, SHAP, LLM, clustering bị cắt;
AQ10/AQ12 tính trên test; chênh lệch Recall theo gender. Nguồn: docs/04_governance.md (Risk Register R1–R11). -->

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
| AQ10 | Timely Support Contact ≥ 80% | Ai liên hệ trước khi năng lực có hạn (K)? | Prescriptive | Risk score + năng lực | Dự đoán AQ7, K = 70 (assumption) | Top-K, phân tầng | So sánh 3 phương án theo Coverage@K | 3 phương án như nhau ở K = 70; **đang tính trên test** | D1 | Partial – cần tính lại trên valid |
| AQ11 | Support quality | Loại hỗ trợ nào cho từng SV? | Prescriptive | Reason codes + concept gap | Reason codes, KG mô phỏng | Luật gán loại hỗ trợ | Luật (có người duyệt) | Phân bố đề xuất trong Risk List; chưa đánh giá hiệu quả | D1 (cố vấn duyệt) | Partial – chưa kiểm chứng |
| AQ12 | Timely Support Contact | Ngưỡng cảnh báo 10/20/30% – đánh đổi? | Prescriptive | Risk score + năng lực | Dự đoán AQ7 | Kịch bản ngưỡng | Recall/precision/tải công việc | Cả 3 ngưỡng vượt năng lực 70 ca/tuần; **đang tính trên test** | D3 | Partial – cần tính lại trên valid |

## AQ Revision Log

> **BẢN NHÁP.** GAP: câu chữ AQ đúng như ở M1 không có trong repo; cột "AQ ở M1" lấy theo `docs/01_project_overview.md`
> (tóm tắt Project Charter V1 + M1). Nhóm đối chiếu lại với báo cáo M1.

| AQ-ID | AQ ở M1 | Finding từ M2/M3 (và lúc chạy) | AQ cuối cùng | Action | Lý do | Ảnh hưởng tới phương pháp |
|---|---|---|---|---|---|---|
| Phạm vi | Module BBB | BBB 2014J: TMA đầu kỳ trọng số 0, điểm gần nhị phân | Module FFF | Modify | Thiết kế bài đánh giá ổn định ở 4 lượt | Mọi AQ chạy lại trên FFF |
| AQ3 | Các bài đánh giá đầu kỳ | FFF chỉ có 1 bài hạn ≤ ngày 41 | Chỉ TMA1 | Modify | Giới hạn của dữ liệu | Feature bài đánh giá ít thông tin |
| AQ6 | Concept/CLO cần hỗ trợ | Không có dữ liệu concept thật | Giữ, dùng KG mô phỏng | Modify | OULAD không có ánh xạ concept | Chỉ minh hoạ cơ chế, không kết luận |
| AQ8 | Rút môn Tuần 7–12 | – | – | Defer | Thiếu thời gian | Ghi vào Future Work |
| AQ10, AQ12 | Ưu tiên, ngưỡng | Đang được tính trên tập test | Tính lại trên valid | Modify | Không chọn tham số bằng test | Cần sửa `prioritize.py` |
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
| AQ10 | `reports/prioritization_report.md` | Coverage@K | 3 phương án như nhau ở K = 70 | Tính trên test | Chờ tính lại trên valid |
| AQ11 | `reports/risk_list.csv` | Luật | Phân bố loại hỗ trợ | Chưa đánh giá hiệu quả | Là gợi ý, cố vấn quyết định |
| AQ12 | `reports/aq12_threshold_scenarios.csv` | Kịch bản | Mọi ngưỡng vượt năng lực | Tính trên test; K là giả định | Cần thêm năng lực hoặc Top-K |

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
