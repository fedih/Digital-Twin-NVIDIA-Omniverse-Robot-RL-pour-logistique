# Telemetry Subscription Fix

## Problem

The telemetry subscriptions were showing "failed" status because:

1. **QuantumLeap** was running in Docker on port 8668
2. **Custom Flask telemetry service** wanted to use the same port 8668 on the host
3. When Orion Context Broker tried to send notifications to `http://localhost:8668`, it was reaching QuantumLeap (not configured) instead of the custom Flask service
4. Docker containers couldn't reach services on the host using `localhost`

## Solution

**Containerized the custom Flask telemetry service** to run inside the Docker network:

### 1. Created Dockerfile for Telemetry Service

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY telemetry_service.py .
EXPOSE 8668
CMD ["python", "telemetry_service.py"]
```

### 2. Updated docker-compose.yml

**Removed:** QuantumLeap service (unused)

**Added:** Custom telemetry-service container

```yaml
telemetry-service:
  build:
    context: ./telemetry_store
    dockerfile: Dockerfile
  container_name: telemetry-service
  hostname: telemetry-service
  ports:
    - "8668:8668"
  networks:
    - fiware-network
  environment:
    - DB_HOST=timescaledb
    - DB_PORT=5432
```

### 3. Updated Telemetry Service Code

Modified `telemetry_service.py` to read database config from environment variables:

```python
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "telemetry"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "postgres")
}
```

### 4. Updated Subscription URL

Modified `telemetry_client.py` to use Docker network hostname:

```python
notification_url: str = "http://telemetry-service:8668/v2/notify"
```

## Testing Results

✅ **Subscriptions created successfully:**

- Robot entity subscription (ID: 6924c2792a57ed9b22adc61b)
- Environment entity subscription (ID: 6924c2792a57ed9b22adc61c)
- Episode entity subscription (ID: 6924c2792a57ed9b22adc61d)

✅ **Notifications received:**

```
172.19.0.4 - - [24/Nov/2025 20:39:37] "POST /v2/notify?subscriptionId=6924c2792a57ed9b22adc61b HTTP/1.1" 200
```

✅ **Data stored in TimescaleDB:**

```sql
time              | entity_id | attribute_name | attribute_value
------------------+-----------+----------------+----------------
2025-11-24 20:40:09 | Robot001  | status        | "moving"
2025-11-24 20:40:09 | Robot001  | battery       | 85
2025-11-24 20:40:09 | Robot001  | position      | {"x":0,"y":0,"z":0}
```

✅ **API queries working:**

```bash
curl "http://localhost:8668/v2/entities/Robot001?lastN=5"
# Returns historical data successfully
```

## How It Works Now

```
┌──────────────────┐
│  Context Broker  │
│   (Orion-LD)     │
└────────┬─────────┘
         │ Notification on entity change
         │ http://telemetry-service:8668/v2/notify
         ▼
┌──────────────────┐
│ Telemetry Service│  (Docker container)
│  (Flask App)     │
└────────┬─────────┘
         │ Store data
         ▼
┌──────────────────┐
│   TimescaleDB    │  (Docker container)
│  (PostgreSQL)    │
└──────────────────┘
```

All services now run in the same Docker network (`fiware-network`), allowing them to communicate using container hostnames.

## Commands to Use

**Start all services:**

```powershell
docker-compose up -d --build
```

**Check telemetry service logs:**

```powershell
docker logs telemetry-service
```

**Query database:**

```powershell
docker exec telemetry-timescaledb psql -U postgres -d telemetry -c "SELECT * FROM telemetry_data ORDER BY time DESC LIMIT 10;"
```

**Query via API:**

```powershell
curl "http://localhost:8668/v2/entities/Robot001?lastN=10"
```

**Update entity (trigger notification):**

```powershell
$headers = @{ "Content-Type" = "application/json"; "Fiware-Service" = "digitaltwin" }
$body = '{"battery": {"value": 85, "type": "Number"}}'
Invoke-RestMethod -Uri "http://localhost:1026/v2/entities/Robot001/attrs" -Method PATCH -Headers $headers -Body $body
```

## Status

🎉 **FIXED** - Telemetry subscriptions are now fully operational!

- ✅ Subscriptions created successfully
- ✅ Notifications received by telemetry service
- ✅ Data stored in TimescaleDB with timestamps
- ✅ Historical queries working via API
- ✅ All services running in Docker network
