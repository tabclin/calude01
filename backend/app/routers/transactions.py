"""Router de Transações (faturamento)."""
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date
import uuid

from app.database import get_db
from app.models.transaction import Transaction, TransactionItem
from app.models.patient import Patient
from app.schemas.transaction import TransactionCreate, TransactionOut

router = APIRouter()


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    clinic_id: str,
    start_date: date | None = Query(default=None),
    end_date:   date | None = Query(default=None),
    patient_id: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    q = db.query(Transaction).filter(Transaction.clinic_id == clinic_id)
    if start_date:
        q = q.filter(Transaction.date >= start_date)
    if end_date:
        q = q.filter(Transaction.date <= end_date)
    if patient_id:
        q = q.filter(Transaction.patient_id == patient_id)
    return q.order_by(Transaction.date.desc()).all()


@router.post("", response_model=TransactionOut, status_code=201)
def create_transaction(
    clinic_id: str, payload: TransactionCreate, db: Session = Depends(get_db)
):
    total = sum(
        (item.unit_price * item.quantity) - item.discount
        for item in payload.items
    )

    tx = Transaction(
        id=str(uuid.uuid4()),
        clinic_id=clinic_id,
        patient_id=payload.patient_id,
        date=payload.date,
        total_amount=total,
        payment_method=payload.payment_method,
        status=payload.status,
        notes=payload.notes,
    )
    db.add(tx)

    for item_data in payload.items:
        item_total = (item_data.unit_price * item_data.quantity) - item_data.discount
        item = TransactionItem(
            id=str(uuid.uuid4()),
            transaction_id=tx.id,
            product_id=item_data.product_id,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            discount=item_data.discount,
            total_price=item_total,
            variable_cost=item_data.variable_cost,
        )
        db.add(item)

    # Atualiza última consulta do paciente
    if payload.patient_id:
        patient = db.query(Patient).filter(Patient.id == payload.patient_id).first()
        if patient and (not patient.last_appointment_date or payload.date > patient.last_appointment_date):
            patient.last_appointment_date = payload.date

    db.commit()
    db.refresh(tx)
    return tx


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(transaction_id: str, clinic_id: str, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(
        Transaction.id == transaction_id, Transaction.clinic_id == clinic_id
    ).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transação não encontrada.")
    return tx


@router.delete("/{transaction_id}", status_code=204)
def cancel_transaction(transaction_id: str, clinic_id: str, db: Session = Depends(get_db)):
    tx = db.query(Transaction).filter(
        Transaction.id == transaction_id, Transaction.clinic_id == clinic_id
    ).first()
    if not tx:
        raise HTTPException(status_code=404, detail="Transação não encontrada.")
    tx.status = "cancelled"
    db.commit()
