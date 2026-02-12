from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

# --- BIOMETRICS ---
class BiometricDataCreate(BaseModel):
    user_id: str        
    eda: float
    temp: float
    hr: float
    bi: float
    accel_x: float
    accel_y: float
    accel_z: float
    stress_level: Optional[float] = None

# --- USER ACTIVITY
class UserActivityCreate(BaseModel):
    user_id: str
    activity_type: str      
    title: str              
    duration_seconds: int   

class UserActivityResponse(BaseModel):
    id: int
    title: str              
    activity_type: str      
    duration_seconds: int
    completed_at: datetime  

    class Config:
        from_attributes = True 

# --- HISTORY & CHARTS ---
class EventResponse(BaseModel):
    id: int
    title: str
    event_type: str             
    start_date: str
    start_time: Optional[str] = None

    class Config:
        from_attributes = True

class StressDataPoint(BaseModel):
    label: str  
    avg_anx: float

class HistoryResponse(BaseModel):
    period: str
    overall_average: float
    stress_data: List[StressDataPoint]
    completed_tasks: List[UserActivityResponse]
    activities: List[EventResponse] = [] 

# --- DEVICES & NOTIFICATIONS ---
class DeviceTokenCreate(BaseModel):
    token: str
    user_id: str 
    device_name: Optional[str] = "Android Device"

# --- TASKS (Βιβλιοθήκη Ασκήσεων) ---
class TaskSchema(BaseModel):
    id: int
    title: str
    description: str
    duration: str
    category: str
    is_favorite: bool
    details: Optional[str] = None

    class Config:
        from_attributes = True

class UserLocationBase(BaseModel):
    user_id: str
    name: str
    address: str
    city: Optional[str] = None
    area: Optional[str] = None
    zip_code: Optional[str] = None
    country: Optional[str] = None
    is_default: bool = False

class UserLocationCreate(UserLocationBase):
    pass

class UserLocationResponse(UserLocationBase):
    id: int

    class Config:
        from_attributes = True

# Στο schemas.py, πρόσθεσε στο τέλος:

class UserUpdate(BaseModel):
    username: str
    email: str
    password: str
