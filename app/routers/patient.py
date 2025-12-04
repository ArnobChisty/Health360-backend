from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import Vital
from app.schemas import VitalCreate
from app.deps import get_current_user

router = APIRouter(prefix="/patient", tags=["Patient"])


# =======================================================
# Monitoring Engine – Alert Evaluation Function
# =======================================================
def evaluate_alert(systolic, diastolic, glucose, heart_rate):
    # ---------------- CRITICAL ----------------
    if systolic and diastolic:
        if systolic >= 180 or diastolic >= 120:
            return "critical"

    if glucose and glucose >= 12:
        return "critical"

    if heart_rate and heart_rate >= 130:
        return "critical"

    # ---------------- WARNING ----------------
    if systolic and diastolic:
        if systolic >= 140 or diastolic >= 90:
            return "warning"

    if glucose and glucose >= 7.0:
        return "warning"

    if heart_rate and heart_rate >= 100:
        return "warning"

    # ---------------- NORMAL ----------------
    return "normal"


# =======================================================
# Database Session Dependency
# =======================================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =======================================================
# 1. PATIENT SUBMITS VITALS
# =======================================================
@router.post("/vitals")
def submit_vitals(
    vital_data: VitalCreate,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Ensure only patients can submit vitals
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can submit vitals")

    # ----------------------------------------
    # Calculate ALERT LEVEL using the engine
    # ----------------------------------------
    alert_level = evaluate_alert(
        vital_data.systolic,
        vital_data.diastolic,
        vital_data.glucose,
        vital_data.heart_rate
    )

    # ----------------------------------------
    # Create the Vital record
    # ----------------------------------------
    new_vital = Vital(
        user_id=current_user.id,
        systolic=vital_data.systolic,
        diastolic=vital_data.diastolic,
        glucose=vital_data.glucose,
        weight=vital_data.weight,
        heart_rate=vital_data.heart_rate,
        symptom=vital_data.symptom,
        alert_level=alert_level
    )

    db.add(new_vital)
    db.commit()
    db.refresh(new_vital)

    # ----------------------------------------
    # Return the response including alert level
    # ----------------------------------------
    return {
        "message": "Vitals submitted successfully",
        "alert_level": alert_level,
        "data": {
            "id": new_vital.id,
            "user_id": current_user.id,
            "systolic": new_vital.systolic,
            "diastolic": new_vital.diastolic,
            "glucose": new_vital.glucose,
            "weight": new_vital.weight,
            "heart_rate": new_vital.heart_rate,
            "symptom": new_vital.symptom,
            "alert_level": new_vital.alert_level,
            "created_at": new_vital.created_at
        }
    }


# =======================================================
# 2. PATIENT — ALERT HISTORY (warning + critical)
# =======================================================
@router.get("/alerts")
def get_patient_alert_history(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Only patients can view alert history
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can view alerts")

    alerts = db.query(Vital).filter(
        Vital.user_id == current_user.id,
        Vital.alert_level != "normal"     # warning + critical only
    ).order_by(Vital.created_at.desc()).all()

    return {
        "patient_id": current_user.id,
        "total_alerts": len(alerts),
        "alerts": [
            {
                "id": v.id,
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
# 3. PATIENT — FULL VITALS HISTORY (Normal + Warning + Critical)
# =======================================================
@router.get("/vitals/history")
def get_patient_vitals_history(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    # Only patients can view their own vitals history
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Only patients can view their vitals history")

    vitals = db.query(Vital).filter(
        Vital.user_id == current_user.id
    ).order_by(Vital.created_at.desc()).all()

    return {
        "patient_id": current_user.id,
        "total_records": len(vitals),
        "vitals": [
            {
                "id": v.id,
                "systolic": v.systolic,
                "diastolic": v.diastolic,
                "glucose": v.glucose,
                "weight": v.weight,
                "heart_rate": v.heart_rate,
                "symptom": v.symptom,
                "alert_level": v.alert_level,
                "created_at": v.created_at
            }
            for v in vitals
        ]
    }
