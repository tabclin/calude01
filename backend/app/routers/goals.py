"""Router de Metas."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models.goal import Goal
from app.schemas.goal import GoalCreate, GoalOut

router = APIRouter()


@router.get("", response_model=list[GoalOut])
def list_goals(
    clinic_id: str,
    year:  int | None = Query(default=None),
    month: int | None = Query(default=None),
    type_: str | None = Query(default=None, alias="type"),
    db: Session = Depends(get_db),
):
    q = db.query(Goal).filter(Goal.clinic_id == clinic_id)
    if year:
        q = q.filter(Goal.year == year)
    if month:
        q = q.filter(Goal.month == month)
    if type_:
        q = q.filter(Goal.type == type_)
    return q.all()


@router.post("", response_model=GoalOut, status_code=201)
def create_goal(clinic_id: str, payload: GoalCreate, db: Session = Depends(get_db)):
    # Evita duplicidade: uma meta por tipo/produto/mês
    existing = db.query(Goal).filter(
        Goal.clinic_id == clinic_id,
        Goal.type == payload.type,
        Goal.year == payload.year,
        Goal.month == payload.month,
        Goal.product_id == payload.product_id,
    ).first()
    if existing:
        raise HTTPException(status_code=409, detail="Já existe uma meta para este período e tipo.")

    goal = Goal(id=str(uuid.uuid4()), clinic_id=clinic_id, **payload.model_dump())
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.put("/{goal_id}", response_model=GoalOut)
def update_goal(goal_id: str, clinic_id: str, payload: GoalCreate, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.clinic_id == clinic_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(goal, field, value)
    db.commit()
    db.refresh(goal)
    return goal


@router.delete("/{goal_id}", status_code=204)
def delete_goal(goal_id: str, clinic_id: str, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.clinic_id == clinic_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Meta não encontrada.")
    db.delete(goal)
    db.commit()
