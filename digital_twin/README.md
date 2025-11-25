# Digital Twin Component

This module manages the Digital Twin entities using NGSI-LD format and communicates with the FIWARE Orion Context Broker.

## Structure

```
digital_twin/
├── models/                      # JSON-LD entity models
│   ├── robot_entity.json       # Robot digital twin model
│   ├── environment_entity.json # Environment model
│   └── episode_entity.json     # RL episode tracking model
├── digital_twin_client.py      # Python client for Context Broker
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Entity Models

### Robot Entity

Represents the physical robot from Isaac Sim:

- **Position**: 3D coordinates (x, y, z)
- **Velocity**: Movement speed in 3D space
- **Orientation**: Quaternion rotation (x, y, z, w)
- **Status**: Current state (idle, moving, error)
- **Battery**: Battery level percentage
- **Sensor Data**: Lidar, camera, IMU data

### Environment Entity

Represents the simulation environment:

- **Temperature**: Environmental temperature
- **Lighting**: Light configuration
- **Obstacles**: List of obstacles in the scene
- **Dimensions**: Environment size

### Episode Entity

Tracks reinforcement learning episodes:

- **Episode Number**: Current episode count
- **Reward**: Accumulated reward
- **Steps**: Number of steps taken
- **Metrics**: Performance metrics (success rate, collisions, distance)

## Usage

### Installation

```powershell
cd digital_twin
pip install -r requirements.txt
```

### Running the Client

```powershell
python digital_twin_client.py
```

This will:

1. Connect to the Context Broker
2. Create the three entity models
3. Demonstrate basic operations (list, update, retrieve)

### Python API Examples

```python
from digital_twin_client import DigitalTwinClient

# Initialize client
client = DigitalTwinClient("http://localhost:1026")

# Check connection
client.check_connection()

# Update robot position
client.update_robot_position("urn:ngsi-ld:Robot:001", x=1.5, y=2.0, z=0.0)

# Update robot velocity
client.update_robot_velocity("urn:ngsi-ld:Robot:001", vx=0.5, vy=0.0, vz=0.0)

# Update episode metrics
client.update_episode_metrics(
    "urn:ngsi-ld:Episode:001",
    reward=150.5,
    steps=100,
    metrics={
        "totalReward": 150.5,
        "successRate": 0.85,
        "collisions": 2
    }
)

# Get robot entity
robot = client.get_entity("urn:ngsi-ld:Robot:001")
print(robot)

# List all robots
robots = client.list_entities(entity_type="Robot")
```

## Integration Points

- **Telemetry Store**: Subscribes to entity changes for historical storage
- **Monitoring Dashboard**: Displays real-time entity states via Context Broker API

## NGSI-LD Context

The entities use a custom JSON-LD context alongside the standard NGSI-LD core context:

```json
{
  "@context": [
    "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
    {
      "Robot": "https://example.org/digitaltwin/Robot",
      "position": "https://example.org/digitaltwin/position",
      "velocity": "https://example.org/digitaltwin/velocity",
      ...
    }
  ]
}
```

This allows:

- **Semantic interoperability**: Standard vocabulary for data exchange
- **Type safety**: Well-defined property types
- **Extensibility**: Easy to add custom properties

## Testing

Verify entities are working:

```powershell
# 1. Create entities
python digital_twin_client.py

# 2. List all robots
curl -X GET http://localhost:1026/ngsi-ld/v1/entities?type=Robot `
  -H "Accept: application/ld+json"

# 3. Get specific entity
curl http://localhost:1026/ngsi-ld/v1/entities/urn:ngsi-ld:Robot:001 `
  -H "Accept: application/ld+json"

# 4. Update position manually
curl -X PATCH http://localhost:1026/ngsi-ld/v1/entities/urn:ngsi-ld:Robot:001/attrs `
  -H "Content-Type: application/json" `
  -d '{
    "position": {
      "type": "GeoProperty",
      "value": {
        "type": "Point",
        "coordinates": [2.5, 3.0, 0.5]
      }
    },
    "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld"
  }'
```

- Publish actions back to simulation
