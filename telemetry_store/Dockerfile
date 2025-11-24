FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY telemetry_service.py .

# Expose port
EXPOSE 8668

# Run the service
CMD ["python", "telemetry_service.py"]
