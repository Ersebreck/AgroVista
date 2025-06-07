import random
from datetime import date, timedelta
from sqlalchemy.orm import Session
from geoalchemy2.shape import from_shape
from shapely.geometry import Polygon
from app.db import engine, SessionLocal
from app.models import Base, Usuario, Ubicacion, Terreno, Parcela, Actividad


def random_polygon(x0, y0, size=1.0):
    return Polygon([
        (x0, y0),
        (x0 + size, y0),
        (x0 + size, y0 + size),
        (x0, y0 + size),
        (x0, y0)
    ])


def create_users(db: Session):
    # Admin
    admin = Usuario(
        nombre="Admin Global",
        correo="admin@agrovista.com",
        contrasena="admin123",  # sin hash por ahora
        rol="admin"
    )
    db.add(admin)

    propietarios = []
    for i in range(5):
        user = Usuario(
            nombre=f"Propietario {i+1}",
            correo=f"user{i+1}@agro.com",
            contrasena="pass123",
            rol="propietario"
        )
        db.add(user)
        propietarios.append(user)
    db.commit()
    return propietarios


def create_terrenos_y_parcelas(db: Session, propietarios):
    actividad_tipos = ["Siembra", "Riego", "Fertilización", "Cosecha", "Inspección"]
    usos = ["Maíz", "Frijol", "Papa", "Reposo", "Caña"]
    estados = ["activa", "inactiva"]

    parcela_id = 1
    for i, prop in enumerate(propietarios):
        for t in range(2):  # 2 terrenos por propietario
            x0, y0 = i * 15 + t * 6, 0
            ubic = Ubicacion(
                tipo="poligono",
                coordenadas=from_shape(random_polygon(x0, y0, 5.0), srid=4326),
                referencia={"nombre": f"Terreno {t+1} de {prop.nombre}"}
            )
            db.add(ubic)
            db.commit()
            terreno = Terreno(
                nombre=f"Terreno_{prop.id}_{t+1}",
                descripcion="Terreno agrícola automatizado.",
                propietario_id=prop.id,
                ubicacion_id=ubic.id
            )
            db.add(terreno)
            db.commit()

            num_parcelas = random.randint(3, 6)
            for p in range(num_parcelas):
                dx, dy = (p % 3) * 1.5, (p // 3) * 1.5
                sub_ubic = Ubicacion(
                    tipo="poligono",
                    coordenadas=from_shape(random_polygon(x0 + dx, y0 + dy, 1.2), srid=4326),
                    referencia={"nombre": f"Parcela {parcela_id}"}
                )
                db.add(sub_ubic)
                db.commit()
                parcela = Parcela(
                    nombre=f"Parcela_{terreno.id}_{p+1}",
                    uso_actual=random.choice(usos),
                    estado=random.choice(estados),
                    terreno_id=terreno.id,
                    ubicacion_id=sub_ubic.id
                )
                db.add(parcela)
                db.commit()

                num_actividades = random.randint(2, 5)
                for a in range(num_actividades):
                    actividad = Actividad(
                        tipo=random.choice(actividad_tipos),
                        fecha=date.today() - timedelta(days=random.randint(0, 100)),
                        descripcion=f"Actividad generada automáticamente {a+1}",
                        usuario_id=prop.id,
                        parcela_id=parcela.id
                    )
                    db.add(actividad)
