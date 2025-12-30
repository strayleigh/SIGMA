"""
SIGMA Database Models
SQLAlchemy models for sensor readings, fruits, and detection logs
"""
from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import config

Base = declarative_base()

class SensorReading(Base):
    """Store all sensor readings from ESP32"""
    __tablename__ = "sensor_readings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fruit_id = Column(String, index=True)
    fruit_type = Column(String)
    r = Column(Integer)  # Red value (0-255)
    g = Column(Integer)  # Green value (0-255)
    b = Column(Integer)  # Blue value (0-255)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    status = Column(String)  # fresh, warning, rotten
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

class Fruit(Base):
    """Track individual fruits being monitored"""
    __tablename__ = "fruits"
    
    fruit_id = Column(String, primary_key=True)
    fruit_type = Column(String)
    current_status = Column(String)  # fresh, warning, rotten
    last_seen = Column(DateTime, default=datetime.utcnow)

class DetectionLog(Base):
    """Log detection events for analysis"""
    __tablename__ = "detection_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    fruit_id = Column(String, index=True)
    detection_time = Column(DateTime, default=datetime.utcnow)
    status = Column(String)
    confidence = Column(Float)  # 0.0 to 1.0

# Database setup
engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
