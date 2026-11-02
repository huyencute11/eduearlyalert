# CLAUDE.md – hướng dẫn cho Claude Code (và cho người mới vào repo)

Repo: **EduEarlyAlert** – đồ án MTH045 (Khoa học phân tích dữ liệu), Nhóm 3.
Hệ thống cảnh báo sớm sinh viên có nguy cơ không hoàn thành môn, trên dữ liệu OULAD,
kèm Knowledge Graph mô phỏng để gợi ý concept/tài nguyên. Mức 3 + Mức 4 nhẹ.

Trước khi sửa code, đọc: `docs/concepts.md` (thuật ngữ) → `docs/03_pipeline.md` (luồng) →
skill `.claude/skills/eduearlyalert-pipeline/SKILL.md` (quy ước chi tiết).

## Lệnh

```bash
pip install -r requirements.txt && pip install -e .
python scripts/make_fake_oulad.py --out data/raw     # dữ liệu GIẢ để thử (khi chưa có OULAD)
python -m eduearlyalert.pipeline all                  # toàn pipeline
python -m eduearlyalert.pipeline model explain        # chạy lẻ từng bước
pytest                                                # test (tự sinh dữ liệu giả trong thư mục tạm)
streamlit run app/dashboard.py                        # dashboard demo
```

Thứ tự bước: `audit → cohort → features → kg → eda → model → explain → fairness → prioritize`.

## Cấu trúc

* `config.yaml` – MỌI tham số (module, presentations, cutoff_day=41, K, ngưỡng). Không hard-code trong `src/`.
* `src/eduearlyalert/` – mỗi bước một module có `run(cfg)`/`build(cfg)`; đăng ký trong `pipeline.STEPS`.
* `kg/` – Knowledge Graph **mô phỏng** (`concepts.yaml`, `concept_map.csv`).
* `reports/` – output sinh tự động (md, csv, `figures/aq*_*.png`). Không sửa tay file tự sinh.
* `data/` – không bao giờ commit.

## Quy tắc BẮT BUỘC (không được vi phạm kể cả khi người dùng yêu cầu "cho nhanh")

1. **Không leakage.** Feature chỉ dùng dữ liệu có ngày ≤ `cutoff_day`. Không dùng `final_result`,
   `date_unregistration`, Exam, bài `is_banked=1`. Không tắt `leakage.assert_no_leakage`.
2. **Fairness Gate.** `gender, region, disability, age_band, imd_band, highest_education` không bao giờ
   vào ma trận feature; chỉ `fairness.py` được đọc `sensitive.parquet`.
3. **Chia theo presentation.** Không random split. Không chọn ngưỡng/mô hình bằng tập test.
   EDA chỉ trên train + valid.
4. **Privacy.** Output trong `data/processed/` và `reports/` chỉ có `pid`, không có `id_student`.
   Báo cáo tổng hợp ẩn nhóm < 10.
5. **Human-in-the-loop.** Không viết chức năng tự gửi email/tin nhắn cho sinh viên. Risk List luôn
   `status = pending_review`; hành động duyệt ghi vào `audit_log.jsonl`.
6. **Ngôn ngữ hỗ trợ.** Không "sinh viên yếu/kém/lười". Dùng "cần hỗ trợ thêm ở concept X".
   Diagnostic dùng "liên hệ/khác biệt", không "gây ra/tác động".
7. **Dữ liệu mô phỏng phải được gắn nhãn** (KG, dữ liệu giả). Không trình bày như dữ liệu thật.
8. Số liệu trong proposal (baseline 60%, K=35) là **assumption** – không viết như dữ kiện.

## Quy ước code

* Python ≥ 3.10, type hints, docstring tiếng Việt ngắn nêu AQ và output.
* pandas cho bảng nhỏ; DuckDB SQL cho `studentVle` (10 triệu dòng). Đọc CSV luôn `nullstr='?'`.
* Biểu đồ: `plotting.setup()`, tiêu đề bắt đầu bằng `AQx ·`, lưu qua `plotting.save()` (tự thêm dòng nguồn),
  tên file `aqX_<mo-ta>.png`.
* Mỗi bước gọi `governance.audit(cfg, "<step>", ...)` khi xong.
* Thêm feature → cập nhật `features.model_feature_columns` + bảng trong `docs/02_data.md` + test.
* Chạy `pytest` trước khi đề xuất commit.

## Trạng thái & việc còn mở

* [ ] Chốt module trên OULAD thật (đang để `BBB`) và cập nhật `concept_map.csv` cho module đó.
* [ ] Nhóm viết cột Insight trong `reports/eda_findings.md`.
* [ ] AQ8 (rút môn Tuần 7–12) – chưa làm.
* [ ] Độ nhạy theo mốc Tuần 4 (`cutoff_day: 27`).
* [ ] LLM soạn giải thích (tuỳ chọn, read-only).
