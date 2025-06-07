# AgroVista 🌾

Visualización interactiva de terrenos agrícolas con subdivisiones. 

## Componentes

- Backend: FastAPI
- Frontend: Streamlit + Folium
- DB: PostgreSQL + PostGIS

## Cómo iniciar

1. `conda activate agrovista`
2. `uvicorn backend.app.main:app --reload`
3. `streamlit run frontend/app.py`

