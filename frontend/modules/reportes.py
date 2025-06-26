import streamlit as st
import pandas as pd
import requests

API = "http://localhost:8000"

def vista_reportes():
    st.title("📂 Reportes y Exportación")
    st.markdown("Explora métricas clave por terreno, parcela o categoría.")

    anio = st.selectbox("Año", [2025, 2024])
    categoria = st.text_input("Filtrar por categoría (opcional)", "")

    try:
        res = requests.get(f"{API}/economia/comparativo", params={"anio": anio})
        res.raise_for_status()
        datos = res.json()
    except Exception as e:
        st.error(f"No se pudo cargar información: {e}")
        return

    df = pd.DataFrame(datos)
    if categoria:
        df = df[df["categoria"].str.contains(categoria, case=False)]

    st.markdown("### 📊 Resumen comparativo")
    st.dataframe(df)

    # Exportar a Excel
    if not df.empty:
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Descargar CSV", data=csv, file_name=f"reporte_{anio}.csv", mime="text/csv")
