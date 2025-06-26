from datetime import timedelta
from collections import Counter
import pandas as pd

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

        estado_parcelas[parcela_id] = estado # MEJORAR ESTOOOOOOOOOOOO

    return estado_parcelas
