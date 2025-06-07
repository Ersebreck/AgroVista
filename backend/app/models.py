from sqlalchemy import Column, Integer, String, ForeignKey, Date, Text
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


class Actividad(Base):
    __tablename__ = 'actividades'

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)
    fecha = Column(Date, nullable=False)
    descripcion = Column(Text)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"))
    parcela_id = Column(Integer, ForeignKey("parcelas.id"))

    usuario = relationship("Usuario", back_populates="actividades")
    parcela = relationship("Parcela", back_populates="actividades")


class Ubicacion(Base):
    __tablename__ = 'ubicaciones'

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # "punto" o "poligono"
    coordenadas = Column(Geometry(geometry_type='GEOMETRY', srid=4326))  # PostGIS
    referencia = Column(JSONB, nullable=True)  # info opcional

    terrenos = relationship("Terreno", backref="ubicacion")
    parcelas = relationship("Parcela", backref="ubicacion")
