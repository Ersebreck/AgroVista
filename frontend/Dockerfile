FROM python:3.11-slim

# Instalación del sistema base para geopandas, folium, shapely
RUN apt-get update && apt-get install -y \
    gdal-bin libgdal-dev python3-dev \
    build-essential && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install uv
RUN uv pip install --system -r requirements.txt
RUN uv cache clean

COPY . /app

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
