"""Sinh bộ dữ liệu GIẢ có cùng schema với OULAD để:
  * chạy thử pipeline trước khi tải dữ liệu thật,
  * chạy test tự động / CI (GitHub Actions).

KHÔNG dùng dữ liệu này để rút ra kết luận. Mọi số liệu đều ngẫu nhiên.

  python scripts/make_fake_oulad.py --out data/raw --students 400
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

ACTIVITY = ["oucontent", "forumng", "quiz", "resource", "homepage", "subpage", "url", "glossary"]
PRESENTATIONS = {"BBB": ["2013B", "2013J", "2014B", "2014J"], "DDD": ["2013J", "2014J"]}
# (loại, hạn nộp, trọng số) – 3 bài đầu nằm trước ngày 41
ASSESS_PLAN = [("TMA", 19, 10), ("CMA", 22, 5), ("CMA", 40, 5), ("TMA", 54, 20),
               ("CMA", 89, 5), ("TMA", 110, 25), ("TMA", 166, 30), ("Exam", None, 100)]


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


def make(out: Path, n_students: int, seed: int) -> None:
    rng = np.random.default_rng(seed)
    out.mkdir(parents=True, exist_ok=True)
    courses, assessments, vle, info, reg, sassess, svle = [], [], [], [], [], [], []
    next_student, next_assess, next_site = 100000, 1000, 500000

    for module, pres_list in PRESENTATIONS.items():
        n_mod = n_students if module == "BBB" else n_students // 4
        for pres in pres_list:
            length = int(rng.integers(255, 270))
            courses.append((module, pres, length))
            a_ids = []
            for typ, due, w in ASSESS_PLAN:
                assessments.append((module, pres, next_assess, typ, due if due is not None else "?", w))
                a_ids.append((next_assess, typ, due))
                next_assess += 1
            sites = []
            for act in ACTIVITY:
                for _ in range(int(rng.integers(2, 6))):
                    vle.append((next_site, module, pres, act, "?", "?"))
                    sites.append((next_site, act))
                    next_site += 1
            site_ids = np.array([s for s, _ in sites])
            site_w = np.array([{"oucontent": 5, "forumng": 3, "homepage": 3, "quiz": 2}.get(a, 1) for _, a in sites], float)
            site_w /= site_w.sum()

            for _ in range(n_mod):
                sid = next_student
                next_student += 1
                eng, abil = rng.multivariate_normal([0, 0], [[1, 0.5], [0.5, 1]])
                gender = rng.choice(["M", "F"])
                age = rng.choice(["0-35", "35-55", "55<="], p=[0.7, 0.28, 0.02])
                region = rng.choice(["Scotland", "London Region", "Wales", "North Region", "South East Region"])
                disability = rng.choice(["N", "Y"], p=[0.9, 0.1])
                imd = rng.choice(["0-10%", "10-20", "20-30%", "30-40%", "40-50%", "50-60%", "?"])
                edu = rng.choice(["A Level or Equivalent", "Lower Than A Level", "HE Qualification"])
                prev = int(rng.choice([0, 0, 0, 1, 2]))
                credits = int(rng.choice([30, 60, 60, 90, 120]))

                p_fail = sigmoid(-0.2 - 1.3 * eng - 1.0 * abil + 0.3 * prev + rng.normal(0, 0.5))
                if rng.random() < p_fail:
                    result = "Withdrawn" if rng.random() < 0.55 else "Fail"
                else:
                    result = "Distinction" if abil + rng.normal(0, 0.5) > 1.2 else "Pass"
                unreg = "?"
                if result == "Withdrawn":
                    unreg = int(np.clip(rng.gamma(2.0, 45) - 20, -25, length - 10))
                date_reg = int(-rng.integers(5, 150))
                info.append((module, pres, sid, gender, region, edu, imd, age, prev, credits, disability, result))
                reg.append((module, pres, sid, date_reg, unreg))

                last_day = length if unreg == "?" else unreg
                days = np.arange(-10, last_day)
                fading = 1.0 if result != "Withdrawn" else 1 / (1 + np.exp((days - (last_day - 30)) / 10))
                p_active = sigmoid(-0.4 + 1.1 * eng) * fading * (0.6 if result == "Fail" else 1.0)
                active = days[rng.random(len(days)) < p_active]
                for dday in active:
                    n_rows = int(rng.integers(1, 4))
                    for site in rng.choice(site_ids, size=n_rows, p=site_w):
                        svle.append((module, pres, sid, int(site), int(dday), int(rng.poisson(max(1, 3 + 2 * eng)) + 1)))

                for aid, typ, due in a_ids:
                    if typ == "Exam" or (unreg != "?" and unreg < due):
                        continue
                    if rng.random() > sigmoid(1.2 + 1.2 * eng + 0.5 * abil):
                        continue
                    sub = due + int(rng.integers(-6, 2)) if rng.random() > 0.15 else due + int(rng.integers(1, 12))
                    score = int(np.clip(rng.normal(68 + 14 * abil, 12), 0, 100))
                    sassess.append((aid, sid, sub, 0, score if rng.random() > 0.01 else "?"))

    def write(name, rows, cols):
        pd.DataFrame(rows, columns=cols).to_csv(out / f"{name}.csv", index=False)

    write("courses", courses, ["code_module", "code_presentation", "module_presentation_length"])
    write("assessments", assessments, ["code_module", "code_presentation", "id_assessment", "assessment_type", "date", "weight"])
    write("vle", vle, ["id_site", "code_module", "code_presentation", "activity_type", "week_from", "week_to"])
    write("studentInfo", info, ["code_module", "code_presentation", "id_student", "gender", "region",
                                "highest_education", "imd_band", "age_band", "num_of_prev_attempts",
                                "studied_credits", "disability", "final_result"])
    write("studentRegistration", reg, ["code_module", "code_presentation", "id_student", "date_registration", "date_unregistration"])
    write("studentAssessment", sassess, ["id_assessment", "id_student", "date_submitted", "is_banked", "score"])
    write("studentVle", svle, ["code_module", "code_presentation", "id_student", "id_site", "date", "sum_click"])
    print(f"Đã sinh dữ liệu GIẢ vào {out} ({len(info)} sinh viên, {len(svle)} dòng studentVle).")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="data/raw")
    p.add_argument("--students", type=int, default=400, help="số sinh viên mỗi presentation của BBB")
    p.add_argument("--seed", type=int, default=7)
    a = p.parse_args()
    make(Path(a.out), a.students, a.seed)
