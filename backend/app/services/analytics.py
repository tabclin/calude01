"""
Serviço de Analytics — consultas históricas e comparativos.

Fornece dados para gráficos de evolução temporal e comparação entre períodos.
"""
from decimal import Decimal
from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from pydantic import BaseModel

from app.models.transaction import Transaction
from app.models.expense import Expense


class MonthlyTrend(BaseModel):
    year: int
    month: int
    revenue: Decimal
    expenses: Decimal
    profit: Decimal


class MonthlyProductRevenue(BaseModel):
    year: int
    month: int
    product_id: str
    product_name: str
    revenue: Decimal


def get_monthly_trend(
    db: Session,
    clinic_id: str,
    months: int = 12,
) -> list[MonthlyTrend]:
    """
    Retorna a evolução mensal de receita, gastos e lucro nos últimos N meses.
    Útil para o gráfico de linha no dashboard.
    """
    rev_rows = (
        db.query(
            extract("year",  Transaction.date).label("yr"),
            extract("month", Transaction.date).label("mo"),
            func.coalesce(func.sum(Transaction.total_amount), 0).label("rev"),
        )
        .filter(
            Transaction.clinic_id == clinic_id,
            Transaction.status == "completed",
        )
        .group_by("yr", "mo")
        .order_by("yr", "mo")
        .all()
    )

    exp_rows = (
        db.query(
            extract("year",  Expense.date).label("yr"),
            extract("month", Expense.date).label("mo"),
            func.coalesce(func.sum(Expense.amount), 0).label("exp"),
        )
        .filter(Expense.clinic_id == clinic_id)
        .group_by("yr", "mo")
        .order_by("yr", "mo")
        .all()
    )

    exp_map = {(int(r.yr), int(r.mo)): Decimal(str(r.exp)) for r in exp_rows}

    trend = []
    for r in rev_rows[-months:]:
        yr, mo = int(r.yr), int(r.mo)
        rev = Decimal(str(r.rev))
        exp = exp_map.get((yr, mo), Decimal("0"))
        trend.append(MonthlyTrend(
            year=yr,
            month=mo,
            revenue=rev,
            expenses=exp,
            profit=rev - exp,
        ))

    return trend
