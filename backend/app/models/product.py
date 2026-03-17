"""Modelo de Produto/Serviço."""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, Text, Numeric, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Product(Base):
    """
    Representa tanto produtos físicos quanto serviços oferecidos pela clínica.
    O campo `variable_cost` é usado no cálculo da margem de contribuição.
    """
    __tablename__ = "products"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type: Mapped[str] = mapped_column(String(20), default="service")  # product | service
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)
    variable_cost: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=0)  # custo variável unitário
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    clinic = relationship("Clinic", back_populates="products")
    transaction_items = relationship("TransactionItem", back_populates="product")
    appointments = relationship("Appointment", back_populates="product")
    goals = relationship("Goal", back_populates="product")
