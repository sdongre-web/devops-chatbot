FROM python:3.11-slim 
 
WORKDIR /app 
 
# Install system dependencies 
RUN apt-get update && apt-get install -y build-essential curl && rm -rf /var/lib/apt/lists/* 
 
# Copy requirements and install 
COPY requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt 
 
# Copy backend code 
COPY . . 
 
EXPOSE 8000 

CMD ["sh", "-c", "echo 'Waiting for Qdrant...' && until curl -f http://qdrant:6333/ 2>/dev/null; do sleep 2; done && echo 'Starting backend...' && uvicorn main:app --host 0.0.0.0 --port 8000"]