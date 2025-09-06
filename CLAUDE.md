# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Vision & Objectives

**AgroVista** is a geospatial agricultural land management platform designed to solve a key problem: the lack of clear, accessible, and visual ways to monitor agricultural parcels and terrains, which hinders decision-making and operational control.

### Main Objective
Enable agricultural landowners to visualize and manage information about their large terrains and subdivisions (parcelas) in a simple, centralized manner, including general and specific data for each parcel.

### Key User Roles
- **Propietario (Owner)**: Views visual maps of all terrains and subdivisions, accesses parcel summaries for strategic decisions
- **Usuario/Encargado (Manager)**: Selects parcels to register completed tasks, views specific parcel information for task execution
- **Administrador (Admin)**: Creates, edits, and deletes terrains and parcels, manages user permissions and system access

### Core Problem Being Solved
Currently there is no clear, accessible, and visual way to monitor or access key information about agricultural parcels and terrains, making decision-making and operational control difficult.

## Project Overview

AgroVista combines FastAPI backend with Streamlit frontend for comprehensive farm management including activities tracking, inventory management, economic analysis, and AI-powered chat assistance. The system supports recursive subdivisions at multiple levels and focuses on map-based visualization as the core interface.

## Architecture

### Backend (FastAPI)
- **Entry point**: `backend/app/main.py` - FastAPI application with CORS middleware and router includes
- **Database**: PostgreSQL with PostGIS extension for geospatial data
- **ORM**: SQLAlchemy with GeoAlchemy2 for spatial operations
- **Models**: `backend/app/models.py` - Contains all database models:
  - Core entities: Usuario, Terreno, Parcela, Ubicacion
  - Activity tracking: Actividad, DetalleActividad
  - Inventory: Inventario, EventoInventario
  - Economics: Transaccion, Presupuesto
  - Simulation: Simulacion, ParametroBiologico
  - Analytics: Indicador, HistorialCambio
- **API Routes**: Organized in `backend/app/routes/` directory:
  - `terrenos.py` - Land management endpoints
  - `parcelas.py` - Parcel operations
  - `actividades.py` - Activity logging
  - `chat.py` - AI chat functionality
  - `economia.py` - Economic tracking
  - `inventario.py` - Inventory management
  - `simulacion.py` - Agricultural simulations
  - `control.py` - System control endpoints

### Frontend (Streamlit)
- **Entry point**: `frontend/app.py` - Multi-page navigation setup
- **Pages**: Located in `frontend/pages/`:
  - `_1_Dashboard.py` - Main analytics dashboard
  - `_2_Mapa.py` - Interactive geospatial map with Folium
  - `_3_Actividades_Inventario.py` - Activity and inventory management
  - `_4_Economia.py` - Economic analysis and budgeting
  - `_5_Asistente_IA.py` - AI chat assistant
- **Mapping**: Uses Folium for interactive maps with geospatial data visualization
- **Chat**: LangChain integration with HuggingFace and Anthropic models

### Database Architecture
- **Core Data Model** (from original design):
  - **Usuario**: id, nombre, correo, contraseña, rol
  - **Terreno**: id, nombre, descripción, propietario_id, ubicacion_id
  - **Parcela**: id, nombre, uso_actual, estado, terreno_id, ubicacion_id
  - **Actividad**: id, tipo, fecha, descripción, usuario_id, parcela_id
  - **Ubicación Geoespacial**: id, tipo (punto/polígono), coordenadas (GeoJSON), referencia
- **Spatial data**: Uses PostGIS with SRID 4326 for geographic coordinates
- **Relationships**: Complex entity relationships with proper foreign keys and cascade operations
- **Flexibility**: JSONB fields for dynamic data (simulation parameters, location references)
- **Geospatial Support**: Full PostGIS integration for polygon and point geometry storage

## Development Commands

### Local Development Setup
```bash
# Full setup (PostgreSQL cluster, database init, and app startup)
bash agrovista_local_setup.sh
```

### Manual Development
```bash
# Backend only
cd backend
uvicorn app.main:app --reload --port 8000

# Frontend only  
cd frontend
streamlit run app.py
```

### Database Operations
```bash
# Initialize database and populate sample data
cd backend
python -m app.init_db

# Populate additional data
python -m app.populate_db
```

### Docker Deployment
```bash
# Full stack with PostgreSQL
docker-compose up --build

# Database only
docker-compose up db
```

