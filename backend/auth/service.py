from sqlalchemy import select
from sqlalchemy.orm import Session

from models import User
from auth.security import hash_password
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