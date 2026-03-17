from pydantic import BaseModel
from datetime import datetime, date
from typing import Literal


class PatientCreate(BaseModel):
    name: str
    date_of_birth: date | None = None
    phone: str | None = None
    email: str | None = None
    cpf: str | None = None
    gender: str | None = None
    address: str | None = None
    notes: str | None = None


class PatientUpdate(PatientCreate):
    name: str | None = None


class PatientOut(PatientCreate):
    id: str
    clinic_id: str
    last_appointment_date: date | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class PatientWithStatus(PatientOut):
    """PatientOut enriquecido com análise RFM calculada em runtime."""
    age_years: int | None = None
    recency_days: int | None = None           # dias desde a última consulta
    frequency: int = 0                         # total de transações
    monetary: float = 0.0                      # total gasto
    status: Literal["OK", "ATENÇÃO", "PERIGO", "NOVO"] = "NOVO"
    days_overdue: int = 0                      # dias além do intervalo ideal
