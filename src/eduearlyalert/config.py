"""Đọc config.yaml và cung cấp đường dẫn tuyệt đối cho toàn pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Config:
    raw: dict[str, Any]
    root: Path

    # ---- truy cập nhanh ----------------------------------------------------
    def __getitem__(self, key: str) -> Any:
        return self.raw[key]

    def path(self, key: str) -> Path:
        """Đường dẫn tuyệt đối từ mục `paths` (tự tạo thư mục cha)."""
        p = self.root / self.raw["paths"][key]
        target_dir = p if p.suffix == "" else p.parent
        target_dir.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def module(self) -> str:
        return self.raw["scope"]["module"]

    @property
    def cutoff_day(self) -> int:
        return int(self.raw["timeline"]["cutoff_day"])

    @property
    def seed(self) -> int:
        return int(self.raw["project"]["seed"])

    @property
    def sensitive(self) -> list[str]:
        return list(self.raw["fairness"]["sensitive_attributes"])

    def presentations(self, split: str | None = None) -> list[str]:
        pres = self.raw["scope"]["presentations"]
        if split is None:
            return [p for s in ("train", "valid", "test") for p in pres[s]]
        return list(pres[split])

    def split_of(self, presentation: str) -> str:
        for s in ("train", "valid", "test"):
            if presentation in self.raw["scope"]["presentations"][s]:
                return s
        return "unused"


def load_config(path: str | Path | None = None) -> Config:
    """Ưu tiên: tham số > biến môi trường EDU_CONFIG > config.yaml ở gốc repo."""
    path = Path(path or os.environ.get("EDU_CONFIG", PROJECT_ROOT / "config.yaml"))
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)
    root = Path(os.environ.get("EDU_ROOT", path.resolve().parent))
    return Config(raw=raw, root=root)
