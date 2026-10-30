"""
FastAPI Server Entry Point for AI Multi-Language Transpiler.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as api_router
from .database.db import init_db

app = FastAPI(
    title="UniversalTranspiler",
    description="Full-stack academic compiler pipeline with AI error detection and auto-correction.",
    version="1.0.0"
)

# Enable CORS for web frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize SQLite database
init_db()

# Mount API routes under /api
app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {
        "status": "online",
        "app": "UniversalTranspiler",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}
