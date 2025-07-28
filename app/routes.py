# app/routes.py
# from fastapi import APIRouter # type: ignore
# from pydantic import BaseModel            # type: ignore # ← add this
# from .assembler import build_snippet

# router = APIRouter(prefix="/api")
# class Query(BaseModel):
#     query: str

# class SnippetResp(BaseModel):
#     success: bool = True
#     snippet: str

# @router.post("/suggest", response_model=SnippetResp)
# def suggest(payload: Query):
#     code = build_snippet(payload.query)
#     return {"success": True, "snippet": code}


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .assembler import build_snippet

router = APIRouter()

class SuggestionRequest(BaseModel):
    query: str

@router.post("/suggest")
async def get_component_suggestions(request: SuggestionRequest):
    try:
        results = build_snippet(request.query)
        return {"success": True, "components": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
