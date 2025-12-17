import os
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from google.adk.cli.fast_api import get_fast_api_app
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME
from routers import vehicle_service_logs, mechanics, file_upload, voice
from auth_db import Base as AuthBase, engine as auth_engine
from routers.auth import router as auth_router
from fastapi.staticfiles import StaticFiles

# 🔹 ML: import the ML service so the model loads at startup
from services.ml_service import ml_service  # <-- ADDED


# ---------- Core setup ----------

repo = Repo(DB_NAME)
service = Service(repo)

AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Explicit CORS origins – must match your Vite dev server
ALLOWED_ORIGINS = [
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

SERVE_WEB_INTERFACE = True

# Make sure auth tables exist in vehicle_service_logs.db
AuthBase.metadata.create_all(bind=auth_engine)

# Get the FastAPI app from Google ADK
# We *won't* rely on its internal CORS; we will add our own middleware.
app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    allow_origins=[],  # let our CORSMiddleware handle it explicitly
    web=SERVE_WEB_INTERFACE,
)

# ---------- CORS middleware (global) ----------

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Auth: /auth/register, /auth/login, /auth/me
app.include_router(auth_router)

# Existing domain routes
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

# Ensure folder exists
IMAGE_DIR = os.path.join(AGENT_DIR, "service_images")
os.makedirs(IMAGE_DIR, exist_ok=True)

# Expose service_images as static
app.mount("/service_images", StaticFiles(directory=IMAGE_DIR), name="service_images")


# 🔹 ML: optional sanity log so you know if model is loaded
if not ml_service.is_ready():  # <-- ADDED
    print("[ML] Warning: service_cost_model.pkl not loaded. Train or place it under backend/ml/")  # <-- ADDED


# ---------- Entrypoint ----------

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
