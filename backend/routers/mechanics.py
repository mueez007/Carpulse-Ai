from fastapi import APIRouter, status, HTTPException
from typing import List, Optional
from models.data_models import Mechanic
from services.service import Service
from repos.repo import Repo
from constants import DB_NAME

router = APIRouter()
repo = Repo(DB_NAME)
service = Service(repo)

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_mechanic(mechanic: Mechanic):
    """Create a new mechanic"""
    return await service.create_mechanic(mechanic)

@router.get("/", response_model=List[Mechanic])
async def get_mechanics():
    """Get all mechanics"""
    return await service.list_mechanics()

@router.get("/{mechanic_id}", response_model=Mechanic)
async def get_mechanic(mechanic_id: str):
    """Get a specific mechanic by ID"""
    mechanic = await service.get_mechanic(mechanic_id)
    if not mechanic:
        raise HTTPException(status_code=404, detail="Mechanic not found")
    return mechanic

@router.put("/{mechanic_id}", response_model=Mechanic)
async def update_mechanic(mechanic_id: str, mechanic: Mechanic):
    """Update a mechanic"""
    return await service.update_mechanic(mechanic_id, mechanic)

@router.delete("/{mechanic_id}")
async def delete_mechanic(mechanic_id: str):
    """Delete a mechanic"""
    return await service.delete_mechanic(mechanic_id)

@router.get("/stats/most-services")
async def get_mechanic_with_most_services():
    """Get mechanic who has completed the most services"""
    return await service.get_mechanic_with_most_services()

@router.get("/stats/service-costs")
async def get_mechanic_service_costs():
    """Get total cost of services performed by each mechanic"""
    return await service.get_mechanic_service_costs()