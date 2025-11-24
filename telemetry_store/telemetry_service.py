"""
Simple Telemetry Store Service
Subscribes to Context Broker notifications and stores them in TimescaleDB
"""

import psycopg2
from flask import Flask, request, jsonify
from datetime import datetime
import json
import os

app = Flask(__name__)

# Database configuration from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "telemetry"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}


def get_db_connection():
    """Create database connection"""
    return psycopg2.connect(**DB_CONFIG)


def init_database():
    """Initialize database schema"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create telemetry table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS telemetry_data (
            id SERIAL,
            time TIMESTAMPTZ NOT NULL,
            entity_id TEXT NOT NULL,
            entity_type TEXT NOT NULL,
            attribute_name TEXT NOT NULL,
            attribute_value JSONB NOT NULL,
            metadata JSONB,
            PRIMARY KEY (id, time)
        );
    """)
    
    # Create hypertable for time-series optimization
    cursor.execute("""
        SELECT create_hypertable('telemetry_data', 'time',  
            if_not_exists => TRUE);
    """)
    
    # Create indexes
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_entity_id 
        ON telemetry_data (entity_id, time DESC);
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_entity_type 
        ON telemetry_data (entity_type, time DESC);
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    print("✓ Database initialized successfully")


@app.route('/v2/notify', methods=['POST'])
def notify():
    """
    Receive notifications from Context Broker
    """
    try:
        notification = request.json
        data = notification.get('data', [])
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for entity in data:
            entity_id = entity.get('id')
            entity_type = entity.get('type')
            timestamp = datetime.utcnow()
            
            # Store each attribute
            for key, value in entity.items():
                if key not in ['id', 'type']:
                    if isinstance(value, dict) and 'type' in value:
                        # It's an NGSI attribute
                        cursor.execute("""
                            INSERT INTO telemetry_data 
                            (time, entity_id, entity_type, attribute_name, attribute_value, metadata)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (
                            timestamp,
                            entity_id,
                            entity_type,
                            key,
                            json.dumps(value.get('value')),
                            json.dumps(value.get('metadata', {}))
                        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"status": "ok"}), 200
    
    except Exception as e:
        print(f"Error processing notification: {str(e)}")
        return jsonify({"error": str(e)}), 500


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        conn.close()
        return jsonify({"status": "healthy"}), 200
    except Exception as e:
        return jsonify({"status": "unhealthy", "error": str(e)}), 503


@app.route('/v2/entities/<entity_id>', methods=['GET'])
def get_entity_history(entity_id):
    """Get historical data for an entity"""
    try:
        limit = request.args.get('lastN', 100, type=int)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT time, attribute_name, attribute_value, metadata
            FROM telemetry_data
            WHERE entity_id = %s
            ORDER BY time DESC
            LIMIT %s
        """, (entity_id, limit))
        
        results = []
        for row in cursor.fetchall():
            try:
                value = json.loads(row[2]) if isinstance(row[2], str) else row[2]
            except (json.JSONDecodeError, TypeError):
                value = row[2]
                
            try:
                metadata = json.loads(row[3]) if row[3] and isinstance(row[3], str) else (row[3] if row[3] else {})
            except (json.JSONDecodeError, TypeError):
                metadata = {}
                
            results.append({
                "time": row[0].isoformat(),
                "attribute": row[1],
                "value": value,
                "metadata": metadata
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({"entityId": entity_id, "data": results}), 200
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    print("=== Initializing Telemetry Store ===\n")
    init_database()
    print("\n=== Starting Telemetry Store Service ===")
    print("Listening on http://0.0.0.0:8668")
    app.run(host='0.0.0.0', port=8668, debug=True)
