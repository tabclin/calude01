"""Modelo de Meta."""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Goal(Base):
    """
    Meta financeira da clínica por período.

    Tipos:
        revenue          → meta de faturamento total
        profit           → meta de lucro
        fixed_expenses   → meta de gastos fixos
        variable_expenses→ meta de gastos variáveis
        product_revenue  → meta de faturamento por produto (requer product_id)
    """
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(50), nullable=False)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.id"))  # apenas para product_revenue
    period_type: Mapped[str] = mapped_column(String(20), default="monthly")    # monthly | annual
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    month: Mapped[int | None] = mapped_column(Integer)  # 1-12; null se anual
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    clinic = relationship("Clinic", back_populates="goals")
    product = relationship("Product", back_populates="goals")
