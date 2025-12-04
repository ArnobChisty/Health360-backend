from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, patient, doctor

app = FastAPI(
    title="Health360 API",
    description="Patient Monitoring & Doctor Dashboard System",
    version="1.0"
)

# ----------------------------
# CORS SETTINGS (IMPORTANT)
# ----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow frontend (localhost:5173) to access backend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------------
# Register Routers
# ----------------------------
app.include_router(auth.router, prefix="/auth")
app.include_router(patient.router)      # prefix already defined inside router
app.include_router(doctor.router)       # prefix already defined inside router

# ----------------------------
# Root Endpoint
# ----------------------------
@app.get("/")
def root():
    return {"message": "Health 360 API is running!"}
