FROM python:3.10-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Create directory for Chroma DB
RUN mkdir -p chroma_store

# Expose the application port
EXPOSE 8510

# Command to run the application
CMD ["python", "main.py"]