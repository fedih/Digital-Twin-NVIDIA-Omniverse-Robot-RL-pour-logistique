# Digital Twin Architecture with FIWARE Orion Context Broker

This project implements a Digital Twin architecture using FIWARE Orion Context Broker (NGSI-LD) as the central hub for managing context information.

## Architecture Components

1. ✅ **Context Broker (NGSI-LD)** - Central hub for managing context data using FIWARE Orion-LD
2. ✅ **Digital Twin (JSON-LD)** - Digital representation with Robot, Environment, and Episode entities
3. ⏳ **Nvidia Omniverse (Isaac Sim)** - Simulation environment (pending)
4. ⏳ **Reinforcement Learning (Policy)** - AI learning component (pending)
5. ✅ **Telemetry Store** - Custom Flask service with TimescaleDB for historical data
6. ✅ **Monitoring Dashboard** - Real-time web-based visualization with Chart.js

## Project Structure

```
tuteuré-projet/
├── docker-compose.yml          # Orion Context Broker + MongoDB + TimescaleDB
├── .env                        # Environment configuration
├── .gitignore                  # Git ignore rules
├── digital_twin/               # Digital Twin component
│   ├── models/                 # NGSI-LD entity models
│   │   ├── robot_entity.json
│   │   ├── environment_entity.json
│   │   └── episode_entity.json
│   ├── digital_twin_client.py  # Python client
│   ├── requirements.txt
│   └── README.md
├── telemetry_store/            # Historical data storage
│   ├── telemetry_service.py    # Flask notification service
│   ├── telemetry_client.py     # Query and subscription client
│   ├── requirements.txt
│   └── README.md
├── dashboard/                  # Web monitoring interface
│   ├── index.html              # Real-time dashboard
│   └── README.md
└── README.md                   # This file
```

## Quick Start

### 1. Start the Context Broker

```powershell
docker-compose up -d
```

Verify it's running:

```powershell
curl http://localhost:1026/version
```

### 2. Set Up Digital Twin

Install Python dependencies:

```powershell
cd digital_twin
pip install -r requirements.txt
```

Create digital twin entities:

```powershell
python digital_twin_client.py
```

This creates three entities in the Context Broker:

- **Robot Entity** (`urn:ngsi-ld:Robot:001`) - Robot state and sensors
- **Environment Entity** (`urn:ngsi-ld:Environment:001`) - Simulation environment
- **Episode Entity** (`urn:ngsi-ld:Episode:001`) - RL training episode

### 3. Start Telemetry Service

Install dependencies and start the Flask service:

```powershell
cd telemetry_store
pip install -r requirements.txt
python telemetry_service.py
```

The telemetry service:

- Listens on port 8668
- Receives notifications from Context Broker
- Stores historical data in TimescaleDB
- Provides query API for historical data

### 4. Open Monitoring Dashboard

```powershell
start dashboard/index.html
```

Or serve with HTTP server:

```powershell
cd dashboard
python -m http.server 8080
```

Then open: http://localhost:8080

The dashboard provides:

- Real-time entity monitoring (auto-refresh every 5 seconds)
- Battery level visualization with Chart.js
- Robot position, velocity, and sensor data
- Training episode metrics
- Environment information

### 5. Verify Entities

List all robots:

```powershell
curl "http://localhost:1026/ngsi-ld/v1/entities?type=Robot" -H "Accept: application/ld+json"
```

Get specific entity:

```powershell
curl "http://localhost:1026/ngsi-ld/v1/entities/urn:ngsi-ld:Robot:001" -H "Accept: application/ld+json"
```

## Management Commands

### Stop Services

```powershell
docker-compose down
```

### Stop and Remove Data

```powershell
docker-compose down -v
```

### View Logs

```powershell
docker logs fiware-orion
docker logs fiware-mongo
docker logs telemetry-timescaledb
```

### Access TimescaleDB

```powershell
docker exec -it telemetry-timescaledb psql -U postgres -d telemetry
```

Query telemetry data:

```sql
-- View all stored telemetry
SELECT * FROM telemetry_data ORDER BY time DESC LIMIT 10;

-- Count records per entity
SELECT entity_id, COUNT(*) FROM telemetry_data GROUP BY entity_id;
```

## API Endpoints

- **Orion Context Broker**: http://localhost:1026
- **MongoDB**: localhost:27017
- **TimescaleDB**: localhost:5432
- **Telemetry Service**: http://localhost:8668

## Key Features Implemented

### ✅ Context Broker (FIWARE Orion-LD 1.5.1)

- NGSI-LD API for semantic data management
- MongoDB 4.4 backend for compatibility
- Entity lifecycle management (Create, Read, Update, Delete)
- Subscription system for notifications

### ✅ Digital Twin Models

- Robot entity with position, velocity, sensors, battery
- Environment entity with temperature, lighting, obstacles
- Episode entity for RL training metrics
- Complete NGSI-LD JSON-LD structure with @context

### ✅ Telemetry Store

- Custom Flask service for historical data
- TimescaleDB hypertable for time-series optimization
- Direct notification endpoint (/v2/notify)
- Query API for retrieving historical data
- Tested with 4+ telemetry records stored

### ✅ Monitoring Dashboard

- Real-time web interface with auto-refresh
- Battery level chart with Chart.js
- Robot status, position, velocity display
- Sensor data visualization (IMU, Lidar, Camera)
- Training episode metrics
- Environment information display

## NGSI-LD Operations

### Create an Entity

```powershell
curl -X POST http://localhost:1026/ngsi-ld/v1/entities/ `
  -H "Content-Type: application/ld+json" `
  -d '{
    "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
    "id": "urn:ngsi-ld:Entity:001",
    "type": "ExampleEntity"
  }'
```

### Get All Entities

```powershell
curl -X GET http://localhost:1026/ngsi-ld/v1/entities/
```

## Testing

All components have been tested and verified:

✅ Context Broker responding on port 1026  
✅ Digital Twin entities created and retrievable  
✅ TimescaleDB storing telemetry data (4+ records)  
✅ Dashboard displaying real-time data  
✅ Direct notifications working with telemetry service

## Known Issues

1. **Subscription Notifications**: Automatic subscriptions show "failed" status. Direct POST to `/v2/notify` works correctly. This may be a network configuration issue between Docker containers.

**Workaround**: Use direct API calls to telemetry service or debug Docker network configuration.

## License

MIT
