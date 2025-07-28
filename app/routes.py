# app/routes.py
import os
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from .assembler import build_snippet, check_ai_setup   # <-- still valid

router = APIRouter()

# ─────────── request / response models ───────────
class SuggestionRequest(BaseModel):
    query: str
    use_ai: Optional[bool] = True          # client can force regex path

class SuggestionResponse(BaseModel):
    success: bool
    snippet: str
    components_used: List[str]
    ai_powered: bool
    query: str
    export_name: str

# ─────────── routes ───────────
@router.post("/suggest", response_model=SuggestionResponse)
async def get_component_suggestions(req: SuggestionRequest):
    """
    Generate a React component based on the user's query.
    """
    try:
        snippet, used_components = build_snippet(req.query)

        has_key   = bool(os.getenv("OPENAI_API_KEY"))
        ai_global = os.getenv("USE_AI_MERGING", "true").lower() == "true"
        ai_powered = has_key and ai_global and req.use_ai

        export_name = (
            "".join(word.title() for word in req.query.split()) or "Generated"
        )

        return SuggestionResponse(
            success=True,
            snippet=snippet,
            components_used=used_components,
            ai_powered=ai_powered,
            query=req.query,
            export_name=export_name,
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": str(e),
                "query": req.query,
                "suggestion": "Check your query and try again.",
            },
        )

@router.get("/patterns")
async def get_cached_patterns():
    """
    Return all queries already saved in the CSV cache.
    """
    from .assembler import _load_cache      # local import avoids circular refs
    patterns = list(_load_cache().keys())
    return {"success": True, "patterns": patterns, "count": len(patterns)}

@router.get("/components")
async def get_available_components():
    """
    List every component in components.json with variant counts.
    """
    from .assembler import NAME2COMP
    components = [
        {"name": n, "variants_count": len(c.get("variants", []))}
        for n, c in NAME2COMP.items()
    ]
    return {"success": True, "components": components, "count": len(components)}

@router.get("/status")
async def get_system_status():
    """
    Health + AI setup info.
    """
    return {
        "success": True,
        "ai_setup": check_ai_setup(),
        "environment": {
            "has_openai_key": bool(os.getenv("OPENAI_API_KEY")),
            "ai_enabled": os.getenv("USE_AI_MERGING", "true").lower() == "true",
            "python_version": os.sys.version,
        },
    }

# Development test route (optional)
@router.post("/test")
async def test_component_generation():
    test_query = "login form"
    snippet, comps = build_snippet(test_query)
    return {
        "success": True,
        "test_query": test_query,
        "snippet": snippet,
        "components_used": comps,
    }
