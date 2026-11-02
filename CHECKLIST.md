# ✅ EduEarlyAlert – Checklist 7 ngày trước khi nộp

> **Cách dùng:** làm xong việc nào thì đổi `- [ ]` thành `- [x]`, commit với message
> `checklist: <việc vừa xong>`. Gặp vướng thì ghi vào mục **Vướng mắc** ở cuối file.
> Mỗi người chỉ sửa dòng của mình để tránh conflict khi merge.

**Hạn nộp:** `__/__/____` · **Repo:** `<link GitHub>`

## Phân vai

| Mã | Thành viên | Phụ trách |
|---|---|---|
| P1 | _[Tên]_ | Dữ liệu & pipeline (audit, cohort, features) |
| P2 | _[Tên]_ | EDA, Data Story, gom Final Report |
| P3 | _[Tên]_ | Mô hình, KG, giải thích |
| P4 | _[Tên]_ | Fairness, ưu tiên, Governance, Slide + Demo |

**Cắt bỏ** (không làm, ghi vào Limitations): AQ8, thử mốc Tuần 4, LLM, SHAP, clustering.

---

## Ngày 1 – Setup + chốt dữ liệu (cả nhóm phải xong trong ngày)

- [ ] **Tất cả** – clone repo, cài môi trường, chạy `make fake` + `make pipeline` thấy chạy được
  - [ ] P1 · [ ] P2 · [ ] P3 · [ ] P4
- [ ] **Tất cả** – tạo `.env`, dùng CHUNG `EDU_SALT` (gửi riêng, không commit)
- [ ] **P1** – tải OULAD, xoá dữ liệu giả trong `data/raw/`, đặt 7 file CSV vào
- [ ] **P1** – chạy `python -m eduearlyalert.pipeline audit`, đọc `reports/module_presentation_counts.csv`
- [ ] **Cả nhóm** – chốt module (ưu tiên BBB/DDD/FFF, có bài đánh giá trước ngày 41)
  - Module đã chốt: `____` · Train: `____` · Valid: `____` · Test: `____`
- [ ] **P1** – sửa `config.yaml`, push lên `main`, báo group
- [ ] **P1** – chạy `pipeline all` trên dữ liệu thật không lỗi

## Ngày 2 – Nền dữ liệu + KG

- [ ] **P1** – điền mục 6 "Nhận định & xử lý" trong `reports/data_quality_report.md`
- [ ] **P1** – viết Data Inventory (nguồn, format, owner, thời gian, rủi ro)
- [ ] **P1** – rà `docs/02_data.md` làm Data Dictionary; ghi số liệu từ `reports/cohort_flow.csv`
- [ ] **P1** – cập nhật baseline Completion Rate thật vào `docs/01_project_overview.md`
  - Completion rate thật: `____ %`
- [ ] **P3** – sửa `kg/concept_map.csv` đúng các bài của module đã chọn, chạy lại `pipeline kg eda`
- [ ] **P2** – tạo khung Final Report đủ 18 mục (Docs chung), chia ai viết mục nào
- [ ] **P4** – hoàn thiện Risk Register ≥ 6 rủi ro (`docs/04_governance.md`)

## Ngày 3 – Phân tích

- [ ] **P2** – xem các hình EDA, bỏ/sửa hình không nói được gì (cần ≥ 8 hình)
- [ ] **P2** – viết cột **Insight** cho từng hình trong `reports/eda_findings.md`
- [ ] **P3** – đọc `reports/model_results.md`
  - Recall test: `____` (≥ 0.80?) · F1 test: `____` (≥ 0.75?) · Mô hình chính: `____`
  - ⚠️ KHÔNG chỉnh ngưỡng trên tập test
- [ ] **P3** – viết error analysis từ `reports/false_negative_analysis.csv`
- [ ] **P3** – điền `docs/templates/model_design_card.md`
- [ ] **P4** – đọc `reports/fairness_report.md`, chốt ngưỡng chênh lệch Recall, viết nhận định
- [ ] **P4** – chọn ngưỡng cảnh báo (bảng AQ12) và phương án ưu tiên (bảng AQ10)
  - Ngưỡng chọn: `____ %` · Phương án: `____`

## Ngày 4 – Viết tài liệu kỹ thuật

