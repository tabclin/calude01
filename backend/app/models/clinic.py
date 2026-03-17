"""Modelos de Clínica e Usuário."""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Clinic(Base):
    __tablename__ = "clinics"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    cnpj: Mapped[str | None] = mapped_column(String(20))
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    address: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relacionamentos
    patients = relationship("Patient", back_populates="clinic", cascade="all, delete-orphan")
    products = relationship("Product", back_populates="clinic", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="clinic", cascade="all, delete-orphan")
    expense_categories = relationship("ExpenseCategory", back_populates="clinic", cascade="all, delete-orphan")
    expenses = relationship("Expense", back_populates="clinic", cascade="all, delete-orphan")
    goals = relationship("Goal", back_populates="clinic", cascade="all, delete-orphan")
    appointments = relationship("Appointment", back_populates="clinic", cascade="all, delete-orphan")
    status_rules = relationship("PatientStatusRule", back_populates="clinic", cascade="all, delete-orphan")
    users = relationship("ClinicUser", back_populates="clinic", cascade="all, delete-orphan")


class ClinicUser(Base):
    """Usuários vinculados a uma clínica (integra com Supabase Auth)."""
    __tablename__ = "clinic_users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    role: Mapped[str] = mapped_column(String(20), default="staff")  # admin | manager | staff
    is_active: Mapped[bool] = mapped_column(default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    clinic = relationship("Clinic", back_populates="users")
