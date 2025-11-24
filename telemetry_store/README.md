# Telemetry Store Component

This module manages historical data storage for the Digital Twin using QuantumLeap and TimescaleDB.

## Architecture

- **QuantumLeap**: FIWARE component that subscribes to Context Broker changes and stores them
- **TimescaleDB**: Time-series PostgreSQL database optimized for telemetry data
- **Subscriptions**: Orion Context Broker notifies QuantumLeap of entity changes

## How It Works

1. **Subscriptions**: QuantumLeap subscribes to entity changes in Orion
2. **Notification**: When an entity attribute changes, Orion notifies QuantumLeap
3. **Storage**: QuantumLeap stores the change with timestamp in TimescaleDB
4. **Query**: Historical data can be queried via QuantumLeap API or directly from TimescaleDB

## Structure

```
telemetry_store/
├── telemetry_client.py      # Python client for QuantumLeap and TimescaleDB
├── requirements.txt         # Python dependencies
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
- QuantumLeap on port 8668

### Create Subscriptions

Run the telemetry client to create subscriptions:

```powershell
python telemetry_client.py
```

This creates subscriptions for:

- Robot entity (position, velocity, battery, status)
- Environment entity (temperature, lighting)
- Episode entity (reward, steps, metrics)

### Python API Examples

```python
from telemetry_client import TelemetryClient, TimescaleDBClient

# Initialize client
telemetry = TelemetryClient()

# Create subscription for Robot entity
telemetry.create_subscription(
    entity_type="Robot",
    watched_attributes=["position", "velocity", "battery"]
)

# Get latest 10 values for a robot
history = telemetry.get_latest_values("urn:ngsi-ld:Robot:001", last_n=10)
print(history)

# Get history for specific time range
from datetime import datetime, timedelta
now = datetime.utcnow()
one_hour_ago = now - timedelta(hours=1)

history = telemetry.get_entity_history(
    entity_id="urn:ngsi-ld:Robot:001",
    attribute="position",
    from_date=one_hour_ago.isoformat() + "Z",
    to_date=now.isoformat() + "Z"
)
```

### Query Historical Data

**Get latest values:**

```powershell
curl "http://localhost:8668/v2/entities/urn:ngsi-ld:Robot:001?lastN=10" `
  -H "Fiware-Service: digitaltwin" `
  -H "Fiware-ServicePath: /"
```

**Get specific attribute history:**

```powershell
curl "http://localhost:8668/v2/entities/urn:ngsi-ld:Robot:001/attrs/position" `
  -H "Fiware-Service: digitaltwin" `
  -H "Fiware-ServicePath: /"
```

**Get time-range data:**

```powershell
curl "http://localhost:8668/v2/entities/urn:ngsi-ld:Robot:001?fromDate=2025-11-24T00:00:00Z&toDate=2025-11-24T23:59:59Z" `
  -H "Fiware-Service: digitaltwin" `
  -H "Fiware-ServicePath: /"
```

## Direct Database Access

You can also query TimescaleDB directly:

```powershell
# Connect to database
docker exec -it telemetry-timescaledb psql -U postgres -d telemetry

# List all tables
\dt

# Query entity data
SELECT * FROM entity_data WHERE entity_id = 'urn:ngsi-ld:Robot:001' LIMIT 10;
```

## Data Model

QuantumLeap stores data with:

- **entity_id**: The NGSI-LD entity identifier
- **entity_type**: Type of the entity
- **attribute_name**: Name of the changed attribute
- **attribute_value**: Value of the attribute
- **timestamp**: When the change occurred
- **metadata**: Additional context information

## Integration Points

- **Context Broker**: Source of real-time entity changes
- **Digital Twin**: Entities whose changes are tracked
- **Monitoring Dashboard**: Visualizes historical trends
- **RL Policy**: Analyzes historical performance metrics

## Monitoring

Check QuantumLeap health:

```powershell
curl http://localhost:8668/health
```

Check TimescaleDB status:

```powershell
docker logs telemetry-timescaledb
```

## Benefits

1. **Time-Series Optimization**: TimescaleDB is optimized for time-series data queries
2. **Automatic Storage**: QuantumLeap automatically stores all subscribed changes
3. **Historical Analysis**: Query past states for analysis and debugging
4. **Performance Metrics**: Track RL training progress over time
5. **Data Retention**: Configurable retention policies for old data
