"""
Serviço de Análise RFM Adaptada — Nível 4.

Classifica automaticamente o status de cada paciente em:
    OK       → dentro do intervalo ideal de retorno
    ATENÇÃO  → ultrapassou o intervalo ideal mas ainda não atingiu o limiar de perigo
    PERIGO   → muito tempo sem retornar
    NOVO     → nunca consultou (sem data de última consulta)

As regras são configuráveis por clínica via tabela PatientStatusRule.
"""
from datetime import date, datetime
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.patient import Patient, PatientStatusRule
from app.models.transaction import Transaction
from app.schemas.patient import PatientWithStatus


def _calculate_age(dob: date | None) -> int | None:
    """Retorna a idade em anos ou None se data de nascimento não informada."""
    if not dob:
        return None
    today = date.today()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))


def _get_applicable_rule(
    rules: list[PatientStatusRule], age_years: int | None
) -> PatientStatusRule | None:
    """
    Encontra a regra mais específica para a faixa etária do paciente.
    Retorna None se nenhuma regra se aplicar.
    """
    best: PatientStatusRule | None = None
    for rule in rules:
        if not rule.is_active:
            continue
        age_min = rule.min_age_years if rule.min_age_years is not None else -1
        age_max = rule.max_age_years if rule.max_age_years is not None else 999

        if age_years is None:
            # sem idade: usa a regra sem restrição de faixa
            if rule.min_age_years is None and rule.max_age_years is None:
                best = rule
        elif age_min <= age_years <= age_max:
            # prioriza regras mais restritas (faixa menor)
            if best is None:
                best = rule
            else:
                current_span = (
                    (best.max_age_years or 999) - (best.min_age_years or 0)
                )
                new_span = age_max - age_min
                if new_span < current_span:
                    best = rule
    return best


def _classify_status(
    recency_days: int | None,
    rule: PatientStatusRule | None,
) -> tuple[str, int]:
    """
    Retorna (status, days_overdue).

    days_overdue = dias além do intervalo ideal (negativo = ainda dentro do prazo).
    """
    if recency_days is None:
        return "NOVO", 0
    if rule is None:
        return "OK", 0

    overdue = recency_days - rule.return_interval_days

    if overdue <= 0:
        return "OK", 0
    elif overdue <= rule.attention_threshold_days:
        return "ATENÇÃO", overdue
    else:
        return "PERIGO", overdue


def get_patients_with_status(
    db: Session,
    clinic_id: str,
    status_filter: str | None = None,
) -> list[PatientWithStatus]:
    """
    Retorna todos os pacientes da clínica com status calculado e dados RFM.

    Args:
        db: Sessão do banco.
        clinic_id: ID da clínica.
        status_filter: Filtra por "OK" | "ATENÇÃO" | "PERIGO" | "NOVO" (opcional).
    """
    today = date.today()
    rules = db.query(PatientStatusRule).filter(
        PatientStatusRule.clinic_id == clinic_id,
        PatientStatusRule.is_active == True,
    ).all()

    patients = db.query(Patient).filter(Patient.clinic_id == clinic_id).all()

    # Frequência e valor monetário por paciente (RFM)
    rfm_rows = (
        db.query(
            Transaction.patient_id,
            func.count(Transaction.id).label("freq"),
            func.coalesce(func.sum(Transaction.total_amount), 0).label("monetary"),
        )
        .filter(
            Transaction.clinic_id == clinic_id,
            Transaction.status == "completed",
            Transaction.patient_id != None,
        )
        .group_by(Transaction.patient_id)
        .all()
    )
    rfm_map = {r.patient_id: (r.freq, float(r.monetary)) for r in rfm_rows}

    result = []
    for p in patients:
        age = _calculate_age(p.date_of_birth)

        # Recência: dias desde a última consulta
        recency_days: int | None = None
        if p.last_appointment_date:
            recency_days = (today - p.last_appointment_date).days

        rule = _get_applicable_rule(rules, age)
        status, days_overdue = _classify_status(recency_days, rule)

        if status_filter and status != status_filter:
            continue

        freq, monetary = rfm_map.get(p.id, (0, 0.0))

        result.append(PatientWithStatus(
            id=p.id,
            clinic_id=p.clinic_id,
            name=p.name,
            date_of_birth=p.date_of_birth,
            phone=p.phone,
            email=p.email,
            cpf=p.cpf,
            gender=p.gender,
            address=p.address,
            notes=p.notes,
            last_appointment_date=p.last_appointment_date,
            created_at=p.created_at,
            age_years=age,
            recency_days=recency_days,
            frequency=freq,
            monetary=monetary,
            status=status,
            days_overdue=days_overdue,
        ))

    # Ordena: PERIGO → ATENÇÃO → OK → NOVO
    priority = {"PERIGO": 0, "ATENÇÃO": 1, "OK": 2, "NOVO": 3}
    result.sort(key=lambda x: (priority.get(x.status, 4), -(x.days_overdue or 0)))
    return result
