# Telemetry Store Component

This module manages historical data storage for the Digital Twin using a custom Flask service and TimescaleDB.

## Architecture

- **Telemetry Service**: Custom Flask application that receives Context Broker notifications
- **TimescaleDB**: Time-series PostgreSQL database optimized for telemetry data
- **Subscriptions**: Orion Context Broker can notify the telemetry service of entity changes
- **Direct API**: Service exposes REST endpoints for manual data storage and queries

## How It Works

### Automatic Mode (via Subscriptions)

1. **Subscriptions**: Telemetry client creates subscriptions in Orion for entity changes
2. **Notification**: When an entity attribute changes, Orion notifies the telemetry service
3. **Storage**: Flask service receives notification and stores in TimescaleDB with timestamp
4. **Query**: Historical data retrieved via telemetry service API

### Manual Mode (Direct API)

1. **Direct POST**: Send entity data directly to `/v2/notify` endpoint
2. **Storage**: Service processes and stores in TimescaleDB
3. **Query**: Retrieve historical data via `/v2/entities/{id}` endpoint

## Structure

```
telemetry_store/
├── telemetry_service.py     # Flask API server (port 8668)
├── telemetry_client.py      # Python client for subscriptions and queries
├── requirements.txt         # Python dependencies (flask, psycopg2-binary)
└── README.md               # This file
```

## Installation

```powershell
cd telemetry_store
pip install -r requirements.txt
```

## Usage

### Start Services

The telemetry services are included in the main docker-compose:

```powershell
docker-compose up -d
```

This starts:

- TimescaleDB (PostgreSQL + TimescaleDB extension) on port 5432

### Start Telemetry Service

Run the Flask service:

```powershell
python telemetry_service.py
```

The service will:

- Start on port 8668
- Initialize TimescaleDB connection
- Create hypertable if needed
- Listen for notifications on `/v2/notify`
- Provide health check on `/health`
- Provide query endpoint on `/v2/entities/{id}`

### Create Subscriptions (Optional)

Run the telemetry client to create subscriptions:

```powershell
python telemetry_client.py
```

This creates subscriptions for:

- Robot entity (position, velocity, battery, status)
- Environment entity (temperature, lighting)
- Episode entity (reward, steps, metrics)

**Note**: Subscription notifications currently show "failed" status. Use direct API calls as workaround.

### Python API Examples

```python
from telemetry_client import TelemetryClient

# Initialize client
telemetry = TelemetryClient()

# Create subscription for Robot entity
telemetry.create_subscription(
    entity_type="Robot",
    watched_attributes=["position", "velocity", "battery"],
    notification_url="http://telemetry-service:8668/v2/notify"
)

# Get latest 10 values for a robot
history = telemetry.get_latest_values("Robot001", last_n=10)
print(history)

# Query specific entity history
history = telemetry.query_entity_history("Robot001")
print(history)
```

### Direct API Usage

**Store data manually (POST):**

```powershell
curl -X POST http://localhost:8668/v2/notify `
  -H "Content-Type: application/json" `
  -d '{
    "data": [{
      "id": "Robot001",
      "type": "Robot",
      "battery": {"type": "Number", "value": 85}
    }]
  }'
```

**Get latest values (GET):**

```powershell
curl "http://localhost:8668/v2/entities/Robot001?lastN=10"
```

**Health check:**

```powershell
curl http://localhost:8668/health
```

### Query Historical Data

**Get latest values:**

```powershell
curl "http://localhost:8668/v2/entities/Robot001?lastN=10"
```

**Response format:**

```json
{
  "data": [
    {
      "time": "2025-11-24T10:30:00Z",
      "entity_id": "Robot001",
      "entity_type": "Robot",
      "attributes": {
        "battery": 85,
        "position": { "x": 1.5, "y": 2.0, "z": 0.0 }
      }
    }
  ]
}
```

## Direct Database Access

You can query TimescaleDB directly:

