from pydantic import BaseModel

class Measurement(BaseModel):
    timestamp: float
    temperature: float
    humidity: float
    battery: float