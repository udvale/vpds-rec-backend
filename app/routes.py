from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.nlp import suggest_components

router = APIRouter()

class SuggestionRequest(BaseModel):
    query: str

@router.post("/suggest")
async def get_component_suggestions(request: SuggestionRequest):
    try:
        results = suggest_components(request.query)
        return {"success": True, "components": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
