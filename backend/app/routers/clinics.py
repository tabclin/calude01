"""Router de Clínicas."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models.clinic import Clinic
from app.schemas.clinic import ClinicCreate, ClinicOut

router = APIRouter()


@router.get("", response_model=list[ClinicOut])
def list_clinics(db: Session = Depends(get_db)):
    return db.query(Clinic).all()


@router.post("", response_model=ClinicOut, status_code=201)
def create_clinic(payload: ClinicCreate, db: Session = Depends(get_db)):
    clinic = Clinic(id=str(uuid.uuid4()), **payload.model_dump())
    db.add(clinic)
    db.commit()
    db.refresh(clinic)
    return clinic


@router.get("/{clinic_id}", response_model=ClinicOut)
def get_clinic(clinic_id: str, db: Session = Depends(get_db)):
    clinic = db.query(Clinic).filter(Clinic.id == clinic_id).first()
    if not clinic:
        raise HTTPException(status_code=404, detail="Clínica não encontrada.")
    return clinic
