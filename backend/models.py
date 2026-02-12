from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

# 1. ΣΥΣΚΕΥΕΣ (Για Notifications)
class UserDevice(Base):
    __tablename__ = "user_devices"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, index=True, nullable=False)
    fcm_token = Column(String, unique=True, nullable=False)
    device_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# 2. ΗΜΕΡΟΛΟΓΙΟ (Events)
class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True) 
    title = Column(String)
    location = Column(String)
    event_type = Column(String, default="event") 
    start_date = Column(String)  
    start_time = Column(String)  
    end_date = Column(String)
    end_time = Column(String)
    notes = Column(String)
    notify_before = Column(String)  
    notified = Column(Boolean, default=False) 

# 3. ΙΣΤΟΡΙΚΟ ΟΛΟΚΛΗΡΩΜΕΝΩΝ ΑΣΚΗΣΕΩΝ
class UserActivity(Base):
    __tablename__ = "user_activity"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    title = Column(String)
    activity_type = Column(String)
    duration_seconds = Column(Integer, default=0)
    completed_at = Column(DateTime, default=datetime.now)

# 4. RAW DATA (Από EmotiBit)
class RawBiometrics(Base):
    __tablename__ = "raw_biometrics"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    eda_value = Column(Float)
    temperature = Column(Float)
    heart_rate = Column(Float)
    hrv_bi = Column(Float)
    movement_val = Column(Float)
    is_moving = Column(Float)
    time = Column(DateTime, default=datetime.now)

# 5. ANXIETY LEVEL (Υπολογισμένο Στρες)
class AnxietyLevel(Base):
    __tablename__ = "anxiety_levels"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    anxiety_score = Column(Float)
    time = Column(DateTime, default=datetime.now)

# 6. TASKS (Η Βιβλιοθήκη των Τεχνικών)
class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    duration = Column(String)
    category = Column(String)
    is_favorite = Column(Boolean, default=False)
    details = Column(Text, nullable=True)

# 7. ΧΡΗΣΤΕΣ (Login/Signup)
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)
    password = Column(String)
    profile_image = Column(String, nullable=True)

# --- ΝΕΟ: 8. ΤΟΠΟΘΕΣΙΕΣ ΧΡΗΣΤΗ (Settings) ---
class UserLocation(Base):
    __tablename__ = "user_locations"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True) 
    name = Column(String)    
    address = Column(String)
    city = Column(String)
    area = Column(String)
    zip_code = Column(String)
    country = Column(String)
    is_default = Column(Boolean, default=False)
