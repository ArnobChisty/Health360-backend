from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.deps import get_db, get_current_user
from app.models import User, Vital, DoctorNote
from app.schemas import DoctorNoteCreate, DoctorNoteOut

router = APIRouter(prefix="/doctor", tags=["Doctor"])


# =======================================================
# Doctor Only Access Check
# =======================================================
def doctor_only(current_user = Depends(get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Doctors only")
    return current_user


# =======================================================
# 1. GET ALL PATIENTS
# =======================================================
@router.get("/patients")
def get_all_patients(
    db: Session = Depends(get_db),
    doctor = Depends(doctor_only)
):
    return db.query(User).filter(User.role == "patient").all()


# =======================================================
# 2. GET ONE PATIENT BY ID
# =======================================================
@router.get("/patient/{patient_id}")
def get_patient_by_id(
    patient_id: int,
    db: Session = Depends(get_db),
    doctor = Depends(doctor_only)
):
    patient = db.query(User).filter(
        User.id == patient_id,
        User.role == "patient"
    ).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    return patient


# =======================================================
# 3. VIEW A SPECIFIC PATIENT'S FULL VITALS HISTORY
# =======================================================
@router.get("/patient/{patient_id}/vitals")
def get_patient_vitals(
    patient_id: int,
    db: Session = Depends(get_db),
    doctor = Depends(doctor_only)
):
    vitals = db.query(Vital).filter(Vital.user_id == patient_id).order_by(Vital.created_at.desc()).all()

    if not vitals:
        return {"message": "No vitals recorded for this patient"}

    return vitals


# =======================================================
# 4. DOCTOR ALERT DASHBOARD — All Alerts (Warning + Critical)
# =======================================================
@router.get("/alerts")
def get_all_patient_alerts(
    db: Session = Depends(get_db),
    doctor = Depends(doctor_only)
):
    alerts = db.query(Vital).filter(
        Vital.alert_level != "normal"
    ).order_by(Vital.created_at.desc()).all()

    return {
        "total_alerts": len(alerts),
        "alerts": [
            {
                "vital_id": v.id,
                "patient_id": v.user_id,
                "systolic": v.systolic,
                "diastolic": v.diastolic,
                "glucose": v.glucose,
                "weight": v.weight,
                "heart_rate": v.heart_rate,
                "symptom": v.symptom,
                "alert_level": v.alert_level,
                "created_at": v.created_at
            }
            for v in alerts
        ]
    }


# =======================================================
# 5. DOCTOR — Alerts for a Specific Patient
# =======================================================
@router.get("/patient/{patient_id}/alerts")
def get_alerts_for_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    doctor = Depends(doctor_only)
):
    alerts = db.query(Vital).filter(
        Vital.user_id == patient_id,
        Vital.alert_level != "normal"
    ).order_by(Vital.created_at.desc()).all()

    return {
        "patient_id": patient_id,
        "total_alerts": len(alerts),
        "alerts": [
            {
                "vital_id": v.id,
                "systolic": v.systolic,
                "diastolic": v.diastolic,
                "glucose": v.glucose,
                "weight": v.weight,
                "heart_rate": v.heart_rate,
                "symptom": v.symptom,
                "alert_level": v.alert_level,
                "created_at": v.created_at
            }
            for v in alerts
        ]
    }


# =======================================================
# 6. DOCTOR — Add a Note to a Vital Record
# =======================================================
@router.post("/vitals/{vital_id}/notes", response_model=DoctorNoteOut)
def add_note_to_vital(
    vital_id: int,
    note_data: DoctorNoteCreate,
    db: Session = Depends(get_db),
    doctor = Depends(doctor_only)
):
    vital = db.query(Vital).filter(Vital.id == vital_id).first()

    if not vital:
        raise HTTPException(status_code=404, detail="Vital record not found")

    new_note = DoctorNote(
        vital_id=vital_id,
        doctor_id=doctor.id,
        note=note_data.note
    )

    db.add(new_note)
    db.commit()
    db.refresh(new_note)

    return new_note


# =======================================================
# 7. DOCTOR — View Notes for a Vital Record
# =======================================================
@router.get("/vitals/{vital_id}/notes", response_model=list[DoctorNoteOut])
def get_notes_for_vital(
    vital_id: int,
    db: Session = Depends(get_db),
    doctor = Depends(doctor_only)
):
    vital = db.query(Vital).filter(Vital.id == vital_id).first()

    if not vital:
        raise HTTPException(status_code=404, detail="Vital record not found")

    notes = db.query(DoctorNote).filter(
        DoctorNote.vital_id == vital_id
    ).order_by(DoctorNote.created_at.desc()).all()

    return notes
