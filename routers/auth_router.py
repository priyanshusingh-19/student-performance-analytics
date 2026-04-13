from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from database import SessionLocal
from models.user import User
from auth.auth_utils import verify_password, create_access_token
from auth.dependencies import get_current_user
import logging

router = APIRouter(tags=["Auth"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# 🔌 DB SESSION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 🔐 LOGIN (Swagger-compatible)
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user:
        logger.warning(f"Login failed: user not found ({form_data.username})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Login failed: wrong password ({form_data.username})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    access_token = create_access_token(
        {"sub": user.username, "role": user.role}
    )

    logger.info(f"User logged in: {user.username}")

    # ⚠️ IMPORTANT: Swagger requires this exact format
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# 👤 CURRENT USER
@router.get("/me")
def get_me(user: dict = Depends(get_current_user)):
    return {
        "status": "success",
        "username": user.get("sub"),
        "role": user.get("role")
    }