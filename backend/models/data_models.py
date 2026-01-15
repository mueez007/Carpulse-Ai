from typing import Optional
from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime, timezone
from uuid import UUID

id: Optional[UUID] = None


class Mechanic(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: Optional[UUID] = None
    name: str
    specialization: str
    contact_number: str
    experience_years: int


class VehicleServiceLog(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: Optional[UUID] = None
    vehicle_model: str
    owner_name: str
    owner_phone_number: Optional[str] = None
    vehicle_id: Optional[str] = None
    service_date: datetime
    service_type: str
    description: Optional[str] = None
    mileage: Optional[int] = 0
    cost: float
    next_service_date: Optional[datetime] = None
    mechanic_name: Optional[str] = None

    @field_validator("service_date", "next_service_date", mode="before")
    @classmethod
    def normalize_datetime(cls, v):
        if v is None:
            return None
        if isinstance(v, datetime) and v.tzinfo is not None:
            return v.astimezone(timezone.utc).replace(tzinfo=None)
        return v
