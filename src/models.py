from pydantic import BaseModel

class MiMeasurement(BaseModel):
    timestamp: float
    temperature: float
    humidity: int
    battery: int