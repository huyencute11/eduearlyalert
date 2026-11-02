# Checklist trước khi commit / khi review PR

## Leakage & đánh giá
- [ ] Feature mới chỉ dùng dữ liệu ngày ≤ cutoff; đã cập nhật `model_feature_columns` và meta ngày
- [ ] Không chọn ngưỡng/mô hình/feature dựa trên tập test
- [ ] EDA không dùng tập test
- [ ] Có so sánh với baseline `rule` và `logistic`

## Governance
- [ ] Không có thuộc tính nhạy cảm trong feature (test `test_leakage.py` pass)
- [ ] Không có `id_student` trong `data/processed/` và `reports/`
- [ ] Không có chức năng tự động liên hệ sinh viên
- [ ] Ngôn ngữ hỗ trợ; không "gây ra/tác động" trong phần diagnostic
- [ ] Dữ liệu mô phỏng được gắn nhãn

## Traceability & tài liệu
- [ ] Hình mới có tiêu đề `AQx ·` và tên file `aqX_*.png`
- [ ] `docs/02_data.md` / `docs/03_pipeline.md` đã cập nhật nếu đổi feature/bước
- [ ] Tham số mới nằm trong `config.yaml`
- [ ] `pytest` pass; không commit `data/`, `.env`, output notebook
