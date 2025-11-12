from datetime import datetime
import aiosqlite
from typing import List, Optional
from models.data_models import VehicleServiceLog
from constants import DB_NAME, TABLE_NAME
from uuid import uuid4

class Repo:
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path

    async def init_db(self):
        """Initialize table if not exists."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(f"""
                CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                    id TEXT PRIMARY KEY,
                    owner_name TEXT,
                    vehicle_type TEXT,
                    vehicle_id TEXT,
                    service_date TEXT,
                    service_type TEXT,
                    description TEXT,
                    mileage INTEGER,
                    cost REAL,
                    next_service_date TEXT
                )
            """)
            await db.commit()

    async def insert(self, log: VehicleServiceLog):
        async with aiosqlite.connect(self.db_path) as db:
            if log.id is None:
                log.id = str(uuid4())
            await db.execute(f"""
                INSERT INTO {TABLE_NAME} (id, owner_name, vehicle_type, vehicle_id, service_date, service_type, description, mileage, cost, next_service_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log.id,
                log.owner_name,
                log.vehicle_type,
                log.vehicle_id,
                log.service_date.isoformat(),
                log.service_type,
                log.description,
                log.mileage,
                log.cost,
                log.next_service_date.isoformat() if log.next_service_date else None
            ))
            await db.commit()

    async def get(self, log_id: str) -> Optional[VehicleServiceLog]:
        query = f"""
            SELECT id, owner_name, vehicle_type, vehicle_id, service_date, service_type, description, mileage, cost, next_service_date
            FROM {TABLE_NAME} WHERE id = ?
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (log_id,))
            row = await cursor.fetchone()
            if row:
                return VehicleServiceLog(
                    id=row[0],
                    owner_name=row[1],
                    vehicle_type=row[2],
                    vehicle_id=row[3],
                    service_date=datetime.fromisoformat(row[4]),
                    service_type=row[5],
                    description=row[6],
                    mileage=row[7],
                    cost=row[8],
                    next_service_date=datetime.fromisoformat(row[9]) if row[9] else None,
                )
            return None


    async def list(self, vehicle_id: Optional[str] = None) -> List[VehicleServiceLog]:
        async with aiosqlite.connect(self.db_path) as db:
            query = f"SELECT id, owner_name, vehicle_type, vehicle_id, service_date, service_type, description, mileage, cost, next_service_date FROM {TABLE_NAME}"
            params = []
            if vehicle_id:
                query += " WHERE vehicle_id = ?"
                params.append(vehicle_id)
            
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [
                VehicleServiceLog(
                    id=row[0],
                    owner_name=row[1],
                    vehicle_type=row[2],
                    vehicle_id=row[3],
                    service_date=datetime.fromisoformat(row[4]),
                    service_type=row[5],
                    description=row[6],
                    mileage=row[7],
                    cost=row[8],
                    next_service_date=datetime.fromisoformat(row[9]) if row[9] else None,
                )
                for row in rows
            ]


    async def delete(self, log_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (log_id,))
            await db.commit()
            return cursor.rowcount

    async def update(self, log: VehicleServiceLog) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                UPDATE {TABLE_NAME}
                SET owner_name = ?, vehicle_type = ?, vehicle_id = ?, service_date = ?, service_type = ?, description = ?, mileage = ?, cost = ?, next_service_date = ?
                WHERE id = ?
            """, (
                log.owner_name,
                log.vehicle_type,
                log.vehicle_id,
                log.service_date.isoformat(),
                log.service_type,
                log.description,
                log.mileage,
                log.cost,
                log.next_service_date.isoformat() if log.next_service_date else None,
                log.id
            ))
            await db.commit()
            return cursor.rowcount > 0
