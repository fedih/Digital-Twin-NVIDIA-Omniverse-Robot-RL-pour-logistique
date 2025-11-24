# Digital Twin Architecture with FIWARE Orion Context Broker

This project implements a Digital Twin architecture using FIWARE Orion Context Broker (NGSI-LD) as the central hub for managing context information.

## Architecture Components

1. ✅ **Context Broker (NGSI-LD)** - Central hub for managing context data using FIWARE Orion-LD
2. ✅ **Digital Twin (JSON-LD)** - Digital representation with Robot, Environment, and Episode entities
3. ⏳ **Nvidia Omniverse (Isaac Sim)** - Simulation environment
4. ⏳ **Reinforcement Learning (Policy)** - AI learning component
5. ⏳ **Telemetry Store** - Data storage
6. ⏳ **Monitoring Dashboard** - Real-time visualization

## Project Structure

```
tuteuré-projet/
├── docker-compose.yml          # Orion Context Broker setup
├── .env                        # Environment configuration
├── digital_twin/               # Digital Twin component
│   ├── models/                 # NGSI-LD entity models
│   │   ├── robot_entity.json
│   │   ├── environment_entity.json
│   │   └── episode_entity.json
│   ├── digital_twin_client.py  # Python client
│   ├── requirements.txt
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

### 3. Verify Entities

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
```

## API Endpoints

- **Orion Context Broker**: http://localhost:1026
- **MongoDB**: localhost:27017

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

## Next Steps

- [ ] Integrate Nvidia Omniverse (Isaac Sim)
- [ ] Set up Digital Twin JSON-LD models
- [ ] Implement Reinforcement Learning component
- [ ] Configure Telemetry Store
- [ ] Build Monitoring Dashboard

## License

MIT
