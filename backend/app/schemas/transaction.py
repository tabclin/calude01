from pydantic import BaseModel, model_validator
from decimal import Decimal
from datetime import datetime, date


class TransactionItemCreate(BaseModel):
    product_id: str | None = None
    quantity: Decimal = Decimal("1")
    unit_price: Decimal
    discount: Decimal = Decimal("0")
    variable_cost: Decimal = Decimal("0")

    @model_validator(mode="after")
    def compute_total(self):
        self.total_price = (self.unit_price * self.quantity) - self.discount
        return self

    total_price: Decimal = Decimal("0")


class TransactionItemOut(TransactionItemCreate):
    id: str
    transaction_id: str

    model_config = {"from_attributes": True}


class TransactionCreate(BaseModel):
    patient_id: str | None = None
    date: date
    payment_method: str | None = None
    status: str = "completed"
    notes: str | None = None
    items: list[TransactionItemCreate]


class TransactionOut(BaseModel):
    id: str
    clinic_id: str
    patient_id: str | None
    date: date
    total_amount: Decimal
    payment_method: str | None
    status: str
    notes: str | None
    items: list[TransactionItemOut]
    created_at: datetime

    model_config = {"from_attributes": True}
