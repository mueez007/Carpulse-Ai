import os
import uvicorn
from google.adk.cli.fast_api import get_fast_api_app
from services.service import Service
from routers import vehicle_service_logs, mechanics
from repos.repo import Repo
from constants import DB_NAME

repo = Repo(DB_NAME)
service = Service(repo)

# Get the directory where main.py is located
AGENT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure allowed origins for CORS - Add your domains here
ALLOWED_ORIGINS = [
    "*"  # Only use this for development - remove for production
]

# Set web=True if you intend to serve a web interface, False otherwise
SERVE_WEB_INTERFACE = True

# Call the function to get the FastAPI app instance
app = get_fast_api_app(
    agents_dir=AGENT_DIR,
    allow_origins=ALLOWED_ORIGINS,
    web=SERVE_WEB_INTERFACE,
)

# Consistent router prefixes - both use /vehicle_service_logs prefix
app.include_router(vehicle_service_logs.router, prefix="/vehicle_service_logs", tags=["VehicleServiceLogs"])
app.include_router(mechanics.router, prefix="/vehicle_service_logs/api/mechanics", tags=["mechanics"])

if __name__ == "__main__":
    # Use the PORT environment variable provided by Cloud Run, defaulting to 8080
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))