# Monitoring Dashboard

Real-time web dashboard for monitoring the Digital Twin system.

## Features

- **Real-time Monitoring**: Auto-refreshes every 5 seconds
- **Robot Status**: Battery level, position, velocity, status
- **Sensor Data**: IMU, Lidar, Camera readings
- **Training Metrics**: Episode number, rewards, steps
- **Environment Info**: Temperature, lighting, dimensions
- **Historical Charts**: Battery level history from telemetry store

## Usage

### Option 1: Open Directly

Simply open `index.html` in your web browser:

```powershell
start dashboard/index.html
```

### Option 2: Simple HTTP Server

For better CORS handling, serve with Python:

```powershell
cd dashboard
python -m http.server 8080
```

Then open: http://localhost:8080

### Option 3: Live Server (VS Code)

If you have Live Server extension:

1. Right-click `index.html`
2. Select "Open with Live Server"

## Requirements

- Context Broker running on `localhost:1026`
- Telemetry Service running on `localhost:8668`
- Modern web browser (Chrome, Firefox, Edge)

## Dashboard Sections

### 🤖 Robot Status

- Current operational status
- Robot name
- Battery level with visual indicator
- Last update timestamp

### 📍 Position & Velocity

- 3D position coordinates (X, Y, Z)
- Velocity vector in 3D space

### 📡 Sensor Data

- IMU acceleration and gyroscope readings
- Lidar point count
- Camera status

### 🎯 Training Episode

- Current episode number
- Accumulated reward
- Step count
- Episode status

### 🌍 Environment

- Temperature
- Lighting configuration
- Environment dimensions

### 📊 Battery History

- Line chart showing battery level over time
- Data from telemetry store
- Last 20 data points

## API Endpoints Used

**Context Broker (NGSI-LD):**

- `GET /ngsi-ld/v1/entities/urn:ngsi-ld:Robot:001`
- `GET /ngsi-ld/v1/entities/urn:ngsi-ld:Episode:001`
- `GET /ngsi-ld/v1/entities/urn:ngsi-ld:Environment:001`

**Telemetry Store:**

- `GET /v2/entities/{entityId}?lastN=20`

## Customization

Edit the `index.html` file to:

- Change refresh interval (default: 5000ms)
- Modify colors and styles
- Add new metrics
- Change chart types

## Technologies

- Pure HTML/CSS/JavaScript
- Chart.js for data visualization
- Fetch API for REST calls
- CSS Grid for responsive layout
