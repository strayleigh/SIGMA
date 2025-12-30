"""
SIGMA Main Application
FastAPI app with WebSocket support and MQTT integration
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Set
import json
import asyncio

import config
import database
import detection
import api
from mqtt_client import SigmaMQTTClient

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        print(f"🔌 WebSocket client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        print(f"🔌 WebSocket client disconnected. Total: {len(self.active_connections)}")
    
    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        message_json = json.dumps(message)
        disconnected = set()
        
        for connection in self.active_connections:
            try:
                await connection.send_text(message_json)
            except Exception as e:
                print(f"❌ Error sending to WebSocket: {e}")
                disconnected.add(connection)
        
        # Remove disconnected clients
        for conn in disconnected:
            self.disconnect(conn)

# Global connection manager and MQTT client
manager = ConnectionManager()
mqtt_client = None

def handle_mqtt_message(topic: str, data: dict):
    """
    Handle incoming MQTT messages
    Process sensor data, run detection, save to DB, and broadcast
    """
    try:
        print(f"🔄 Processing MQTT message from topic: {topic}")
        
        # Extract data from payload
        fruit_id = data.get("fruitId")
        fruit_type = data.get("fruitType", "unknown")
        color_sensor = data.get("colorSensor", {})
        temperature = data.get("temperature")
        humidity = data.get("humidity")
        
        if not fruit_id or not color_sensor:
            print("⚠️ Missing required fields in MQTT message")
            return
        
        r = color_sensor.get("r", 0)
        g = color_sensor.get("g", 0)
        b = color_sensor.get("b", 0)
        
        # Run detection logic
        status, confidence = detection.detect_freshness(fruit_type, r, g, b, temperature)
        
        print(f"🔍 Detection result for {fruit_id}: {status} (confidence: {confidence:.2f})")
        
        # Save to database
        db = next(database.get_db())
        
        # Create sensor reading
        reading = database.SensorReading(
            fruit_id=fruit_id,
            fruit_type=fruit_type,
            r=r,
            g=g,
            b=b,
            temperature=temperature,
            humidity=humidity,
            status=status,
            timestamp=datetime.utcnow()
        )
        db.add(reading)
        
        # Update or create fruit record
        fruit = db.query(database.Fruit).filter(database.Fruit.fruit_id == fruit_id).first()
        if fruit:
            fruit.current_status = status
            fruit.last_seen = datetime.utcnow()
        else:
            fruit = database.Fruit(
                fruit_id=fruit_id,
                fruit_type=fruit_type,
                current_status=status,
                last_seen=datetime.utcnow()
            )
            db.add(fruit)
        
        # Log detection
        log = database.DetectionLog(
            fruit_id=fruit_id,
            detection_time=datetime.utcnow(),
            status=status,
            confidence=confidence
        )
        db.add(log)
        
        db.commit()
        db.close()
        
        print(f"💾 Data saved to database")
        
        # Broadcast to WebSocket clients
        broadcast_data = {
            "type": "sensor_update",
            "fruit_id": fruit_id,
            "fruit_type": fruit_type,
            "r": r,
            "g": g,
            "b": b,
            "temperature": temperature,
            "humidity": humidity,
            "status": status,
            "confidence": confidence,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Schedule broadcast (must be done in async context)
        asyncio.create_task(manager.broadcast(broadcast_data))
        
    except Exception as e:
        print(f"❌ Error handling MQTT message: {e}")
        import traceback
        traceback.print_exc()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    print("🚀 Starting SIGMA Backend...")
    
    # Initialize database
    database.init_db()
    print("✅ Database initialized")
    
    # Start MQTT client
    global mqtt_client
    mqtt_client = SigmaMQTTClient(on_message_callback=handle_mqtt_message)
    if mqtt_client.connect():
        mqtt_client.start()
        print("✅ MQTT client started")
    else:
        print("⚠️ Failed to start MQTT client")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down SIGMA Backend...")
    if mqtt_client:
        mqtt_client.stop()

# Create FastAPI app
app = FastAPI(
    title="SIGMA API",
    description="Sistem Indeks Kelayakan dan Kematangan Pangan",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api.router)

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connected",
            "message": "Connected to SIGMA WebSocket",
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Keep connection alive and handle incoming messages
        while True:
            # Wait for messages from client (e.g., ping)
            data = await websocket.receive_text()
            
            # Echo back or handle client messages
            if data == "ping":
                await websocket.send_json({"type": "pong"})
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
        manager.disconnect(websocket)

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SIGMA API - Sistem Indeks Kelayakan dan Kematangan Pangan",
        "version": "1.0.0",
        "endpoints": {
            "api": "/api/fruits, /api/sensors/latest, /api/sensors/history, /api/stats",
            "websocket": "/ws"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
