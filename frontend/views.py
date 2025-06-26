import streamlit as st
import altair as alt
import pandas as pd

def mostrar_presupuesto_vs_ejecucion_terreno(parcela_ids):
    import requests
    API = "http://localhost:8000"
    anio = pd.Timestamp.today().year
    all_data = []

    for parcela_id in parcela_ids:
        try:
            res = requests.get(f"{API}/economia/comparativo", params={"anio": anio, "parcela_id": parcela_id})
            res.raise_for_status()
            all_data += res.json()
        except Exception as e:
            st.warning(f"Error en parcela {parcela_id}: {e}")

    if not all_data:
        st.warning("No hay datos económicos disponibles para este terreno.")
        return

    df = pd.DataFrame(all_data)
    resumen = df.groupby("categoria").agg({
        "monto_presupuestado": "sum",
        "monto_ejecutado": "sum",
    }).reset_index()
    resumen["categoria"] = resumen["categoria"].str.capitalize()

    chart = alt.Chart(resumen).transform_fold(
        ["monto_presupuestado", "monto_ejecutado"],
        as_=["Tipo", "Monto"]
    ).mark_bar().encode(
        x=alt.X("categoria:N", title="Categoría"),
        y=alt.Y("Monto:Q", title="Total $"),
        color=alt.Color("Tipo:N", scale=alt.Scale(range=["#6666ff", "#76b900"])),
        tooltip=["categoria", "Monto", "Tipo"]
    ).properties(width=500, height=300)

    st.altair_chart(chart, use_container_width=True)


def mostrar_kpis_terreno(df_terreno, indicadores_df=None):
    st.markdown("### 📊 KPIs")

    ultima_fecha = df_terreno["fecha"].max()
    dias_inactiva = (pd.Timestamp.today().normalize() - ultima_fecha).days

    st.metric("Última actividad registrada", ultima_fecha.strftime("%d %b %Y"))
    st.metric("Promedio días sin actividad", round(dias_inactiva, 1))

    if indicadores_df is not None and not indicadores_df.empty:
        total_prod = indicadores_df[indicadores_df["nombre"] == "Producción acumulada"]["valor"].sum()
        unidad = indicadores_df[indicadores_df["nombre"] == "Producción acumulada"]["unidad"].unique()[0]
        st.metric("Producción total estimada", f"{round(total_prod, 2)} {unidad}")

    st.markdown("---")


def mostrar_presupuesto_vs_ejecucion(parcela_id):
    import requests
    API = "http://localhost:8000"  # ajustar si es necesario

    try:
        res = requests.get(f"{API}/economia/comparativo", params={"anio": pd.Timestamp.today().year, "parcela_id": parcela_id})
        res.raise_for_status()
        data = res.json()

        df = pd.DataFrame(data)
        df["categoria"] = df["categoria"].str.capitalize()
        chart = alt.Chart(df).mark_bar().encode(
            x=alt.X("categoria:N", title="Categoría"),
            y=alt.Y("monto_ejecutado:Q", title="Monto Ejecutado ($)"),
            color=alt.value("#76b900"),
            tooltip=["categoria", "monto_presupuestado", "monto_ejecutado", "diferencia"]
        ).properties(width=500, height=300).interactive()

        st.altair_chart(chart, use_container_width=True)

    except Exception as e:
        st.warning(f"Error cargando comparativo económico: {e}")


def mostrar_kpis_parcela(df_parcela, indicadores_df=None):
    st.markdown("### 📊 Indicadores clave")

    # Última actividad
    ultima_fecha = df_parcela["fecha"].max()
    dias_inactiva = (pd.Timestamp.today().normalize() - ultima_fecha).days
    st.metric("Última actividad", ultima_fecha.strftime("%d %b %Y"))
    st.metric("Días sin actividad", dias_inactiva)

    # Producción (si viene en indicadores_df)
    if indicadores_df is not None and not indicadores_df.empty:
        prod = indicadores_df[indicadores_df["nombre"] == "Producción acumulada"]
        if not prod.empty:
            valor = prod.iloc[0]["valor"]
            unidad = prod.iloc[0]["unidad"]
            st.metric("Producción acumulada", f"{valor} {unidad}")

    st.markdown("---")


def mostrar_frecuencia(df_parcela):
    freq = df_parcela["tipo"].value_counts()
    st.bar_chart(freq)

def mostrar_detalles(df_parcela, detalles_df):
    df_det = detalles_df.merge(
        df_parcela[["id", "nombre", "tipo", "fecha"]],
        left_on="actividad_id",
        right_on="id",
        suffixes=("_detalle", "_actividad")
    )
    df_det["valor_num"] = pd.to_numeric(df_det["valor"], errors="coerce")
    df_plot = df_det[df_det["valor_num"].notnull()]
    
    if not df_plot.empty:
        chart = alt.Chart(df_plot).mark_bar().encode(
            x="nombre_detalle:N",
            y="valor_num:Q",
            color="tipo:N",
            tooltip=["nombre_detalle", "tipo", "valor", "unidad", "fecha"]
        ).properties(width=600, height=400)
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("No hay detalles numéricos disponibles.")

def mostrar_ultimas(df_parcela):
    df_ult = df_parcela.sort_values("fecha", ascending=False).head(5)
    st.dataframe(df_ult[["tipo", "fecha"]], use_container_width=True)
    st.metric("Última actividad", df_ult["fecha"].max().strftime("%d %b"))
