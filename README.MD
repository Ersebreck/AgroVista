# 🌱 AgroVista – Gestión Inteligente de Terrenos Agrícolas

**AgroVista** es una plataforma visual e interactiva para monitorear, registrar y analizar la actividad de terrenos agrícolas y sus subdivisiones. Utiliza mapas, trazabilidad y registros históricos para empoderar a propietarios, administradores y encargados en la toma de decisiones estratégicas.



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

### 3. Instalar dependencias
```bash
pip install -r backend/requirements.txt
pip install -r frontend/requirements.txt
```

### 4. Iniciar PostgreSQL + PostGIS y poblar la base de datos
```bash
bash agrovista_local_setup.sh
```

Esto activará el entorno, verificará la base de datos y lanzará automáticamente el backend y el frontend.



## 🧪 Acceso a la App

- **Backend API (Swagger):** http://localhost:8000/docs
- **Frontend (Mapa interactivo):** http://localhost:8501



## 🧠 Estructura del Proyecto

```
agrovista/
├── backend/        # API en FastAPI, modelos, rutas y población de datos
│   └── app/
│       ├── models.py
│       ├── routes/
│       └── ...
├── frontend/       # Interfaz en Streamlit con mapas y chatbot
│   ├── main.py
│   ├── map.py
│   └── chat.py
├── agrovista_local_setup.sh   # Script de inicio sin Docker
└── docker-compose.yml         # Configuración para despliegue con contenedores
```



## 🧭 Roadmap (Futuro)

- ✅ Dashboards con KPIs
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
