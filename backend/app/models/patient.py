"""Modelos de Paciente e Regras de Status."""
import uuid
from datetime import datetime, date
from sqlalchemy import String, Text, Date, DateTime, Integer, Boolean, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    date_of_birth: Mapped[date | None] = mapped_column(Date)
    phone: Mapped[str | None] = mapped_column(String(20))
    email: Mapped[str | None] = mapped_column(String(255))
    cpf: Mapped[str | None] = mapped_column(String(14))
    gender: Mapped[str | None] = mapped_column(String(20))
    address: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    last_appointment_date: Mapped[date | None] = mapped_column(Date)  # cache para cálculo de recência
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    clinic = relationship("Clinic", back_populates="patients")
    transactions = relationship("Transaction", back_populates="patient")
    appointments = relationship("Appointment", back_populates="patient")


class PatientStatusRule(Base):
    """
    Regras configuráveis para classificação automática do status do paciente.

    Exemplo:
        Pacientes adultos devem retornar em até 180 dias.
        Após 30 dias de atraso → ATENÇÃO
        Após 60 dias de atraso → PERIGO
    """
    __tablename__ = "patient_status_rules"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    min_age_years: Mapped[int | None] = mapped_column(Integer)   # null = sem mínimo
    max_age_years: Mapped[int | None] = mapped_column(Integer)   # null = sem máximo
    return_interval_days: Mapped[int] = mapped_column(Integer, nullable=False)
    attention_threshold_days: Mapped[int] = mapped_column(Integer, nullable=False)  # dias além do intervalo → ATENÇÃO
    danger_threshold_days: Mapped[int] = mapped_column(Integer, nullable=False)     # dias além do intervalo → PERIGO
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    clinic = relationship("Clinic", back_populates="status_rules")
