"""
SIGMA REST API
API endpoints for querying sensor data, fruits, and history
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import database
import detection

router = APIRouter(prefix="/api")

# Pydantic models for API responses
class SensorReadingResponse(BaseModel):
    id: int
    fruit_id: str
    fruit_type: str
    r: int
    g: int
    b: int
    temperature: Optional[float]
    humidity: Optional[float]
    status: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

class FruitResponse(BaseModel):
    fruit_id: str
    fruit_type: str
    current_status: str
    last_seen: datetime
    status_color: str
    
    class Config:
        from_attributes = True

class StatsResponse(BaseModel):
    total_readings: int
    active_fruits: int
    fresh_count: int
    warning_count: int
    rotten_count: int

@router.get("/fruits", response_model=List[FruitResponse])
async def get_all_fruits(db: Session = Depends(database.get_db)):
    """Get all monitored fruits with their current status"""
    fruits = db.query(database.Fruit).all()
    
    # Add status color to response
    result = []
    for fruit in fruits:
        fruit_dict = {
            "fruit_id": fruit.fruit_id,
            "fruit_type": fruit.fruit_type,
            "current_status": fruit.current_status,
            "last_seen": fruit.last_seen,
            "status_color": detection.get_status_color(fruit.current_status)
        }
        result.append(fruit_dict)
    
    return result

@router.get("/fruits/{fruit_id}", response_model=FruitResponse)
async def get_fruit(fruit_id: str, db: Session = Depends(database.get_db)):
    """Get specific fruit details"""
    fruit = db.query(database.Fruit).filter(database.Fruit.fruit_id == fruit_id).first()
    
    if not fruit:
        return {"error": "Fruit not found"}
    
    return {
        "fruit_id": fruit.fruit_id,
        "fruit_type": fruit.fruit_type,
        "current_status": fruit.current_status,
        "last_seen": fruit.last_seen,
        "status_color": detection.get_status_color(fruit.current_status)
    }

@router.get("/sensors/latest", response_model=List[SensorReadingResponse])
async def get_latest_sensors(db: Session = Depends(database.get_db)):
    """Get the latest sensor reading for each fruit"""
    # Subquery to get max timestamp for each fruit
    from sqlalchemy import func
    subq = db.query(
        database.SensorReading.fruit_id,
        func.max(database.SensorReading.timestamp).label('max_timestamp')
    ).group_by(database.SensorReading.fruit_id).subquery()
    
    # Join to get full records
    latest_readings = db.query(database.SensorReading).join(
        subq,
        (database.SensorReading.fruit_id == subq.c.fruit_id) &
        (database.SensorReading.timestamp == subq.c.max_timestamp)
    ).all()
    
    return latest_readings

@router.get("/sensors/history", response_model=List[SensorReadingResponse])
async def get_sensor_history(
    fruit_id: Optional[str] = Query(None, description="Filter by fruit ID"),
    hours: int = Query(24, description="Number of hours to look back"),
    limit: int = Query(100, description="Maximum number of records"),
    db: Session = Depends(database.get_db)
):
    """Get historical sensor data with filters"""
    # Calculate time threshold
    time_threshold = datetime.utcnow() - timedelta(hours=hours)
    
    # Build query
    query = db.query(database.SensorReading).filter(
        database.SensorReading.timestamp >= time_threshold
    )
    
    # Add fruit filter if specified
    if fruit_id:
        query = query.filter(database.SensorReading.fruit_id == fruit_id)
    
    # Order by timestamp descending and limit
    readings = query.order_by(desc(database.SensorReading.timestamp)).limit(limit).all()
    
    return readings

@router.get("/stats", response_model=StatsResponse)
async def get_stats(db: Session = Depends(database.get_db)):
    """Get system statistics"""
    from sqlalchemy import func
    
    total_readings = db.query(func.count(database.SensorReading.id)).scalar()
    active_fruits = db.query(func.count(database.Fruit.fruit_id)).scalar()
    
    # Count by status
    fresh_count = db.query(func.count(database.Fruit.fruit_id)).filter(
        database.Fruit.current_status == "fresh"
    ).scalar()
    
    warning_count = db.query(func.count(database.Fruit.fruit_id)).filter(
        database.Fruit.current_status == "warning"
    ).scalar()
    
    rotten_count = db.query(func.count(database.Fruit.fruit_id)).filter(
        database.Fruit.current_status == "rotten"
    ).scalar()
    
    return {
        "total_readings": total_readings or 0,
        "active_fruits": active_fruits or 0,
        "fresh_count": fresh_count or 0,
        "warning_count": warning_count or 0,
        "rotten_count": rotten_count or 0
    }
