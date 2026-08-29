from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.core.config import settings
from app.routers import (
    auth, assets, complaints, ai, risk, work_orders,
    contractors, analytics, audit, uploads, satellite, notifications,
)

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="InfraSetu infrastructure management backend",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=settings.upload_dir), name="media")

prefix = "/api"
app.include_router(auth.router, prefix=prefix)
app.include_router(assets.router, prefix=prefix)
app.include_router(complaints.router, prefix=prefix)
app.include_router(ai.router, prefix=prefix)
app.include_router(risk.router, prefix=prefix)
app.include_router(work_orders.router, prefix=prefix)
app.include_router(contractors.router, prefix=prefix)
app.include_router(analytics.router, prefix=prefix)
app.include_router(audit.router, prefix=prefix)
app.include_router(uploads.router, prefix=prefix)
app.include_router(satellite.router, prefix=prefix)
app.include_router(notifications.router, prefix=prefix)


@app.get("/health")
def health():
    return {"status": "ok"}
