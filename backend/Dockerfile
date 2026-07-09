FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (needed for compiling some ML libraries or psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Also install xgboost and scikit-learn from the MVP requirements if they are missing
# (Since the backend loads ML models)
RUN pip install --no-cache-dir xgboost scikit-learn pandas numpy

# Copy backend code
COPY backend /app/backend

# Copy the models explicitly because Docker doesn't resolve symlinks outside the context well
COPY ml_pipeline/models /app/backend/app/ml/models

# Set the working directory to backend so uvicorn can find app.main
WORKDIR /app/backend

# Expose port
EXPOSE 8000

# Start server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
