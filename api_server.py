from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Measurement(BaseModel):
    timestamp: float
    temperature: float
    humidity: float
    battery: float

@app.post("/data")
async def get_data(measurement: Measurement):
    print(f"Recieved: {measurement}")
    return {"ok": True}