from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime, date
from typing import Literal


class ExpenseCategoryCreate(BaseModel):
    name: str
    type: Literal["fixed", "variable"]
    description: str | None = None
    is_active: bool = True


class ExpenseCategoryOut(ExpenseCategoryCreate):
    id: str
    clinic_id: str

    model_config = {"from_attributes": True}


class ExpenseCreate(BaseModel):
    category_id: str | None = None
    description: str | None = None
    amount: Decimal
    date: date
    payment_method: str | None = None
    status: str = "paid"
    recurrent: bool = False
    notes: str | None = None


class ExpenseOut(ExpenseCreate):
    id: str
    clinic_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
