import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime


class DigitalTwinClient:
    
    def __init__(self, orion_url: str = "http://localhost:1026"):
        self.orion_url = orion_url
        self.base_url = f"{orion_url}/ngsi-ld/v1"
        self.headers = {
            "Content-Type": "application/ld+json",
            "Accept": "application/ld+json"
        }
    
    def create_entity(self, entity_data: Dict[str, Any]) -> bool:
        try:
            response = requests.post(
                f"{self.base_url}/entities/",
                headers=self.headers,
                json=entity_data
            )
            if response.status_code == 201:
                print(f"Entity {entity_data['id']} created")
                return True
            else:
                print(f"Failed to create entity: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        try:
            response = requests.get(
                f"{self.base_url}/entities/{entity_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Entity not found: {response.status_code}")
                return None
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
    
    def update_entity_attribute(self, entity_id: str, attribute_name: str, 
                               attribute_value: Any, attribute_type: str = "Property") -> bool:
        try:
            attribute_data = {
                "@context": "https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld",
                "type": attribute_type,
                "value": attribute_value,
                "observedAt": datetime.now(datetime.UTC if hasattr(datetime, 'UTC') else None).isoformat().replace('+00:00', 'Z') if hasattr(datetime, 'UTC') else datetime.utcnow().isoformat() + "Z"
            }
            
            response = requests.patch(
                f"{self.base_url}/entities/{entity_id}/attrs/{attribute_name}",
                headers=self.headers,
                json=attribute_data
            )
            if response.status_code == 204:
                return True
            else:
                print(f"Failed to update: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def delete_entity(self, entity_id: str) -> bool:
        try:
            response = requests.delete(
                f"{self.base_url}/entities/{entity_id}",
                headers=self.headers
            )
            if response.status_code == 204:
                print(f"Entity {entity_id} deleted")
                return True
            else:
                print(f"Failed to delete: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False
    
    def list_entities(self, entity_type: Optional[str] = None) -> list:
        try:
            params = {}
            if entity_type:
                params["type"] = entity_type
            
            get_headers = {
                "Accept": "application/ld+json"
            }
            
            response = requests.get(
                f"{self.base_url}/entities/",
                headers=get_headers,
                params=params
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Failed to list entities: {response.status_code}")
                return []
        except Exception as e:
            print(f"Error: {str(e)}")
            return []
    
    def update_robot_position(self, robot_id: str, x: float, y: float, z: float) -> bool:
        position_value = {
            "type": "Point",
            "coordinates": [x, y, z]
        }
        return self.update_entity_attribute(robot_id, "position", position_value, "GeoProperty")
    
    def update_robot_velocity(self, robot_id: str, vx: float, vy: float, vz: float) -> bool:
        velocity_value = {"x": vx, "y": vy, "z": vz}
        return self.update_entity_attribute(robot_id, "velocity", velocity_value)
    
    def update_episode_metrics(self, episode_id: str, reward: float, 
                               steps: int, metrics: Dict[str, Any]) -> bool:
        success = True
        success &= self.update_entity_attribute(episode_id, "reward", reward)
        success &= self.update_entity_attribute(episode_id, "steps", steps)
        success &= self.update_entity_attribute(episode_id, "metrics", metrics)
        return success
    
    def check_connection(self) -> bool:
        try:
            response = requests.get(f"{self.orion_url}/version")
            if response.status_code == 200:
                version_info = response.json()
                print(f"Connected to Orion-LD {version_info.get('orionld version', 'unknown')}")
                return True
            else:
                print(f"Connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"Connection error: {str(e)}")
            return False


def load_entity_from_file(file_path: str) -> Optional[Dict[str, Any]]:
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"✗ Error loading file {file_path}: {str(e)}")
        return None


if __name__ == "__main__":
    print("Digital Twin Client Test\n")
    
    client = DigitalTwinClient()
    
    if not client.check_connection():
        print("\nCannot connect to Context Broker. Make sure it's running.")
        exit(1)
    
    entities_to_create = [
        "models/robot_entity.json",
        "models/environment_entity.json",
        "models/episode_entity.json"
    ]
    
    for entity_file in entities_to_create:
        entity_data = load_entity_from_file(entity_file)
        if entity_data:
            client.create_entity(entity_data)
    
    entities = client.list_entities(entity_type="Robot")
    for entity in entities:
        print(f"- {entity.get('id')} (Type: {entity.get('type')})")
    
    client.update_robot_position("urn:ngsi-ld:Robot:001", 1.5, 2.3, 0.0)
    
    robot = client.get_entity("urn:ngsi-ld:Robot:001")
    if robot:
        print(f"Robot Name: {robot.get('name', {}).get('value')}")
        print(f"Position: {robot.get('position', {}).get('value', {}).get('coordinates')}")
