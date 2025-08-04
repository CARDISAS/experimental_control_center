from pydantic import BaseModel
from datetime import datetime

class SensorReading(BaseModel):
    timestamp: datetime
    lux: int
    ph: float
    ec: float
