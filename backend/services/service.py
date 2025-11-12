from typing import List, Optional
from fastapi import HTTPException
from models.data_models import VehicleServiceLog
from repos.repo import Repo

class Service:
    def __init__(self, repo: Repo):
        self.repo = repo

    async def create_vehicle_service_log(self, log: VehicleServiceLog):
        await self.repo.init_db()
        if isinstance(log, dict):
            log = VehicleServiceLog(**log)
        # The ID is now generated in the repo, so we don't check for existing ID here
        await self.repo.insert(log)
        return log

    async def get_vehicle_service_logs(self, vehicle_id: Optional[str] = None) -> List[VehicleServiceLog]:
        await self.repo.init_db()
        return await self.repo.list(vehicle_id)

    async def update_vehicle_service_log(self, log_id: str, log: VehicleServiceLog) -> VehicleServiceLog:
        await self.repo.init_db()
        if isinstance(log, dict):
            log = VehicleServiceLog(**log)
        log.id = log_id
        updated = await self.repo.update(log)
        if not updated:
            raise HTTPException(status_code=404, detail="Vehicle service log not found to update")
        return log

    async def delete_vehicle_service_log(self, log_id: str):
        await self.repo.init_db()
        deleted_count = await self.repo.delete(log_id)
        if deleted_count == 0:
            raise HTTPException(status_code=404, detail="Vehicle service log not found to delete")
        return {"message": f"Vehicle service log with id {log_id} deleted successfully"}
