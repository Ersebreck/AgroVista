from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.db import get_db

router = APIRouter(prefix="/economy", tags=["Economy"])


# ----- TRANSACTIONS -----


@router.post("/transaction/", response_model=schemas.TransactionOut)
def create_transaction(
    transaction: schemas.TransactionCreate, db: Session = Depends(get_db)
) -> models.Transaction:
    """Create a new financial transaction."""
    db_transaction = models.Transaction(**transaction.model_dump())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.get("/transaction/{id}", response_model=schemas.TransactionOut)
def get_transaction(id: int, db: Session = Depends(get_db)) -> models.Transaction:
    """Get a transaction by ID."""
    db_transaction = (
        db.query(models.Transaction).filter(models.Transaction.id == id).first()
    )
    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return db_transaction


@router.get("/transactions/", response_model=List[schemas.TransactionOut])
def list_transactions(db: Session = Depends(get_db)) -> List[models.Transaction]:
    """List all transactions."""
    return db.query(models.Transaction).all()


# ----- BUDGETS -----


@router.post("/budget/", response_model=schemas.BudgetOut)
def create_budget(
    budget: schemas.BudgetCreate, db: Session = Depends(get_db)
) -> models.Budget:
    """Create a new budget."""
    db_budget = models.Budget(**budget.model_dump())
    db.add(db_budget)
    db.commit()
    db.refresh(db_budget)
    return db_budget


@router.get("/budget/{id}", response_model=schemas.BudgetOut)
def get_budget(id: int, db: Session = Depends(get_db)) -> models.Budget:
    """Get a budget by ID."""
    db_budget = db.query(models.Budget).filter(models.Budget.id == id).first()
    if not db_budget:
        raise HTTPException(status_code=404, detail="Budget not found")
    return db_budget


@router.get("/budgets/", response_model=List[schemas.BudgetOut])
def list_budgets(db: Session = Depends(get_db)) -> List[models.Budget]:
    """List all budgets."""
    return db.query(models.Budget).all()


