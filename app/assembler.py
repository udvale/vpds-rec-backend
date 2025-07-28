import csv, ast, json, re
from pathlib import Path
from .merge import merge_variants        # ← you already have this

ROOT = Path(__file__).resolve().parents[1]          # vpds‑rec‑backend/
csv_path   = ROOT / "data" / "pattern-dataset.csv"
json_path  = ROOT / "data" / "components.json"

# --------------------------------------------------------------------
# 1) pattern‑dataset.csv  →  PATTERN2COMP dict
# --------------------------------------------------------------------
PATTERN2COMP: dict[str, list[str]] = {}

with csv_path.open(newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    next(reader, None)                      # ← skip header
    for query, components in reader:
        PATTERN2COMP[query.strip().lower()] = ast.literal_eval(components)

# --------------------------------------------------------------------
# 2) components.json  →  NAME2COMP lookup
# --------------------------------------------------------------------
COMPONENTS  = json.loads(json_path.read_text(encoding="utf-8"))
NAME2COMP   = {c["component"]: c for c in COMPONENTS}

def pick_variant(comp: dict) -> str:
    """very simple: first variant"""
    return comp["variants"][0]["code"]

def build_snippet(query: str) -> str:
    comps = PATTERN2COMP.get(query.lower())
    if not comps:
        return "// unknown pattern"

    variant_codes = [pick_variant(NAME2COMP[name]) for name in comps]
    exported_name = re.sub(r"[^a-zA-Z0-9]", " ", query).title().replace(" ", "")
    return merge_variants(variant_codes, exported_name or "Generated")
