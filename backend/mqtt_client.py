"""
SIGMA MQTT Client
Subscribes to ESP32 sensor data and processes incoming messages
"""
import json
import paho.mqtt.client as mqtt
from datetime import datetime
from typing import Callable
import config

class SigmaMQTTClient:
    def __init__(self, on_message_callback: Callable):
        """
        Initialize MQTT client
        
        Args:
            on_message_callback: Function to call when message received
                                 Should accept (topic, payload_dict)
        """
        self.client = mqtt.Client(client_id="sigma_backend")
        self.on_message_callback = on_message_callback
        
        # Set callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        if rc == 0:
            print(f"✅ Connected to MQTT broker: {config.MQTT_BROKER}")
            # Subscribe to all SIGMA topics
            for topic in config.MQTT_TOPICS:
                client.subscribe(topic)
                print(f"📡 Subscribed to topic: {topic}")
        else:
            print(f"❌ Connection failed with code {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        if rc != 0:
            print(f"⚠️ Unexpected disconnection from MQTT broker")
    
    def _on_message(self, client, userdata, msg):
        """
        Callback when message received
        Parse JSON payload and call the registered callback
        """
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            print(f"📨 Received message on topic: {topic}")
            print(f"   Payload: {payload}")
            
            # Parse JSON
            data = json.loads(payload)
            
            # Add timestamp if not present
            if 'timestamp' not in data:
                data['timestamp'] = datetime.utcnow().isoformat()
            
            # Call the registered callback
            self.on_message_callback(topic, data)
            
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON: {e}")
        except Exception as e:
            print(f"❌ Error processing message: {e}")
    
    def connect(self):
        """Connect to MQTT broker"""
        try:
            self.client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
            return True
        except Exception as e:
            print(f"❌ Failed to connect to MQTT broker: {e}")
            return False
    
    def start(self):
        """Start the MQTT client loop in background"""
        self.client.loop_start()
    
    def stop(self):
        """Stop the MQTT client"""
        self.client.loop_stop()
        self.client.disconnect()
        print("🛑 MQTT client stopped")
