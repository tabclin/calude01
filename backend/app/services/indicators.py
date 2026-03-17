"""
Serviço de Indicadores Financeiros.

Implementa os cálculos dos Níveis 1, 2 e 3 do sistema de análise gerencial.

Nível 1 → Visão geral (lucro, margens, % de meta)
Nível 2 → Faturamento detalhado + gastos detalhados
Nível 3 → Margem de contribuição
"""
from decimal import Decimal
from datetime import date
from sqlalchemy.orm import Session
from sqlalchemy import func, extract

from app.models.transaction import Transaction, TransactionItem
from app.models.expense import Expense, ExpenseCategory
from app.models.goal import Goal
from app.models.product import Product
from app.schemas.dashboard import (
    Level1Summary, Level2Revenue, Level2Expenses, Level3ContributionMargin,
    ProductRanking, ExpenseCategorySummary, ProductContribution,
)


def _safe_pct(numerator: Decimal, denominator: Decimal) -> float:
    """Retorna (numerator / denominator * 100) ou 0.0 se denominador for zero."""
    if not denominator:
        return 0.0
    return float(numerator / denominator * 100)


def _get_goal(db: Session, clinic_id: str, type_: str, year: int, month: int,
              product_id: str | None = None) -> Decimal:
    """Busca o valor de uma meta; retorna 0 se não cadastrada."""
    q = db.query(Goal).filter(
        Goal.clinic_id == clinic_id,
        Goal.type == type_,
        Goal.year == year,
        Goal.month == month,
    )
    if product_id:
        q = q.filter(Goal.product_id == product_id)
    goal = q.first()
    return goal.amount if goal else Decimal("0")


# ── Nível 1 ───────────────────────────────────────────────────────────────────

def get_level1_summary(db: Session, clinic_id: str, year: int, month: int) -> Level1Summary:
    """
    Retorna o painel principal com faturamento, gastos, lucro e % de metas.

    Fórmulas:
        lucro          = faturamento - gastos
        % meta lucro   = lucro / meta_lucro * 100
        margem lucro % = lucro / faturamento * 100
        % meta receita = faturamento / meta_faturamento * 100
    """
    # Faturamento total do mês (transações completed)
    revenue_row = db.query(func.coalesce(func.sum(Transaction.total_amount), 0)).filter(
        Transaction.clinic_id == clinic_id,
        Transaction.status == "completed",
        extract("year",  Transaction.date) == year,
        extract("month", Transaction.date) == month,
    ).scalar()
    revenue = Decimal(str(revenue_row))

    # Gastos totais do mês
    expenses_row = db.query(func.coalesce(func.sum(Expense.amount), 0)).filter(
        Expense.clinic_id == clinic_id,
        extract("year",  Expense.date) == year,
        extract("month", Expense.date) == month,
    ).scalar()
    expenses = Decimal(str(expenses_row))

    profit = revenue - expenses

    # Metas
    profit_goal  = _get_goal(db, clinic_id, "profit",  year, month)
    revenue_goal = _get_goal(db, clinic_id, "revenue", year, month)

    return Level1Summary(
        revenue=revenue,
        expenses=expenses,
        profit=profit,
        profit_goal=profit_goal,
        profit_goal_pct=_safe_pct(profit, profit_goal),
        profit_margin_pct=_safe_pct(profit, revenue),
        revenue_goal=revenue_goal,
        revenue_goal_pct=_safe_pct(revenue, revenue_goal),
    )


# ── Nível 2-A — Faturamento ───────────────────────────────────────────────────

def get_level2_revenue(db: Session, clinic_id: str, year: int, month: int) -> Level2Revenue:
    """
    Detalhamento do faturamento: total vs meta e ranking de produtos.

    Ranking ordenado por receita decrescente.
    """
    # Total de receita
    revenue_row = db.query(func.coalesce(func.sum(Transaction.total_amount), 0)).filter(
        Transaction.clinic_id == clinic_id,
        Transaction.status == "completed",
        extract("year",  Transaction.date) == year,
        extract("month", Transaction.date) == month,
    ).scalar()
    total_revenue = Decimal(str(revenue_row))

    revenue_goal = _get_goal(db, clinic_id, "revenue", year, month)

    # Receita e quantidade por produto
    rows = (
        db.query(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            func.coalesce(func.sum(TransactionItem.quantity), 0).label("qty"),
            func.coalesce(func.sum(TransactionItem.total_price), 0).label("rev"),
        )
        .join(TransactionItem, TransactionItem.product_id == Product.id)
        .join(Transaction, Transaction.id == TransactionItem.transaction_id)
        .filter(
            Product.clinic_id == clinic_id,
            Transaction.status == "completed",
            extract("year",  Transaction.date) == year,
            extract("month", Transaction.date) == month,
        )
        .group_by(Product.id, Product.name)
        .all()
    )

    # ordena em Python para evitar conflito de aggregate no ORDER BY
    rows = sorted(rows, key=lambda r: r.rev, reverse=True)

    top_products = []
    for r in rows:
        prod_goal = _get_goal(db, clinic_id, "product_revenue", year, month, product_id=r.product_id)
        rev = Decimal(str(r.rev))
        top_products.append(ProductRanking(
            product_id=r.product_id,
            product_name=r.product_name,
            quantity_sold=Decimal(str(r.qty)),
            revenue=rev,
            revenue_goal=prod_goal if prod_goal else None,
            revenue_goal_pct=_safe_pct(rev, prod_goal) if prod_goal else None,
        ))

    return Level2Revenue(
        total_revenue=total_revenue,
        revenue_goal=revenue_goal,
        revenue_goal_pct=_safe_pct(total_revenue, revenue_goal),
        top_products=top_products,
    )


