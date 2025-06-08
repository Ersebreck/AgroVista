import streamlit as st
from utils import obtener_terrenos, obtener_parcelas_por_terreno, obtener_parcela, obtener_ubicacion

def ver_detalle_parcela():
    st.subheader("🔍 Detalle de Parcelas")

    terrenos = obtener_terrenos()
    if not terrenos:
        st.warning("No hay terrenos disponibles.")
        return

    terreno_options = {f"{t['nombre']} (ID: {t['id']})": t["id"] for t in terrenos}
    selected = st.selectbox("Selecciona un terreno", list(terreno_options.keys()))

    terreno_id = terreno_options[selected]
    parcelas = obtener_parcelas_por_terreno(terreno_id)

    if not parcelas:
        st.info("Este terreno no tiene parcelas registradas.")
        return

    parcela_options = {f"{p['nombre']} (ID: {p['id']})": p["id"] for p in parcelas}
    parcela_key = st.selectbox("Selecciona una parcela", list(parcela_options.keys()))
    parcela_id = parcela_options[parcela_key]

    parcela = obtener_parcela(parcela_id)
    ubicacion = obtener_ubicacion(parcela["ubicacion_id"]) if parcela.get("ubicacion_id") else None

    st.markdown("### 📋 Información de la Parcela")
    st.write(f"**Nombre:** {parcela['nombre']}")
    st.write(f"**Uso Actual:** {parcela.get('uso_actual', 'No especificado')}")
    st.write(f"**Estado:** {parcela.get('estado', 'No especificado')}")
    if ubicacion:
        st.write(f"**Ubicación:** Tipo: {ubicacion['tipo']}")
        st.json(ubicacion['coordenadas'])
        if ubicacion.get("referencia"):
            st.write(f"**Referencia:** {ubicacion['referencia'].get('nombre', '')}")
