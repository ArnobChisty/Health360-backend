from sqlalchemy import Column, Integer, String, Enum, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .database import Base


# ================================
# USER TABLE
# ================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    phone = Column(String(20), unique=True)
    role = Column(Enum("patient", "doctor", name="user_roles"), nullable=False)
    password_hash = Column(String(255), nullable=False)

    # relationship to vitals (patients only)
    vitals = relationship("Vital", back_populates="user")

    # relationship to notes (doctors only)
    doctor_notes = relationship("DoctorNote", back_populates="doctor")


# ================================
# VITALS TABLE
# ================================
class Vital(Base):
    __tablename__ = "vitals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))

    systolic = Column(Integer, nullable=True)
    diastolic = Column(Integer, nullable=True)
    glucose = Column(Float, nullable=True)
    weight = Column(Float, nullable=True)
    heart_rate = Column(Integer, nullable=True)
    symptom = Column(String(255), nullable=True)

    # alert level (normal / warning / critical)
    alert_level = Column(String(20), nullable=False, default="normal")

    created_at = Column(DateTime, default=datetime.utcnow)

    # relationship back to user (patient)
    user = relationship("User", back_populates="vitals")

    # relationship to doctor notes
    notes = relationship("DoctorNote", back_populates="vital", cascade="all, delete-orphan")


# ================================
# DOCTOR NOTES TABLE
# ================================
class DoctorNote(Base):
    __tablename__ = "doctor_notes"

    id = Column(Integer, primary_key=True, index=True)
    vital_id = Column(Integer, ForeignKey("vitals.id"), nullable=False)
    doctor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    note = Column(String(500), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)

    # relationships
    vital = relationship("Vital", back_populates="notes")
    doctor = relationship("User", back_populates="doctor_notes")
