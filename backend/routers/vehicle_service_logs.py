from fastapi import APIRouter, status
from typing import List, Optional  # Combine imports
from models.data_models import VehicleServiceLog
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME

router = APIRouter()
repo = Repo(DB_NAME)
service = Service(repo)

@router.get("/", response_model=List[VehicleServiceLog])
async def get_vehicle_service_logs(vehicle_id: Optional[str] = None):
    """Retrieve vehicle service logs, optionally filtered by vehicle ID"""
    return await service.get_vehicle_service_logs(vehicle_id)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_vehicle_service_log(log: VehicleServiceLog):
    """Create a new vehicle service log record"""
    return await service.create_vehicle_service_log(log)

@router.put("/{log_id}", status_code=status.HTTP_200_OK)
async def update_vehicle_service_log(log_id: str, log: VehicleServiceLog):
    """Update an existing vehicle service log record"""
    return await service.update_vehicle_service_log(log_id, log)

@router.delete("/{log_id}", status_code=status.HTTP_200_OK)
async def delete_vehicle_service_log(log_id: str):
    """Delete a vehicle service log record"""
    return await service.delete_vehicle_service_log(log_id)