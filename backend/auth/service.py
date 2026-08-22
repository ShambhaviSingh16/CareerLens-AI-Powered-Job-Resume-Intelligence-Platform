from sqlalchemy import select
from sqlalchemy.orm import Session

from models import User
from auth.security import hash_password, verify_password, create_access_token
from auth.schemas import RegisterRequest


def register_user(
    db: Session,
    data: RegisterRequest,
) -> User:
    existing_user = db.scalar(
        select(User).where(User.email == data.email)
    )

    if existing_user:
        raise ValueError("Email is already registered")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
) -> User:
    user = db.scalar(
        select(User).where(User.email == email)
    )

    if not user:
        raise ValueError("Invalid email or password")

    if not verify_password(password, user.password_hash):
        raise ValueError("Invalid email or password")

    return user


def login_user(
    db: Session,
    email: str,
    password: str,
) -> dict:
    user = authenticate_user(db, email, password)

    access_token = create_access_token(str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }