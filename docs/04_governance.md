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

## Fairness audit AQ9 – nhận định (G3)

> **BẢN NHÁP – P4 cần rà và chốt.** Claude soạn ngày 11/11/2026 từ `reports/fairness_report.md` và
> `reports/fairness_by_group.csv` (FFF, tập test, Recall chung 0,805). Ngưỡng đề xuất dưới đây là gợi ý,
> P4 và cả nhóm cần quyết định.

**Vấn đề khi đọc bảng:** `min_group_size = 10` tính theo số sinh viên, nhưng Recall chỉ được tính trên số
sinh viên y=1 của nhóm. Nhiều nhóm chỉ có vài chục, thậm chí vài sinh viên y=1, nên Recall dao động rất mạnh.
Ví dụ, với 44 sinh viên y=1 và Recall khoảng 0,8, sai số chuẩn khoảng 0,06, tức khoảng tin cậy 95% rộng chừng ±0,12.

| Thuộc tính | Chênh lệch trong report | Nhận định |
|---|---:|---|
| `highest_education` | 0,33 | Do hai nhóm rất nhỏ: Post Graduate (n = 13, khoảng 3 sinh viên y=1, Recall 0,67) và No Formal quals (n = 10, khoảng 4 sinh viên y=1, Recall 1,0). Ba nhóm lớn chỉ chênh 0,78–0,83, khoảng 0,04 |
| `region` | 0,19 | Thấp nhất East Anglian (0,705, 44 y=1), cao nhất South West (0,896, 48 y=1). Cả hai nhóm đều nhỏ, nên chênh lệch còn trong vùng dao động ngẫu nhiên. Cần theo dõi, chưa đủ bằng chứng để kết luận |
| `imd_band` | 0,18 | Thấp nhất 30–40% (0,714, 77 y=1), cao nhất là nhóm "Không rõ" (0,895, chỉ 19 y=1). Không thấy xu hướng theo mức thiếu thốn: nhóm 0–10% có 0,824 |
| `gender` | 0,08 | F 0,736 (n = 345, khoảng 121 y=1) so với M 0,819 (n = 1.489). Hai nhóm đủ lớn, nên đây là **chênh lệch đáng chú ý nhất**: mô hình bỏ sót sinh viên nữ nhiều hơn (FNR 0,26 so với 0,18). FFF có ít sinh viên nữ (19%) |
| `age_band`, `disability` | ≤ 0,01 | Không có chênh lệch đáng kể. Nhóm 55+ (n = 9) đã bị ẩn |

**Ngưỡng đề xuất (P4 chốt):** chênh lệch Recall > 0,10 giữa hai nhóm **cùng có ≥ 30 sinh viên y=1** thì
phải có hành động. Nhóm nhỏ hơn chỉ báo cáo, không kết luận. Theo ngưỡng này, chưa thuộc tính nào vượt; `gender`
(0,08) gần ngưỡng nhất và nên ghi vào báo cáo.

**Hành động đề xuất:** (1) Ghi rõ chênh lệch theo `gender` trong Final Report và Limitations. (2) Không đưa
thuộc tính nhạy cảm vào mô hình để "sửa" (Fairness Gate). Thay vào đó, khi cố vấn duyệt Risk List, xem thêm
danh sách gần ngưỡng (tầng "Theo dõi"). (3) Báo cáo khoảng tin cậy Recall theo nhóm. Đây là việc cần sửa
`fairness.py` và có thể làm sau.

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
| R10 | Thiết kế môn/bài đánh giá thay đổi giữa các lượt, làm mô hình học ở lượt cũ không còn đúng ở lượt mới (đã xảy ra: BBB 2014J có TMA đầu kỳ trọng số 0, Recall giảm từ 0.80 trên valid xuống 0.53 trên test) | TB | Cao | Bước audit so sánh `assessments` giữa các lượt trước khi chạy mô hình; chọn FFF vì thiết kế ổn định; khi triển khai thì huấn luyện lại mỗi lượt | Problem & Data |
| R11 | Precision thấp nên cố vấn mất công liên hệ những người không cần hỗ trợ (FFF test: F1 0.66 < 0.75, precision khoảng 0.56) | Cao | TB | Không chỉnh ngưỡng trên test; dùng Top-K và phân tầng (AQ10, AQ12) để giới hạn khối lượng; ghi rõ là "chưa đạt" trong report | Modeling + Eval & Gov |

> **BẢN NHÁP – P4 cần rà.** R10 và R11 do Claude thêm ngày 11/11/2026 từ `reports/model_results.md` (module FFF)
> và lần chạy thử BBB. Với R3, kết quả FFF hiện có chênh lệch Recall lớn nhất ở `highest_education` (0.33),
> `region` (0.19) và `imd_band` (0.18) (`reports/fairness_report.md`). P4 cần chốt ngưỡng chênh lệch chấp nhận được (Ngày 3).
