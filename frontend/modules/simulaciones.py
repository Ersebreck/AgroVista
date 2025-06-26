import streamlit as st
import pandas as pd
import requests
import altair as alt

API = "http://localhost:8000"

def mostrar_simulaciones():
    st.title("🧪 Simulaciones")
    st.markdown("Explora las proyecciones guardadas y lanza nuevas simulaciones.")

    # Mostrar simulaciones existentes
    try:
        res = requests.get(f"{API}/simulacion/historico")
        res.raise_for_status()
        sims = res.json()
    except Exception as e:
        st.error(f"No se pudieron cargar simulaciones: {e}")
        return

    if not sims:
        st.info("No hay simulaciones guardadas.")
    else:
        st.markdown("### 📋 Simulaciones guardadas")
        opciones = {f"{s['nombre']} ({s['fecha_creacion']})": s for s in sims}
        seleccion = st.selectbox("Selecciona un escenario:", list(opciones.keys()))
        datos = opciones[seleccion]
        df = pd.DataFrame.from_dict(datos["resultados"], orient="index", columns=["Unidades"]).reset_index()
        df.rename(columns={"index": "Año"}, inplace=True)

        chart = alt.Chart(df).mark_line(point=True).encode(
            x="Año:O", y="Unidades:Q"
        ).properties(width=600, height=300)
        st.altair_chart(chart, use_container_width=True)

    # Crear nueva simulación
    st.markdown("### ➕ Nueva simulación")
    with st.form("form_simulacion"):
        anio_inicio = st.number_input("Año de inicio", value=2025, step=1)
        anios = st.slider("Años a simular", 1, 10, 5)
        unidad_inicial = st.number_input("Unidades iniciales", value=100)
        natalidad = st.number_input("Tasa natalidad (%)", value=20) / 100
        venta = st.number_input("Tasa venta (%)", value=10) / 100
        mortalidad = st.number_input("Tasa mortalidad (%)", value=5) / 100
        nombre = st.text_input("Nombre del escenario", "Proyección demo")
        submitted = st.form_submit_button("Simular y guardar")

    if submitted:
        payload = {
            "anio_inicio": anio_inicio,
            "anios": anios,
            "unidad_inicial": unidad_inicial,
            "tasas": {
                "natalidad": natalidad,
                "venta": venta,
                "mortalidad": mortalidad
            },
            "nombre": nombre,
            "guardar": True,
            "usuario_id": 1
        }
        try:
            res = requests.post(f"{API}/simulacion/simular", json=payload)
            res.raise_for_status()
            st.success("✅ Simulación guardada.")
        except Exception as e:
            st.error(f"Error al simular: {e}")
