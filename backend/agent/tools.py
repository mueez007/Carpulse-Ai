import os
import random
from typing import Dict, Optional, List
from datetime import datetime, timedelta, timezone

from twilio.rest import Client

from models.data_models import VehicleServiceLog, Mechanic
from services.service import Service
from repos.repo import Repo

repo = Repo()
service = Service(repo)


def normalize_dt(dt):
    if dt is None:
        return None
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    if dt.tzinfo is not None:
        return dt.astimezone(timezone.utc).replace(tzinfo=None)
    return dt


# ---------------- CORE CRUD ---------------- #

async def add_vehicle_service_log(
    vehicle_model: str,
    owner_name: str,
    owner_phone_number: str,
    service_type: str,
    service_date: str,
    next_service_date: str,
    service_cost: float,
    description: str = "",
    mileage: int = 0,
    mechanic_name: Optional[str] = None
) -> Dict:
    try:
        vehicle_id = f"{vehicle_model.replace(' ', '_').lower()}_{random.randint(1000,9999)}"

        log = VehicleServiceLog(
            vehicle_model=vehicle_model,
            owner_name=owner_name,
            owner_phone_number=owner_phone_number,
            vehicle_id=vehicle_id,
            service_type=service_type,
            mechanic_name=mechanic_name,
            description=description,
            mileage=mileage,
            cost=service_cost,
            service_date=normalize_dt(datetime.strptime(service_date, "%Y-%m-%d")),
            next_service_date=normalize_dt(datetime.strptime(next_service_date, "%Y-%m-%d")) if next_service_date else None,
        )

        res = await service.create_vehicle_service_log(log)
        return {"success": True, "data": res.model_dump(mode="json")}
    except Exception as e:
        return {"success": False, "message": str(e)}


async def list_services_by_vehicle(vehicle_model: str) -> Dict:
    logs = await service.get_services_by_vehicle_model(vehicle_model)
    return {"success": True, "data": [l.model_dump(mode="json") for l in logs]}


async def get_vehicles_service_due_soon(days: int = 30) -> Dict:
    logs = await service.get_vehicle_service_logs(None)
    today = datetime.utcnow()
    due = []

    for l in logs:
        if l.next_service_date:
            ns = normalize_dt(l.next_service_date)
            if 0 <= (ns - today).days <= days:
                due.append(l.model_dump(mode="json"))

    return {"success": True, "data": due}


async def update_service_cost_by_vehicle(vehicle_model: str, new_cost: float) -> Dict:
    success = await service.update_service_cost_by_model(vehicle_model, new_cost)
    return {"success": success}


async def remove_service_log_by_vehicle(vehicle_model: str) -> Dict:
    success = await service.delete_by_vehicle_model(vehicle_model)
    return {"success": success}


async def get_vehicle_service_logs(vehicle_id: Optional[str] = None) -> Dict:
    logs = await service.get_vehicle_service_logs(vehicle_id)
    return {"success": True, "data": [l.model_dump(mode="json") for l in logs]}


# ---------------- ANALYTICS ---------------- #

async def get_total_services_count() -> Dict:
    logs = await service.get_vehicle_service_logs(None)
    return {"count": len(logs)}


async def get_average_service_cost() -> Dict:
    logs = await service.get_vehicle_service_logs(None)
    return {"average_cost": round(sum(l.cost for l in logs) / len(logs), 2) if logs else 0}


async def get_most_frequent_service_type() -> Dict:
    logs = await service.get_vehicle_service_logs(None)
    freq = {}
    for l in logs:
        freq[l.service_type] = freq.get(l.service_type, 0) + 1
    return {"most_frequent_type": max(freq, key=freq.get) if freq else None}


# ---------------- AUDITING ---------------- #

async def get_most_recent_service() -> Dict:
    logs = [l for l in await service.get_vehicle_service_logs(None) if l.service_date]
    if not logs:
        return {"most_recent_service": None}
    logs.sort(key=lambda x: x.service_date, reverse=True)
    return {"most_recent_service": logs[0].model_dump(mode="json")}


async def get_overdue_services() -> Dict:
    today = datetime.utcnow()
    overdue = []
    for l in await service.get_vehicle_service_logs(None):
        if l.next_service_date and normalize_dt(l.next_service_date) < today:
            overdue.append(l.model_dump(mode="json"))
    return {"data": overdue}


async def get_owner_with_most_services() -> Dict:
    count = {}
    for l in await service.get_vehicle_service_logs(None):
        count[l.owner_name] = count.get(l.owner_name, 0) + 1
    return {"top_owner": max(count, key=count.get) if count else None}


# ---------------- MECHANICS ---------------- #

async def add_mechanic(name: str, specialization: str, contact_number: str, experience_years: int) -> Dict:
    m = Mechanic(name=name, specialization=specialization, contact_number=contact_number, experience_years=experience_years)
    res = await service.create_mechanic(m)
    return {"success": True, "data": res.model_dump(mode="json")}


async def list_mechanics() -> Dict:
    mechs = await service.list_mechanics()
    return {"success": True, "data": [m.model_dump(mode="json") for m in mechs]}


async def get_mechanic_with_most_services() -> Dict:
    count = {}
    for l in await service.get_vehicle_service_logs(None):
        if l.mechanic_name:
            count[l.mechanic_name] = count.get(l.mechanic_name, 0) + 1
    return {"top_mechanic": max(count, key=count.get) if count else None}


async def get_total_cost_by_mechanic() -> Dict:
    stats = {}
    for l in await service.get_vehicle_service_logs(None):
        if l.mechanic_name:
            stats[l.mechanic_name] = stats.get(l.mechanic_name, 0) + l.cost
    return {"mechanic_costs": stats}


# ---------------- IMAGES ---------------- #

IMAGE_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "service_images"))

async def get_vehicle_images(vehicle_id: str) -> Dict:
    if not os.path.exists(IMAGE_FOLDER):
        return {"success": False, "data": []}
    files = [f"/service_images/{f}" for f in os.listdir(IMAGE_FOLDER) if f.startswith(vehicle_id)]
    return {"success": True, "data": files}
# ---------------- DOCUMENTATION ---------------- #

async def upload_service_documentation(
    vehicle_model: str,
    service_date: str,
    document_type: str,
    description: str = ""
) -> Dict:
    return {
        "success": True,
        "data": {
            "vehicle_model": vehicle_model,
            "service_date": service_date,
            "document_type": document_type,
            "description": description,
            "uploaded_at": datetime.utcnow().isoformat()
        }
    }


async def get_service_documentation(vehicle_model: str) -> Dict:
    return {
        "success": True,
        "data": {
            "vehicle_model": vehicle_model,
            "documents": []
        }
    }


async def process_uploaded_service_images(
    vehicle_model: str,
    image_description: str = ""
) -> Dict:
    return {
        "success": True,
        "data": {
            "vehicle_model": vehicle_model,
            "image_description": image_description,
            "processed_at": datetime.utcnow().isoformat()
        }
    }


# ---------------- REMINDERS ---------------- #

async def send_service_reminders(days: int = 7) -> Dict:
    logs = await service.get_vehicle_service_logs(None)
    today = datetime.utcnow()

    due = [
        l for l in logs
        if l.next_service_date and
        0 <= (normalize_dt(l.next_service_date) - today).days <= days
    ]

    return {
        "success": True,
        "count": len(due),
        "vehicles": [l.model_dump(mode="json") for l in due]
    }
