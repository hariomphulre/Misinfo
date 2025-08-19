FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements-minimal.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy only YouTube collector
COPY youtube.py .

# Create a simple web server to keep the service running
COPY main.py .

EXPOSE 8080

# Run the main service
CMD ["python", "main.py"]
