import pandas as pd
import random
from datetime import date, timedelta

terrenos = pd.DataFrame([
    {"id": 1, "nombre": "Terreno 1", "descripcion": "Cultivo de maíz"},
    {"id": 2, "nombre": "Terreno 2", "descripcion": "Ganadería"}
])

# Parcelas
parcelas = pd.DataFrame([
    {"id": 1, "nombre": "Parcela 1A", "terreno_id": 1, "uso_actual": "Maíz joven", "estado": "activo"},
    {"id": 2, "nombre": "Parcela 1B", "terreno_id": 1, "uso_actual": "Maíz maduro", "estado": "cosecha"},
    {"id": 3, "nombre": "Parcela 2A", "terreno_id": 2, "uso_actual": "Pasto", "estado": "activo"},
    {"id": 4, "nombre": "Parcela 2B", "terreno_id": 2, "uso_actual": "Corrales", "estado": "mantenimiento"}
])

parcelas_info = {
    'Terreno 1': "🌽 Cultivo de maíz.\nUso mixto: joven y maduro.",
    'Parcela 1A': "🌱 Maíz joven.\nÁrea experimental.",
    'Parcela 1B': "🌽 Maíz maduro.\nListo para cosecha.",
    'Terreno 2': "🐄 Ganadería.\nDivisión entre pasto y corrales.",
    'Parcela 2A': "🌾 Zona de pasto.\nRotación semanal.",
    'Parcela 2B': "🐖 Corrales.\nRequiere limpieza.",
}


def simular_datos(parcelas):
    # Simulación de actividades con detalles
    tipos_actividad = ["Riego", "Fertilización", "Fumigación", "Cosecha", "Siembra", "Limpieza", "Pesaje", "Vacunación", "Ordeño"]
    actividades = []

    base_date = date(2025, 6, 1)
    for parcela_id in parcelas["id"]:
        for _ in range(10):
            tipo = random.choice(tipos_actividad)
            actividades.append({
                "parcela_id": parcela_id,
                "nombre": parcelas[parcelas["id"] == parcela_id]["nombre"].values[0],
                "tipo": tipo,
                "descripcion": "Tarea realizada",
                "fecha": base_date + timedelta(days=random.randint(0, 15))
            })

    df_actividades = pd.DataFrame(actividades).reset_index(drop=True)
    df_actividades["id"] = df_actividades.index + 1
    df_actividades["fecha"] = pd.to_datetime(df_actividades["fecha"])


    # ----------------------------
    # Detalles por actividad
    detalles = []

    for actividad in df_actividades.itertuples():
        if actividad.tipo == "Fertilización":
            detalles.append({"actividad_id": actividad.id, "nombre": "Fertilizante NPK", "valor": 50, "unidad": "kg"})
        elif actividad.tipo == "Cosecha":
            detalles.append({"actividad_id": actividad.id, "nombre": "Kg cosechados", "valor": random.randint(800, 1500), "unidad": "kg"})
        elif actividad.tipo == "Riego":
            detalles.append({"actividad_id": actividad.id, "nombre": "Agua utilizada", "valor": random.randint(200, 800), "unidad": "l"})
        elif actividad.tipo == "Pesaje":
            detalles.append({"actividad_id": actividad.id, "nombre": "Peso ganado", "valor": random.randint(300, 600), "unidad": "kg"})
        elif actividad.tipo == "Vacunación":
            detalles.append({"actividad_id": actividad.id, "nombre": "Vacuna aplicada", "valor": "Fiebre Aftosa", "unidad": "dosis"})
        elif actividad.tipo == "Ordeño":
            detalles.append({"actividad_id": actividad.id, "nombre": "Litros ordeñados", "valor": random.randint(10, 30), "unidad": "l"})

    detalles_df = pd.DataFrame(detalles)
    return df_actividades, detalles_df
