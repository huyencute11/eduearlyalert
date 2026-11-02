# Knowledge Graph – Competency Questions (tự sinh)

> **Dữ liệu mô phỏng.** Ánh xạ trong `kg/` do nhóm tự xây dựng, không phải chương trình thật.

- Số node: 27, số cạnh: 40
- Bài đánh giá trước mốc dự báo có trong dữ liệu: ['CMA1', 'CMA2', 'TMA1']
- Bài đánh giá đã được ánh xạ trong KG: ['CMA1', 'CMA2', 'CMA3', 'TMA1', 'TMA2', 'TMA3']

## CQ1 – Mỗi bài đánh giá kiểm tra concept nào? (CQ5 – đường giải thích)

- CMA1 → C01 (Thuật ngữ và khái niệm nền tảng) → CLO1 ⇒ gợi ý: R01, R09
- CMA1 → C02 (Các quan điểm lý thuyết chính) → CLO1, CLO3 ⇒ gợi ý: R02, R09
- CMA2 → C04 (Phương pháp thu thập dữ liệu) → CLO2 ⇒ gợi ý: R04
- CMA2 → C05 (Đọc biểu đồ và số liệu cơ bản) → CLO2, CLO3 ⇒ gợi ý: R05, R06, R09
- CMA3 → C02 (Các quan điểm lý thuyết chính) → CLO1, CLO3 ⇒ gợi ý: R02, R09
- CMA3 → C06 (Lập luận dựa trên bằng chứng) → CLO3 ⇒ gợi ý: R06
- TMA1 → C03 (Đọc hiểu nguồn tài liệu học thuật) → CLO2 ⇒ gợi ý: R03
- TMA1 → C07 (Cấu trúc bài luận học thuật) → CLO4 ⇒ gợi ý: R07
- TMA1 → C08 (Trích dẫn và liêm chính học thuật) → CLO4 ⇒ gợi ý: R08
- TMA2 → C05 (Đọc biểu đồ và số liệu cơ bản) → CLO2, CLO3 ⇒ gợi ý: R05, R06, R09
- TMA2 → C06 (Lập luận dựa trên bằng chứng) → CLO3 ⇒ gợi ý: R06
- TMA2 → C07 (Cấu trúc bài luận học thuật) → CLO4 ⇒ gợi ý: R07
- TMA3 → C06 (Lập luận dựa trên bằng chứng) → CLO3 ⇒ gợi ý: R06
- TMA3 → C08 (Trích dẫn và liêm chính học thuật) → CLO4 ⇒ gợi ý: R08

## CQ3 – CLO chưa được đánh giá trước mốc dự báo

Không có

## CQ4 – Quan hệ tiền đề

- C02 cần trước: ['C01']
- C06 cần trước: ['C03', 'C05']
- C08 cần trước: ['C07']

## Tỷ lệ sinh viên cần hỗ trợ thêm theo concept

| concept_id   |   share_needs_support |
|:-------------|----------------------:|
| C04          |                 0.464 |
| C05          |                 0.464 |
| C03          |                 0.374 |
| C07          |                 0.374 |
| C08          |                 0.374 |
| C01          |                 0.353 |
| C02          |                 0.353 |