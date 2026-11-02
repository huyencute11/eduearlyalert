# data/

| Thư mục | Nội dung | Commit? |
|---|---|---|
| `raw/` | 7 file CSV gốc của OULAD (hoặc dữ liệu giả từ `scripts/make_fake_oulad.py`) | ❌ |
| `interim/` | DuckDB, cohort (còn `id_student`), bảng nhạy cảm, bảng trung gian | ❌ |
| `processed/` | features đã pseudonymize, mô hình, dự báo | ❌ |

Cách lấy dữ liệu: xem `docs/02_data.md`. Mỗi thành viên tự tải về máy.
`data/interim/sensitive.parquet` chỉ được đọc bởi `fairness.py`.
