import requests
import pandas as pd
from datetime import timedelta
from collections import Counter

API_URL = "http://localhost:8000"  # Ajusta si corres desde Docker o con dominio

def resumen_estado_parcelas(estado_parcelas):
    resumen = Counter({"Óptimo": 0, "Atención": 0, "Crítico": 0})
    for estados in estado_parcelas.values():
        if "Inactiva" in estados:
            resumen["Crítico"] += 1
        elif "Pendiente de intervención" in estados:
            resumen["Atención"] += 1
        elif "Activa" in estados:
            resumen["Óptimo"] += 1
        else:
            resumen["Atención"] += 1
    return resumen

def evaluar_estado_parcelas(df_actividades):
    hoy = pd.Timestamp.today().normalize()
    estado_parcelas = {}

    for parcela_id, grupo in df_actividades.groupby("parcela_id"):
        grupo = grupo.copy()
        grupo["fecha"] = pd.to_datetime(grupo["fecha"], errors="coerce")

        ultima_fecha = grupo["fecha"].max()
        dias_sin_actividad = (hoy - ultima_fecha).days
        estado = []

        if dias_sin_actividad <= 5:
            estado.append("Activa")
        elif dias_sin_actividad <= 10:
            estado.append("Pendiente de intervención")
        else:
            estado.append("Inactiva")

        if "Cosecha" in grupo["tipo"].tolist():
            fechas_cosecha = grupo[grupo["tipo"] == "Cosecha"]["fecha"]
            if any((hoy - fechas_cosecha).dt.days <= 3):
                estado.append("Cosechada recientemente")

        tareas_recientes = grupo[grupo["fecha"] >= hoy - timedelta(days=3)]
        if len(tareas_recientes) >= 3:
            estado.append("Alta carga de tareas")

        if grupo["tipo"].isin(["Cosecha", "Ordeño", "Pesaje"]).any():
            estado.append("Tiene productividad")

        estado_parcelas[parcela_id] = estado

    return estado_parcelas


def cargar_datos():
    # Revisar que la conexion con el backend esta bien
    try:
        terrenos = obtener_terrenos()
    except Exception as e:
        print(f"Error al obtener terrenos: {e}")
        return [], [], [], {}
    
    parcelas = []
    for terreno in terrenos:
        parcelas += obtener_parcelas_por_terreno(terreno["id"])

    df_actividades = []
    for parcela in parcelas:
        acts = obtener_actividades_por_parcela(parcela["id"])
        for act in acts:
            act["nombre"] = parcela["nombre"]
        df_actividades += acts

    df_actividades = pd.DataFrame(df_actividades)
    df_actividades["fecha"] = pd.to_datetime(df_actividades["fecha"], errors="coerce")
    parcelas_df = pd.DataFrame(parcelas)
    terrenos_df = pd.DataFrame(terrenos)
    parcelas_ids = {row["nombre"]: row["id"] for _, row in parcelas_df.iterrows()}
    return df_actividades, parcelas_df, terrenos_df, parcelas_ids


def obtener_respuesta_llm(prompt: str) -> str:
    try:
        res = requests.post(
            f"{API_URL}/chat",
            json={"prompt": prompt},
            timeout=15  # opcional
        )
        res.raise_for_status()
        return res.json().get("respuesta", "[Sin respuesta del modelo]")
    except Exception as e:
        print(f"Error al consultar el LLM: {e}")
        return "[Error en la conexión con el backend]"

def obtener_actividades_por_parcela(parcela_id):
    try:
        res = requests.get(f"{API_URL}/actividades/por-parcela/{parcela_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener actividades: {e}")
        return []

def obtener_terrenos():
    try:
        res = requests.get(f"{API_URL}/terrenos")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener terrenos: {e}")
        return []

def obtener_parcelas_por_terreno(terreno_id):
    try:
        res = requests.get(f"{API_URL}/parcelas/por-terreno/{terreno_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener parcelas: {e}")
        return []

def obtener_parcela(parcela_id):
    try:
        res = requests.get(f"{API_URL}/parcelas/{parcela_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener parcela: {e}")
        return {}

def obtener_ubicacion(ubicacion_id):
    try:
        res = requests.get(f"{API_URL}/ubicaciones/{ubicacion_id}")
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al obtener ubicación: {e}")
        return {}

def registrar_actividad(data):
    try:
        res = requests.post(f"{API_URL}/actividades/", json=data)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        print(f"Error al registrar actividad: {e}")
        return None
