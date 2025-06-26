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

    model_config = {"from_attributes": True}



# ---------- UBICACION ----------

class UbicacionBase(BaseModel):
    tipo: str  # "punto" o "poligono"
    coordenadas: dict  # GeoJSON crudo o usar Point/Polygon si se quiere más rigidez
    referencia: Optional[dict] = None

class UbicacionCreate(UbicacionBase):
    pass

class UbicacionOut(UbicacionBase):
    id: int

    model_config = {"from_attributes": True}



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

    model_config = {"from_attributes": True}



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

    model_config = {"from_attributes": True}



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

    model_config = {"from_attributes": True}


# ---------- DETALLE ACTIVIDAD ----------

class DetalleActividadCreate(BaseModel):
    actividad_id: int
    nombre: str
    valor: str
    unidad: Optional[str] = None

class DetalleActividadOut(DetalleActividadCreate):
    id: int

    model_config = {"from_attributes": True}


# ---------- CHAT ----------

class ChatRequest(BaseModel):
    prompt: str


# ---------- INVENTARIO Y EVENTO INVENTARIO ----------

class InventarioBase(BaseModel):
    nombre: str
    tipo: str
    cantidad_actual: float
    unidad: str
    parcela_id: Optional[int] = None

class InventarioCreate(InventarioBase):
    pass

class InventarioOut(InventarioBase):
    id: int
    model_config = {"from_attributes": True}


class EventoInventarioBase(BaseModel):
    inventario_id: int
    actividad_id: Optional[int] = None
    tipo_movimiento: str  # entrada / salida
    cantidad: float
    fecha: date
    observacion: Optional[str] = None

class EventoInventarioCreate(EventoInventarioBase):
    pass

class EventoInventarioOut(EventoInventarioBase):
    id: int
    model_config = {"from_attributes": True}



# ---------- TRANSACCIÓN Y PRESUPUESTO ----------

class TransaccionBase(BaseModel):
    fecha: date
    tipo: str  # ingreso / gasto
    categoria: str
    descripcion: Optional[str]
    monto: float
    parcela_id: int
    actividad_id: Optional[int] = None

class TransaccionCreate(TransaccionBase):
    pass

class TransaccionOut(TransaccionBase):
    id: int
    model_config = {"from_attributes": True}


class PresupuestoBase(BaseModel):
    anio: int
    categoria: str
    monto_estimado: float
    parcela_id: int

class PresupuestoCreate(PresupuestoBase):
    pass

class PresupuestoOut(PresupuestoBase):
    id: int
    model_config = {"from_attributes": True}



# ---------- PARÁMETROS BIOLÓGICOS Y SIMULACIÓN ----------

class ParametroBiologicoBase(BaseModel):
    nombre: str
    valor: float
    unidad: Optional[str] = None
    descripcion: Optional[str] = None
    parcela_id: int

class ParametroBiologicoCreate(ParametroBiologicoBase):
    pass

class ParametroBiologicoOut(ParametroBiologicoBase):
    id: int
    model_config = {"from_attributes": True}


class SimulacionBase(BaseModel):
    nombre: str
    descripcion: Optional[str]
    fecha_creacion: date
    parametros: Optional[Dict[str, Any]] = None
    resultados: Optional[Dict[str, Any]] = None
    usuario_id: int

class SimulacionCreate(SimulacionBase):
    pass

class SimulacionOut(SimulacionBase):
    id: int
    model_config = {"from_attributes": True}



# ---------- HISTORIAL CAMBIOS Y KPI ----------

class HistorialCambioBase(BaseModel):
    tabla: str
    campo: str
    valor_anterior: Optional[str]
    valor_nuevo: Optional[str]
    fecha: date
    usuario_id: int
    motivo: Optional[str] = None

class HistorialCambioCreate(HistorialCambioBase):
    pass

class HistorialCambioOut(HistorialCambioBase):
    id: int
    model_config = {"from_attributes": True}


class IndicadorBase(BaseModel):
    nombre: str
    valor: float
    unidad: Optional[str] = None
    fecha: date
    parcela_id: int
    descripcion: Optional[str] = None

class IndicadorCreate(IndicadorBase):
    pass

class IndicadorOut(IndicadorBase):
    id: int
    model_config = {"from_attributes": True}



