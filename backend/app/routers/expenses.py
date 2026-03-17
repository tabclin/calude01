"""Router de Gastos e Categorias."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
import uuid

from app.database import get_db
from app.models.expense import Expense, ExpenseCategory
from app.schemas.expense import (
    ExpenseCategoryCreate, ExpenseCategoryOut,
    ExpenseCreate, ExpenseOut,
)

router = APIRouter()


# ── Categorias ────────────────────────────────────────────────────────────────

@router.get("/categories", response_model=list[ExpenseCategoryOut])
def list_categories(clinic_id: str, db: Session = Depends(get_db)):
    return db.query(ExpenseCategory).filter(
        ExpenseCategory.clinic_id == clinic_id,
        ExpenseCategory.is_active == True,
    ).order_by(ExpenseCategory.type, ExpenseCategory.name).all()


@router.post("/categories", response_model=ExpenseCategoryOut, status_code=201)
def create_category(clinic_id: str, payload: ExpenseCategoryCreate, db: Session = Depends(get_db)):
    cat = ExpenseCategory(id=str(uuid.uuid4()), clinic_id=clinic_id, **payload.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


# ── Gastos ────────────────────────────────────────────────────────────────────

@router.get("", response_model=list[ExpenseOut])
def list_expenses(
    clinic_id: str,
    start_date: date | None = Query(default=None),
    end_date:   date | None = Query(default=None),
    category_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    q = db.query(Expense).filter(Expense.clinic_id == clinic_id)
    if start_date:
        q = q.filter(Expense.date >= start_date)
    if end_date:
        q = q.filter(Expense.date <= end_date)
    if category_id:
        q = q.filter(Expense.category_id == category_id)
    return q.order_by(Expense.date.desc()).all()


@router.post("", response_model=ExpenseOut, status_code=201)
def create_expense(clinic_id: str, payload: ExpenseCreate, db: Session = Depends(get_db)):
    expense = Expense(id=str(uuid.uuid4()), clinic_id=clinic_id, **payload.model_dump())
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.put("/{expense_id}", response_model=ExpenseOut)
def update_expense(
    expense_id: str, clinic_id: str, payload: ExpenseCreate, db: Session = Depends(get_db)
):
    expense = db.query(Expense).filter(
        Expense.id == expense_id, Expense.clinic_id == clinic_id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto não encontrado.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(expense, field, value)
    db.commit()
    db.refresh(expense)
    return expense


@router.delete("/{expense_id}", status_code=204)
def delete_expense(expense_id: str, clinic_id: str, db: Session = Depends(get_db)):
    expense = db.query(Expense).filter(
        Expense.id == expense_id, Expense.clinic_id == clinic_id
    ).first()
    if not expense:
        raise HTTPException(status_code=404, detail="Gasto não encontrado.")
    db.delete(expense)
    db.commit()
