from typing import Optional, List
from uuid import uuid4, UUID
from datetime import datetime, timedelta, timezone

from models.data_models import VehicleServiceLog, Mechanic
from db import PostgresDB


def normalize_dt(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


def row_to_dict(row):
    return {
        k: str(v) if isinstance(v, UUID) else v
        for k, v in dict(row).items()
    }


class Repo:

    async def insert(self, log: VehicleServiceLog) -> VehicleServiceLog:
        log.id = log.id or str(uuid4())
        log.service_date = normalize_dt(log.service_date)
        log.next_service_date = normalize_dt(log.next_service_date)

        q = """
        INSERT INTO vehicle_service_logs VALUES
        ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12)
        """

        async with PostgresDB.pool.acquire() as conn:
            await conn.execute(
                q,
                UUID(log.id), log.owner_name, log.owner_phone_number,
                log.vehicle_model, log.vehicle_id, log.service_date,
                log.service_type, log.description, log.mileage,
                log.cost, log.next_service_date, log.mechanic_name
            )
        return log

    async def get(self, log_id: str):
        async with PostgresDB.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM vehicle_service_logs WHERE id=$1", UUID(log_id)
            )
        return VehicleServiceLog(**row_to_dict(row)) if row else None

    async def list(self, vehicle_id: Optional[str] = None):
        async with PostgresDB.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM vehicle_service_logs" +
                (" WHERE vehicle_id=$1" if vehicle_id else ""),
                *( [vehicle_id] if vehicle_id else [] )
            )
        return [VehicleServiceLog(**row_to_dict(r)) for r in rows]

    async def list_by_vehicle_model(self, model: str):
        async with PostgresDB.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM vehicle_service_logs WHERE vehicle_model ILIKE $1",
                f"%{model}%"
            )
        return [VehicleServiceLog(**row_to_dict(r)) for r in rows]

    async def get_vehicles_due_soon(self, days=30):
        today = normalize_dt(datetime.now(timezone.utc))
        future = today + timedelta(days=days)

        async with PostgresDB.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM vehicle_service_logs WHERE next_service_date BETWEEN $1 AND $2",
                today, future
            )
        return [VehicleServiceLog(**row_to_dict(r)) for r in rows]

    async def update_service_cost_by_model(self, model, cost):
        async with PostgresDB.pool.acquire() as conn:
            r = await conn.execute(
                "UPDATE vehicle_service_logs SET cost=$1 WHERE vehicle_model ILIKE $2",
                cost, f"%{model}%"
            )
        return r.endswith("1")

    async def delete_by_vehicle_model(self, model):
        async with PostgresDB.pool.acquire() as conn:
            r = await conn.execute(
                "DELETE FROM vehicle_service_logs WHERE vehicle_model ILIKE $1",
                f"%{model}%"
            )
        return int(r.split()[-1]) > 0

    async def delete(self, log_id: str):
        async with PostgresDB.pool.acquire() as conn:
            r = await conn.execute(
                "DELETE FROM vehicle_service_logs WHERE id=$1", UUID(log_id)
            )
        return int(r.split()[-1])

    async def update(self, log: VehicleServiceLog):
        log.service_date = normalize_dt(log.service_date)
        log.next_service_date = normalize_dt(log.next_service_date)

        q = """
        UPDATE vehicle_service_logs SET
            owner_name=$1, owner_phone_number=$2, vehicle_model=$3,
            vehicle_id=$4, service_date=$5, service_type=$6,
            description=$7, mileage=$8, cost=$9,
            next_service_date=$10, mechanic_name=$11
        WHERE id=$12
        """

        async with PostgresDB.pool.acquire() as conn:
            r = await conn.execute(
                q,
                log.owner_name, log.owner_phone_number, log.vehicle_model,
                log.vehicle_id, log.service_date, log.service_type,
                log.description, log.mileage, log.cost,
                log.next_service_date, log.mechanic_name, UUID(log.id)
            )
        return r.endswith("1")

    async def create_mechanic(self, m: Mechanic):
        m.id = m.id or str(uuid4())
        async with PostgresDB.pool.acquire() as conn:
            await conn.execute(
                "INSERT INTO mechanics VALUES ($1,$2,$3,$4,$5)",
                UUID(m.id), m.name, m.specialization, m.contact_number, m.experience_years
            )
        return m

    async def list_mechanics(self):
        async with PostgresDB.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM mechanics")
        return [Mechanic(**row_to_dict(r)) for r in rows]
