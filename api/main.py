from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from api.core import settings
from api.routers import projects, toronto

app = FastAPI(
    title="Ontario Build Planning API",
    version="0.1.0",
    description="Public infrastructure portfolio intelligence and procurement radar for Ontario.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
app.include_router(projects.router)
app.include_router(toronto.router)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.app_env}


app.mount("/", StaticFiles(directory=settings.frontend_dir, html=True), name="frontend")
