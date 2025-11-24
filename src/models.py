from pydantic import BaseModel
from typing import Union

class Measurement(BaseModel):
    type: str
    data: Union["MiData", "O2Data"]

class MiData(BaseModel):
    timestamp: float
    temperature: float
    humidity: int
    battery: int

class O2Data(BaseModel):
    timestamp: float
    spo2: int
    pr: int

Measurement.model_rebuild()