@router.get("/comparison/")
def budget_vs_actual_comparison(
    year: int = Query(..., description="Analysis year"),
    parcel_id: int = Query(None, description="Filter by parcel"),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Compare budgeted vs actual expenses by category."""
    # BUDGET grouped by category
    budget_query = db.query(
        models.Budget.category,
        func.sum(models.Budget.estimated_amount).label("budgeted_amount"),
    ).filter(models.Budget.year == year)

    if parcel_id:
        budget_query = budget_query.filter(models.Budget.parcel_id == parcel_id)

    budget_data = {
        row.category: row.budgeted_amount
        for row in budget_query.group_by(models.Budget.category).all()
    }

    # TRANSACTIONS grouped by category
    transaction_query = db.query(
        models.Transaction.category,
        func.sum(models.Transaction.amount).label("executed_amount"),
    ).filter(
        func.extract("year", models.Transaction.date) == year,
        models.Transaction.type == "expense",
    )

    if parcel_id:
        transaction_query = transaction_query.filter(
            models.Transaction.parcel_id == parcel_id
        )

    transaction_data = {
        row.category: row.executed_amount
        for row in transaction_query.group_by(models.Transaction.category).all()
    }

    # Merge results
    categories = set(budget_data.keys()).union(transaction_data.keys())
    result = []
    for category in categories:
        planned = budget_data.get(category, 0.0)
        actual = transaction_data.get(category, 0.0)
        difference = planned - actual
        alert = abs(difference) > (0.15 * planned) if planned > 0 else False

        result.append(
            {
                "category": category,
                "budgeted_amount": round(planned, 2),
                "executed_amount": round(actual, 2),
                "difference": round(difference, 2),
                "alert": alert,
            }
        )

    return result


@router.get("/global-summary/")
def global_economic_summary(
    year: int = Query(..., description="Analysis year"),
    parcel_id: int = Query(None, description="Filter by parcel"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get global economic summary with totals and alerts."""
    budget_query = db.query(func.sum(models.Budget.estimated_amount)).filter(
        models.Budget.year == year
    )
    transaction_query = db.query(func.sum(models.Transaction.amount)).filter(
        func.extract("year", models.Transaction.date) == year,
        models.Transaction.type == "expense",
    )

    if parcel_id:
        budget_query = budget_query.filter(models.Budget.parcel_id == parcel_id)
        transaction_query = transaction_query.filter(
            models.Transaction.parcel_id == parcel_id
        )

    budget_total = budget_query.scalar() or 0.0
    executed_total = transaction_query.scalar() or 0.0
    difference = budget_total - executed_total
    global_alert = (
        abs(difference) > (0.15 * budget_total) if budget_total > 0 else False
    )

    return {
        "budget_total": round(budget_total, 2),
        "executed_total": round(executed_total, 2),
        "difference_total": round(difference, 2),
        "global_alert": global_alert,
    }


@router.get("/monthly-comparison/")
def monthly_comparison(
    year: int = Query(...),
    category: str = Query(None),
    parcel_id: int = Query(None),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Get monthly expense comparison."""
    query = db.query(
        func.extract("month", models.Transaction.date).label("month"),
        func.sum(models.Transaction.amount).label("executed_amount"),
    ).filter(
        func.extract("year", models.Transaction.date) == year,
        models.Transaction.type == "expense",
    )

    if category:
        query = query.filter(models.Transaction.category == category)
    if parcel_id:
        query = query.filter(models.Transaction.parcel_id == parcel_id)

    query = query.group_by(func.extract("month", models.Transaction.date)).order_by(
        "month"
    )

    return [
        {"month": int(row.month), "executed_amount": round(row.executed_amount, 2)}
        for row in query.all()
    ]


# ----------------------
# LEGACY ENDPOINTS (Spanish names for backwards compatibility)
# ----------------------


# Transaction legacy endpoints
@router.post("/transaccion/", response_model=schemas.TransactionOut)
def crear_transaccion(
    transaccion: schemas.TransactionCreate, db: Session = Depends(get_db)
) -> models.Transaction:
    """Legacy: Create transaction (Spanish name)."""
    return create_transaction(transaccion, db)


@router.get("/transaccion/{id}", response_model=schemas.TransactionOut)
def obtener_transaccion(id: int, db: Session = Depends(get_db)) -> models.Transaction:
    """Legacy: Get transaction (Spanish name)."""
    return get_transaction(id, db)


@router.get("/transacciones/", response_model=List[schemas.TransactionOut])
def listar_transacciones(db: Session = Depends(get_db)) -> List[models.Transaction]:
    """Legacy: List transactions (Spanish name)."""
    return list_transactions(db)


# Budget legacy endpoints
@router.post("/presupuesto/", response_model=schemas.BudgetOut)
def crear_presupuesto(
    presupuesto: schemas.BudgetCreate, db: Session = Depends(get_db)
) -> models.Budget:
    """Legacy: Create budget (Spanish name)."""
    return create_budget(presupuesto, db)


@router.get("/presupuesto/{id}", response_model=schemas.BudgetOut)
def obtener_presupuesto(id: int, db: Session = Depends(get_db)) -> models.Budget:
    """Legacy: Get budget (Spanish name)."""
    return get_budget(id, db)


@router.get("/presupuestos/", response_model=List[schemas.BudgetOut])
def listar_presupuestos(db: Session = Depends(get_db)) -> List[models.Budget]:
    """Legacy: List budgets (Spanish name)."""
    return list_budgets(db)


# Analysis legacy endpoints
@router.get("/comparativo/")
def comparativo_presupuesto_vs_real(
    anio: int = Query(..., description="Analysis year"),
    parcela_id: int = Query(None, description="Filter by parcel"),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Legacy: Budget vs actual comparison (Spanish name)."""
    return budget_vs_actual_comparison(anio, parcela_id, db)


@router.get("/resumen-global/")
def resumen_economico_global(
    anio: int = Query(..., description="Analysis year"),
    parcela_id: int = Query(None, description="Filter by parcel"),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Legacy: Global economic summary (Spanish name)."""
    return global_economic_summary(anio, parcela_id, db)


@router.get("/comparativo-mensual/")
def comparativo_mensual(
    anio: int = Query(...),
    categoria: str = Query(None),
    parcela_id: int = Query(None),
    db: Session = Depends(get_db),
) -> List[Dict[str, Any]]:
    """Legacy: Monthly comparison (Spanish name)."""
    return monthly_comparison(anio, categoria, parcela_id, db)
