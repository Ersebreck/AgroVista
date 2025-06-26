from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text,  Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from sqlalchemy.dialects.postgresql import JSONB

Base = declarative_base()

class Usuario(Base):
    __tablename__ = 'usuarios'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    correo = Column(String, unique=True, nullable=False)
    contrasena = Column(String, nullable=False)
    rol = Column(String, nullable=False)  # e.g. "propietario", "encargado", "admin"

    actividades = relationship("Actividad", back_populates="usuario")
    simulaciones = relationship("Simulacion", backref="usuario", cascade="all, delete-orphan")
    cambios = relationship("HistorialCambio", backref="usuario", cascade="all, delete-orphan")


class Terreno(Base):
    __tablename__ = 'terrenos'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    propietario_id = Column(Integer, ForeignKey("usuarios.id"))
    ubicacion_id = Column(Integer, ForeignKey("ubicaciones.id"))

    propietario = relationship("Usuario")
    parcelas = relationship("Parcela", back_populates="terreno")


class Parcela(Base):
    __tablename__ = 'parcelas'

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    uso_actual = Column(String)
    estado = Column(String)
    terreno_id = Column(Integer, ForeignKey("terrenos.id"))
    ubicacion_id = Column(Integer, ForeignKey("ubicaciones.id"))

    terreno = relationship("Terreno", back_populates="parcelas")
    actividades = relationship("Actividad", back_populates="parcela")
    inventarios = relationship("Inventario", backref="parcela", cascade="all, delete-orphan")
    transacciones = relationship("Transaccion", backref="parcela", cascade="all, delete-orphan")
    presupuestos = relationship("Presupuesto", backref="parcela", cascade="all, delete-orphan")
    indicadores = relationship("Indicador", backref="parcela", cascade="all, delete-orphan")
    parametros_biologicos = relationship("ParametroBiologico", backref="parcela", cascade="all, delete-orphan")



class Actividad(Base):
    __tablename__ = 'actividades'

    id = Column(Integer, primary_key=True)
    tipo = Column(String, nullable=False)  # e.g. "Fertilización", "Cosecha", "Pesaje"
    fecha = Column(Date, nullable=False)
    descripcion = Column(Text)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    parcela_id = Column(Integer, ForeignKey("parcelas.id"))

    usuario = relationship("Usuario", back_populates="actividades")
    parcela = relationship("Parcela", back_populates="actividades")
    detalles = relationship("DetalleActividad", back_populates="actividad", cascade="all, delete-orphan")
    eventos_inventario = relationship("EventoInventario", backref="actividad", cascade="all, delete-orphan")


class DetalleActividad(Base):
    __tablename__ = 'detalle_actividad'

    id = Column(Integer, primary_key=True)
    actividad_id = Column(Integer, ForeignKey("actividades.id"))
    nombre = Column(String, nullable=False)  # e.g. "Fertilizante", "Kg cosechados", "Peso ganado"
    valor = Column(String, nullable=False)   # puede ser número, texto, unidad
    unidad = Column(String, nullable=True)   # e.g. "kg", "l", "m3", "cabezas"

    actividad = relationship("Actividad", back_populates="detalles")


class Ubicacion(Base):
    __tablename__ = 'ubicaciones'

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # "punto" o "poligono"
    coordenadas = Column(Geometry(geometry_type='GEOMETRY', srid=4326))  # PostGIS
    referencia = Column(JSONB, nullable=True)  # info opcional

    terrenos = relationship("Terreno", backref="ubicacion")
    parcelas = relationship("Parcela", backref="ubicacion")
    
# -------------------------
# INVENTARIO Y MOVIMIENTO
# -------------------------

class Inventario(Base):
    __tablename__ = 'inventarios'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    tipo = Column(String, nullable=False)  # ej: "Fertilizante", "Concentrado", "Maquinaria"
    cantidad_actual = Column(Float, nullable=False)
    unidad = Column(String, nullable=False)  # ej: "kg", "l", "unidades"
    parcela_id = Column(Integer, ForeignKey("parcelas.id"), nullable=True)

    movimientos = relationship("EventoInventario", back_populates="inventario")

class EventoInventario(Base):
    __tablename__ = 'eventos_inventario'

    id = Column(Integer, primary_key=True)
    inventario_id = Column(Integer, ForeignKey("inventarios.id"))
    actividad_id = Column(Integer, ForeignKey("actividades.id"), nullable=True)
    tipo_movimiento = Column(String, nullable=False)  # "entrada" o "salida"
    cantidad = Column(Float, nullable=False)
    fecha = Column(Date, nullable=False)
    observacion = Column(Text, nullable=True)

    inventario = relationship("Inventario", back_populates="movimientos")


# -------------------------
# ECONOMÍA Y PRESUPUESTO
# -------------------------

class Transaccion(Base):
    __tablename__ = 'transacciones'

    id = Column(Integer, primary_key=True)
    fecha = Column(Date, nullable=False)
    tipo = Column(String, nullable=False)  # "gasto" o "ingreso"
    categoria = Column(String, nullable=False)  # ej: "compra fertilizante", "venta leche"
    descripcion = Column(Text)
    monto = Column(Float, nullable=False)
    parcela_id = Column(Integer, ForeignKey("parcelas.id"))
    actividad_id = Column(Integer, ForeignKey("actividades.id"), nullable=True)

class Presupuesto(Base):
    __tablename__ = 'presupuestos'

    id = Column(Integer, primary_key=True)
    anio = Column(Integer, nullable=False)
    categoria = Column(String, nullable=False)
    monto_estimado = Column(Float, nullable=False)
    parcela_id = Column(Integer, ForeignKey("parcelas.id"))


# -------------------------
# PARÁMETROS Y SIMULACIONES
# -------------------------

class ParametroBiologico(Base):
    __tablename__ = 'parametros_biologicos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)  # ej: "crecimiento ganado", "ciclo cultivo"
    valor = Column(Float, nullable=False)
    unidad = Column(String, nullable=True)   # ej: "kg/mes", "días"
    descripcion = Column(Text)
    parcela_id = Column(Integer, ForeignKey("parcelas.id"))


class Simulacion(Base):
    __tablename__ = 'simulaciones'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    descripcion = Column(Text)
    fecha_creacion = Column(Date, nullable=False)
    parametros = Column(JSONB, nullable=True)
    resultados = Column(JSONB, nullable=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))


# -------------------------
# TRAZABILIDAD Y KPIs
# -------------------------

class HistorialCambio(Base):
    __tablename__ = 'historial_cambios'

    id = Column(Integer, primary_key=True)
    tabla = Column(String, nullable=False)
    campo = Column(String, nullable=False)
    valor_anterior = Column(String, nullable=True)
    valor_nuevo = Column(String, nullable=True)
    fecha = Column(Date, nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    motivo = Column(Text)

class Indicador(Base):
    __tablename__ = 'indicadores'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    valor = Column(Float, nullable=False)
    unidad = Column(String, nullable=True)
    fecha = Column(Date, nullable=False)
    parcela_id = Column(Integer, ForeignKey("parcelas.id"))
    descripcion = Column(Text)