from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as suggestion_router

app = FastAPI(
    title="VPDS Component Suggestion API",
    description="Suggests Visa Product Design System components based on natural language input.",
)

origins = ["http://localhost:3000"]

# CORS Middleware (adjust origin for your frontend URL in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(suggestion_router, prefix="/api")
