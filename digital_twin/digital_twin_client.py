"""
Digital Twin Client for NGSI-LD Context Broker
Manages digital twin entities and interactions with FIWARE Orion
"""

import requests
import json
from typing import Dict, Any, Optional
from datetime import datetime


class DigitalTwinClient:
    """Client for managing digital twin entities in NGSI-LD format"""
    
    def __init__(self, orion_url: str = "http://localhost:1026"):
        """
        Initialize the Digital Twin client
        
        Args:
            orion_url: URL of the FIWARE Orion Context Broker
        """
        self.orion_url = orion_url
        self.base_url = f"{orion_url}/ngsi-ld/v1"
        self.headers = {
            "Content-Type": "application/ld+json",
            "Accept": "application/ld+json"
        }
    
    def create_entity(self, entity_data: Dict[str, Any]) -> bool:
        """
        Create a new entity in the Context Broker
        
        Args:
            entity_data: NGSI-LD entity data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.post(
                f"{self.base_url}/entities/",
                headers=self.headers,
                json=entity_data
            )
            if response.status_code == 201:
                print(f"✓ Entity {entity_data['id']} created successfully")
                return True
            else:
                print(f"✗ Failed to create entity: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error creating entity: {str(e)}")
            return False
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve an entity from the Context Broker
        
        Args:
            entity_id: ID of the entity to retrieve
            
        Returns:
            Entity data if found, None otherwise
        """
        try:
            response = requests.get(
                f"{self.base_url}/entities/{entity_id}",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"✗ Entity not found: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Error retrieving entity: {str(e)}")
            return None
    
    def update_entity_attribute(self, entity_id: str, attribute_name: str, 
                               attribute_value: Any, attribute_type: str = "Property") -> bool:
        """
        Update a specific attribute of an entity
        
        Args:
            entity_id: ID of the entity to update
            attribute_name: Name of the attribute to update
            attribute_value: New value for the attribute
            attribute_type: Type of the attribute (Property, GeoProperty, Relationship)
            
        Returns:
            True if successful, False otherwise
        """
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
                print(f"✗ Failed to update attribute: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error updating attribute: {str(e)}")
            return False
    
    def delete_entity(self, entity_id: str) -> bool:
        """
        Delete an entity from the Context Broker
        
        Args:
            entity_id: ID of the entity to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = requests.delete(
                f"{self.base_url}/entities/{entity_id}",
                headers=self.headers
            )
            if response.status_code == 204:
                print(f"✓ Entity {entity_id} deleted successfully")
                return True
            else:
                print(f"✗ Failed to delete entity: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Error deleting entity: {str(e)}")
            return False
    
    def list_entities(self, entity_type: Optional[str] = None) -> list:
        """
        List all entities or filter by type
        
        Args:
            entity_type: Optional entity type to filter by
            
        Returns:
            List of entities
        """
        try:
            params = {}
            if entity_type:
                params["type"] = entity_type
            
            # Use simplified headers for GET requests
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
                print(f"✗ Failed to list entities: {response.status_code} - {response.text}")
                return []
        except Exception as e:
            print(f"✗ Error listing entities: {str(e)}")
            return []
    
    def update_robot_position(self, robot_id: str, x: float, y: float, z: float) -> bool:
        """
        Update robot position
        
        Args:
            robot_id: ID of the robot entity
            x, y, z: New position coordinates
            
        Returns:
            True if successful, False otherwise
        """
        position_value = {
            "type": "Point",
            "coordinates": [x, y, z]
        }
        return self.update_entity_attribute(robot_id, "position", position_value, "GeoProperty")
    
    def update_robot_velocity(self, robot_id: str, vx: float, vy: float, vz: float) -> bool:
        """
        Update robot velocity
        
        Args:
            robot_id: ID of the robot entity
            vx, vy, vz: Velocity components
            
        Returns:
            True if successful, False otherwise
        """
        velocity_value = {"x": vx, "y": vy, "z": vz}
        return self.update_entity_attribute(robot_id, "velocity", velocity_value)
    
    def update_episode_metrics(self, episode_id: str, reward: float, 
                               steps: int, metrics: Dict[str, Any]) -> bool:
        """
        Update episode metrics
        
        Args:
            episode_id: ID of the episode entity
            reward: Current reward value
            steps: Number of steps
            metrics: Dictionary of additional metrics
            
        Returns:
            True if successful, False otherwise
        """
        success = True
        success &= self.update_entity_attribute(episode_id, "reward", reward)
        success &= self.update_entity_attribute(episode_id, "steps", steps)
        success &= self.update_entity_attribute(episode_id, "metrics", metrics)
        return success
    
    def check_connection(self) -> bool:
        """
        Check if connection to Context Broker is working
        
        Returns:
            True if connected, False otherwise
        """
        try:
            response = requests.get(f"{self.orion_url}/version")
            if response.status_code == 200:
                version_info = response.json()
                print(f"✓ Connected to Orion-LD version {version_info.get('orionld version', 'unknown')}")
                return True
            else:
                print(f"✗ Connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Connection error: {str(e)}")
            return False


def load_entity_from_file(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Load entity data from a JSON file
    
    Args:
        file_path: Path to the JSON file
        
    Returns:
        Entity data if successful, None otherwise
    """
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"✗ Error loading file {file_path}: {str(e)}")
        return None


if __name__ == "__main__":
    # Example usage
    print("=== Digital Twin Client Test ===\n")
    
    # Initialize client
    client = DigitalTwinClient()
    
    # Check connection
    if not client.check_connection():
        print("\n✗ Cannot connect to Context Broker. Make sure it's running.")
        exit(1)
    
    print("\n--- Creating Digital Twin Entities ---\n")
    
    # Load and create entities
    entities_to_create = [
        "models/robot_entity.json",
        "models/environment_entity.json",
        "models/episode_entity.json"
    ]
    
    for entity_file in entities_to_create:
        entity_data = load_entity_from_file(entity_file)
        if entity_data:
            client.create_entity(entity_data)
    
    print("\n--- Listing All Entities ---\n")
    entities = client.list_entities(entity_type="Robot")
    for entity in entities:
        print(f"- {entity.get('id')} (Type: {entity.get('type')})")
    
    print("\n--- Updating Robot Position ---\n")
    client.update_robot_position("urn:ngsi-ld:Robot:001", 1.5, 2.3, 0.0)
    
    print("\n--- Retrieving Robot Entity ---\n")
    robot = client.get_entity("urn:ngsi-ld:Robot:001")
    if robot:
        print(f"Robot Name: {robot.get('name', {}).get('value')}")
        print(f"Position: {robot.get('position', {}).get('value', {}).get('coordinates')}")
    
    print("\n=== Test Complete ===")
