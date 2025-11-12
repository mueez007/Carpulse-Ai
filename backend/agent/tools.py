import requests, os, random, json
from typing import Dict, Optional
from models.data_models import VehicleServiceLog
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME

repo = Repo(DB_NAME)
service = Service(repo)

async def get_vehicle_service_logs(vehicle_id: Optional[str] = None) -> dict:
    return await service.get_vehicle_service_logs(vehicle_id)
