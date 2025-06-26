from datetime import date, timedelta
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon
from app.models import (
    Usuario, Terreno, Parcela, Ubicacion, Actividad, DetalleActividad,
    Transaccion, Inventario, EventoInventario, Indicador
)
import random
import pandas as pd
from app.data_simulation import simular_transacciones, simular_inventario, simular_indicadores

def create_users(db: Session):
    admin = Usuario(nombre="Admin", correo="admin@agro.com", contrasena="admin123", rol="admin")
    propietario = Usuario(nombre="Propietario Demo", correo="prop@agro.com", contrasena="demo123", rol="propietario")
    db.add_all([admin, propietario])
    db.commit()
    return propietario

def create_terrenos_y_parcelas(db: Session, propietario):
    hoy = date.today()

    terrenos_coords = {
        "Terreno 1": [
            [5.490012, -74.689513], [5.491388, -74.686458], [5.493076, -74.686186],
            [5.494909, -74.687275], [5.495821, -74.687296], [5.495455, -74.689642],
            [5.492761, -74.690266]
        ],
        "Terreno 2": [
            [5.490012, -74.689513], [5.491388, -74.686458], [5.489541, -74.683064],
            [5.485220, -74.683948], [5.487558, -74.688777]
        ]
    }

    parcelas_coords = {
        "Parcela 1A": [
            [5.490012, -74.689513], [5.490818, -74.687843], 
            [5.493041, -74.688052], [5.492761, -74.690266]
        ],
        "Parcela 1B": [
            [5.493021, -74.688042], [5.493201, -74.686225], 
            [5.494670, -74.687154], [5.495789, -74.687333], 
            [5.495671, -74.688349]
        ],
        "Parcela 2A": [
            [5.488324, -74.685804], [5.486298, -74.686302], 
            [5.485390, -74.683935], [5.487827, -74.683315]
        ],
        "Parcela 2B": [
            [5.488324, -74.685804], [5.487951, -74.683294], 
            [5.489582, -74.683106], [5.490635, -74.685222]
        ]
    }

    # Estados: 2 óptimas, 1 en atención, 1 crítica
    parcelas_info = {
        # Parcelas en estado óptimo (activas con pocos días sin actividad)
        "Parcela 1A": {"uso": "Caña joven", "estado": "activo", "dias_sin_actividad": 1, "estado_salud": "óptimo"},
        "Parcela 1B": {"uso": "Caña de azucar", "estado": "activo", "dias_sin_actividad": 2, "estado_salud": "óptimo"},
        # Parcela en estado de atención (algún indicador fuera de rango)
        "Parcela 2A": {"uso": "Pasto", "estado": "activo", "dias_sin_actividad": 5, "estado_salud": "atención"},
        # Parcela en estado crítico (mucho tiempo sin mantenimiento)
        "Parcela 2B": {"uso": "Corrales", "estado": "mantenimiento", "dias_sin_actividad": 15, "estado_salud": "crítico"}
    }

    terreno_objs = {}
    for nombre, coords in terrenos_coords.items():
        poligono = Polygon([(lon, lat) for lat, lon in coords])
        ubicacion = Ubicacion(
            tipo="poligono",
            coordenadas=from_shape(poligono, srid=4326),
            referencia={"nombre": nombre}
        )
        db.add(ubicacion)
        db.commit()

        terreno = Terreno(
            nombre=nombre,
            descripcion="Terreno generado con coordenadas reales.",
            propietario_id=propietario.id,
            ubicacion_id=ubicacion.id
        )
        db.add(terreno)
        db.commit()
        terreno_objs[nombre] = terreno

    for i, (nombre, coords) in enumerate(parcelas_coords.items(), start=1):
        terreno_id = 1 if "1" in nombre else 2
        info = parcelas_info[nombre]
        poligono = Polygon([(lon, lat) for lat, lon in coords])
        ubic = Ubicacion(
            tipo="poligono",
            coordenadas=from_shape(poligono, srid=4326),
            referencia={"nombre": nombre}
        )
        db.add(ubic)
        db.commit()

        parcela = Parcela(
            nombre=nombre,
            uso_actual=info["uso"],
            estado=info["estado"],
            terreno_id=terreno_objs[f"Terreno {terreno_id}"].id,
            ubicacion_id=ubic.id
        )
        db.add(parcela)
        db.commit()

        base_date = hoy - timedelta(days=info["dias_sin_actividad"])
        
        # Definir actividades según el estado de salud de la parcela
        if info["estado_salud"] == "óptimo":
            # Parcelas óptimas tienen actividades recientes y en buen estado
            actividades = [
                ("Riego", base_date - timedelta(hours=2), "Riego programado", "200", "l"),
                ("Fertilización", base_date - timedelta(days=1), "Aplicación de fertilizante", "30", "kg"),
                ("Cosecha", base_date - timedelta(days=3), "Cosecha parcial", "1000", "kg")
            ]
        elif info["estado_salud"] == "atención":
            # Parcela que necesita atención tiene actividades más espaciadas
            actividades = [
                ("Riego", base_date - timedelta(days=2), "Riego insuficiente", "100", "l"),
                ("Fertilización", base_date - timedelta(days=7), "Fertilización pendiente", "20", "kg"),
                ("Mantenimiento", base_date - timedelta(days=10), "Revisión necesaria", "1", "revisión")
            ]
        else:  # estado crítico
            # Parcela crítica tiene actividades muy antiguas o faltantes
            actividades = [
                ("Riego", base_date - timedelta(days=14), "Último riego", "50", "l"),
                ("Mantenimiento", base_date - timedelta(days=30), "Mantenimiento urgente requerido", "1", "urgencia")
            ]
        
        # Crear las actividades
        for tipo, fecha, desc, valor, unidad in actividades:
            actividad = Actividad(
                tipo=tipo,
                fecha=fecha,
                descripcion=desc,
                usuario_id=propietario.id,
                parcela_id=parcela.id
            )
            db.add(actividad)
            db.flush()  # Para obtener el ID de la actividad
            
            # Crear detalles específicos para cada tipo de actividad
            if tipo == "Fertilización":
                detalle = DetalleActividad(
                    nombre="Fertilizante NPK",
                    valor=valor,
                    unidad=unidad,
                    actividad_id=actividad.id
                )
            elif tipo == "Cosecha":
                detalle = DetalleActividad(
                    nombre="Kg cosechados",
                    valor=valor,
                    unidad=unidad,
                    actividad_id=actividad.id
                )
            elif tipo == "Riego":
                detalle = DetalleActividad(
                    nombre="Agua utilizada",
                    valor=valor,
                    unidad=unidad,
                    actividad_id=actividad.id
                )
            elif tipo == "Mantenimiento":
                detalle = DetalleActividad(
                    nombre="Estado",
                    valor=desc,
                    unidad=unidad,
                    actividad_id=actividad.id
                )
            
            if detalle:
                db.add(detalle)
        
        db.commit()

    # --------------------------
    # NUEVAS ENTIDADES
    # --------------------------
    parcelas_creadas = db.query(Parcela).all()

    # Transacciones deterministas según estado de salud
    transacciones_por_estado = {
        "óptimo": [
            {"tipo": "ingreso", "categoria": "Venta maíz", "descripcion": "Ingreso por venta de maíz", "monto": 1800},
            {"tipo": "gasto", "categoria": "Compra fertilizante", "descripcion": "Compra de fertilizante NPK", "monto": 200},
        ],
        "atención": [
            {"tipo": "gasto", "categoria": "Riego mecanizado", "descripcion": "Riego adicional por sequía", "monto": 500},
            {"tipo": "gasto", "categoria": "Mantenimiento maquinaria", "descripcion": "Reparación de maquinaria", "monto": 400},
            {"tipo": "ingreso", "categoria": "Venta leche", "descripcion": "Ingreso bajo por baja producción", "monto": 600},
        ],
        "crítico": [
            {"tipo": "gasto", "categoria": "Mantenimiento maquinaria", "descripcion": "Reparación urgente de infraestructura", "monto": 900},
            {"tipo": "gasto", "categoria": "Compra alimento animal", "descripcion": "Compra de emergencia de alimento", "monto": 700},
        ]
    }
    hoy = date.today()
    for parcela in parcelas_creadas:
        estado_salud = None
        # Determinar el estado de salud de la parcela
        for nombre, info in parcelas_info.items():
            if parcela.nombre == nombre:
                estado_salud = info["estado_salud"]
                break
        if not estado_salud:
            estado_salud = "óptimo"  # fallback
        transacciones = transacciones_por_estado.get(estado_salud, [])
        for idx, trans in enumerate(transacciones):
            db.add(Transaccion(
                parcela_id=parcela.id,
                fecha=hoy - timedelta(days=idx*5),
                tipo=trans["tipo"],
                categoria=trans["categoria"],
                descripcion=trans["descripcion"],
                monto=trans["monto"]
            ))
    db.commit()

    # Inventario y eventos deterministas según estado de salud
    inventario_por_estado = {
        "óptimo": [
            {"nombre": "Fertilizante NPK", "tipo": "Fertilizante", "cantidad_actual": 400, "unidad": "kg"},
            {"nombre": "Alimento ganado", "tipo": "Alimento", "cantidad_actual": 300, "unidad": "kg"}
        ],
        "atención": [
            {"nombre": "Fertilizante NPK", "tipo": "Fertilizante", "cantidad_actual": 150, "unidad": "kg"},
            {"nombre": "Alimento ganado", "tipo": "Alimento", "cantidad_actual": 100, "unidad": "kg"}
        ],
        "crítico": [
            {"nombre": "Fertilizante NPK", "tipo": "Fertilizante", "cantidad_actual": 30, "unidad": "kg"},
            {"nombre": "Alimento ganado", "tipo": "Alimento", "cantidad_actual": 10, "unidad": "kg"}
        ]
    }
    evento_por_estado = {
        "óptimo": [
            {"tipo_movimiento": "salida", "cantidad": 30, "observacion": "Uso regular"}
        ],
        "atención": [
            {"tipo_movimiento": "salida", "cantidad": 60, "observacion": "Consumo elevado"}
        ],
        "crítico": [
            {"tipo_movimiento": "salida", "cantidad": 90, "observacion": "Consumo crítico"}
        ]
    }
    inventario_id_map = {}
    inventario_id_counter = 1
    hoy = date.today()
    for parcela in parcelas_creadas:
        estado_salud = None
        for nombre, info in parcelas_info.items():
            if parcela.nombre == nombre:
                estado_salud = info["estado_salud"]
                break
        if not estado_salud:
            estado_salud = "óptimo"
        inventarios = inventario_por_estado.get(estado_salud, [])
        for inv in inventarios:
            inv_obj = Inventario(
                nombre=inv["nombre"],
                tipo=inv["tipo"],
                cantidad_actual=inv["cantidad_actual"],
                unidad=inv["unidad"],
                parcela_id=parcela.id
            )
            db.add(inv_obj)
            db.flush()
            inventario_id_map[inventario_id_counter] = inv_obj.id
            inventario_id_counter += 1
        eventos = evento_por_estado.get(estado_salud, [])
        for ev in eventos:
            db.add(EventoInventario(
                inventario_id=inv_obj.id,
                actividad_id=None,
                tipo_movimiento=ev["tipo_movimiento"],
                cantidad=ev["cantidad"],
                fecha=hoy - timedelta(days=2),
                observacion=ev["observacion"]
            ))
    db.commit()

    # Indicadores deterministas según estado de salud
    indicadores_por_estado = {
        "óptimo": [
            {"nombre": "Avance operativo", "valor": 98, "unidad": "%", "descripcion": "Todo al día"},
            {"nombre": "Producción acumulada", "valor": 2500, "unidad": "kg", "descripcion": "Producción máxima"}
        ],
        "atención": [
            {"nombre": "Avance operativo", "valor": 70, "unidad": "%", "descripcion": "Algunas tareas pendientes"},
            {"nombre": "Producción acumulada", "valor": 1200, "unidad": "kg", "descripcion": "Producción media"}
        ],
        "crítico": [
            {"nombre": "Avance operativo", "valor": 30, "unidad": "%", "descripcion": "Tareas críticas sin realizar"},
            {"nombre": "Producción acumulada", "valor": 200, "unidad": "kg", "descripcion": "Producción muy baja"}
        ]
    }
    for parcela in parcelas_creadas:
        estado_salud = None
        for nombre, info in parcelas_info.items():
            if parcela.nombre == nombre:
                estado_salud = info["estado_salud"]
                break
        if not estado_salud:
            estado_salud = "óptimo"
        indicadores = indicadores_por_estado.get(estado_salud, [])
        for ind in indicadores:
            db.add(Indicador(
                parcela_id=parcela.id,
                nombre=ind["nombre"],
                valor=ind["valor"],
                unidad=ind["unidad"],
                fecha=hoy,
                descripcion=ind["descripcion"]
            ))
    db.commit()

    print("✅ Base poblada con actividades, inventario, transacciones e indicadores.")
