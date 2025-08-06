FROM python:3.11-slim

# Install system libraries required for psycopg2 and GeoAlchemy2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Create working directory
WORKDIR /app

# Copy dependencies and code
COPY ./requirements.txt /app/requirements.txt
RUN pip install uv
RUN uv pip install --system -r requirements.txt
RUN uv cache clean

COPY . /app
