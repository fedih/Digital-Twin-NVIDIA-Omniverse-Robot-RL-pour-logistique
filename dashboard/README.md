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

- Change refresh interval (default: 5000ms / 5 seconds)
- Modify colors and styles (CSS in `<style>` section)
- Add new metrics or sections
- Change chart configuration (Chart.js options)
- Adjust API endpoints if running on different ports

### Example: Change Refresh Rate

Find this line in the JavaScript:

```javascript
setInterval(loadAllData, 5000); // Refresh every 5 seconds
```

Change to 10 seconds:

```javascript
setInterval(loadAllData, 10000); // Refresh every 10 seconds
```

### Example: Add New Chart

```javascript
// Create new chart for velocity
const velocityChart = new Chart(ctx, {
  type: "line",
  data: {
    labels: timestamps,
    datasets: [
      {
        label: "Velocity",
        data: velocityData,
        borderColor: "rgb(75, 192, 192)",
      },
    ],
  },
});
```

## Technologies

- Pure HTML/CSS/JavaScript (no build tools required)
- Chart.js 3.9.1 for data visualization (loaded via CDN)
- Fetch API for REST calls to Context Broker and Telemetry Service
- CSS Grid for responsive layout
- Modern ES6+ JavaScript

## Architecture

```
┌─────────────┐
│  Dashboard  │
│ (index.html)│
└──────┬──────┘
       │
       ├─────────────────┐
       │                 │
       ▼                 ▼
┌────────────┐    ┌──────────────┐
│  Context   │    │  Telemetry   │
│  Broker    │    │   Service    │
│ (port 1026)│    │  (port 8668) │
└────────────┘    └──────────────┘
```

The dashboard makes REST API calls every 5 seconds to:

1. Context Broker for real-time entity states (Robot, Episode, Environment)
2. Telemetry Service for historical battery data (last 20 records)

## Data Flow

1. **Robot Data**: `GET /ngsi-ld/v1/entities/urn:ngsi-ld:Robot:001` → Display position, velocity, sensors, battery
2. **Episode Data**: `GET /ngsi-ld/v1/entities/urn:ngsi-ld:Episode:001` → Display training metrics
3. **Environment Data**: `GET /ngsi-ld/v1/entities/urn:ngsi-ld:Environment:001` → Display environment info
4. **Battery History**: `GET /v2/entities/Robot001?lastN=20` → Chart.js visualization

## Troubleshooting

**Dashboard shows "Loading..." forever:**

- Check if Context Broker is running: `curl http://localhost:1026/version`
- Check if Telemetry Service is running: `curl http://localhost:8668/health`
- Open browser console (F12) to see any error messages

**Battery chart not showing:**

- Verify telemetry service has stored data
- Check database: `docker exec telemetry-timescaledb psql -U postgres -d telemetry -c "SELECT COUNT(*) FROM telemetry_data;"`
- Ensure at least one battery update has been stored

**CORS errors:**

- If opening `index.html` directly (`file://`), use HTTP server instead
- Run: `python -m http.server 8080` in dashboard folder

## Future Enhancements

- [ ] Add velocity magnitude chart
- [ ] Display sensor data as time-series graphs
- [ ] Add episode rewards chart
- [ ] Implement WebSocket for real-time updates (instead of polling)
- [ ] Add entity selection dropdown
- [ ] Export data to CSV
- [ ] Add alerts for low battery or errors
