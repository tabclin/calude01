"""Modelo de Agendamento/Consulta."""
import uuid
from datetime import datetime
from sqlalchemy import String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Appointment(Base):
    __tablename__ = "appointments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clinic_id: Mapped[str] = mapped_column(ForeignKey("clinics.id"), nullable=False)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"), nullable=False)
    product_id: Mapped[str | None] = mapped_column(ForeignKey("products.id"))
    scheduled_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="scheduled")  # scheduled | completed | cancelled | no_show
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    clinic = relationship("Clinic", back_populates="appointments")
    patient = relationship("Patient", back_populates="appointments")
    product = relationship("Product", back_populates="appointments")
