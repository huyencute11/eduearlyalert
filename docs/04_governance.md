# 04 · Governance & Responsible Analytics

Áp dụng xuyên suốt, không chỉ ở GĐ8 (Mục 10 đề cương). Cột "Kiểm soát trong code" là
bằng chứng cho phần Governance của Final Report.

## 9 nguyên tắc ↔ cơ chế

| Nguyên tắc | Cơ chế | Kiểm soát trong code |
|---|---|---|
| Purpose limitation | Chỉ phục vụ D1–D3 trong proposal | Scope ở `config.yaml`; không có module dự báo ngoài scope |
| Data minimization | Chỉ lấy cột cần cho AQ | `cohort.py` chọn cột tường minh; `features.parquet` bỏ `id_student`, `date_unregistration` |
| Privacy | Pseudonymize, ẩn nhóm nhỏ, dữ liệu không lên git | `governance.pseudonymize`, `suppress_small_groups`, `.gitignore` |
| Fairness | Thuộc tính nhạy cảm không vào mô hình, chỉ audit | `leakage.assert_no_leakage` (Fairness Gate), `fairness.py` |
| Transparency | Mọi output ghi rõ nguồn, dữ liệu mô phỏng | Chú thích nguồn trên mọi hình; provenance trong KG |
| Explainability | Mỗi cảnh báo kèm lý do | `explain.reason_codes`, KG explanation path |
| Accountability | Biết ai làm gì, khi nào | `reports/audit_log.jsonl` (`governance.audit`) |
| Human oversight | Hệ thống chỉ đề xuất | Risk List `status = pending_review`; nút duyệt trên dashboard |
| Auditability | Tái lập được | `config.yaml` + seed + test + CI |

## Human validation gates

| Gate | Khi nào | Ai | Tiêu chí qua gate |
|---|---|---|---|
| G1 – Data | Sau `audit` | Problem & Data Lead + cả nhóm | Đã điền mục 6 của Data Quality Report |
| G2 – Model | Sau `model` | Modeling + Eval Lead | Đạt/không đạt tiêu chí được ghi rõ; có FN analysis |
| G3 – Fairness | Sau `fairness` | Eval & Governance Lead | Chênh lệch Recall trong ngưỡng đã thống nhất, hoặc có hành động |
| G4 – Từng ca | Mỗi tuần, trên dashboard | Cố vấn | Phê duyệt / bỏ qua kèm ghi chú; không liên hệ khi chưa duyệt |

## Quy tắc ngôn ngữ

Không dùng: "sinh viên yếu/kém", "lười", "học dốt". Dùng: "sinh viên cần hỗ trợ thêm ở concept X",
"chưa nộp bài TMA1 – nên hỏi thăm khó khăn". `governance.check_language` chặn tự động
trong reason codes và Risk List. Trong báo cáo dùng "liên hệ/khác biệt", không dùng "gây ra".

## AI-assisted component (nếu thêm LLM)

| | |
|---|---|
| AI được phép | Diễn đạt lại reason codes + concept gaps thành đoạn gợi ý cho cố vấn |
| AI không được phép | Tạo số liệu mới, đổi risk score, gửi tin cho sinh viên, đọc thuộc tính nhạy cảm |
| Tool | Read-only trên `risk_list.csv` |
| Cần phê duyệt | Mọi nội dung trước khi tới sinh viên |
| Log | Prompt, output, người duyệt → `audit_log.jsonl` |

## Risk register – khởi đầu (≥ 6 rủi ro, nhóm hoàn thiện ở GĐ8)

| # | Rủi ro | Khả năng | Ảnh hưởng | Giảm thiểu | Owner |
|---|---|---|---|---|---|
| R1 | Leakage làm mô hình đẹp giả tạo | TB | Cao | `leakage.py` + test; quần thể dự báo loại người đã rút | Modeling |
| R2 | Bỏ sót sinh viên cần hỗ trợ (FN) | Cao | Cao | Ngưỡng ưu tiên Recall; FN analysis; tầng "Theo dõi" | Modeling |
| R3 | Recall chênh lệch giữa nhóm nhân khẩu | TB | Cao | AQ9 audit; ngưỡng chênh lệch; hành động khi vượt | Eval & Gov |
| R4 | Gán nhãn tiêu cực / kỳ thị | TB | Cao | Quy tắc ngôn ngữ, chỉ cố vấn thấy cá nhân | Eval & Gov |
| R5 | Tự động hoá hành động với sinh viên | Thấp | Cao | Không có chức năng gửi; human gate G4 | Report & Pres |
| R6 | Ngoại suy OULAD sang bối cảnh VN | Cao | TB | Ghi rõ limitation; không khái quát kết luận | Problem & Data |
| R7 | Diễn giải KG mô phỏng như dữ liệu thật | TB | TB | Nhãn "MÔ PHỎNG" trên hình, provenance trong triples | Modeling/KG |
| R8 | Danh sách quá dài so với năng lực cố vấn | Cao | TB | Top-K, phân tầng, AQ12 | Eval & Gov |
| R9 | Rò rỉ dữ liệu qua git / notebook output | TB | TB | `.gitignore`, clear output, salt trong `.env` | Cả nhóm |
