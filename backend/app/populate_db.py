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

    parcelas_info = {
        "Parcela 1A": {"uso": "Maíz joven", "estado": "activo", "dias_sin_actividad": 1},
        "Parcela 1B": {"uso": "Caña de azucar", "estado": "activo", "dias_sin_actividad": 2},
        "Parcela 2A": {"uso": "Pasto", "estado": "activo", "dias_sin_actividad": 7},
        "Parcela 2B": {"uso": "Corrales", "estado": "mantenimiento", "dias_sin_actividad": 12}
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
        for a in range(3):
            tipo = random.choice(["Riego", "Fertilización", "Cosecha", "Vacunación", "Ordeño"])
            actividad = Actividad(
                tipo=tipo,
                fecha=base_date - timedelta(days=a),
                descripcion=f"{tipo} automática",
                usuario_id=propietario.id,
                parcela_id=parcela.id
            )
            db.add(actividad)
            db.commit()

            detalle = None
            if tipo == "Fertilización":
                detalle = DetalleActividad(nombre="Fertilizante NPK", valor="50", unidad="kg", actividad_id=actividad.id)
            elif tipo == "Cosecha":
                detalle = DetalleActividad(nombre="Kg cosechados", valor=str(random.randint(800, 1500)), unidad="kg", actividad_id=actividad.id)
            elif tipo == "Riego":
                detalle = DetalleActividad(nombre="Agua utilizada", valor=str(random.randint(200, 800)), unidad="l", actividad_id=actividad.id)
            elif tipo == "Vacunación":
                detalle = DetalleActividad(nombre="Vacuna aplicada", valor="Fiebre Aftosa", unidad="dosis", actividad_id=actividad.id)
            elif tipo == "Ordeño":
                detalle = DetalleActividad(nombre="Litros ordeñados", valor=str(random.randint(10, 30)), unidad="l", actividad_id=actividad.id)

            if detalle:
                db.add(detalle)
                db.commit()

    # --------------------------
    # NUEVAS ENTIDADES
    # --------------------------
    parcelas_creadas = db.query(Parcela).all()

    # Transacciones
    df_transacciones = simular_transacciones(pd.DataFrame([p.__dict__ for p in parcelas_creadas]))
    for row in df_transacciones.to_dict(orient="records"):
        db.add(Transaccion(**row))
    db.commit()

    # Inventario y eventos
    df_inv, df_eventos = simular_inventario(pd.DataFrame([p.__dict__ for p in parcelas_creadas]))
    inventario_id_map = {}
    for row in df_inv.to_dict(orient="records"):
        inv = Inventario(**row)
        db.add(inv)
        db.flush()
        inventario_id_map[row["id"]] = inv.id
    db.commit()

    for ev in df_eventos.to_dict(orient="records"):
        ev["inventario_id"] = inventario_id_map.get(ev["inventario_id"], 1)
        db.add(EventoInventario(**ev))
    db.commit()

    # Indicadores
    df_ind = simular_indicadores(pd.DataFrame([p.__dict__ for p in parcelas_creadas]))
    for row in df_ind.to_dict(orient="records"):
        db.add(Indicador(**row))
    db.commit()

    print("✅ Base poblada con actividades, inventario, transacciones e indicadores.")
