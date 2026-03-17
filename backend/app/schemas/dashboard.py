"""Schemas de resposta para os endpoints do Dashboard."""
from pydantic import BaseModel
from decimal import Decimal


# ── Nível 1 ───────────────────────────────────────────────────────────────────

class Level1Summary(BaseModel):
    """Visão geral financeira do mês."""
    revenue: Decimal              # faturamento total
    expenses: Decimal             # gastos totais
    profit: Decimal               # lucro real
    profit_goal: Decimal          # meta de lucro
    profit_goal_pct: float        # % da meta de lucro atingida (0-100)
    profit_margin_pct: float      # margem de lucro % (lucro / receita)
    revenue_goal: Decimal         # meta de faturamento
    revenue_goal_pct: float       # % da meta de faturamento atingida


# ── Nível 2 ───────────────────────────────────────────────────────────────────

class ProductRanking(BaseModel):
    product_id: str
    product_name: str
    quantity_sold: Decimal
    revenue: Decimal
    revenue_goal: Decimal | None
    revenue_goal_pct: float | None  # % da meta atingida


class Level2Revenue(BaseModel):
    """Análise detalhada de faturamento."""
    total_revenue: Decimal
    revenue_goal: Decimal
    revenue_goal_pct: float
    top_products: list[ProductRanking]


class ExpenseCategorySummary(BaseModel):
    category_id: str
    category_name: str
    type: str            # fixed | variable
    actual: Decimal
    goal: Decimal | None
    efficiency_pct: float | None  # meta / real * 100


class Level2Expenses(BaseModel):
    """Análise detalhada de gastos."""
    total_expenses: Decimal
    fixed_expenses: Decimal
    variable_expenses: Decimal
    fixed_goal: Decimal
    variable_goal: Decimal
    fixed_efficiency_pct: float | None
    variable_efficiency_pct: float | None
    by_category: list[ExpenseCategorySummary]


# ── Nível 3 ───────────────────────────────────────────────────────────────────

class ProductContribution(BaseModel):
    product_id: str
    product_name: str
    revenue: Decimal
    variable_cost: Decimal
    contribution_margin: Decimal
    contribution_margin_pct: float  # margem / receita


class Level3ContributionMargin(BaseModel):
    """Margem de contribuição da clínica."""
    revenue: Decimal
    total_variable_cost: Decimal
    contribution_margin: Decimal        # receita - custo variável
    contribution_margin_pct: float      # MC / receita
    by_product: list[ProductContribution]
