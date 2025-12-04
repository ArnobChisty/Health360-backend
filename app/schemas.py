from pydantic import BaseModel, EmailStr
from datetime import datetime


# ================================
# USER SCHEMAS
# ================================
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    phone: str
    role: str   # "patient" or "doctor"
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    role: str

    class Config:
        from_attributes = True   # Pydantic v2 replacement for orm_mode


# ================================
# VITALS SCHEMAS
# ================================
class VitalCreate(BaseModel):
    systolic: int | None = None
    diastolic: int | None = None
    glucose: float | None = None
    weight: float | None = None
    heart_rate: int | None = None
    symptom: str | None = None


class VitalOut(BaseModel):
    id: int
    user_id: int
    systolic: int | None
    diastolic: int | None
    glucose: float | None
    weight: float | None
    heart_rate: int | None
    symptom: str | None
    alert_level: str
    created_at: datetime

    class Config:
        from_attributes = True


# ================================
# DOCTOR NOTES SCHEMAS
# ================================
class DoctorNoteCreate(BaseModel):
    note: str


class DoctorNoteOut(BaseModel):
    id: int
    vital_id: int
    doctor_id: int
    note: str
    created_at: datetime

    class Config:
        from_attributes = True
