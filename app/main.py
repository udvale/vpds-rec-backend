# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from .routes import router

# Load environment variables
load_dotenv()

app = FastAPI(
    title="AI Component Generator",
    description="Generate React components using AI-powered merging",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5173",   # vite
        "http://127.0.0.1:5173",
        "*",  # Remove in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/")
async def root():
    """Health check endpoint"""
    ai_enabled = bool(os.getenv('OPENAI_API_KEY'))
    return {
        "message": "AI Component Generator API",
        "ai_enabled": ai_enabled,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    """Detailed health check"""
    from .assembler import check_ai_setup
    
    return {
        "status": "healthy",
        "ai_setup": check_ai_setup(),
        "environment": {
            "has_openai_key": bool(os.getenv('OPENAI_API_KEY')),
            "ai_enabled": os.getenv('USE_AI_MERGING', 'true').lower() == 'true'
        }
    }