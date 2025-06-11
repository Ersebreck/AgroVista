import streamlit as st
import altair as alt
import pandas as pd

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
