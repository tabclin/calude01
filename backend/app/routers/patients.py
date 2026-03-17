"""
Router de Pacientes — Nível 4 (análise da carteira).

Endpoints:
    GET    /patients                → lista com status RFM calculado
    POST   /patients                → cadastra paciente
    GET    /patients/{id}           → detalhe do paciente
    PUT    /patients/{id}           → atualiza paciente
    DELETE /patients/{id}           → remove paciente
    GET    /patients/rules          → lista regras de status
    POST   /patients/rules          → cria regra de status
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.patient import Patient, PatientStatusRule
from app.schemas.patient import PatientCreate, PatientUpdate, PatientOut, PatientWithStatus
from app.services.rfm import get_patients_with_status
import uuid

router = APIRouter()


# ── Pacientes ─────────────────────────────────────────────────────────────────

@router.get("", response_model=list[PatientWithStatus])
def list_patients(
    clinic_id: str,
    status: str | None = Query(default=None, description="Filtrar por: OK | ATENÇÃO | PERIGO | NOVO"),
    db: Session = Depends(get_db),
):
    """Lista todos os pacientes com status RFM calculado automaticamente."""
    return get_patients_with_status(db, clinic_id, status_filter=status)


@router.post("", response_model=PatientOut, status_code=201)
def create_patient(clinic_id: str, payload: PatientCreate, db: Session = Depends(get_db)):
    patient = Patient(id=str(uuid.uuid4()), clinic_id=clinic_id, **payload.model_dump())
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("/{patient_id}", response_model=PatientWithStatus)
def get_patient(patient_id: str, clinic_id: str, db: Session = Depends(get_db)):
    patients = get_patients_with_status(db, clinic_id)
    found = next((p for p in patients if p.id == patient_id), None)
    if not found:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    return found


@router.put("/{patient_id}", response_model=PatientOut)
def update_patient(
    patient_id: str, clinic_id: str, payload: PatientUpdate, db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(
        Patient.id == patient_id, Patient.clinic_id == clinic_id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(patient, field, value)
    db.commit()
    db.refresh(patient)
    return patient


@router.delete("/{patient_id}", status_code=204)
def delete_patient(patient_id: str, clinic_id: str, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(
        Patient.id == patient_id, Patient.clinic_id == clinic_id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado.")
    db.delete(patient)
    db.commit()


# ── Regras de Status ──────────────────────────────────────────────────────────

from pydantic import BaseModel

class StatusRuleCreate(BaseModel):
    name: str
    min_age_years: int | None = None
    max_age_years: int | None = None
    return_interval_days: int
    attention_threshold_days: int
    danger_threshold_days: int
    is_active: bool = True


@router.get("/rules/", response_model=list[dict])
def list_rules(clinic_id: str, db: Session = Depends(get_db)):
    rules = db.query(PatientStatusRule).filter(PatientStatusRule.clinic_id == clinic_id).all()
    return [
        {
            "id": r.id, "name": r.name,
            "min_age_years": r.min_age_years, "max_age_years": r.max_age_years,
            "return_interval_days": r.return_interval_days,
            "attention_threshold_days": r.attention_threshold_days,
            "danger_threshold_days": r.danger_threshold_days,
            "is_active": r.is_active,
        }
        for r in rules
    ]


@router.post("/rules/", status_code=201)
def create_rule(clinic_id: str, payload: StatusRuleCreate, db: Session = Depends(get_db)):
    rule = PatientStatusRule(id=str(uuid.uuid4()), clinic_id=clinic_id, **payload.model_dump())
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return {"id": rule.id, "name": rule.name}
