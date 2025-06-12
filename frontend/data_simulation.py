import pandas as pd
import random
from datetime import date, timedelta

terrenos = pd.DataFrame([
    {"id": 1, "nombre": "Terreno 1", "descripcion": "Cultivo mixto de hortalizas"},
    {"id": 2, "nombre": "Terreno 2", "descripcion": "Ganadería y forraje"}
])

# Parcelas con control de días sin actividad para simular estado
parcelas = pd.DataFrame([
    {"id": 1, "nombre": "Parcela 1A", "terreno_id": 1, "uso_actual": "Maíz joven", "estado": "activo", "dias_sin_actividad": 1},  # Óptimo
    {"id": 2, "nombre": "Parcela 1B", "terreno_id": 1, "uso_actual": "Tomate en invernadero", "estado": "activo", "dias_sin_actividad": 2},  # Óptimo
    {"id": 3, "nombre": "Parcela 2A", "terreno_id": 2, "uso_actual": "Pasto", "estado": "activo", "dias_sin_actividad": 7},  # Atención
    {"id": 4, "nombre": "Parcela 2B", "terreno_id": 2, "uso_actual": "Corrales", "estado": "mantenimiento", "dias_sin_actividad": 12}  # Crítico
])

parcelas_info = {
    'Terreno 1': "🌽 Cultivo mixto de maíz y tomate.",
    'Parcela 1A': "🌱 Maíz joven.",
    'Parcela 1B': "🍅 Tomate bajo invernadero.",
    'Terreno 2': "🐄 Zona de ganadería y forraje.",
    'Parcela 2A': "🌾 Pasto para rotación.",
    'Parcela 2B': "🐖 Corrales en mantenimiento.",
}

def simular_datos(parcelas):
    tipos_actividad = ["Riego", "Fertilización", "Fumigación", "Cosecha", "Siembra", "Limpieza", "Pesaje", "Vacunación", "Ordeño"]
    actividades = []
    hoy = date.today()

    for _, row in parcelas.iterrows():
        base_date = hoy - timedelta(days=row["dias_sin_actividad"])
        for i in range(5):
            tipo = random.choice(tipos_actividad)
            actividades.append({
                "parcela_id": row["id"],
                "nombre": row["nombre"],
                "tipo": tipo,
                "descripcion": "Tarea realizada",
                "fecha": base_date - timedelta(days=i)
            })

    df_actividades = pd.DataFrame(actividades).reset_index(drop=True)
    df_actividades["id"] = df_actividades.index + 1
    df_actividades["fecha"] = pd.to_datetime(df_actividades["fecha"])

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
