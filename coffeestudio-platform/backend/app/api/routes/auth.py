from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import verify_password, create_access_token, hash_password
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, TokenResponse, UserOut
from app.core.config import settings

from email_validator import validate_email, EmailNotValidError

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    token = create_access_token(sub=user.email, role=user.role)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user


# Dev-only bootstrap: creates admin if empty.
@router.post("/dev/bootstrap")
def dev_bootstrap(db: Session = Depends(get_db)):
    if db.query(User).count() > 0:
        return {"status": "skipped"}

    if not settings.BOOTSTRAP_ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="BOOTSTRAP_ADMIN_PASSWORD is not set (configure it via .env)",
        )

    try:
        # Fail-fast on invalid emails (e.g. admin@local)
        validate_email(settings.BOOTSTRAP_ADMIN_EMAIL, check_deliverability=False)
    except EmailNotValidError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid BOOTSTRAP_ADMIN_EMAIL: {e}",
        )

    admin = User(
        email=settings.BOOTSTRAP_ADMIN_EMAIL,
        password_hash=hash_password(settings.BOOTSTRAP_ADMIN_PASSWORD),
        role="admin",
        is_active=True,
    )
    db.add(admin)
    db.commit()
    return {"status": "created", "email": admin.email}
