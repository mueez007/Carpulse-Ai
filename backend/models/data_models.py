from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class Mechanic(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})
    id: Optional[str] = None
    name: str
    specialization: str
    contact_number: str
    experience_years: int

class VehicleServiceLog(BaseModel):
    id: Optional[str] = None
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
    # you probably added this:
    mechanic_name: Optional[str] = None  
