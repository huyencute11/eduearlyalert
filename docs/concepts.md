# Concepts – thuật ngữ dùng trong dự án

Đọc file này trước khi code. Khi tranh luận, dùng đúng định nghĩa ở đây.

**Cutoff day / mốc dự báo** – ngày 41 (hết Tuần 6). Mọi dữ liệu dùng để dự báo phải có ngày ≤ 41.
Đây là "thời điểm cố vấn mở dashboard".

**Observation window / outcome window** – cửa sổ quan sát là ngày ≤ 41 (gồm trước ngày 0 nếu bật);
cửa sổ kết quả là đến hết môn (`final_result`).

**Quần thể dự báo (prediction population)** – sinh viên còn theo học tại mốc dự báo. Người đã rút
trước đó không thuộc đối tượng "cảnh báo sớm".

**Leakage** – dùng thông tin mà tại mốc dự báo chưa thể biết (điểm cuối kỳ, ngày rút môn sau mốc,
bài nộp sau ngày 41…). Làm mô hình đẹp trên giấy nhưng vô dụng khi dùng thật.

**Temporal split / hold-out theo presentation** – train trên học kỳ cũ, test trên học kỳ sau, mô
phỏng đúng cách hệ thống được dùng.

**Baseline** – điểm so sánh tối thiểu. Ở đây là luật đơn giản mà cố vấn tự làm được; mô hình phải
tốt hơn rõ mới đáng dùng.

**Recall (Early Detection Recall)** – trong số sinh viên cuối cùng không hoàn thành, bao nhiêu % đã
được cảnh báo tại cuối Tuần 6. **FNR** = 1 − Recall = tỷ lệ bỏ sót.

**Precision** – trong số được cảnh báo, bao nhiêu % thực sự không hoàn thành. Thấp = nhiều báo nhầm,
cố vấn mất thời gian.

**F1** – trung bình điều hoà của Precision và Recall. **PR-AUC** – chất lượng xếp hạng không phụ
thuộc ngưỡng, hợp với dữ liệu lệch lớp.

**Calibration** – xác suất 0.7 có thực sự nghĩa là ~70% không hoàn thành không.

**Coverage@K / Precision@K** – nếu chỉ liên hệ K người đầu danh sách: bắt được bao nhiêu % người cần
hỗ trợ / bao nhiêu % trong K người là đúng. Thước đo của AQ10.

**Năng lực K** – số ca chủ động một cố vấn làm được mỗi tuần (giả định 35). **Assumption**, cần xác nhận.

**Risk tier** – Rất cao (top 10% risk), Cao (top 25%), Theo dõi (còn lại trong danh sách).

**Reason code** – câu giải thích vì sao sinh viên nằm trong danh sách, viết bằng ngôn ngữ hỗ trợ. Là
tín hiệu dữ liệu, **không** phải nguyên nhân.

**Effect size (Cliff's delta)** – độ lớn khác biệt giữa hai nhóm, từ −1 đến 1. Với n lớn, p-value gần
như luôn nhỏ; hãy đọc effect size. |δ| < 0.147 không đáng kể, < 0.33 nhỏ, < 0.474 vừa, còn lại lớn.

**Holm correction** – hiệu chỉnh p-value khi kiểm định nhiều chỉ báo cùng lúc.

**Odds ratio / SD** – trong hồi quy logistic giải thích (AQ5): tăng 1 độ lệch chuẩn của biến thì odds
không hoàn thành nhân lên bao nhiêu lần, *khi giữ các biến khác cố định*. Vẫn chỉ là liên hệ.

**Pseudonymization** – thay `id_student` bằng mã băm có salt. Khác anonymization: ai có salt + id gốc
vẫn nối lại được, nên salt phải giữ bí mật.

**Fairness Gate** – quy tắc: thuộc tính nhạy cảm không được vào mô hình; chỉ dùng sau dự báo để audit.

**Knowledge Graph (KG)** – đồ thị node Assessment, Concept, CLO, Resource với cạnh ASSESSES, SUPPORTS,
COVERS, PREREQUISITE_OF. **Competency question** – câu hỏi KG phải trả lời được (CQ1–CQ5 trong `kg.py`).
**Provenance** – nguồn gốc của mỗi cạnh; ở đây toàn bộ là `synthetic`.

**Concept gap** – điểm hiệu dụng của sinh viên ở một concept < 40 (bài chưa nộp tính 0).

**Human-in-the-loop** – hệ thống chỉ đề xuất; con người phê duyệt trước mọi hành động với sinh viên.

**Observation vs Insight** – observation: cái thấy được trong dữ liệu. Insight: điều đó có nghĩa gì cho
quyết định của một stakeholder cụ thể.

**Two-way / one-way door** – quyết định dễ / khó đảo ngược. D1 (liên hệ ai) là two-way; D3 (mở rộng
chương trình) gần one-way nên cần bằng chứng mạnh hơn (pilot).
