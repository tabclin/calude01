from pydantic import BaseModel, EmailStr
from datetime import datetime


class ClinicCreate(BaseModel):
    name: str
    cnpj: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    address: str | None = None


class ClinicOut(ClinicCreate):
    id: str
    created_at: datetime

    model_config = {"from_attributes": True}
