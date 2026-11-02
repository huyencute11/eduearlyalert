# EduEarlyAlert 🎓

**Hệ thống cảnh báo sớm rủi ro học tập và gợi ý lộ trình cải thiện**
Đồ án cuối kỳ MTH045 – Khoa học phân tích dữ liệu · Nhóm 3

> Nhận diện sớm (cuối Tuần 6) sinh viên có nguy cơ không hoàn thành môn blended learning,
> xếp thứ tự ưu tiên trong giới hạn năng lực cố vấn, và giải thích lý do kèm concept cần hỗ trợ –
> **mọi đề xuất đều cần con người phê duyệt.**

Dữ liệu: [OULAD](https://analyse.kmi.open.ac.uk/open_dataset) (Open University, Anh, 2013–2014, đã ẩn danh, CC-BY 4.0)
+ Knowledge Graph Concept–CLO–Resource **mô phỏng** do nhóm tự xây dựng.
Mức độ project: Mức 3 (Predictive/Explanatory) + Mức 4 nhẹ (Knowledge Graph).

---

## 1. Bắt đầu nhanh (5 phút)

```bash
git clone <URL-repo-cua-nhom> eduearlyalert
cd eduearlyalert

# Tạo môi trường ảo
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
pip install -e .

cp .env.example .env               # Windows: copy .env.example .env  → sửa EDU_SALT (cả nhóm dùng chung)
```

**Chạy thử ngay với dữ liệu giả** (chưa cần tải OULAD):

```bash
python scripts/make_fake_oulad.py --out data/raw
python -m eduearlyalert.pipeline all
streamlit run app/dashboard.py
```

> ⚠️ Dữ liệu giả chỉ để kiểm tra code chạy. Trước khi phân tích thật, **xoá `data/raw/*`** và đặt OULAD vào.

**Chạy với OULAD thật:** tải zip ở trang chính thức, giải nén 7 file CSV vào `data/raw/`
(chi tiết: [`docs/02_data.md`](docs/02_data.md)), rồi:

```bash
python -m eduearlyalert.pipeline audit     # xem reports/module_presentation_counts.csv để chốt module
# sửa config.yaml › scope nếu cần, rồi:
python -m eduearlyalert.pipeline all
```

Có `make`? Dùng `make setup`, `make fake`, `make pipeline`, `make test`, `make dashboard`.

## 2. Pipeline

```
audit → cohort → features → kg → eda → model → explain → fairness → prioritize → dashboard
 GĐ3     GĐ3      GĐ3–5     GĐ6   GĐ4    GĐ5     GĐ6       GĐ8        GĐ8         GĐ10
          ↑ leakage check tự động ở features & model
```

| Bước | Trả lời | Output chính trong `reports/` |
|---|---|---|
| `audit` | Data quality, chọn module | `data_quality_report.md`, `module_presentation_counts.csv` |
| `cohort` | Nhãn, quần thể, pseudonymize | `cohort_flow.csv` |
| `features` | Feature ≤ ngày 41 | `data/processed/features.parquet`, `feature_list.json` |
| `kg` | AQ6 · KG mô phỏng | `kg_triples.csv`, `kg_competency_questions.md` |
| `eda` | AQ1–AQ6 · ≥ 8 biểu đồ | `figures/aq1..6_*.png`, `eda_findings.md` |
| `model` | AQ7 · rule → logistic → gboost | `model_results.md`, `figures/aq7_*.png` |
| `explain` | Lý do cảnh báo | `explainability_report.md` |
| `fairness` | AQ9 · Recall theo nhóm | `fairness_report.md` |
| `prioritize` | AQ10–AQ12 · ưu tiên theo năng lực K | `prioritization_report.md`, `risk_list.csv` |

Chạy lẻ: `python -m eduearlyalert.pipeline model explain`. Chi tiết: [`docs/03_pipeline.md`](docs/03_pipeline.md).

## 3. Cấu trúc repo

```
eduearlyalert/
├── README.md                 ← bạn đang đọc
├── CLAUDE.md                 ← quy tắc cho Claude Code / người mới
├── config.yaml               ← MỌI tham số (module, cutoff, K, ngưỡng)
├── requirements.txt · pyproject.toml · Makefile · .env.example
├── .claude/skills/eduearlyalert-pipeline/   ← skill: quy ước & quy trình code
├── .github/workflows/ci.yml  ← test tự động mỗi lần push/PR
├── docs/
│   ├── 01_project_overview.md   (problem, KPI, AQ ↔ code)
│   ├── 02_data.md               (tải OULAD, cohort, data dictionary)
│   ├── 03_pipeline.md           (từng bước, quyết định thiết kế)
│   ├── 04_governance.md         (9 nguyên tắc, human gates, risk register)
│   ├── 05_data_story.md         (mạch kể, slide, demo)
│   ├── 06_team_workflow.md      (phân vai, git, mốc tuần)
│   ├── concepts.md              (thuật ngữ)
│   └── templates/model_design_card.md
├── kg/                       ← Knowledge Graph MÔ PHỎNG (concepts.yaml, concept_map.csv)
├── src/eduearlyalert/        ← code pipeline
├── app/dashboard.py          ← dashboard Streamlit (PM / Lecturer / Advisor)
├── scripts/make_fake_oulad.py← sinh dữ liệu giả cùng schema
├── tests/                    ← pytest (chạy trên dữ liệu giả)
├── notebooks/                ← khám phá cá nhân
├── data/{raw,interim,processed}/  ← KHÔNG commit
└── reports/                  ← output sinh tự động + figures/
```

## 4. Dashboard

`streamlit run app/dashboard.py`, chọn vai trò ở sidebar:

* **Program Manager** – completion rate, Recall/F1, kịch bản ngưỡng, fairness. Không thấy cá nhân.
* **Lecturer** – tình trạng nộp bài, điểm, concept cần hỗ trợ thêm (tổng hợp).
* **Advisor** – Risk List top-K kèm lý do, concept và tài nguyên gợi ý; nút *Phê duyệt / Bỏ qua /
  Đã liên hệ* ghi vào `reports/audit_log.jsonl`. Không có tin nhắn nào được gửi tự động.

## 5. Quy tắc bắt buộc (tóm tắt – đầy đủ ở `CLAUDE.md` và `docs/04_governance.md`)

1. Feature chỉ dùng dữ liệu đến hết ngày 41; pipeline tự dừng nếu leakage.
2. Giới tính, vùng, khuyết tật, tuổi, imd_band, học vấn **không** vào mô hình – chỉ để audit.
3. Chia train/valid/test theo presentation; không nhìn tập test khi chọn mô hình.
4. Không commit dữ liệu; output chỉ có mã `pid`.
5. Hệ thống chỉ đề xuất – cố vấn phê duyệt mọi hành động.
6. Không gán nhãn tiêu cực ("sinh viên yếu") – dùng "cần hỗ trợ thêm ở concept X".
7. KG và dữ liệu giả phải ghi rõ là mô phỏng; baseline 60%, K = 35 là assumption.

## 6. Làm việc nhóm

* Nhánh `feat/<ten>-<viec>` → Pull Request → 1 người review → merge vào `main`.
* `pytest` phải xanh (CI tự chạy). Đổi `config.yaml` = PR riêng, cả nhóm đồng ý.
* Phân vai, mốc tuần, Definition of Done: [`docs/06_team_workflow.md`](docs/06_team_workflow.md).

**Đẩy repo lên GitHub lần đầu** (trưởng nhóm làm một lần):

```bash
git init
git add .
git commit -m "Khởi tạo EduEarlyAlert pipeline"
git branch -M main
git remote add origin https://github.com/<to-chuc-hoac-user>/eduearlyalert.git
git push -u origin main
```

Sau đó vào *Settings → Collaborators* mời các thành viên; mỗi người `git clone` rồi làm theo Mục 1.

## 7. Dùng với Claude Code

Repo có `CLAUDE.md` và skill `.claude/skills/eduearlyalert-pipeline/`. Mở terminal trong repo và chạy
`claude`; Claude sẽ đọc quy tắc (leakage, fairness, ngôn ngữ, human-in-the-loop) trước khi sửa code.

## 8. Trích dẫn

Kuzilek J., Hlosta M., Zdrahal Z. *Open University Learning Analytics dataset.* Scientific Data 4, 170171 (2017).
doi:10.1038/sdata.2017.171

## Thành viên

Trần Ngọc Thảo Ngân (25C12028) · Trần Thị Minh Huyền (25C12026) · Nguyễn Anh Vũ (25C12017) · Nguyễn Trương Anh Tuấn (25C12037)
