/**
 * SIGMA Frontend Application
 * Real-time fruit monitoring with WebSocket and REST API integration
 */

// Configuration
const API_BASE_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';

// Global state
let websocket = null;
let chart = null;
let reconnectInterval = null;

// DOM elements
const connectionStatus = document.getElementById('connectionStatus');
const freshCount = document.getElementById('freshCount');
const warningCount = document.getElementById('warningCount');
const rottenCount = document.getElementById('rottenCount');
const totalReadings = document.getElementById('totalReadings');
const latestSensors = document.getElementById('latestSensors');
const fruitsGrid = document.getElementById('fruitsGrid');
const fruitSelect = document.getElementById('fruitSelect');
const timeRange = document.getElementById('timeRange');
const refreshChart = document.getElementById('refreshChart');

// Fruit emoji mapping
const FRUIT_EMOJIS = {
    apple: '🍎',
    banana: '🍌',
    orange: '🍊',
    grape: '🍇',
    strawberry: '🍓',
    default: '🍎'
};

/**
 * Initialize application
 */
async function init() {
    console.log('🚀 Initializing SIGMA Frontend...');
    
    // Connect to WebSocket
    connectWebSocket();
    
    // Load initial data
    await loadStats();
    await loadFruits();
    await loadLatestSensors();
    await loadHistoricalData();
    
    // Set up event listeners
    refreshChart.addEventListener('click', loadHistoricalData);
    timeRange.addEventListener('change', loadHistoricalData);
    fruitSelect.addEventListener('change', loadHistoricalData);
}

/**
 * WebSocket connection
 */
function connectWebSocket() {
    console.log('🔌 Connecting to WebSocket...');
    
    try {
        websocket = new WebSocket(WS_URL);
        
        websocket.onopen = () => {
            console.log('✅ WebSocket connected');
            updateConnectionStatus(true);
            
            // Clear reconnect interval
            if (reconnectInterval) {
                clearInterval(reconnectInterval);
                reconnectInterval = null;
            }
        };
        
        websocket.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                console.log('📨 WebSocket message:', data);
                handleWebSocketMessage(data);
            } catch (error) {
                console.error('❌ Error parsing WebSocket message:', error);
            }
        };
        
        websocket.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
            updateConnectionStatus(false);
        };
        
        websocket.onclose = () => {
            console.log('🔌 WebSocket disconnected');
            updateConnectionStatus(false);
            
            // Auto-reconnect after 5 seconds
            if (!reconnectInterval) {
                reconnectInterval = setInterval(() => {
                    console.log('🔄 Attempting to reconnect...');
                    connectWebSocket();
                }, 5000);
            }
        };
        
    } catch (error) {
        console.error('❌ Failed to create WebSocket:', error);
        updateConnectionStatus(false);
    }
}

/**
 * Handle WebSocket messages
 */
function handleWebSocketMessage(data) {
    if (data.type === 'connected') {
        console.log('✅ WebSocket connection confirmed');
    } else if (data.type === 'sensor_update') {
        console.log('📡 Sensor update received');
        
        // Update displays
        loadStats();
        loadFruits();
        loadLatestSensors();
        
        // Show notification (optional)
        showNotification(data);
    }
}

/**
 * Update connection status indicator
 */
function updateConnectionStatus(connected) {
    if (connected) {
        connectionStatus.classList.add('connected');
        connectionStatus.classList.remove('disconnected');
        connectionStatus.querySelector('.status-text').textContent = 'Connected';
    } else {
        connectionStatus.classList.add('disconnected');
        connectionStatus.classList.remove('connected');
        connectionStatus.querySelector('.status-text').textContent = 'Disconnected';
    }
}

/**
 * Load statistics
 */
async function loadStats() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/stats`);
        const data = await response.json();
        
        freshCount.textContent = data.fresh_count;
        warningCount.textContent = data.warning_count;
        rottenCount.textContent = data.rotten_count;
        totalReadings.textContent = data.total_readings;
        
    } catch (error) {
        console.error('❌ Error loading stats:', error);
    }
}

/**
 * Load all fruits
 */
async function loadFruits() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/fruits`);
        const fruits = await response.json();
        
        if (fruits.length === 0) {
            fruitsGrid.innerHTML = '<div class="empty-state"><p>No fruits being monitored yet</p></div>';
            return;
        }
        
        // Update fruit select dropdown
        fruitSelect.innerHTML = '<option value="">All Fruits</option>';
        fruits.forEach(fruit => {
            const option = document.createElement('option');
            option.value = fruit.fruit_id;
            option.textContent = `${fruit.fruit_id} (${fruit.fruit_type})`;
            fruitSelect.appendChild(option);
        });
        
        // Render fruit cards
        fruitsGrid.innerHTML = fruits.map(fruit => createFruitCard(fruit)).join('');
        
    } catch (error) {
        console.error('❌ Error loading fruits:', error);
    }
}

/**
 * Create fruit card HTML
 */
function createFruitCard(fruit) {
    const emoji = FRUIT_EMOJIS[fruit.fruit_type.toLowerCase()] || FRUIT_EMOJIS.default;
    const lastSeen = new Date(fruit.last_seen).toLocaleString();
    
    return `
        <div class="fruit-card">
            <div class="fruit-emoji">${emoji}</div>
            <div class="fruit-name">${fruit.fruit_id}</div>
            <div class="fruit-type">${fruit.fruit_type}</div>
            <div class="fruit-status ${fruit.current_status}">
                ${fruit.current_status}
            </div>
            <div class="sensor-timestamp">Last seen: ${lastSeen}</div>
        </div>
    `;
}