## Key Dependencies

### Backend
- **FastAPI**: Web framework with automatic API documentation
- **SQLAlchemy + GeoAlchemy2**: ORM with geospatial support
- **PostGIS/PostgreSQL**: Spatial database
- **LangChain**: AI/ML pipeline for chat functionality
- **Sentence-transformers**: Text embeddings
- **Anthropic**: Claude AI integration

### Frontend
- **Streamlit**: Web application framework
- **Folium**: Interactive mapping
- **GeoPandas**: Geospatial data manipulation
- **Plotly**: Data visualization

## Development Notes

### Database Configuration
- **Port**: 5434 (custom PostgreSQL cluster)
- **Database**: agrovista
- **User**: usuario / password
- **Connection**: Uses connection pooling via SQLAlchemy SessionLocal

### API Endpoints
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs (Swagger)
- **Frontend**: http://localhost:8501

### Geospatial Considerations
- All coordinates stored as PostGIS GEOMETRY with SRID 4326
- Supports both point locations and polygon boundaries
- Uses GeoJSON for frontend-backend communication

### AI Chat System
- Embeddings-based context retrieval from agricultural data
- Integration with both local models (HuggingFace) and API models (Anthropic)
- Context includes farm operational state and historical data

## MVP Features & Scope

### Current MVP Implementation
- ✅ **Map Visualization**: Interactive terrains and parcels display with Folium
- ✅ **Detailed Parcel Views**: Clickable parcels showing specific information
- ✅ **Activity Registration**: Task logging system for agricultural activities
- ✅ **Admin Operations**: Basic CRUD operations for terrains and parcels
- ✅ **Multi-level Subdivisions**: Support for recursive terrain subdivisions
- ✅ **Geospatial Data**: Full PostGIS integration with polygon/point storage
- ✅ **Dashboard Analytics**: KPIs, metrics, and economic tracking
- ✅ **AI Chat Assistant**: Agricultural advisory system with context awareness

### Design Principles (from original wireframes)
- **Map-Centric Design**: Map as the core interface element
- **Progressive Views**: General overview → detailed drill-down
- **Visual State Indicators**: Icons/colors to differentiate parcel states
- **Split Interface**: Map + lateral panel for information display
- **Interactive Navigation**: Click-through exploration of terrain hierarchy

### Future Scope & Vision
- **Short-term**: Practical MVP with real-world validation potential
- **Long-term**: Scalable SaaS platform for territorial management
- **Target Market**: Real agricultural clients for MVP validation
- **Expansion**: "Permaculture as a Service" concept integration

## Technology Stack (Validated Choice)

The current stack aligns with the original technical vision:
- **Frontend**: Streamlit + Folium (as planned)
- **Backend**: FastAPI (Python) (as planned)
- **Database**: PostgreSQL + PostGIS (as planned)
- **ORM**: SQLAlchemy + GeoAlchemy2 (as planned)
- **Geospatial**: GeoPandas, Shapely, streamlit-folium (as planned)
- **Deployment**: Docker support (as planned)

## Testing and Quality

The project uses automated setup scripts and database initialization. When making changes:
- Test backend endpoints via FastAPI docs at `/docs`
- Verify database connectivity through the init script
- Check frontend page navigation and map rendering
- Validate geospatial data integrity when working with coordinates
- Ensure role-based functionality works for different user types (Owner/Manager/Admin)
- Test progressive navigation: terrain → parcel → detail views

## Development Context & User Stories

When implementing features, consider these key user scenarios from the original design:

### Owner (Propietario) Workflows
- Quick visual overview of all terrain states via map interface
- Strategic decision-making based on parcel summaries
- High-level monitoring of farm operations

### Manager (Usuario/Encargado) Workflows  
- Daily task registration for specific parcels
- Access to detailed parcel information for operational tasks
- Activity history tracking and reporting

### Administrator Workflows
- System maintenance via CRUD operations
- User permission management
- Data integrity and system configuration

### UI/UX Patterns
- **Click-through Navigation**: Main map → terrain selection → parcel details
- **State Visualization**: Color-coded parcels (green/blue/orange/purple for terrains, state-based icons for parcels)
- **Information Hierarchy**: Progressive disclosure from general to specific
- **Lateral Panel**: Contextual information display alongside map interaction

This context should guide all development decisions to ensure the final product aligns with the original agricultural management vision.