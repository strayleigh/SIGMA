"""
SIGMA Configuration
Settings for MQTT, database, and detection rules
"""
import os
from dotenv import load_dotenv

load_dotenv()

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "test.mosquitto.org")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPICS = ["sigma/#"]  # Subscribe to all SIGMA topics

# Database Configuration
DATABASE_URL = "sqlite:///./sigma.db"

# Detection Rules - RGB thresholds for different fruit types
DETECTION_RULES = {
    "apple": {
        "fresh": {"r_min": 150, "g_min": 50, "g_max": 100, "b_max": 60},
        "warning": {"r_min": 120, "g_min": 40, "b_max": 80},
        # Anything else is considered rotten
    },
    "banana": {
        "fresh": {"r_min": 200, "g_min": 180, "b_min": 50, "b_max": 100},
        "warning": {"r_min": 150, "g_min": 120, "b_max": 80},
    },
    "orange": {
        "fresh": {"r_min": 200, "g_min": 100, "g_max": 150, "b_max": 60},
        "warning": {"r_min": 150, "g_min": 70, "b_max": 80},
    },
    "default": {
        "fresh": {"r_min": 150, "g_min": 80, "b_max": 100},
        "warning": {"r_min": 100, "g_min": 50, "b_max": 120},
    }
}

# WebSocket Configuration
WS_HEARTBEAT_INTERVAL = 30  # seconds

# CORS Origins
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
