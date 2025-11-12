from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class VehicleServiceLog(BaseModel):
    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.isoformat()})
    id: Optional[str] = None
    owner_name: Optional[str] = None
    vehicle_type: Optional[str] = None
    vehicle_id: str
    service_date: datetime
    service_type: str
    description: Optional[str] = None
    mileage: int
    cost: float
    next_service_date: Optional[datetime] = None




