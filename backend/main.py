import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from google.adk.cli.fast_api import get_fast_api_app

from services.service import Service
from repos.repo import Repo
from routers import vehicle_service_logs, mechanics, file_upload, voice
from auth_db import Base as AuthBase, engine as auth_engine
from routers.auth import router as auth_router
from services.ml_service import ml_service
from contextlib import asynccontextmanager
from db import PostgresDB

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

ALLOWED_ORIGINS = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

SERVE_WEB_INTERFACE = True

repo = Repo()
service = Service(repo)

AuthBase.metadata.create_all(bind=auth_engine)

app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    allow_origins=[],
    web=SERVE_WEB_INTERFACE,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

app.include_router(
    vehicle_service_logs.router,
    prefix="/vehicle_service_logs",
    tags=["VehicleServiceLogs"],
)

app.include_router(
    mechanics.router,
    prefix="/vehicle_service_logs/api/mechanics",
    tags=["mechanics"],
)

app.include_router(
    file_upload.router,
    prefix="/vehicle_service_logs/api/files",
    tags=["files"],
)

app.include_router(
    voice.router,
    prefix="/vehicle_service_logs/api/voice",
    tags=["voice"],
)

IMAGE_DIR = os.path.join(AGENT_DIR, "service_images")
os.makedirs(IMAGE_DIR, exist_ok=True)

app.mount("/service_images", StaticFiles(directory=IMAGE_DIR), name="service_images")

if not ml_service.is_ready():
    print("[ML] Warning: service_cost_model.pkl not loaded.")

# -------------------- Postgres bootstrap --------------------

@asynccontextmanager
async def lifespan(app):
    await PostgresDB.connect()

    async with PostgresDB.pool.acquire() as conn:
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS vehicle_service_logs (
            id UUID PRIMARY KEY,
            owner_name TEXT,
            owner_phone_number TEXT,
            vehicle_model TEXT,
            vehicle_id TEXT,
            service_date TIMESTAMP,
            service_type TEXT,
            description TEXT,
            mileage INTEGER,
            cost REAL,
            next_service_date TIMESTAMP,
            mechanic_name TEXT
        );
        """)

        await conn.execute("""
        CREATE TABLE IF NOT EXISTS mechanics (
            id UUID PRIMARY KEY,
            name TEXT,
            specialization TEXT,
            contact_number TEXT,
            experience_years INTEGER
        );
        """)

    yield

app.router.lifespan_context = lifespan
# ----------------------------------------------------------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
