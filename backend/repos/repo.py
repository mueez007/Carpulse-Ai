from datetime import datetime
import aiosqlite
from typing import List, Optional
from models.data_models import VehicleServiceLog, Mechanic
from constants import DB_NAME, TABLE_NAME
from uuid import uuid4
import datetime as dt

class Repo:
    def __init__(self, db_path: str = DB_NAME):
        self.db_path = db_path

    async def init_db(self):
        """Initialize tables if not exists and handle schema migration."""
        async with aiosqlite.connect(self.db_path) as db:
            # Vehicle service logs table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS vehicle_service_logs (
                    id TEXT PRIMARY KEY,
                    owner_name TEXT,
                    vehicle_model TEXT,
                    vehicle_id TEXT,
                    service_date TEXT,
                    service_type TEXT,
                    description TEXT,
                    mileage INTEGER,
                    cost REAL,
                    next_service_date TEXT,
                    mechanic_id TEXT
                )
            """)
            
            # Mechanics table
            await db.execute("""
                CREATE TABLE IF NOT EXISTS mechanics (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    specialization TEXT,
                    contact_number TEXT,
                    experience_years INTEGER
                )
            """)
            
            # Check if we need to migrate from old schema
            try:
                # Try to query the vehicle_model column
                await db.execute("SELECT vehicle_model FROM vehicle_service_logs LIMIT 1")
            except aiosqlite.OperationalError:
                # If vehicle_model doesn't exist, we need to migrate
                try:
                    # Check if old vehicle_type column exists
                    await db.execute("SELECT vehicle_type FROM vehicle_service_logs LIMIT 1")
                    # If we get here, vehicle_type exists - migrate to vehicle_model
                    await db.execute("ALTER TABLE vehicle_service_logs RENAME COLUMN vehicle_type TO vehicle_model")
                    print("Database schema migrated: vehicle_type → vehicle_model")
                except aiosqlite.OperationalError:
                    # Neither column exists in old format, table is empty or newly created
                    pass
            
            await db.commit()

    async def insert(self, log: VehicleServiceLog):
        async with aiosqlite.connect(self.db_path) as db:
            if log.id is None:
                log.id = str(uuid4())
            await db.execute(f"""
                INSERT INTO {TABLE_NAME} (id, owner_name, vehicle_model, vehicle_id, service_date, service_type, description, mileage, cost, next_service_date, mechanic_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                log.id,
                log.owner_name,
                log.vehicle_model,
                log.vehicle_id,
                log.service_date.isoformat(),
                log.service_type,
                log.description,
                log.mileage,
                log.cost,
                log.next_service_date.isoformat() if log.next_service_date else None,
                log.mechanic_id
            ))
            await db.commit()

    async def get(self, log_id: str) -> Optional[VehicleServiceLog]:
        query = f"""
            SELECT id, owner_name, vehicle_model, vehicle_id, service_date, service_type, description, mileage, cost, next_service_date, mechanic_id
            FROM {TABLE_NAME} WHERE id = ?
        """
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(query, (log_id,))
            row = await cursor.fetchone()
            if row:
                return VehicleServiceLog(
                    id=row[0],
                    owner_name=row[1],
                    vehicle_model=row[2],
                    vehicle_id=row[3],
                    service_date=datetime.fromisoformat(row[4]),
                    service_type=row[5],
                    description=row[6],
                    mileage=row[7],
                    cost=row[8],
                    next_service_date=datetime.fromisoformat(row[9]) if row[9] else None,
                    mechanic_id=row[10]
                )
            return None

    async def list(self, vehicle_id: Optional[str] = None) -> List[VehicleServiceLog]:
        async with aiosqlite.connect(self.db_path) as db:
            query = f"SELECT id, owner_name, vehicle_model, vehicle_id, service_date, service_type, description, mileage, cost, next_service_date, mechanic_id FROM {TABLE_NAME}"
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
                    vehicle_model=row[2],
                    vehicle_id=row[3],
                    service_date=datetime.fromisoformat(row[4]),
                    service_type=row[5],
                    description=row[6],
                    mileage=row[7],
                    cost=row[8],
                    next_service_date=datetime.fromisoformat(row[9]) if row[9] else None,
                    mechanic_id=row[10]
                )
                for row in rows
            ]

    async def list_by_vehicle_model(self, vehicle_model: str) -> List[VehicleServiceLog]:
        """List all services for a specific vehicle model"""
        async with aiosqlite.connect(self.db_path) as db:
            query = f"SELECT id, owner_name, vehicle_model, vehicle_id, service_date, service_type, description, mileage, cost, next_service_date, mechanic_id FROM {TABLE_NAME} WHERE vehicle_model LIKE ?"
            cursor = await db.execute(query, (f"%{vehicle_model}%",))
            rows = await cursor.fetchall()
            return [
                VehicleServiceLog(
                    id=row[0],
                    owner_name=row[1],
                    vehicle_model=row[2],
                    vehicle_id=row[3],
                    service_date=datetime.fromisoformat(row[4]),
                    service_type=row[5],
                    description=row[6],
                    mileage=row[7],
                    cost=row[8],
                    next_service_date=datetime.fromisoformat(row[9]) if row[9] else None,
                    mechanic_id=row[10]
                )
                for row in rows
            ]

    async def get_vehicles_due_soon(self, days_threshold: int = 30) -> List[VehicleServiceLog]:
        """Get vehicles with next service due within specified days"""
        try:
            from datetime import datetime, timedelta
            
            # Calculate future date
            today = datetime.now().date()
            future_date = (today + timedelta(days=days_threshold)).isoformat()
            
            async with aiosqlite.connect(self.db_path) as db:
                query = f"""
                    SELECT id, owner_name, vehicle_model, vehicle_id, service_date, service_type, 
                           description, mileage, cost, next_service_date, mechanic_id
                    FROM {TABLE_NAME} 
                    WHERE next_service_date IS NOT NULL 
                    AND date(next_service_date) <= date(?)
                    AND date(next_service_date) >= date(?)
                """
                
                # Use today's date and future date for comparison
                cursor = await db.execute(query, (future_date, today.isoformat()))
                rows = await cursor.fetchall()
                
                logs = []
                for row in rows:
                    try:
                        log = VehicleServiceLog(
                            id=row[0],
                            owner_name=row[1],
                            vehicle_model=row[2],
                            vehicle_id=row[3],
                            service_date=datetime.fromisoformat(row[4]),
                            service_type=row[5],
                            description=row[6],
                            mileage=row[7],
                            cost=row[8],
                            next_service_date=datetime.fromisoformat(row[9]) if row[9] else None,
                            mechanic_id=row[10]
                        )
                        logs.append(log)
                    except Exception as e:
                        print(f"Error parsing log {row[0]}: {e}")
                        continue
                
                return logs
                
        except Exception as e:
            print(f"Error in get_vehicles_due_soon: {e}")
            return []

    async def update_service_cost_by_model(self, vehicle_model: str, new_cost: float) -> bool:
        """Update service cost for all logs of a specific vehicle model"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"UPDATE {TABLE_NAME} SET cost = ? WHERE vehicle_model LIKE ?", (new_cost, f"%{vehicle_model}%"))
            await db.commit()
            return cursor.rowcount > 0

    async def delete_by_vehicle_model(self, vehicle_model: str) -> bool:
        """Delete all logs for a specific vehicle model"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"DELETE FROM {TABLE_NAME} WHERE vehicle_model LIKE ?", (f"%{vehicle_model}%",))
            await db.commit()
            return cursor.rowcount > 0

    async def delete(self, log_id: str) -> int:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (log_id,))
            await db.commit()
            return cursor.rowcount

    async def update(self, log: VehicleServiceLog) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(f"""
                UPDATE {TABLE_NAME}
                SET owner_name = ?, vehicle_model = ?, vehicle_id = ?, service_date = ?, service_type = ?, description = ?, mileage = ?, cost = ?, next_service_date = ?, mechanic_id = ?
                WHERE id = ?
            """, (
                log.owner_name,
                log.vehicle_model,
                log.vehicle_id,
                log.service_date.isoformat(),
                log.service_type,
                log.description,
                log.mileage,
                log.cost,
                log.next_service_date.isoformat() if log.next_service_date else None,
                log.mechanic_id,
                log.id
            ))
            await db.commit()
            return cursor.rowcount > 0

    # Mechanic methods
    async def create_mechanic(self, mechanic: Mechanic) -> Mechanic:
        async with aiosqlite.connect(self.db_path) as db:
            if mechanic.id is None:
                mechanic.id = str(uuid4())
            await db.execute("""
                INSERT INTO mechanics (id, name, specialization, contact_number, experience_years)
                VALUES (?, ?, ?, ?, ?)
            """, (
                mechanic.id,
                mechanic.name,
                mechanic.specialization,
                mechanic.contact_number,
                mechanic.experience_years
            ))
            await db.commit()
            return mechanic

    async def get_mechanic(self, mechanic_id: str) -> Optional[Mechanic]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT id, name, specialization, contact_number, experience_years FROM mechanics WHERE id = ?", (mechanic_id,))
            row = await cursor.fetchone()
            if row:
                return Mechanic(
                    id=row[0],
                    name=row[1],
                    specialization=row[2],
                    contact_number=row[3],
                    experience_years=row[4]
                )
            return None

    async def list_mechanics(self) -> List[Mechanic]:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("SELECT id, name, specialization, contact_number, experience_years FROM mechanics")
            rows = await cursor.fetchall()
            return [
                Mechanic(
                    id=row[0],
                    name=row[1],
                    specialization=row[2],
                    contact_number=row[3],
                    experience_years=row[4]
                )
                for row in rows
            ]

    # CHALLENGE 5: Add these methods for multi-modal support
    async def update_mechanic(self, mechanic: Mechanic) -> Mechanic:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                UPDATE mechanics 
                SET name = ?, specialization = ?, contact_number = ?, experience_years = ?
                WHERE id = ?
            """, (
                mechanic.name,
                mechanic.specialization,
                mechanic.contact_number,
                mechanic.experience_years,
                mechanic.id
            ))
            await db.commit()
            return mechanic if cursor.rowcount > 0 else None

    async def delete_mechanic(self, mechanic_id: str) -> bool:
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("DELETE FROM mechanics WHERE id = ?", (mechanic_id,))
            await db.commit()
            return cursor.rowcount > 0

    async def get_mechanic_with_most_services(self):
        """Get mechanic who has completed the most services"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT m.id, m.name, COUNT(vsl.id) as service_count
                FROM mechanics m
                LEFT JOIN vehicle_service_logs vsl ON m.id = vsl.mechanic_id
                GROUP BY m.id, m.name
                ORDER BY service_count DESC
                LIMIT 1
            """)
            result = await cursor.fetchone()
            if result:
                return {
                    "mechanic_id": result[0],
                    "mechanic_name": result[1],
                    "service_count": result[2] or 0
                }
            return None

    async def get_mechanic_service_costs(self):
        """Get total cost of services performed by each mechanic"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT m.id, m.name, COALESCE(SUM(vsl.cost), 0) as total_cost
                FROM mechanics m
                LEFT JOIN vehicle_service_logs vsl ON m.id = vsl.mechanic_id
                GROUP BY m.id, m.name
                ORDER BY total_cost DESC
            """)
            rows = await cursor.fetchall()
            return [
                {
                    "mechanic_id": row[0],
                    "mechanic_name": row[1],
                    "total_cost": row[2] or 0
                }
                for row in rows
            ]