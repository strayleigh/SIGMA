# 🍎 SIGMA - Sistem Indeks Kelayakan dan Kematangan Pangan

Real-time fruit freshness monitoring system using ESP32, color sensors, MQTT, and Python backend.

## 🎯 Features

- ✅ **Real-time Monitoring** - Live sensor data from ESP32 via MQTT
- ✅ **WebSocket Updates** - Instant UI updates without page refresh
- ✅ **Rule-Based Detection** - Fruit freshness analysis (Fresh/Warning/Rotten)
- ✅ **Historical Data** - Track sensor trends over time with charts
- ✅ **Multi-Fruit Support** - Monitor multiple fruits simultaneously
- ✅ **Vibrant UI** - Modern, colorful, and responsive design
- ✅ **Database Storage** - Persistent SQLite database
- ✅ **REST API** - Query sensor data and statistics
- ✅ **ML Ready** - Structured data for future machine learning integration

## 🏗️ Architecture

```
ESP32 → MQTT Broker → Python Backend (FastAPI) → SQLite Database
                              ↓
                        REST API + WebSocket
                              ↓
                         Web Frontend
```

## 📋 Prerequisites

- Python 3.8 or higher
- Pip (Python package installer)
- Modern web browser (Chrome, Firefox, Edge)
- MQTT broker (uses test.mosquitto.org by default)
- ESP32 with color sensor (for actual testing)

## 🚀 Installation

### 1. Clone/Download the Project

```bash
cd "c:\Users\KUKU PAPA\OneDrive\Documents\Tugas SMT 6\ELECTRICAL ENGINEERING THINGS\Tugas SMT 7\SIGMA"
```

### 2. Set Up Backend

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt
```

### 3. Set Up Frontend

No installation needed for frontend - it's pure HTML/CSS/JavaScript!

## ▶️ Running the Application

### Start Backend Server

```bash
# From the backend directory
python main.py
```

Or using uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend will start on `http://localhost:8000`

### Start Frontend

Open a new terminal:

```bash
# From the frontend directory
cd ../frontend
python -m http.server 3000
```

Or use any static file server. The frontend will be available at `http://localhost:3000`

### Open in Browser

Navigate to `http://localhost:3000` in your web browser.

## 📡 MQTT Configuration

### Default Settings

- **Broker**: `test.mosquitto.org`
- **Port**: `1883`
- **Topics**: `sigma/#` (subscribes to all SIGMA topics)

### Expected MQTT Topics

Your ESP32 should publish to:

- `sigma/fruit/{fruitId}/data` - Sensor readings

### ESP32 Message Format

```json
{
  "fruitId": "fruit_1",
  "fruitType": "apple",
  "colorSensor": {
    "r": 180,
    "g": 50,
    "b": 40
  },
  "temperature": 25.5,
  "humidity": 60
}
```

## 🧪 Testing with MQTT

You can test the system without ESP32 using MQTT publish:

```bash
# Install mosquitto clients (if not already installed)
# Windows: Download from mosquitto.org
# Linux: sudo apt-get install mosquitto-clients

# Publish test data
mosquitto_pub -h test.mosquitto.org -t "sigma/fruit/fruit_1/data" -m '{"fruitId":"fruit_1","fruitType":"apple","colorSensor":{"r":180,"g":50,"b":40},"temperature":25.5,"humidity":60}'

# Test with different fruits
mosquitto_pub -h test.mosquitto.org -t "sigma/fruit/fruit_2/data" -m '{"fruitId":"fruit_2","fruitType":"banana","colorSensor":{"r":220,"g":200,"b":60},"temperature":24.0,"humidity":55}'

mosquitto_pub -h test.mosquitto.org -t "sigma/fruit/fruit_3/data" -m '{"fruitId":"fruit_3","fruitType":"orange","colorSensor":{"r":230,"g":120,"b":30},"temperature":26.0,"humidity":58}'
```

## 🎨 Detection Rules

Fruit freshness is detected based on RGB color values:

### Apple

- **Fresh**: R > 150, G: 50-100, B < 60
- **Warning**: R > 120, G > 40, B < 80
- **Rotten**: Otherwise

### Banana

- **Fresh**: R > 200, G > 180, B: 50-100
- **Warning**: R > 150, G > 120, B < 80
- **Rotten**: Otherwise

### Orange

- **Fresh**: R > 200, G: 100-150, B < 60
- **Warning**: R > 150, G > 70, B < 80
- **Rotten**: Otherwise

You can customize these rules in `backend/config.py`.

## 📊 API Endpoints

- `GET /` - API information
- `GET /api/fruits` - List all monitored fruits
- `GET /api/fruits/{fruitId}` - Get specific fruit
- `GET /api/sensors/latest` - Latest sensor readings
- `GET /api/sensors/history?hours=24&fruit_id=fruit_1` - Historical data
- `GET /api/stats` - System statistics
- `WebSocket /ws` - Real-time updates

## 📁 Project Structure

```
SIGMA/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── database.py          # SQLAlchemy models
│   ├── mqtt_client.py       # MQTT subscriber
│   ├── detection.py         # Freshness detection logic
│   ├── api.py               # REST API endpoints
│   ├── config.py            # Configuration settings
│   ├── requirements.txt     # Python dependencies
│   └── sigma.db             # SQLite database (created on first run)
│
└── frontend/
    ├── index.html           # Main HTML page
    ├── styles.css           # Vibrant CSS styling
    └── app.js               # JavaScript application
```

## 🔧 Configuration

Edit `backend/config.py` to customize:

- MQTT broker settings
- Detection rule thresholds
- Database path
- CORS origins

## 🤖 Future ML Integration

The system is designed for easy ML integration:

- All sensor data stored in structured database
- Detection confidence scores logged
- Historical patterns available for training
- Simply replace rule-based `detection.py` with ML model

## 🐛 Troubleshooting

### Backend won't start

- Check if port 8000 is available
- Verify Python dependencies are installed
- Check firewall settings

### Frontend can't connect to backend

- Verify backend is running on port 8000
- Check CORS settings in `config.py`
- Ensure frontend URL is in `CORS_ORIGINS`

### No MQTT data received

- Verify MQTT broker is accessible
- Check ESP32 is publishing to correct topics
- Test with `mosquitto_pub` command
- Check backend logs for MQTT connection status

### WebSocket disconnects

- Check backend is running
- Verify firewall allows WebSocket connections
- Frontend will auto-reconnect every 5 seconds

## 📝 License

This project is for educational and research purposes.

## 👥 Contributors

SIGMA - Sistem Indeks Kelayakan dan Kematangan Pangan

---

**Happy Monitoring! 🍎🍌🍊**
