from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime


class ProductCreate(BaseModel):
    name: str
    type: str = "service"  # product | service
    description: str | None = None
    price: Decimal = Decimal("0")
    variable_cost: Decimal = Decimal("0")
    is_active: bool = True


class ProductUpdate(ProductCreate):
    name: str | None = None


class ProductOut(ProductCreate):
    id: str
    clinic_id: str
    created_at: datetime

    model_config = {"from_attributes": True}