```powershell
# Connect to database
docker exec -it telemetry-timescaledb psql -U postgres -d telemetry

# List all tables
\dt

# View telemetry data
SELECT * FROM telemetry_data ORDER BY time DESC LIMIT 10;

# Count records per entity
SELECT entity_id, COUNT(*) FROM telemetry_data GROUP BY entity_id;

# Get specific entity history
SELECT time, attribute_name, attribute_value
FROM telemetry_data
WHERE entity_id = 'Robot001'
ORDER BY time DESC;
```

## Database Schema

The telemetry service creates the following schema in TimescaleDB:

```sql
CREATE TABLE telemetry_data (
    id SERIAL,
    time TIMESTAMPTZ NOT NULL,
    entity_id TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    attribute_name TEXT NOT NULL,
    attribute_value JSONB NOT NULL,
    metadata JSONB,
    PRIMARY KEY (id, time)
);

-- Hypertable for time-series optimization
SELECT create_hypertable('telemetry_data', 'time');
```

**Fields:**

- **id**: Auto-incrementing record ID
- **time**: Timestamp when data was recorded (used for hypertable partitioning)
- **entity_id**: NGSI-LD entity identifier (e.g., "Robot001")
- **entity_type**: Type of entity (e.g., "Robot", "Environment")
- **attribute_name**: Name of the changed attribute
- **attribute_value**: JSONB value of the attribute
- **metadata**: Additional context information (optional)

## Integration Points

- **Context Broker**: Source of real-time entity changes (via subscriptions or manual updates)
- **Digital Twin**: Entities whose changes are tracked
- **Monitoring Dashboard**: Visualizes historical trends via telemetry API
- **RL Policy**: Can analyze historical performance metrics for training

## Monitoring

Check telemetry service health:

```powershell
curl http://localhost:8668/health
```

Response:

```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-24T10:30:00Z"
}
```

Check TimescaleDB status:

```powershell
docker logs telemetry-timescaledb
docker ps | grep timescaledb
```

## Endpoints

| Method | Endpoint                    | Description                               |
| ------ | --------------------------- | ----------------------------------------- |
| POST   | `/v2/notify`                | Receive notifications from Context Broker |
| GET    | `/v2/entities/{id}`         | Get historical data for entity            |
| GET    | `/v2/entities/{id}?lastN=X` | Get last N records                        |
| GET    | `/health`                   | Health check endpoint                     |

## Testing

Verify telemetry storage is working:

```powershell
# 1. Start telemetry service
python telemetry_service.py

# 2. Send test data
curl -X POST http://localhost:8668/v2/notify `
  -H "Content-Type: application/json" `
  -d '{
    "data": [{
      "id": "TestRobot",
      "type": "Robot",
      "battery": {"type": "Number", "value": 95}
    }]
  }'

# 3. Query stored data
curl http://localhost:8668/v2/entities/TestRobot?lastN=5

# 4. Check database
docker exec telemetry-timescaledb psql -U postgres -d telemetry `
  -c "SELECT * FROM telemetry_data WHERE entity_id='TestRobot';"
```

## Benefits

1. **Time-Series Optimization**: TimescaleDB hypertable for efficient time-series queries
2. **Flexible Storage**: Custom Flask service allows easy customization
3. **Historical Analysis**: Query past states for debugging and analysis
4. **Performance Metrics**: Track RL training progress over time
5. **Simple Integration**: Standard REST API compatible with FIWARE ecosystem
6. **Direct Access**: Can query TimescaleDB directly for advanced analytics

## Known Issues & Workarounds

**Issue**: Subscription notifications show "failed" status in Context Broker

**Workaround**: Use direct API calls to `/v2/notify` endpoint:

```python
import requests
response = requests.post(
    "http://localhost:8668/v2/notify",
    json={"data": [entity_data]}
)
```

**Root Cause**: Possible Docker network configuration issue. Direct API calls work correctly.
