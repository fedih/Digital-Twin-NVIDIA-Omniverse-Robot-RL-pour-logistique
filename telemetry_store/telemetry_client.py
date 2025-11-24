"""
Telemetry Store Client for QuantumLeap and TimescaleDB
Manages historical data storage and retrieval for digital twin entities
"""

import requests
import psycopg2
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import json


class TelemetryClient:
    """Client for managing telemetry data via QuantumLeap"""
    
    def __init__(self, quantumleap_url: str = "http://localhost:8668", 
                 orion_url: str = "http://localhost:1026"):
        """
        Initialize the Telemetry client
        
        Args:
            quantumleap_url: URL of QuantumLeap service
            orion_url: URL of the FIWARE Orion Context Broker
        """
        self.quantumleap_url = quantumleap_url
        self.orion_url = orion_url
        self.headers = {
            "Content-Type": "application/json",
            "Fiware-Service": "digitaltwin",
            "Fiware-ServicePath": "/"
        }
    
    def create_subscription(self, entity_type: str, watched_attributes: List[str]) -> bool:
        """
        Create a subscription in Orion to notify QuantumLeap of entity changes
        
        Args:
            entity_type: Type of entity to watch
            watched_attributes: List of attributes to monitor
            
        Returns:
            True if successful, False otherwise
        """
        subscription = {
            "description": f"Notify Telemetry Store of {entity_type} changes",
            "subject": {
                "entities": [{"idPattern": ".*", "type": entity_type}],
                "condition": {
                    "attrs": watched_attributes
                }
            },
            "notification": {
                "http": {
                    "url": f"{self.quantumleap_url}/v2/notify"
                },
                "attrs": watched_attributes,
                "metadata": ["dateCreated", "dateModified"]
            }
        }
        
        try:
            response = requests.post(
                f"{self.orion_url}/v2/subscriptions",
                headers=self.headers,
                json=subscription
            )
            if response.status_code == 201:
                subscription_id = response.headers.get('Location', '').split('/')[-1]
                print(f"✓ Subscription created for {entity_type} (ID: {subscription_id})")
                return True
            else:
                print(f"✗ Failed to create subscription: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"✗ Error creating subscription: {str(e)}")
            return False
    
    def list_subscriptions(self) -> List[Dict[str, Any]]:
        """
        List all subscriptions
        
        Returns:
            List of subscriptions
        """
        try:
            response = requests.get(
                f"{self.orion_url}/v2/subscriptions",
                headers=self.headers
            )
            if response.status_code == 200:
                return response.json()
            else:
                print(f"✗ Failed to list subscriptions: {response.status_code}")
                return []
        except Exception as e:
            print(f"✗ Error listing subscriptions: {str(e)}")
            return []
    
    def get_entity_history(self, entity_id: str, attribute: Optional[str] = None,
                          from_date: Optional[str] = None, 
                          to_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get historical data for an entity
        
        Args:
            entity_id: ID of the entity
            attribute: Optional specific attribute to retrieve
            from_date: Start date (ISO 8601 format)
            to_date: End date (ISO 8601 format)
            
        Returns:
            Historical data if found, None otherwise
        """
        try:
            params = {}
            if from_date:
                params['fromDate'] = from_date
            if to_date:
                params['toDate'] = to_date
            
            url = f"{self.quantumleap_url}/v2/entities/{entity_id}"
            if attribute:
                url += f"/attrs/{attribute}"
            
            response = requests.get(
                url,
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"✗ Failed to get history: {response.status_code} - {response.text}")
                return None
        except Exception as e:
            print(f"✗ Error getting history: {str(e)}")
            return None
    
    def get_latest_values(self, entity_id: str, last_n: int = 10) -> Optional[Dict[str, Any]]:
        """
        Get the latest N values for an entity
        
        Args:
            entity_id: ID of the entity
            last_n: Number of latest values to retrieve
            
        Returns:
            Latest values if found, None otherwise
        """
        try:
            params = {'lastN': last_n}
            response = requests.get(
                f"{self.quantumleap_url}/v2/entities/{entity_id}",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"✗ Failed to get latest values: {response.status_code}")
                return None
        except Exception as e:
            print(f"✗ Error getting latest values: {str(e)}")
            return None
    
    def check_connection(self) -> bool:
        """
        Check if connection to QuantumLeap is working
        
        Returns:
            True if connected, False otherwise
        """
        try:
            response = requests.get(f"{self.quantumleap_url}/health")
            if response.status_code == 200:
                health_info = response.json()
                print(f"✓ Connected to QuantumLeap (Status: {health_info.get('status', 'unknown')})")
                return True
            else:
                print(f"✗ Connection failed: {response.status_code}")
                return False
        except Exception as e:
            print(f"✗ Connection error: {str(e)}")
            return False


class TimescaleDBClient:
    """Direct client for TimescaleDB queries"""
    
    def __init__(self, host: str = "localhost", port: int = 5432,
                 database: str = "telemetry", user: str = "postgres", 
                 password: str = "postgres"):
        """
        Initialize TimescaleDB client
        
        Args:
            host: Database host
            port: Database port
            database: Database name
            user: Database user
            password: Database password
        """
        self.connection_params = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password
        }
    
    def connect(self):
        """Establish database connection"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            return conn
        except Exception as e:
            print(f"✗ Database connection error: {str(e)}")
            return None
    
    def execute_query(self, query: str, params: tuple = None) -> Optional[List[tuple]]:
        """
        Execute a SQL query
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Query results if successful, None otherwise
        """
        conn = self.connect()
        if not conn:
            return None
        
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        except Exception as e:
            print(f"✗ Query error: {str(e)}")
            if conn:
                conn.close()
            return None
    
    def get_statistics(self, entity_id: str, attribute: str, 
                      time_window: str = "1 hour") -> Optional[Dict[str, float]]:
        """
        Get statistical aggregations for an attribute
        
        Args:
            entity_id: ID of the entity
            attribute: Attribute name
            time_window: Time window for aggregation (e.g., '1 hour', '1 day')
            
        Returns:
            Statistics dictionary if successful, None otherwise
        """
        # This is a placeholder - actual implementation depends on QuantumLeap's schema
        query = f"""
        SELECT 
            AVG(value) as average,
            MIN(value) as minimum,
            MAX(value) as maximum,
            STDDEV(value) as std_deviation
        FROM entity_data
        WHERE entity_id = %s 
        AND attribute_name = %s
        AND timestamp > NOW() - INTERVAL '{time_window}'
        """
        
        results = self.execute_query(query, (entity_id, attribute))
        if results and len(results) > 0:
            row = results[0]
            return {
                "average": float(row[0]) if row[0] else 0,
                "minimum": float(row[1]) if row[1] else 0,
                "maximum": float(row[2]) if row[2] else 0,
                "std_deviation": float(row[3]) if row[3] else 0
            }
        return None


if __name__ == "__main__":
    print("=== Telemetry Store Client Test ===\n")
    
    # Initialize client
    telemetry = TelemetryClient()
    
    # Check connection
    if not telemetry.check_connection():
        print("\n✗ Cannot connect to QuantumLeap. Make sure it's running.")
        print("Run: docker-compose up -d")
        exit(1)
    
    print("\n--- Creating Subscriptions ---\n")
    
    # Create subscriptions for different entity types
    subscriptions = [
        {
            "type": "Robot",
            "attrs": ["position", "velocity", "battery", "status"]
        },
        {
            "type": "Environment", 
            "attrs": ["temperature", "lighting"]
        },
        {
            "type": "Episode",
            "attrs": ["reward", "steps", "metrics"]
        }
    ]
    
    for sub in subscriptions:
        telemetry.create_subscription(sub["type"], sub["attrs"])
    
    print("\n--- Listing Subscriptions ---\n")
    subs = telemetry.list_subscriptions()
    for sub in subs:
        print(f"- {sub.get('description')} (ID: {sub.get('id')})")
    
    print("\n--- Getting Latest Robot Data ---\n")
    history = telemetry.get_latest_values("urn:ngsi-ld:Robot:001", last_n=5)
    if history:
        print(json.dumps(history, indent=2))
    else:
        print("No historical data yet. Update some entity attributes to generate data.")
    
    print("\n=== Test Complete ===")
