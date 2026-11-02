"""Fixture: sinh dữ liệu GIẢ (schema OULAD) vào thư mục tạm và chạy toàn bộ pipeline 1 lần."""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from eduearlyalert.config import load_config  # noqa: E402
from eduearlyalert.pipeline import main as pipeline_main  # noqa: E402


@pytest.fixture(scope="session")
def cfg(tmp_path_factory):
    root = tmp_path_factory.mktemp("edu")
    shutil.copy(ROOT / "config.yaml", root / "config.yaml")
    shutil.copytree(ROOT / "kg", root / "kg")
    subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "make_fake_oulad.py"),
         "--out", str(root / "data" / "raw"), "--students", "200", "--seed", "11"],
        check=True,
    )
    return load_config(root / "config.yaml")


@pytest.fixture(scope="session")
def pipeline_done(cfg):
    pipeline_main(["--config", str(cfg.root / "config.yaml"), "all"])
    return cfg
