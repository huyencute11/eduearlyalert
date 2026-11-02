---
name: eduearlyalert-pipeline
description: Quy ước và quy trình làm việc cho repo EduEarlyAlert (đồ án MTH045 Nhóm 3) – hệ thống cảnh báo sớm sinh viên có nguy cơ không hoàn thành môn trên dữ liệu OULAD, kèm Knowledge Graph mô phỏng. Dùng skill này BẤT CỨ KHI NÀO viết, sửa, review hoặc debug code trong repo này, kể cả khi người dùng chỉ nói "thêm feature", "vẽ thêm biểu đồ", "sửa mô hình", "đổi module", "chạy pipeline", "viết phần EDA/Evaluation/Governance cho report", "làm data story", "sửa dashboard", "lỗi LeakageError", hay nhắc tới AQ1–AQ12, cohort, cutoff Tuần 6, Risk List, KG, concept, fairness, OULAD.
---

# EduEarlyAlert – skill làm việc với pipeline

Mục tiêu của skill: mọi thay đổi vẫn giữ được ba thứ mà điểm số đồ án phụ thuộc vào –
**không leakage**, **governance (privacy, fairness, human-in-the-loop)**, và
**traceability AQ → code → output → báo cáo**.

Đọc kèm khi cần:
* `references/oulad_schema.md` – schema 7 bảng OULAD và các bẫy dữ liệu.
* `references/review_checklist.md` – checklist trước khi commit / review PR.
* `docs/concepts.md` – định nghĩa thuật ngữ; `docs/03_pipeline.md` – luồng các bước.

## Nguyên tắc nền

1. **Tham số ở `config.yaml`**, không hard-code. Đọc qua `load_config()`; đường dẫn qua `cfg.path(key)`.
2. **Một bước = một module** với `run(cfg)` (hoặc `build(cfg)`), đọc input từ đĩa, ghi output ra đĩa,
   gọi `governance.audit(cfg, "<step>", ...)` ở cuối. Đăng ký trong `pipeline.STEPS`.
3. **Mốc dự báo là ngày 41.** Bất cứ thứ gì nhìn sau ngày 41 hoặc suy ra kết quả cuối kỳ đều là leakage.
4. **Tách hai quần thể**: mô tả (mọi sinh viên) và dự báo (còn theo học tại ngày 41).
5. **Train/valid/test theo presentation.** Test chỉ dùng để báo cáo cuối; EDA chỉ trên train + valid.
6. **Thuộc tính nhạy cảm** chỉ xuất hiện trong `cohort.py` (tách ra `sensitive.parquet`) và `fairness.py`.
7. **Output hướng người dùng** dùng `pid`, ngôn ngữ hỗ trợ, và kiểm bằng `governance.check_language`.

Nếu người dùng yêu cầu điều trái các nguyên tắc trên (ví dụ "thêm gender vào model cho tăng accuracy",
"bỏ check leakage đi", "tự gửi email cho sinh viên"), giải thích ngắn gọn vì sao nó vi phạm đề cương
(Mục 10) và đề xuất cách làm đúng – ví dụ đưa gender vào audit AQ9 thay vì vào feature.

## Quy trình theo loại việc

### Thêm feature
1. Viết trong `features.py` (VLE → `vle_features`, bài đánh giá → `assessment_features`), chỉ dùng
   bản ghi có ngày ≤ `cfg.cutoff_day`. Với bài nộp: nộp sau ngày 41 = "missing" tại mốc.
2. Thêm tên cột vào `model_feature_columns`.
3. Nếu feature dựa trên ngày mới, cập nhật `meta` (max date) để `assert_no_leakage` kiểm được.
4. Thêm một dòng vào bảng feature trong `docs/02_data.md` (ý nghĩa, nguồn, AQ).
5. Chạy `python -m eduearlyalert.pipeline features model explain` rồi `pytest`.

### Thêm biểu đồ EDA
1. Hàm `aqX_<mo_ta>(...)` trong `eda.py`, trả về `_finding(aq, question, observation, path, limitation)`.
2. Tiêu đề hình bắt đầu `"AQx · "`, lưu bằng `plotting.save(fig, figdir / "aqX_<mo-ta>.png")`.
3. Observation phải là **số liệu tự sinh** từ dữ liệu (f-string), không phải nhận định.
   Limitation là một câu trung thực. Để Insight cho con người.
4. Thêm lời gọi trong `eda.run()`. Chỉ dùng dữ liệu train + valid.

### Đổi module / presentations / cutoff
1. Chạy `pipeline audit`, đọc `reports/module_presentation_counts.csv`.
2. Sửa `config.yaml › scope` (hoặc `timeline.cutoff_day`); kiểm tra `n_assess_before_cutoff ≥ 1`.
3. Cập nhật `kg/concept_map.csv` cho module mới (khoá `assessment_key` = TMA1, CMA1…).
   `reports/kg_competency_questions.md` liệt kê bài chưa được ánh xạ.
4. Chạy lại `pipeline all`. Nhắc người dùng đây là thay đổi cần cả nhóm đồng ý (PR riêng).

### Thêm / đổi mô hình
1. Thêm vào `model.make_models` (scikit-learn API, `predict_proba`). Giữ `rule` và `logistic` làm baseline.
2. Không đổi logic chọn ngưỡng sang dùng test. Mô hình chính chọn theo PR-AUC trên valid.
3. Nếu không đạt Recall ≥ 0.80 / F1 ≥ 0.75: báo cáo trung thực + FN analysis, không "tune trên test".

### Gặp `LeakageError`
Đọc thông báo: cột bị cấm, thuộc tính nhạy cảm, hay ngày > cutoff. Sửa nguồn của feature,
**không** sửa `FORBIDDEN_COLUMNS` hay bỏ lời gọi kiểm tra.

### Viết phần báo cáo từ output
Lấy số từ `reports/*.md|csv|json`, không tự bịa. Gắn mỗi kết quả với AQ và quyết định (D1/D2/D3).
Nêu rõ: dữ liệu OULAD (Anh 2013–14), KG mô phỏng, liên hệ không phải nhân quả, số liệu proposal là
assumption. Dùng khung Observation → Insight → Evidence → Limitation (`docs/05_data_story.md`).

### Sửa dashboard
`app/dashboard.py` chỉ đọc từ `reports/`. Program Manager và Lecturer **không** được thấy dữ liệu
cá nhân. Mọi nút hành động của Advisor phải ghi `governance.audit`. Không thêm chức năng gửi tin.

## Kiểm tra trước khi kết thúc một tác vụ

Chạy `pytest`, rồi đi qua `references/review_checklist.md`. Báo cho người dùng file nào đã đổi,
output nào cần chạy lại, và phần docs nào cần cập nhật.