- [ ] **P2** – Data Story 1–2 trang theo 6 chương (`docs/05_data_story.md`)
- [ ] **P2** – Dashboard wireframe = chụp màn hình Streamlit + chú thích
- [ ] **P3** – KG Schema + competency questions + triples ví dụ + provenance
- [ ] **P3** – Explainability Report (nêu rõ reason code ≠ nguyên nhân)
- [ ] **P4** – Evaluation Plan cho từng thành phần (EDA, mô hình, KG, Risk List)
- [ ] **P4** – Governance Plan: 9 nguyên tắc, human gates, quy tắc ngôn ngữ
- [ ] **P4** – AI Component Card = dashboard có bước phê duyệt (không dùng LLM, giải thích vì sao)

## Ngày 5 – Final Report bản đủ

- [ ] **Tất cả** – viết xong mục được giao, dán vào Docs chung trước 18h
  - [ ] P1 · [ ] P2 · [ ] P3 · [ ] P4
- [ ] **P2** – gom 18 mục, thống nhất văn phong, đánh số hình/bảng
- [ ] **Tất cả** – mọi con số trong report lấy từ `reports/`, không gõ tay
- [ ] **Tất cả** – Data + Limitations ghi rõ: OULAD (Anh 2013–14), KG MÔ PHỎNG, chỉ liên hệ
      không nhân quả, 60% và K = 35 là giả định

## Ngày 6 – Slide + demo + rà soát

- [ ] **P4** – 10–15 slide (title → problem → stakeholders → data → AQ → EDA → method →
      results → evaluation → governance → demo → limitations → kết luận → Q&A)
- [ ] **P4** – kịch bản demo: câu hỏi cố vấn → Risk List → đọc lý do → Phê duyệt → audit log
- [ ] **P4** – quay video demo dự phòng 2–3 phút
- [ ] **P2 + P3** – đọc chéo report, sửa lỗi
- [ ] **Tất cả** – tập trình bày; mỗi người giải thích được toàn bộ project
  - [ ] P1 · [ ] P2 · [ ] P3 · [ ] P4
- [ ] **Tất cả** – điền Peer Review Form cho nhóm được phân công

## Ngày 7 – Chốt & nộp

- [ ] **P1** – chạy lại `pipeline all` + `pytest` lần cuối trên bản code cuối
- [ ] **P1** – kiểm tra không có `id_student` / dữ liệu thô trong repo và report
- [ ] **P2** – xuất Final Report PDF
- [ ] **Tất cả** – điền Checklist tự đánh giá (Mục 11 đề cương)
- [ ] **Trưởng nhóm** – nộp bài

---

## 📦 Danh sách nộp cuối (đối chiếu Mục 8 đề cương)

| Sản phẩm | Nguồn trong repo | Xong |
|---|---|---|
| Final Report 18 mục (PDF) | Docs chung | ☐ |
| Slide 10–15 trang | – | ☐ |
| Demo (trực tiếp + video dự phòng) | `app/dashboard.py` | ☐ |
| Data Inventory, Data Dictionary, Data Quality Report | `docs/02_data.md`, `reports/data_quality_report.md` | ☐ |
| ≥ 8 hình EDA + bảng Observation–Insight–Evidence–Limitation | `reports/eda_findings.md`, `reports/figures/` | ☐ |
| Model Design Card | `docs/templates/model_design_card.md` | ☐ |
| KG Schema + Explainability Report | `reports/kg_competency_questions.md`, `reports/explainability_report.md` | ☐ |
| Evaluation Plan, Risk Register, Governance Plan | `docs/04_governance.md` | ☐ |
| Peer Review Form | – | ☐ |
| Checklist tự đánh giá | – | ☐ |
| Link GitHub repo | – | ☐ |

> Bảng này đổi `☐` thành `☑` khi xong.

## ⚠️ Luật chung

- Sau ngày 1 không ai push thẳng `main` – làm nhánh riêng, nhờ 1 người duyệt.
- Kẹt quá 1 tiếng thì báo group ngay.
- Không viết "sinh viên yếu", không viết "gây ra" – dùng "cần hỗ trợ thêm", "có liên hệ với".

---

## 🚧 Vướng mắc (ghi ngày – người – vấn đề – trạng thái)

| Ngày | Người | Vấn đề | Trạng thái |
|---|---|---|---|
| | | | |

## 📝 Nhật ký tiến độ

| Ngày | Đã xong | Còn lại |
|---|---|---|
| Ngày 1 | | |
| Ngày 2 | | |
| Ngày 3 | | |
| Ngày 4 | | |
| Ngày 5 | | |
| Ngày 6 | | |
| Ngày 7 | | |
