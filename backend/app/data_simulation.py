import pandas as pd
import random
from datetime import date, timedelta

# ----------------------
# DATOS ESTÁTICOS BASE
# ----------------------

terrenos = pd.DataFrame([
    {"id": 1, "nombre": "Terreno 1", "descripcion": "Cultivo mixto de hortalizas"},
    {"id": 2, "nombre": "Terreno 2", "descripcion": "Ganadería y forraje"},
])

parcelas = pd.DataFrame([
    {"id": 1, "nombre": "Parcela 1A", "terreno_id": 1, "uso_actual": "Maíz joven", "estado": "activo", "dias_sin_actividad": 1},
    {"id": 2, "nombre": "Parcela 1B", "terreno_id": 1, "uso_actual": "Tomate en invernadero", "estado": "activo", "dias_sin_actividad": 2},
    {"id": 3, "nombre": "Parcela 2A", "terreno_id": 2, "uso_actual": "Pasto", "estado": "activo", "dias_sin_actividad": 7},
    {"id": 4, "nombre": "Parcela 2B", "terreno_id": 2, "uso_actual": "Corrales", "estado": "mantenimiento", "dias_sin_actividad": 12},
])

parcelas_info = {
    'Terreno 1': "🌽 Cultivo mixto de maíz y tomate.",
    'Parcela 1A': "🌱 Maíz joven.",
    'Parcela 1B': "🍅 Tomate bajo invernadero.",
    'Terreno 2': "🐄 Zona de ganadería y forraje.",
    'Parcela 2A': "🌾 Pasto para rotación.",
    'Parcela 2B': "🐖 Corrales en mantenimiento.",
}

tipos_actividad = [
    "Riego", "Fertilización", "Fumigación", "Cosecha",
    "Siembra", "Limpieza", "Pesaje", "Vacunación", "Ordeño"
]

# ----------------------
# FUNCIONES SIMULADORAS
# ----------------------

def generar_actividad(parcela_id, nombre_parcela, fecha_base, cantidad=5):
    actividades = []
    for i in range(cantidad):
        tipo = random.choice(tipos_actividad)
        fecha = fecha_base - timedelta(days=i)
        actividades.append({
            "parcela_id": parcela_id,
            "nombre": nombre_parcela,
            "tipo": tipo,
            "descripcion": f"{tipo} realizada en campo",
            "fecha": fecha
        })
    return actividades

def generar_detalles(df_actividades: pd.DataFrame) -> pd.DataFrame:
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
        # puedes agregar más aquí fácilmente

    return pd.DataFrame(detalles)

# ----------------------
# SIMULACIÓN DE TRANSACCIONES
# ----------------------

def simular_transacciones(parcelas_df: pd.DataFrame, n_por_parcela: int = 3) -> pd.DataFrame:
    categorias_gasto = ["Compra fertilizante", "Riego mecanizado", "Mantenimiento maquinaria", "Compra alimento animal"]
    categorias_ingreso = ["Venta maíz", "Venta leche", "Venta ganado"]

    transacciones = []
    hoy = date.today()

    for _, parcela in parcelas_df.iterrows():
        for _ in range(n_por_parcela):
            tipo = random.choice(["gasto", "ingreso"])
            categoria = random.choice(categorias_ingreso if tipo == "ingreso" else categorias_gasto)
            monto = round(random.uniform(100, 1000), 2) if tipo == "gasto" else round(random.uniform(500, 2000), 2)

            transacciones.append({
                "parcela_id": parcela["id"],
                "fecha": hoy - timedelta(days=random.randint(1, 60)),
                "tipo": tipo,
                "categoria": categoria,
                "descripcion": f"{tipo.capitalize()} registrado automáticamente",
                "monto": monto
            })

    return pd.DataFrame(transacciones)

# ----------------------
# SIMULACIÓN DE INVENTARIO
# ----------------------


def simular_inventario(parcelas_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    tipos_insumo = ["Fertilizante NPK", "Alimento ganado", "Vacuna bovina", "Pesticida"]
    inventario = []
    eventos = []
    id_counter = 1
    hoy = date.today()

    for _, parcela in parcelas_df.iterrows():
        for insumo in tipos_insumo:
            cantidad = round(random.uniform(50, 500), 2)
            unidad = "kg" if "Fertilizante" in insumo else "l" if "Pesticida" in insumo else "dosis"
            inventario.append({
                "id": id_counter,
                "nombre": insumo,
                "tipo": insumo.split()[0],
                "cantidad_actual": cantidad,
                "unidad": unidad,
                "parcela_id": parcela["id"]
            })

            # Un evento de consumo
            eventos.append({
                "inventario_id": id_counter,
                "actividad_id": None,
                "tipo_movimiento": "salida",
                "cantidad": round(random.uniform(5, 30), 2),
                "fecha": hoy - timedelta(days=random.randint(1, 20)),
                "observacion": "Consumo rutinario"
            })
            id_counter += 1

    return pd.DataFrame(inventario), pd.DataFrame(eventos)

# ----------------------
# SIMULACIÓN DE INDICADORES
# ----------------------


def simular_indicadores(parcelas_df: pd.DataFrame) -> pd.DataFrame:
    indicadores = []
    hoy = date.today()

    for _, parcela in parcelas_df.iterrows():
        indicadores += [
            {
                "parcela_id": parcela["id"],
                "nombre": "Avance operativo",
                "valor": round(random.uniform(60, 100), 1),
                "unidad": "%",
                "fecha": hoy,
                "descripcion": "Porcentaje de tareas completadas en el mes"
            },
            {
                "parcela_id": parcela["id"],
                "nombre": "Producción acumulada",
                "valor": round(random.uniform(800, 3000), 2),
                "unidad": "kg",
                "fecha": hoy,
                "descripcion": "Volumen estimado cosechado"
            },
        ]

    return pd.DataFrame(indicadores)



# ----------------------
# FUNCIÓN PRINCIPAL
# ----------------------

def simular_datos(parcelas_df: pd.DataFrame):
    hoy = date.today()
    actividades = []

    for _, row in parcelas_df.iterrows():
        base_date = hoy - timedelta(days=row["dias_sin_actividad"])
        actividades += generar_actividad(row["id"], row["nombre"], base_date)

    df_actividades = pd.DataFrame(actividades).reset_index(drop=True)
    df_actividades["id"] = df_actividades.index + 1
    df_actividades["fecha"] = pd.to_datetime(df_actividades["fecha"])
    df_transacciones = simular_transacciones(parcelas)
    df_inventario, df_eventos = simular_inventario(parcelas)
    df_indicadores = simular_indicadores(parcelas)


    detalles_df = generar_detalles(df_actividades)

    return df_actividades, detalles_df, df_transacciones, df_inventario, df_eventos, df_indicadores