/**
 * Load latest sensor readings
 */
async function loadLatestSensors() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/sensors/latest`);
        const sensors = await response.json();
        
        if (sensors.length === 0) {
            latestSensors.innerHTML = `
                <div class="empty-state">
                    <p>Waiting for sensor data...</p>
                    <p class="empty-hint">Make sure your ESP32 is publishing to MQTT</p>
                </div>
            `;
            return;
        }
        
        // Render sensor cards
        latestSensors.innerHTML = sensors.map(sensor => createSensorCard(sensor)).join('');
        
    } catch (error) {
        console.error('❌ Error loading sensors:', error);
    }
}

/**
 * Create sensor card HTML
 */
function createSensorCard(sensor) {
    const timestamp = new Date(sensor.timestamp).toLocaleString();
    const rPercent = (sensor.r / 255 * 100).toFixed(0);
    const gPercent = (sensor.g / 255 * 100).toFixed(0);
    const bPercent = (sensor.b / 255 * 100).toFixed(0);
    
    return `
        <div class="sensor-card">
            <div class="sensor-header">
                <div class="sensor-id">${sensor.fruit_id}</div>
                <div class="sensor-badge ${sensor.status}">${sensor.status}</div>
            </div>
            
            <div class="rgb-display">
                <div class="rgb-bar">
                    <div class="rgb-bar-fill" style="width: ${rPercent}%; background: #ef4444;"></div>
                </div>
                <div class="rgb-bar">
                    <div class="rgb-bar-fill" style="width: ${gPercent}%; background: #4ade80;"></div>
                </div>
                <div class="rgb-bar">
                    <div class="rgb-bar-fill" style="width: ${bPercent}%; background: #3b82f6;"></div>
                </div>
            </div>
            
            <div class="sensor-values">
                <div class="sensor-value">
                    <div class="sensor-value-label">R</div>
                    <div class="sensor-value-number" style="color: #ef4444;">${sensor.r}</div>
                </div>
                <div class="sensor-value">
                    <div class="sensor-value-label">G</div>
                    <div class="sensor-value-number" style="color: #4ade80;">${sensor.g}</div>
                </div>
                <div class="sensor-value">
                    <div class="sensor-value-label">B</div>
                    <div class="sensor-value-number" style="color: #3b82f6;">${sensor.b}</div>
                </div>
            </div>
            
            ${sensor.temperature ? `
                <div class="sensor-values" style="margin-top: 0.5rem;">
                    <div class="sensor-value">
                        <div class="sensor-value-label">🌡️ Temp</div>
                        <div class="sensor-value-number">${sensor.temperature.toFixed(1)}°C</div>
                    </div>
                    <div class="sensor-value">
                        <div class="sensor-value-label">💧 Humidity</div>
                        <div class="sensor-value-number">${sensor.humidity?.toFixed(1) || 'N/A'}%</div>
                    </div>
                </div>
            ` : ''}
            
            <div class="sensor-timestamp">${timestamp}</div>
        </div>
    `;
}

/**
 * Load historical data and render chart
 */
async function loadHistoricalData() {
    try {
        const hours = timeRange.value;
        const selectedFruit = fruitSelect.value;
        
        let url = `${API_BASE_URL}/api/sensors/history?hours=${hours}&limit=500`;
        if (selectedFruit) {
            url += `&fruit_id=${selectedFruit}`;
        }
        
        const response = await fetch(url);
        const data = await response.json();
        
        if (data.length === 0) {
            console.log('No historical data available');
            return;
        }
        
        // Reverse to show oldest first
        data.reverse();
        
        // Prepare chart data
        const labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
        const rData = data.map(d => d.r);
        const gData = data.map(d => d.g);
        const bData = data.map(d => d.b);
        const tempData = data.map(d => d.temperature || null);
        
        renderChart(labels, rData, gData, bData, tempData);
        
    } catch (error) {
        console.error('❌ Error loading historical data:', error);
    }
}

/**
 * Render Chart.js chart
 */
function renderChart(labels, rData, gData, bData, tempData) {
    const ctx = document.getElementById('sensorChart').getContext('2d');
    
    // Destroy existing chart
    if (chart) {
        chart.destroy();
    }
    
    chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Red (R)',
                    data: rData,
                    borderColor: '#ef4444',
                    backgroundColor: 'rgba(239, 68, 68, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Green (G)',
                    data: gData,
                    borderColor: '#4ade80',
                    backgroundColor: 'rgba(74, 222, 128, 0.1)',
                    tension: 0.4
                },
                {
                    label: 'Blue (B)',
                    data: bData,
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    labels: {
                        color: '#ffffff',
                        font: {
                            family: 'Poppins'
                        }
                    }
                },
                title: {
                    display: true,
                    text: 'RGB Color Sensor Trends',
                    color: '#ffffff',
                    font: {
                        size: 16,
                        family: 'Poppins',
                        weight: 600
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 255,
                    ticks: {
                        color: '#a0aec0'
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                },
                x: {
                    ticks: {
                        color: '#a0aec0',
                        maxTicksLimit: 10
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.1)'
                    }
                }
            }
        }
    });
}

/**
 * Show notification for sensor update (optional)
 */
function showNotification(data) {
    console.log(`🔔 ${data.fruit_id}: ${data.status.toUpperCase()}`);
    // Could implement toast notifications here
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
