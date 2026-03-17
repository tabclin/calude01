"""Modelos de Gasto e Categoria de Gasto."""
import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Text, Date, Numeric, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class ExpenseCategory(Base):
    """
    Categoria de gasto classificada como Fixo ou Variável.

    Exemplos fixos: Aluguel, Folha de pagamento.
    Exemplos variáveis: Comissões, Materiais consumidos.
    """
    __tablename__ = "expense_categories"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # fixed | variable
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    clinic = relationship("Clinic", back_populates="expense_categories")
    expenses = relationship("Expense", back_populates="category")


class Expense(Base):
    """Registro de um gasto/despesa da clínica."""
    __tablename__ = "expenses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), nullable=False)
    category_id: Mapped[str | None] = mapped_column(ForeignKey("expense_categories.id"))
    description: Mapped[str | None] = mapped_column(String(255))
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(20), default="paid")  # pending | paid
    recurrent: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    clinic = relationship("Clinic", back_populates="expenses")
    category = relationship("ExpenseCategory", back_populates="expenses")
