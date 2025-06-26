#!/bin/bash

echo "🟢 Iniciando clúster PostgreSQL 'agrovista' en puerto 5434..."
sudo systemctl start postgresql@16-agrovista

echo "🗃️ Verificando base de datos 'agrovista' y usuario 'usuario' en clúster agrovista..."
sudo -u postgres psql -p 5434 <<EOF
DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'usuario') THEN
      CREATE USER usuario WITH PASSWORD 'password';
   END IF;
END
\$\$;

DO \$\$
BEGIN
   IF NOT EXISTS (SELECT FROM pg_database WHERE datname = 'agrovista') THEN
      CREATE DATABASE agrovista OWNER usuario;
   END IF;
END
\$\$;
EOF

echo "📦 Activando extensión PostGIS en 'agrovista'..."
sudo -u postgres psql -p 5434 -d agrovista -c "CREATE EXTENSION IF NOT EXISTS postgis;"

echo "🔐 Asegurando permisos del usuario 'usuario' sobre el esquema 'public'..."
sudo -u postgres psql -p 5434 -d agrovista <<EOF
GRANT ALL ON SCHEMA public TO usuario;
ALTER SCHEMA public OWNER TO usuario;
EOF

echo "🧱 Inicializando tablas y datos iniciales..."
cd backend || exit
python3 -m app.init_db || { echo "❌ Error al inicializar base de datos."; exit 1; }
cd ..

echo "🚀 Levantando Backend (FastAPI)..."
gnome-terminal -- bash -c "cd backend && uvicorn app.main:app --reload --port 8000; exec bash"

sleep 2

echo "🌐 Levantando Frontend (Streamlit)..."
gnome-terminal -- bash -c "cd frontend && streamlit run main.py; exec bash"

echo "✅ Sistema iniciado. Backend en http://localhost:8000/docs, Frontend en http://localhost:8501"
