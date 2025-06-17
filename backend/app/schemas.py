from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date
from geojson_pydantic import Polygon, Point, Feature  # Para GeoJSON en entrada/salida
from typing import Dict, Any


# ---------- USUARIO ----------

class UsuarioBase(BaseModel):
    nombre: str
    correo: EmailStr
    rol: str

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioOut(UsuarioBase):
    id: int

    class Config:
        orm_mode = True


# ---------- UBICACION ----------

class UbicacionBase(BaseModel):
    tipo: str  # "punto" o "poligono"
    coordenadas: dict  # GeoJSON crudo o usar Point/Polygon si se quiere más rigidez
    referencia: Optional[dict] = None

class UbicacionCreate(UbicacionBase):
    pass

class UbicacionOut(UbicacionBase):
    id: int

    class Config:
        orm_mode = True


# ---------- TERRENO ----------

class TerrenoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    propietario_id: int
    ubicacion_id: Optional[int] = None

class TerrenoCreate(TerrenoBase):
    pass

class TerrenoOut(TerrenoBase):
    id: int

    class Config:
        orm_mode = True


# ---------- PARCELA ----------

class ParcelaBase(BaseModel):
    nombre: str
    uso_actual: Optional[str] = None
    estado: Optional[str] = None
    terreno_id: int
    ubicacion_id: Optional[int] = None

class ParcelaCreate(ParcelaBase):
    pass

class ParcelaOut(ParcelaBase):
    id: int

    class Config:
        orm_mode = True


# ---------- ACTIVIDAD ----------

class ActividadBase(BaseModel):
    tipo: str
    fecha: date
    descripcion: Optional[str] = None
    usuario_id: int
    parcela_id: int

class ActividadCreate(ActividadBase):
    pass

class ActividadOut(ActividadBase):
    id: int

    class Config:
        orm_mode = True

# ---------- DETALLE ACTIVIDAD ----------

class DetalleActividadCreate(BaseModel):
    actividad_id: int
    nombre: str
    valor: str
    unidad: Optional[str] = None

class DetalleActividadOut(DetalleActividadCreate):
    id: int

    class Config:
        orm_mode = True

# ---------- CHAT ----------

class ChatRequest(BaseModel):
    prompt: str
    actividades: List[Dict[str, Any]]
    detalles: List[Dict[str, Any]]
    estado_parcelas: Dict[str, List[str]]  # o Dict[str, Any] si es más general

