from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.database import SessionLocal
from app.models import User
from app.schemas import UserCreate, UserOut
from app.deps import hash_password, pwd_context, create_access_token

router = APIRouter()

# DB session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):

    # check existing email
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_pw = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        password_hash=hashed_pw,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):

    # 1. find user by email
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # 2. verify password
    if not pwd_context.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    # 3. create JWT with user role
    access_token = create_access_token({
        "sub": str(user.id),
        "role": user.role
    })

    # 4. return token + user info
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "role": user.role
    }
