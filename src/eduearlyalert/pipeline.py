"""CLI chạy pipeline.

  python -m eduearlyalert.pipeline all          # chạy toàn bộ
  python -m eduearlyalert.pipeline audit        # chỉ 1 bước
  python -m eduearlyalert.pipeline model explain fairness
  python -m eduearlyalert.pipeline --config path/to/other.yaml all
"""

from __future__ import annotations

import argparse
import sys
import time

from . import audit, cohort, eda, explain, fairness, features, kg, model, prioritize
from .config import load_config

STEPS = {
    "audit": audit.run,          # GĐ3  Data Inventory / Quality
    "cohort": cohort.build,      # GĐ3  Cohort & nhãn
    "features": features.build,  # GĐ3–5 Feature (≤ cutoff) + leakage check
    "kg": kg.run,                # GĐ6  Knowledge Graph mô phỏng
    "eda": eda.run,              # GĐ4  AQ1–AQ6
    "model": model.run,          # GĐ5  AQ7
    "explain": explain.run,      # GĐ6  Explainability
    "fairness": fairness.run,    # GĐ8  AQ9
    "prioritize": prioritize.run,  # AQ10–AQ12
}


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="EduEarlyAlert pipeline")
    p.add_argument("steps", nargs="+", choices=[*STEPS, "all"])
    p.add_argument("--config", default=None)
    a = p.parse_args(argv)
    cfg = load_config(a.config)
    steps = list(STEPS) if "all" in a.steps else a.steps
    for s in steps:
        t0 = time.time()
        print(f"▶ {s} ...", flush=True)
        STEPS[s](cfg)
        print(f"  ✓ {s} ({time.time() - t0:.1f}s)", flush=True)
    print(f"Xong. Xem kết quả trong {cfg.path('reports_dir')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
