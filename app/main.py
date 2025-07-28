from fastapi import FastAPI # type: ignore
from .routes import router

app = FastAPI(title="VPDS Snippet API")
app.include_router(router, prefix="/api")

