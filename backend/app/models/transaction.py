"""Modelos de Transação (vendas/faturamento)."""
import uuid
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Text, Date, Numeric, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Transaction(Base):
    """
    Registro financeiro de uma venda/atendimento.
    Cada transação pode ter múltiplos itens (TransactionItem).
    """
    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), nullable=False)
    patient_id: Mapped[str | None] = mapped_column(ForeignKey("patients.id"))
    date: Mapped[date] = mapped_column(Date, nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[str | None] = mapped_column(String(50))  # dinheiro | cartão | pix | convênio
    status: Mapped[str] = mapped_column(String(20), default="completed")  # pending | completed | cancelled
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    clinic = relationship("Clinic", back_populates="transactions")
    patient = relationship("Patient", back_populates="transactions")
    items = relationship("TransactionItem", back_populates="transaction", cascade="all, delete-orphan")


class TransactionItem(Base):
    """Item de linha dentro de uma transação."""
    __tablename__ = "transaction_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    transaction_id: Mapped[str] = mapped_column(ForeignKey("transactions.id"), nullable=False)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=1)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    discount: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    total_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    variable_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # custo variável no momento da venda
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    transaction = relationship("Transaction", back_populates="items")
    product = relationship("Product", back_populates="transaction_items")
