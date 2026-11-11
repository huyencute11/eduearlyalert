"""Nội dung do NHÓM viết, được ghép vào report tự sinh (không bị ghi đè khi chạy lại pipeline).

Input:
  docs/data_quality_notes.md  → mục 6 của reports/data_quality_report.md (audit.py)
  docs/eda_insights.md        → cột Insight của reports/eda_findings.md (eda.py)

Định dạng eda_insights.md: mỗi insight nằm dưới một heading `## <tên file hình>`, ví dụ
`## aq1_outcomes_by_presentation.png`. Khoá là tên hình vì nó ổn định giữa các lần chạy,
còn số thứ tự mục thì không.
"""

from __future__ import annotations

import re
from pathlib import Path

from .governance import check_language

_HEADING = re.compile(r"^##\s+(\S+\.png)\s*$")


class LanguageRuleError(ValueError):
    """Nội dung nhóm viết vi phạm quy tắc ngôn ngữ hỗ trợ (CLAUDE.md quy tắc 6)."""


def _strip_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def _check(source: Path, texts: list[str]) -> None:
    bad = check_language(texts)
    if bad:
        raise LanguageRuleError(f"{source}: vi phạm quy tắc ngôn ngữ, sửa lại câu: {bad}")


def load_section(path: Path) -> str | None:
    """Trả về toàn bộ nội dung file (bỏ comment HTML), hoặc None nếu file không có/rỗng."""
    if not path.exists():
        return None
    text = _strip_comments(path.read_text(encoding="utf-8")).strip()
    if not text:
        return None
    _check(path, [text])
    return text


def load_insights(path: Path) -> dict[str, str]:
    """{tên file hình: insight}. Insight nhiều dòng được nối thành 1 dòng (nằm trong ô bảng)."""
    if not path.exists():
        return {}
    insights: dict[str, list[str]] = {}
    current: str | None = None
    for line in _strip_comments(path.read_text(encoding="utf-8")).splitlines():
        m = _HEADING.match(line)
        if m:
            current = m.group(1)
            if current in insights:
                raise ValueError(f"{path}: hình '{current}' xuất hiện hai lần")
            insights[current] = []
        elif line.startswith("#"):
            current = None  # heading khác (tiêu đề file, ghi chú) không thuộc hình nào
        elif current is not None and line.strip():
            insights[current].append(line.strip().replace("|", "\\|"))
    out = {fig: " ".join(parts) for fig, parts in insights.items() if parts}
    _check(path, list(out.values()))
    return out
