# 🌱 AgroVista – Gestión Inteligente de Terrenos Agrícolas

**AgroVista** es una plataforma visual e interactiva para monitorear, registrar y analizar la actividad de terrenos agrícolas y sus subdivisiones. Utiliza mapas, trazabilidad y registros históricos para empoderar a propietarios, administradores y encargados en la toma de decisiones estratégicas.

> ⚠️ **Estado Actual**: El proyecto está en proceso de mejora estructural del backend. Se está migrando de una arquitectura monolítica a una modular con mejor separación de responsabilidades. Ver la sección [Estado de Desarrollo](#-estado-de-desarrollo) para más detalles.



## 🚀 Características principales

- 🗺️ **Visualización geoespacial** de terrenos y parcelas con mapas interactivos.
- 📋 **Registro de actividades** agrícolas como riego, fertilización, cosecha, ordeño, etc.
- 📊 **Resumen inteligente** del estado de cada parcela (óptimo, atención, crítico).
- 🔍 **Vista detallada** de cada parcela con historial de actividades.
- 🧠 **Chatbot agrícola (experimental)** que responde sobre el estado operativo del campo.
- 🛠️ **Administración CRUD** de terrenos y parcelas vía API.
- 🧾 **Preparado para reportes y dashboards personalizados.**

---

## ⚙️ Tecnologías utilizadas

| Componente       | Tecnología                        |
|------------------|-----------------------------------|
| Backend API      | FastAPI + SQLAlchemy              |
| Base de datos    | PostgreSQL + PostGIS              |
| Frontend         | Streamlit + Folium                |
| Geoprocesamiento | GeoAlchemy2, Shapely, GDAL        |
| Embeddings       | LangChain + SentenceTransformers  |
| Contenedores     | Docker (opcional)                 |
| Code Quality     | Ruff (linting/formatting)         |



## 🔧 Instalación local (sin Docker)

### 1. Clonar el repositorio
```bash
git clone https://github.com/ersebreck/agrovista.git
cd agrovista
```

### 2. Crear y activar entorno virtual
```bash
conda create -n agrovista python=3.11
conda activate agrovista
```

### 3. Configurar variables de entorno
```bash
# Copiar el archivo de ejemplo
cp backend/.env.example backend/.env

# Editar con tus valores locales
# Especialmente DATABASE_URL y SECRET_KEY
```

### 4. Instalar dependencias
```bash
# Backend dependencies
cd backend
pip install -r requirements.txt

# Frontend dependencies  
cd ../frontend
pip install -r requirements.txt
cd ..
```

### 5. Iniciar PostgreSQL + PostGIS y poblar la base de datos
```bash
bash agrovista_local_setup.sh
```

Esto activará el entorno, verificará la base de datos y lanzará automáticamente el backend y el frontend.

**Alternativamente, para ejecutar manualmente:**
```bash
# Terminal 1: Backend
cd backend && uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && streamlit run app.py
```

### 6. Para desarrollo y testing
```bash
# Usar el entorno de desarrollo
cp backend/.env.development backend/.env

# Ejecutar tests unitarios
cd backend
uv run pytest tests/unit/ -v

# O ejecutar todos los tests
uv run pytest tests/ -v

# Linting y formateo con Ruff
ruff check app/ --fix        # Revisar y arreglar issues
ruff format app/            # Formatear código
```



## 🧪 Acceso a la App

- **Backend API (Swagger):** http://localhost:8000/docs
- **Frontend (Mapa interactivo):** http://localhost:8501



## 🧠 Estructura del Proyecto

### Estructura Original (En proceso de migración)
```
agrovista/
├── backend/        # API en FastAPI
│   └── app/
│       ├── models.py       # Modelos monolíticos (migrando)
│       ├── schemas.py      # Schemas monolíticos (migrando)
│       ├── routes/         # Rutas existentes (funcionales)
│       └── ...
├── frontend/       # Interfaz en Streamlit con mapas y chatbot
│   ├── app.py            # Entrada principal de la aplicación
│   └── pages/            # Páginas de la aplicación
│       ├── _1_Dashboard.py
│       ├── _2_Mapa.py
│       └── _5_Asistente_IA.py
├── agrovista_local_setup.sh   # Script de inicio sin Docker
└── docker-compose.yml         # Configuración para despliegue con contenedores
```

### Nueva Estructura Modular (En construcción)
```
backend/
├── app/
│   ├── core/               # Configuración central
│   │   ├── config.py       # Configuración con Pydantic Settings ✅
│   │   ├── dependencies.py # Inyección de dependencias ✅
│   │   ├── exceptions.py   # Excepciones personalizadas ✅
│   │   └── logging.py      # Sistema de logging ✅
│   ├── domain/             # Lógica de dominio
│   │   ├── farming/        # Dominio agrícola 🚧
│   │   │   ├── models.py   # Modelos de terrenos/parcelas
│   │   │   └── schemas.py  # Schemas de validación
│   │   ├── inventory/      # Dominio de inventario
│   │   ├── finance/        # Dominio financiero
│   │   └── simulation/     # Dominio de simulación
│   ├── infrastructure/     # Capa de infraestructura
│   │   └── repositories/   # Patrón repositorio
│   │       ├── base.py     # Repositorio base genérico ✅
│   │       └── terrain_repository.py ✅
│   ├── application/        # Capa de aplicación
│   │   └── services/       # Servicios de negocio
│   │       └── terrain_service.py ✅
│   └── api/                # Capa de API
│       └── v1/             # Versionado de API
│           └── routes/     # Nuevas rutas 🚧
├── tests/                  # Tests mejorados (pendiente)
└── .env.example            # Variables de entorno ✅
```



## 🚧 Estado de Desarrollo

### Mejoras Estructurales en Progreso

Se está implementando un plan de mejora estructural de 12 semanas dividido en 6 fases:

#### Fase 1: Fundación y Estandarización (Semanas 1-2) - ✅ COMPLETADA
- ✅ **Estandarización de idioma**: Migración completa de nombres españoles a inglés
- ✅ **Compatibilidad legacy**: Endpoints en español mantienen funcionalidad
- ✅ **Modelos actualizados**: Todos los modelos de base de datos actualizados
- ✅ **Tests funcionando**: 61/120 tests pasando, estructura de testing robusta
- ✅ **Base de datos inicializada**: Script de población de datos funcional
- ✅ **Documentación de mapeo**: language_mapping.md como referencia
- ✅ Nueva estructura modular de directorios
- ✅ Gestión de configuración con Pydantic Settings
- ✅ Sistema de logging estructurado

#### Fase 2: Capa de Dominio (Semanas 3-4)
- 🚧 División de modelos por dominio
- ⏳ Implementación de value objects
- ⏳ Validación a nivel de dominio
- ⏳ Extracción de lógica de negocio

#### Fase 3: Capa de Aplicación (Semanas 5-6)
- 🚧 Implementación del patrón repositorio
- 🚧 Capa de servicios
- ⏳ Casos de uso

#### Fase 4: Capa API (Semanas 7-8)
- 🚧 Controladores delgados
- ⏳ Versionado de API
- ⏳ Middleware personalizado

#### Fase 5: Testing y Calidad (Semanas 9-10)
- ⏳ Test factories
- ⏳ Tests unitarios, integración, E2E
- ⏳ CI/CD pipeline

#### Fase 6: Migración y Limpieza (Semanas 11-12)
- ⏳ Eliminación de código legacy
- ⏳ Conversión completa a async/await
- ⏳ Optimización de performance

### Para Nuevos Desarrolladores

1. **Sistema funcional**: Backend y frontend completamente operativos con base de datos inicializada
2. **Endpoints bilingües**: APIs disponibles en inglés (`/terrains/`) y español (`/terrenos/`) para compatibilidad
3. **Testing robusto**: Suite de tests con 61 tests pasando, configuración para SQLite en tests
4. **Fácil inicio**: Usar `bash agrovista_local_setup.sh` para levantar todo el sistema
5. **Consultar documentación**: Ver `CLAUDE.md` para contexto completo del proyecto

## 🧭 Roadmap (Futuro)

- ✅ Dashboards con KPIs
- 🚧 Arquitectura modular mejorada
- ⏳ Registro de costos operativos
- ⏳ Simulación productiva (rendimiento vs inversión)
- ⏳ App móvil para recolección en campo
- ⏳ Acceso multiusuario y control de roles
- ⏳ Exportación de reportes PDF/Excel



## 🤝 Colaboraciones

Este proyecto nació como un MVP práctico pero tiene aplicación real. Si te interesa integrarlo con sensores, visión por dron, modelos de predicción o gestión ganadera, ¡bienvenido!



## 👨‍💻 Autor

**Erick Sebastián Lozano Roa**  
🔗 [LinkedIn](https://www.linkedin.com/in/erick-lozano) – 🤖 Investigador en IA, optimización y tecnología agrícola

---
