from datetime import date
from typing import Any, Dict, List

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

router = APIRouter(prefix="/simulation", tags=["Simulation"])


# ----- SIMULATIONS -----


@router.post("/", response_model=schemas.SimulationOut)
def create_simulation(
    simulation: schemas.SimulationCreate, db: Session = Depends(get_db)
) -> models.Simulation:
    """Create a new simulation."""
    db_simulation = models.Simulation(**simulation.model_dump())
    db.add(db_simulation)
    db.commit()
    db.refresh(db_simulation)
    return db_simulation


@router.get("/{id}", response_model=schemas.SimulationOut)
def get_simulation(id: int, db: Session = Depends(get_db)) -> models.Simulation:
    """Get a simulation by ID."""
    db_simulation = (
        db.query(models.Simulation).filter(models.Simulation.id == id).first()
    )
    if not db_simulation:
        raise HTTPException(status_code=404, detail="Simulation not found")
    return db_simulation


@router.get("/", response_model=List[schemas.SimulationOut])
def list_simulations(db: Session = Depends(get_db)) -> List[models.Simulation]:
    """List all simulations."""
    return db.query(models.Simulation).all()


# ----- BIOLOGICAL PARAMETERS -----


@router.post("/parameter/", response_model=schemas.BiologicalParameterOut)
def create_biological_parameter(
    parameter: schemas.BiologicalParameterCreate, db: Session = Depends(get_db)
) -> models.BiologicalParameter:
    """Create a new biological parameter."""
    db_parameter = models.BiologicalParameter(**parameter.model_dump())
    db.add(db_parameter)
    db.commit()
    db.refresh(db_parameter)
    return db_parameter


@router.get("/parameter/{id}", response_model=schemas.BiologicalParameterOut)
def get_biological_parameter(
    id: int, db: Session = Depends(get_db)
) -> models.BiologicalParameter:
    """Get a biological parameter by ID."""
    db_parameter = (
        db.query(models.BiologicalParameter)
        .filter(models.BiologicalParameter.id == id)
        .first()
    )
    if not db_parameter:
        raise HTTPException(status_code=404, detail="Biological parameter not found")
    return db_parameter


@router.get("/parameters/", response_model=List[schemas.BiologicalParameterOut])
def list_biological_parameters(
    db: Session = Depends(get_db),
) -> List[models.BiologicalParameter]:
    """List all biological parameters."""
    return db.query(models.BiologicalParameter).all()


def simulate_growth(
    start_year: int, years: int, initial_units: float, rates: Dict[str, float]
) -> Dict[int, float]:
    """Simulate population growth over time based on rates."""
    results = {}
    current = initial_units
    for i in range(years):
        year = start_year + i
        births = current * rates.get("birth_rate", 0)
        sales = current * rates.get("sale_rate", 0)
        deaths = current * rates.get("mortality_rate", 0)
        current = current + births - sales - deaths
        results[year] = round(current, 2)
    return results


@router.post("/simulate")
def simulate_projection(
    payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Run a projection simulation with given parameters."""
    start_year = payload["start_year"]
    years = payload["years"]
    initial_units = payload["initial_units"]
    rates = payload.get("rates", {})
    save = payload.get("save", False)
    name = payload.get("name", f"Simulation {date.today()}")
    user_id = payload.get("user_id", 1)

    results = simulate_growth(start_year, years, initial_units, rates)

    if save:
        simulation = models.Simulation(
            name=name,
            description="Automatic simulation",
            creation_date=date.today(),
            parameters=rates,
            results=results,
            user_id=user_id,
        )
        db.add(simulation)
        db.commit()

    return {"results": results}


# ----------------------
# LEGACY ENDPOINTS (Spanish names for backwards compatibility)
# ----------------------


# Simulation legacy endpoints
@router.post("/simulacion/", response_model=schemas.SimulationOut)
def crear_simulacion(
    simulacion: schemas.SimulationCreate, db: Session = Depends(get_db)
) -> models.Simulation:
    """Legacy: Create simulation (Spanish name)."""
    return create_simulation(simulacion, db)


@router.get("/simulacion/{id}", response_model=schemas.SimulationOut)
def obtener_simulacion(id: int, db: Session = Depends(get_db)) -> models.Simulation:
    """Legacy: Get simulation (Spanish name)."""
    return get_simulation(id, db)


@router.get("/simulaciones/", response_model=List[schemas.SimulationOut])
def listar_simulaciones(db: Session = Depends(get_db)) -> List[models.Simulation]:
    """Legacy: List simulations (Spanish name)."""
    return list_simulations(db)


# Parameter legacy endpoints
@router.post("/parametro/", response_model=schemas.BiologicalParameterOut)
def crear_parametro(
    parametro: schemas.BiologicalParameterCreate, db: Session = Depends(get_db)
) -> models.BiologicalParameter:
    """Legacy: Create biological parameter (Spanish name)."""
    return create_biological_parameter(parametro, db)


@router.get("/parametro/{id}", response_model=schemas.BiologicalParameterOut)
def obtener_parametro(
    id: int, db: Session = Depends(get_db)
) -> models.BiologicalParameter:
    """Legacy: Get biological parameter (Spanish name)."""
    return get_biological_parameter(id, db)


@router.get("/parametros/", response_model=List[schemas.BiologicalParameterOut])
def listar_parametros(
    db: Session = Depends(get_db),
) -> List[models.BiologicalParameter]:
    """Legacy: List biological parameters (Spanish name)."""
    return list_biological_parameters(db)


# Simulation legacy endpoint
@router.post("/simular")
def simular_proyeccion(
    payload: Dict[str, Any] = Body(...), db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """Legacy: Run simulation projection (Spanish name)."""
    # Map Spanish field names to English
    english_payload = {
        "start_year": payload.get("anio_inicio", payload.get("start_year")),
        "years": payload.get("anios", payload.get("years")),
        "initial_units": payload.get("unidad_inicial", payload.get("initial_units")),
        "rates": payload.get("tasas", payload.get("rates", {})),
        "save": payload.get("guardar", payload.get("save", False)),
        "name": payload.get(
            "nombre", payload.get("name", f"Simulation {date.today()}")
        ),
        "user_id": payload.get("usuario_id", payload.get("user_id", 1)),
    }
    return simulate_projection(english_payload, db)
