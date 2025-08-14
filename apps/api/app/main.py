from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import search, wells
import os

app = FastAPI(title="TX Well Lookup API", version="0.1.0")

origins = [origin.strip() for origin in os.getenv("CORS_ORIGINS", "http://localhost:4321").split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}

app.include_router(search.router, prefix="/v1")
app.include_router(wells.router, prefix="/v1")