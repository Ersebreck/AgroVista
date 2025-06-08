import streamlit as st
from datetime import date
from utils import obtener_terrenos, obtener_parcelas_por_terreno, registrar_actividad

def formulario_registro():
    st.subheader("🛠️ Registrar Nueva Actividad")

    terrenos = obtener_terrenos()
    if not terrenos:
        st.warning("No hay terrenos disponibles.")
        return

    terreno_options = {f"{t['nombre']} (ID: {t['id']})": t["id"] for t in terrenos}
    selected = st.selectbox("Selecciona un terreno", list(terreno_options.keys()))
    terreno_id = terreno_options[selected]

    parcelas = obtener_parcelas_por_terreno(terreno_id)
    if not parcelas:
        st.info("Este terreno no tiene parcelas.")
        return

    parcela_options = {f"{p['nombre']} (ID: {p['id']})": p["id"] for p in parcelas}
    parcela_key = st.selectbox("Selecciona una parcela", list(parcela_options.keys()))
    parcela_id = parcela_options[parcela_key]

    st.markdown("### Detalles de la Actividad")
    tipo = st.selectbox("Tipo de Actividad", ["Siembra", "Riego", "Fertilización", "Cosecha", "Inspección"])
    descripcion = st.text_area("Descripción")
    fecha_actividad = st.date_input("Fecha", value=date.today())
    usuario_id = st.number_input("ID del Usuario que realizó la actividad", min_value=1, step=1)

    if st.button("Registrar Actividad"):
        datos = {
            "tipo": tipo,
            "fecha": fecha_actividad.isoformat(),
            "descripcion": descripcion,
            "usuario_id": usuario_id,
            "parcela_id": parcela_id
        }
        result = registrar_actividad(datos)
        if result:
            st.success("✅ Actividad registrada correctamente.")
        else:
            st.error("❌ Error al registrar la actividad.")