# ── Nível 2-B — Gastos ────────────────────────────────────────────────────────

def get_level2_expenses(db: Session, clinic_id: str, year: int, month: int) -> Level2Expenses:
    """
    Detalhamento de gastos fixos e variáveis vs metas.

    Eficiência para gastos:
        eficiência % = meta / real * 100
        > 100% → gastou menos do que o planejado (bom)
        < 100% → estourou o orçamento (ruim)
    """
    rows = (
        db.query(
            ExpenseCategory.id.label("cat_id"),
            ExpenseCategory.name.label("cat_name"),
            ExpenseCategory.type.label("cat_type"),
            func.coalesce(func.sum(Expense.amount), 0).label("total"),
        )
        .join(Expense, Expense.category_id == ExpenseCategory.id)
        .filter(
            ExpenseCategory.clinic_id == clinic_id,
            extract("year",  Expense.date) == year,
            extract("month", Expense.date) == month,
        )
        .group_by(ExpenseCategory.id, ExpenseCategory.name, ExpenseCategory.type)
        .all()
    )

    fixed_total    = Decimal("0")
    variable_total = Decimal("0")
    by_category    = []

    for r in rows:
        actual = Decimal(str(r.total))
        goal_type = "fixed_expenses" if r.cat_type == "fixed" else "variable_expenses"
        cat_goal = _get_goal(db, clinic_id, goal_type, year, month)

        by_category.append(ExpenseCategorySummary(
            category_id=r.cat_id,
            category_name=r.cat_name,
            type=r.cat_type,
            actual=actual,
            goal=cat_goal if cat_goal else None,
            efficiency_pct=_safe_pct(cat_goal, actual) if cat_goal and actual else None,
        ))

        if r.cat_type == "fixed":
            fixed_total += actual
        else:
            variable_total += actual

    fixed_goal    = _get_goal(db, clinic_id, "fixed_expenses",    year, month)
    variable_goal = _get_goal(db, clinic_id, "variable_expenses", year, month)

    return Level2Expenses(
        total_expenses=fixed_total + variable_total,
        fixed_expenses=fixed_total,
        variable_expenses=variable_total,
        fixed_goal=fixed_goal,
        variable_goal=variable_goal,
        fixed_efficiency_pct=_safe_pct(fixed_goal, fixed_total) if fixed_total else None,
        variable_efficiency_pct=_safe_pct(variable_goal, variable_total) if variable_total else None,
        by_category=by_category,
    )


# ── Nível 3 — Margem de Contribuição ─────────────────────────────────────────

def get_level3_contribution_margin(
    db: Session, clinic_id: str, year: int, month: int
) -> Level3ContributionMargin:
    """
    Calcula a margem de contribuição da clínica e por produto.

    MC = Faturamento - Custos Variáveis (TransactionItem.variable_cost * qty)
    MC% = MC / Faturamento * 100
    """
    rows = (
        db.query(
            Product.id.label("product_id"),
            Product.name.label("product_name"),
            func.coalesce(func.sum(TransactionItem.total_price), 0).label("revenue"),
            func.coalesce(
                func.sum(TransactionItem.variable_cost * TransactionItem.quantity), 0
            ).label("var_cost"),
        )
        .join(TransactionItem, TransactionItem.product_id == Product.id)
        .join(Transaction, Transaction.id == TransactionItem.transaction_id)
        .filter(
            Product.clinic_id == clinic_id,
            Transaction.status == "completed",
            extract("year",  Transaction.date) == year,
            extract("month", Transaction.date) == month,
        )
        .group_by(Product.id, Product.name)
        .all()
    )

    total_revenue   = Decimal("0")
    total_var_cost  = Decimal("0")
    by_product      = []

    for r in rows:
        rev = Decimal(str(r.revenue))
        vc  = Decimal(str(r.var_cost))
        mc  = rev - vc
        total_revenue  += rev
        total_var_cost += vc

        by_product.append(ProductContribution(
            product_id=r.product_id,
            product_name=r.product_name,
            revenue=rev,
            variable_cost=vc,
            contribution_margin=mc,
            contribution_margin_pct=_safe_pct(mc, rev),
        ))

    # ordena do maior para o menor MC
    by_product.sort(key=lambda x: x.contribution_margin, reverse=True)

    total_mc = total_revenue - total_var_cost

    return Level3ContributionMargin(
        revenue=total_revenue,
        total_variable_cost=total_var_cost,
        contribution_margin=total_mc,
        contribution_margin_pct=_safe_pct(total_mc, total_revenue),
        by_product=by_product,
    )
