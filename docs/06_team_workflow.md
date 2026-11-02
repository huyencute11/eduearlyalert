# 06 · Quy trình làm việc nhóm

## Phân vai (theo đề cương Mục 3)

| Vai trò | Phụ trách code/tài liệu | Thành viên |
|---|---|---|
| Problem & Data Lead | `audit.py`, `cohort.py`, `features.py`, `docs/02_data.md` | _điền_ |
| Analytics/EDA Lead | `eda.py`, `eda_findings.md` (Insight), data story | _điền_ |
| Modeling/KG Lead | `model.py`, `explain.py`, `kg.py`, `kg/` | _điền_ |
| Evaluation & Governance Lead | `fairness.py`, `prioritize.py`, `docs/04_governance.md` | _điền_ |
| Report & Presentation Lead | `app/dashboard.py`, slide, Final Report | _điền_ |

Một người có thể giữ nhiều vai; ai cũng phải chạy được toàn pipeline và giải thích được mọi phần.

## Git

* `main` luôn chạy được (`pytest` xanh). Không push thẳng lên `main`.
* Nhánh: `feat/<ten>-<viec>`, ví dụ `feat/vu-aq5-regression`, `fix/ngan-cohort-filter`.
* Commit nhỏ, message tiếng Việt hoặc Anh đều được, nêu rõ AQ: `AQ4: thêm Cliff's delta`.
* Mở Pull Request, ít nhất **1 người khác review**. CI tự chạy test với dữ liệu giả.
* Đổi `config.yaml` (module, cutoff, K…) = PR riêng, ghi lý do, cả nhóm đồng ý.

## Definition of Done cho một PR

- [ ] `pytest` pass
- [ ] Không commit dữ liệu, `.env`, output notebook
- [ ] Feature/bước mới đã cập nhật `docs/`
- [ ] Biểu đồ mới có tiêu đề gắn AQ và dòng nguồn dữ liệu
- [ ] Không có ngôn ngữ gán nhãn tiêu cực / nhân quả

## Mốc theo tuần (đề cương Mục 7)

| Tuần | Mốc nộp | Lệnh / file liên quan |
|---|---|---|
| 3 | Data Inventory, Dictionary, Quality Report | `pipeline audit cohort features` → `data_quality_report.md`, `docs/02_data.md` |
| 4–5 | EDA ≥ 8 biểu đồ + wireframe + Data Story | `pipeline kg eda` → `eda_findings.md`, `docs/05_data_story.md` |
| 6 | Model Design Card + baseline | `pipeline model` → `docs/templates/model_design_card.md` |
| 7 | KG Schema / Explainability | `pipeline explain` → `kg_competency_questions.md`, `explainability_report.md` |
| 8 | AI Component Card + prototype | `app/dashboard.py` (+ LLM tuỳ chọn) |
| 9 | Evaluation Plan, Risk Register, Governance | `pipeline fairness prioritize`, `docs/04_governance.md` |
| 10–11 | Final Report, slide, demo | `reports/` + dashboard |

## Commit output khi nộp bài

Mặc định `reports/` được commit (trừ `audit_log.jsonl`, `risk_list*.csv`). Trước khi nộp:
chạy `pipeline all` trên dữ liệu thật, kiểm tra không có `id_student` trong file nào, rồi commit
hình và báo cáo `.md`.
