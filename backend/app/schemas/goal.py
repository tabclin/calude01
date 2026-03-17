from pydantic import BaseModel, model_validator
from decimal import Decimal
from datetime import datetime
from typing import Literal


GoalType = Literal["revenue", "profit", "fixed_expenses", "variable_expenses", "product_revenue"]


class GoalCreate(BaseModel):
    type: GoalType
    product_id: str | None = None
    period_type: Literal["monthly", "annual"] = "monthly"
    year: int
    month: int | None = None  # obrigatório se period_type == "monthly"
    amount: Decimal

    @model_validator(mode="after")
    def validate_month(self):
        if self.period_type == "monthly" and self.month is None:
            raise ValueError("month é obrigatório para metas mensais.")
        if self.type == "product_revenue" and self.product_id is None:
            raise ValueError("product_id é obrigatório para metas de produto.")
        return self


class GoalOut(GoalCreate):
    id: str
    clinic_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
