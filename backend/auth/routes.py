from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.schemas import RegisterRequest, LoginRequest, TokenResponse
from auth.service import register_user, login_user
from database import get_db
from auth.dependencies import get_current_user
from models import User
from models import Analysis, AnalysisAttempt, Job, Resume
from sqlalchemy import delete
from auth.schemas import DeleteAccountRequest
from auth.security import verify_password


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return {"id": user.id, "email": user.email}


@router.delete("/me", status_code=204)
def delete_account(data: DeleteAccountRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not verify_password(data.password, user.password_hash):
        raise HTTPException(403, "The password is incorrect.")
    for model in (Analysis, AnalysisAttempt, Resume, Job):
        db.execute(delete(model).where(model.user_id == user.id))
    db.execute(delete(User).where(User.id == user.id))
    db.commit()


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
)
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db),
):
    try:
        user = register_user(db, data)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

    return {
        "id": user.id,
        "email": user.email,
        "created_at": user.created_at,
    }


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):
    try:
        return login_user(
            db,
            data.email,
            data.password,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        )
