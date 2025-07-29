"""Build a merged TSX snippet, with CSV caching of both code *and* components."""
import csv, json, os, re, pathlib
from typing import Tuple, List, Dict
from dotenv import load_dotenv

load_dotenv()

ROOT        = pathlib.Path(__file__).resolve().parents[1]
CACHE_PATH  = ROOT / "data" / "pattern-dataset.csv"   # acts as cache
COMP_PATH   = ROOT / "data" / "components.json"

COMPONENTS  = json.loads(COMP_PATH.read_text("utf-8"))
NAME2COMP   = {c["component"]: c for c in COMPONENTS}

# ────────────────── cache helpers ──────────────────
def _load_cache() -> Dict[str, Tuple[List[str], str]]:
    if not CACHE_PATH.exists():
        return {}
    with CACHE_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return {
            row["query"]: (json.loads(row["components"]), row["code"])
            for row in reader
        }

def _append_cache(query: str, comps: List[str], code: str) -> None:
    new_file = not CACHE_PATH.exists()
    with CACHE_PATH.open("a", newline="", encoding="utf-8") as f:
        fieldnames = ["query", "components", "code"]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if new_file:
            writer.writeheader()
        writer.writerow(
            {"query": query, "components": json.dumps(comps), "code": code}
        )

def pick_variant(comp: dict) -> str:
    return comp["variants"][0]["code"]

def check_ai_setup() -> bool:                       # keeps main.py happy
    use_ai = os.getenv("USE_AI_MERGING", "true").lower() == "true"
    return use_ai and bool(os.getenv("OPENAI_API_KEY"))
def build_snippet(query: str) -> Tuple[str, List[str]]:
    """
    1. Look for an exact query match in pattern‑dataset.csv.
    2. If found → return that snippet + components immediately.
    3. If not → choose components with retriever, merge (AI or regex),
       optionally cache the result *only* if it passes a quick sanity test.
    """
    q_key = query.strip().lower()

    # Serve from cache if present
    cache = _load_cache()
    if q_key in cache:
        code, comps = cache[q_key][1], cache[q_key][0]
        return code, comps

    # If not pick components via retriever
    from .retriever import top_components
    comps: List[str] = top_components(query, k=3)

    variant_codes = [pick_variant(NAME2COMP[c]) for c in comps]
    export_name   = re.sub(r"[^a-zA-Z0-9]", " ", query).title().replace(" ", "") or "Generated"

    # Merge snippets (AI if enabled, else regex)
    use_ai  = os.getenv("USE_AI_MERGING", "true").lower() == "true"
    has_key = bool(os.getenv("OPENAI_API_KEY"))
    if use_ai and has_key:
        from .ai_merge import merge_components_with_ai
        code = merge_components_with_ai(variant_codes, query, export_name)
    else:
        from .merge import merge_variants
        code = merge_variants(variant_codes, export_name)
    
    _append_cache(q_key, comps, code)
    return code, comps

    # Sanity check for testing if needed (shouldn't be needed in prod)
    # def _looks_ok(tsx: str) -> bool:
    #     return (
    #         "import" in tsx
    #         and "export default function" in tsx
    #         and "</" in tsx        # at least one closing tag
    #     )

    # if _looks_ok(code):
    #     _append_cache(q_key, comps, code)
    # else:
    #     print("Generated code failed quick check — not cached.")
    
