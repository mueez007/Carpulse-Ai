from typing import List, Optional
from fastapi import HTTPException
from models.data_models import VehicleServiceLog, Mechanic
from repos.repo import Repo

class Service:
    def __init__(self, repo: Repo):
        self.repo = repo

    # Vehicle Service Log Methods
    async def create_vehicle_service_log(self, log: VehicleServiceLog) -> VehicleServiceLog:
        await self.repo.init_db()
        if isinstance(log, dict):
            log = VehicleServiceLog(**log)
        return await self.repo.insert(log)

    async def get_vehicle_service_logs(self, vehicle_id: Optional[str] = None) -> List[VehicleServiceLog]:
        await self.repo.init_db()
        return await self.repo.list(vehicle_id)

    async def get_vehicle_service_log_by_id(self, log_id: str) -> Optional[VehicleServiceLog]:
        await self.repo.init_db()
        return await self.repo.get(log_id)

    async def update_vehicle_service_log(self, log_id: str, log: VehicleServiceLog) -> VehicleServiceLog:
        await self.repo.init_db()
        if isinstance(log, dict):
            log = VehicleServiceLog(**log)
        
        # Check if log exists
        existing_log = await self.repo.get(log_id)
        if not existing_log:
            raise HTTPException(status_code=404, detail="Vehicle service log not found")
        
        log.id = log_id
        success = await self.repo.update(log)
        if not success:
            raise HTTPException(status_code=404, detail="Vehicle service log not found to update")
        return log

    async def delete_vehicle_service_log(self, log_id: str) -> dict:
        await self.repo.init_db()
        deleted_count = await self.repo.delete(log_id)
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Vehicle service log not found to delete")
        return {"message": f"Vehicle service log with id {log_id} deleted successfully"}

    # Additional service methods
    async def get_services_by_vehicle_model(self, vehicle_model: str) -> List[VehicleServiceLog]:
        """Get all services for a specific vehicle model"""
        await self.repo.init_db()
        return await self.repo.list_by_vehicle_model(vehicle_model)

    async def get_vehicles_due_soon(self, days_threshold: int = 30) -> List[VehicleServiceLog]:
        """Get vehicles with service due soon"""
        await self.repo.init_db()
        return await self.repo.get_vehicles_due_soon(days_threshold)

    async def update_service_cost_by_model(self, vehicle_model: str, new_cost: float) -> bool:
        """Update service cost for a vehicle model"""
        await self.repo.init_db()
        return await self.repo.update_service_cost_by_model(vehicle_model, new_cost)

    async def delete_by_vehicle_model(self, vehicle_model: str) -> bool:
        """Delete all logs for a vehicle model"""
        await self.repo.init_db()
        return await self.repo.delete_by_vehicle_model(vehicle_model)

    # Mechanic methods
    async def create_mechanic(self, mechanic: Mechanic) -> Mechanic:
        await self.repo.init_db()
        if isinstance(mechanic, dict):
            mechanic = Mechanic(**mechanic)
        return await self.repo.create_mechanic(mechanic)

    async def get_mechanic(self, mechanic_id: str) -> Optional[Mechanic]:
        await self.repo.init_db()
        return await self.repo.get_mechanic(mechanic_id)

    async def list_mechanics(self) -> List[Mechanic]:
        await self.repo.init_db()
        return await self.repo.list_mechanics()

    # CHALLENGE 5: Add these methods for multi-modal support
    async def update_mechanic(self, mechanic_id: str, mechanic: Mechanic) -> Mechanic:
        await self.repo.init_db()
        if isinstance(mechanic, dict):
            mechanic = Mechanic(**mechanic)
        
        existing_mechanic = await self.repo.get_mechanic(mechanic_id)
        if not existing_mechanic:
            raise HTTPException(status_code=404, detail="Mechanic not found")
        
        mechanic.id = mechanic_id
        updated_mechanic = await self.repo.update_mechanic(mechanic)
        if not updated_mechanic:
            raise HTTPException(status_code=404, detail="Mechanic not found to update")
        return updated_mechanic

    async def delete_mechanic(self, mechanic_id: str) -> dict:
        await self.repo.init_db()
        success = await self.repo.delete_mechanic(mechanic_id)
        if not success:
            raise HTTPException(status_code=404, detail="Mechanic not found to delete")
        return {"message": f"Mechanic with id {mechanic_id} deleted successfully"}

    async def get_mechanic_with_most_services(self):
        """Get mechanic who has completed the most services"""
        await self.repo.init_db()
        return await self.repo.get_mechanic_with_most_services()

    async def get_mechanic_service_costs(self):
        """Get total cost of services performed by each mechanic"""
        await self.repo.init_db()
        return await self.repo.get_mechanic_service_costs()