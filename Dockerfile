FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Set environment variables (these will be overridden by Cloud Run)
ENV PYTHONUNBUFFERED=1

# Run the script
CMD ["python", "main_time.py"]

