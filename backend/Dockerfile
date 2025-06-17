FROM python:3.11-slim

# Instalar librerías del sistema necesarias para psycopg2 y GeoAlchemy2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear carpeta de trabajo
WORKDIR /app

# Copiar dependencias y código
COPY ./requirements.txt /app/requirements.txt
RUN pip install uv
RUN uv pip install --system -r requirements.txt
RUN uv cache clean

COPY . /app
