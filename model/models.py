from datetime import datetime
from pydantic import BaseModel, field_validator


class GpsData(BaseModel):
    latitude: float
    longitude: float


class AccelerometerData(BaseModel):
    x: float
    y: float
    z: float


class AgentData(BaseModel):
    accelerometer: AccelerometerData
    gps: GpsData
    timestamp: datetime

    @classmethod
    @field_validator('timestamp', mode='before')
    from datetime import datetime

class YourClassName:
    
    @classmethod
    def check_timestamp(cls, value):
        try:
            if isinstance(value, datetime):
                return value
            return datetime.fromisoformat(value)
        
        except (TypeError, ValueError) as e:
            # Catch specific exceptions and provide a more informative error message
            raise ValueError(f"ERROR. Unable to parse timestamp. Reason: {str(e)}")

class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData


class ProcessedAgentDataInDB(BaseModel):
    id: int
    road_state: str
    x: float
    y: float
    z: float
    latitude: float
    longitude: float
    timestamp: datetime
