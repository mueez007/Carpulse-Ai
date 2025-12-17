from fastapi import APIRouter, status
from typing import List, Optional
from pydantic import BaseModel
from services.ml_service import ml_service
from models.data_models import VehicleServiceLog
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME

router = APIRouter()
repo = Repo(DB_NAME)
service = Service(repo)


@router.get("/", response_model=List[VehicleServiceLog])
async def get_vehicle_service_logs(vehicle_id: Optional[str] = None):
    """
    Retrieve vehicle service logs, optionally filtered by vehicle ID.

    Each log includes:
    - owner_name
    - owner_phone_number
    - vehicle_model
    - vehicle_id
    - service_date
    - service_type
    - description
    - mileage
    - cost
    - next_service_date
    - mechanic_id
    """
    return await service.get_vehicle_service_logs(vehicle_id)


@router.post(
    "/", 
    status_code=status.HTTP_201_CREATED,
    response_model=VehicleServiceLog,
)
async def create_vehicle_service_log(log: VehicleServiceLog):
    """
    Create a new vehicle service log record.

    Required fields:
    - vehicle_id
    - service_date
    - service_type
    - mileage
    - cost

    Recommended fields:
    - owner_name
    - owner_phone_number
    - vehicle_model
    - next_service_date
    - mechanic_id
    """
    return await service.create_vehicle_service_log(log)


@router.put(
    "/{log_id}",
    status_code=status.HTTP_200_OK,
    response_model=VehicleServiceLog,
)
async def update_vehicle_service_log(log_id: str, log: VehicleServiceLog):
    """
    Update an existing vehicle service log record by ID.

    Any of these can be updated:
    - owner_name
    - owner_phone_number
    - vehicle_model
    - vehicle_id
    - service_date
    - service_type
    - description
    - mileage
    - cost
    - next_service_date
    - mechanic_id
    """
    return await service.update_vehicle_service_log(log_id, log)


@router.delete("/{log_id}", status_code=status.HTTP_200_OK)
async def delete_vehicle_service_log(log_id: str):
    """
    Delete a vehicle service log record by ID.
    """
    return await service.delete_vehicle_service_log(log_id)

class CostEstimateRequest(BaseModel):
    vehicle_model: str
    service_type: str
    mileage: int
    mechanic_name: Optional[str] = None


@router.post("/estimate-cost")
async def estimate_cost(req: CostEstimateRequest):
    """
    ML-based service cost estimate.

    Uses:
    - vehicle_model
    - service_type
    - mileage
    - mechanic_name (optional)
    """
    if not ml_service.is_ready():
        return {
            "success": False,
            "message": "ML model not available. Train it first."
        }

    result = ml_service.estimate_cost(
        vehicle_model=req.vehicle_model,
        service_type=req.service_type,
        mileage=req.mileage,
        mechanic_name=req.mechanic_name,
    )

    return {
        "success": True,
        "message": "Estimated service cost",
        "data": result,
    }
