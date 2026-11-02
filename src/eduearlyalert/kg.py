"""GĐ6 – Knowledge Graph quy mô nhỏ (Assessment → Concept → CLO, Resource → Concept).

Khoá ánh xạ là `assessment_key` = loại bài + thứ tự theo hạn nộp trong presentation
(ví dụ TMA1, CMA2). Nhờ vậy một bảng map dùng được cho mọi presentation của module,
không phụ thuộc id_assessment.

Mọi cạnh mang thuộc tính `provenance`. Toàn bộ KG là DỮ LIỆU MÔ PHỎNG.

Output:
  reports/kg_triples.csv          (subject, predicate, object, provenance)
  reports/kg_competency_questions.md
  data/interim/concept_gaps.parquet  (pid × concept: điểm hiệu dụng, có hụt không)
"""

from __future__ import annotations

import networkx as nx
import pandas as pd
import yaml

from .config import Config
from .governance import audit


# ---------------------------------------------------------------------------
# Nạp & dựng đồ thị
# ---------------------------------------------------------------------------
def load_spec(cfg: Config) -> tuple[dict, pd.DataFrame]:
    with open(cfg.root / cfg["kg"]["concepts"], encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    cmap = pd.read_csv(cfg.root / cfg["kg"]["concept_map"])
    unknown = set(cmap["concept_id"]) - set(spec["concepts"])
    if unknown:
        raise ValueError(f"concept_map.csv tham chiếu concept không có trong concepts.yaml: {unknown}")
    return spec, cmap


def build_graph(cfg: Config) -> nx.DiGraph:
    spec, cmap = load_spec(cfg)
    prov = spec.get("provenance", "synthetic")
    g = nx.DiGraph()
    for clo, desc in spec["clos"].items():
        g.add_node(clo, kind="CLO", label=desc)
    for cid, c in spec["concepts"].items():
        g.add_node(cid, kind="Concept", label=c["name"])
        for clo in c["clo"]:
            g.add_edge(cid, clo, rel="SUPPORTS", provenance=prov)
    for a, b in spec.get("prerequisites", []):
        g.add_edge(a, b, rel="PREREQUISITE_OF", provenance=prov)
    for rid, r in spec["resources"].items():
        g.add_node(rid, kind="Resource", label=r["title"])
        for cid in r["concepts"]:
            g.add_edge(rid, cid, rel="COVERS", provenance=prov)
    for row in cmap[cmap["code_module"] == cfg.module].itertuples(index=False):
        node = f"{row.code_module}:{row.assessment_key}"
        g.add_node(node, kind="Assessment", label=row.assessment_key)
        g.add_edge(node, row.concept_id, rel="ASSESSES", weight=float(row.weight), provenance=row.provenance)
    return g


def triples(g: nx.DiGraph) -> pd.DataFrame:
    return pd.DataFrame(
        [{"subject": u, "predicate": d["rel"], "object": v, "provenance": d.get("provenance", "")}
         for u, v, d in g.edges(data=True)]
    )


# ---------------------------------------------------------------------------
# Competency questions (CQ) – các câu KG phải trả lời được
# ---------------------------------------------------------------------------
def cq_concepts_of_assessment(g: nx.DiGraph, assessment_node: str) -> list[str]:
    """CQ1: Bài đánh giá X kiểm tra những concept nào?"""
    return [v for v in g.successors(assessment_node) if g.edges[assessment_node, v]["rel"] == "ASSESSES"]


def cq_resources_for_concept(g: nx.DiGraph, concept: str) -> list[str]:
    """CQ2: Nên gợi ý tài nguyên nào cho concept X?"""
    return [u for u in g.predecessors(concept) if g.edges[u, concept]["rel"] == "COVERS"]


def cq_clos_not_assessed(g: nx.DiGraph) -> list[str]:
    """CQ3: CLO nào chưa có bài đánh giá nào trước mốc dự báo?"""
    assessed = {
        clo
        for a, d in g.nodes(data=True) if d["kind"] == "Assessment"
        for c in cq_concepts_of_assessment(g, a)
        for clo in g.successors(c) if g.edges[c, clo]["rel"] == "SUPPORTS"
    }
    return sorted(n for n, d in g.nodes(data=True) if d["kind"] == "CLO" and n not in assessed)


def cq_prerequisites(g: nx.DiGraph, concept: str) -> list[str]:
    """CQ4: Concept X cần nắm concept nào trước?"""
    return [u for u in g.predecessors(concept) if g.edges[u, concept]["rel"] == "PREREQUISITE_OF"]


def explanation_path(g: nx.DiGraph, assessment_key: str, module: str) -> list[str]:
    """CQ5: Đường giải thích Assessment → Concept → CLO → Resource (dạng chuỗi đọc được)."""
    node = f"{module}:{assessment_key}"
    if node not in g:
        return []
    paths = []
    for c in cq_concepts_of_assessment(g, node):
        clos = [v for v in g.successors(c) if g.edges[c, v]["rel"] == "SUPPORTS"]
        res = cq_resources_for_concept(g, c)
        paths.append(
            f"{assessment_key} → {c} ({g.nodes[c]['label']}) → {', '.join(clos)}"
            f" ⇒ gợi ý: {', '.join(res) or 'chưa có tài nguyên'}"
        )
    return paths


# ---------------------------------------------------------------------------
# Gán concept cho bài đánh giá và tính "concept gap" của từng sinh viên
# ---------------------------------------------------------------------------
def add_assessment_key(long: pd.DataFrame) -> pd.DataFrame:
    """TMA1, TMA2, CMA1... theo thứ tự hạn nộp trong mỗi presentation."""
    order = (
        long[["code_presentation", "id_assessment", "assessment_type", "due_date"]]
        .drop_duplicates()
        .sort_values(["code_presentation", "assessment_type", "due_date", "id_assessment"])
    )
    order["seq"] = order.groupby(["code_presentation", "assessment_type"]).cumcount() + 1
    order["assessment_key"] = order["assessment_type"] + order["seq"].astype(str)
    return long.merge(order[["id_assessment", "assessment_key"]], on="id_assessment", how="left")


def concept_gaps(cfg: Config, long: pd.DataFrame) -> pd.DataFrame:
    """pid × concept: điểm hiệu dụng (bài thiếu = 0) và cờ 'cần hỗ trợ thêm'."""
    _, cmap = load_spec(cfg)
    cmap = cmap[cmap["code_module"] == cfg.module]
    cmap = cmap.rename(columns={"weight": "concept_weight"})[["assessment_key", "concept_id", "concept_weight"]]
    df = add_assessment_key(long).merge(cmap, on="assessment_key", how="inner")
    if df.empty:
        return pd.DataFrame(columns=["pid", "code_presentation", "concept_id", "concept_score", "needs_support"])
    df["eff_score"] = df["score"].fillna(0.0)  # chưa nộp → chưa có bằng chứng nắm concept
    df["w_score"] = df["eff_score"] * df["concept_weight"]
    agg = df.groupby(["pid", "code_presentation", "concept_id"]).agg(w=("concept_weight", "sum"), ws=("w_score", "sum"))
    agg["concept_score"] = agg["ws"] / agg["w"]
    agg["needs_support"] = agg["concept_score"] < cfg["kg"]["pass_threshold"]
    return agg[["concept_score", "needs_support"]].reset_index()


def run(cfg: Config) -> dict:
    g = build_graph(cfg)
    reports, interim = cfg.path("reports_dir"), cfg.path("interim_dir")
    triples(g).to_csv(reports / "kg_triples.csv", index=False)

    long = pd.read_parquet(interim / "assess_long.parquet")
    gaps = concept_gaps(cfg, long)
    gaps.to_parquet(interim / "concept_gaps.parquet", index=False)

    assess_nodes = sorted(n for n, d in g.nodes(data=True) if d["kind"] == "Assessment")
    keys_in_data = sorted(add_assessment_key(long)["assessment_key"].dropna().unique()) if not long.empty else []
    lines = [
        "# Knowledge Graph – Competency Questions (tự sinh)",
        "",
        "> **Dữ liệu mô phỏng.** Ánh xạ trong `kg/` do nhóm tự xây dựng, không phải chương trình thật.",
        "",
        f"- Số node: {g.number_of_nodes()}, số cạnh: {g.number_of_edges()}",
        f"- Bài đánh giá trước mốc dự báo có trong dữ liệu: {keys_in_data}",
        f"- Bài đánh giá đã được ánh xạ trong KG: {[a.split(':')[1] for a in assess_nodes]}",
        "",
        "## CQ1 – Mỗi bài đánh giá kiểm tra concept nào? (CQ5 – đường giải thích)",
        "",
    ]
    for a in assess_nodes:
        for p in explanation_path(g, a.split(":")[1], cfg.module):
            lines.append(f"- {p}")
    lines += ["", "## CQ3 – CLO chưa được đánh giá trước mốc dự báo", "", f"{cq_clos_not_assessed(g) or 'Không có'}", ""]
    lines += ["## CQ4 – Quan hệ tiền đề", ""]
    for n, d in g.nodes(data=True):
        if d["kind"] == "Concept" and cq_prerequisites(g, n):
            lines.append(f"- {n} cần trước: {cq_prerequisites(g, n)}")
    if not gaps.empty:
        rate = gaps.groupby("concept_id")["needs_support"].mean().sort_values(ascending=False)
        lines += ["", "## Tỷ lệ sinh viên cần hỗ trợ thêm theo concept", "",
                  rate.rename("share_needs_support").round(3).to_frame().to_markdown()]
    unmapped = sorted(set(keys_in_data) - {a.split(":")[1] for a in assess_nodes})
    if unmapped:
        lines += ["", f"⚠️ Bài chưa có trong concept_map.csv: {unmapped} – bổ sung để AQ6/AQ11 đầy đủ."]
    (reports / "kg_competency_questions.md").write_text("\n".join(lines), encoding="utf-8")
    audit(cfg, "kg", nodes=g.number_of_nodes(), edges=g.number_of_edges())
    return {"graph": g, "gaps": gaps}
