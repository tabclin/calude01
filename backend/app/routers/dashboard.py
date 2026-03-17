"""
Router do Dashboard — agrega os 3 níveis de análise financeira.

Endpoints:
    GET /dashboard/summary          → Nível 1 (visão geral)
    GET /dashboard/revenue          → Nível 2-A (faturamento)
    GET /dashboard/expenses         → Nível 2-B (gastos)
    GET /dashboard/contribution     → Nível 3 (margem de contribuição)
    GET /dashboard/trend            → Evolução mensal (gráficos)
"""
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import indicators, analytics
from app.schemas.dashboard import (
    Level1Summary, Level2Revenue, Level2Expenses, Level3ContributionMargin,
)

router = APIRouter()


def _current_year_month():
    today = date.today()
    return today.year, today.month


@router.get("/summary", response_model=Level1Summary)
def summary(
    clinic_id: str,
    year:  int = Query(default=None),
    month: int = Query(default=None),
    db: Session = Depends(get_db),
):
    """Nível 1 — Painel principal: receita, gastos, lucro e % das metas."""
    y, m = _current_year_month()
    return indicators.get_level1_summary(db, clinic_id, year or y, month or m)


@router.get("/revenue", response_model=Level2Revenue)
def revenue(
    clinic_id: str,
    year:  int = Query(default=None),
    month: int = Query(default=None),
    db: Session = Depends(get_db),
):
    """Nível 2-A — Faturamento detalhado e ranking de produtos."""
    y, m = _current_year_month()
    return indicators.get_level2_revenue(db, clinic_id, year or y, month or m)


@router.get("/expenses", response_model=Level2Expenses)
def expenses(
    clinic_id: str,
    year:  int = Query(default=None),
    month: int = Query(default=None),
    db: Session = Depends(get_db),
):
    """Nível 2-B — Gastos detalhados por categoria vs metas."""
    y, m = _current_year_month()
    return indicators.get_level2_expenses(db, clinic_id, year or y, month or m)


@router.get("/contribution", response_model=Level3ContributionMargin)
def contribution_margin(
    clinic_id: str,
    year:  int = Query(default=None),
    month: int = Query(default=None),
    db: Session = Depends(get_db),
):
    """Nível 3 — Margem de contribuição da clínica e por produto."""
    y, m = _current_year_month()
    return indicators.get_level3_contribution_margin(db, clinic_id, year or y, month or m)


@router.get("/trend")
def trend(
    clinic_id: str,
    months: int = Query(default=12, ge=1, le=36),
    db: Session = Depends(get_db),
):
    """Evolução mensal dos últimos N meses (para gráficos de linha)."""
    return analytics.get_monthly_trend(db, clinic_id, months)
