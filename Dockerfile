FROM python:3.13-slim

# Install build tools and dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    g++ \
    libomp-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Update pip
RUN pip install --upgrade pip

# Set working directory
WORKDIR /app

# Copy and install requirements
COPY req.txt   .
RUN pip install --no-cache-dir -r req.txt

# Copy application files
COPY Data/data.csv Data/data.csv
COPY fitness_assistant .
COPY notebooks .

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]