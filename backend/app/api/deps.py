from collections.abc import Generator

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import AppException
from app.core.security import TokenService
from app.db.session import SessionLocal
from app.models.user import User, UserStatus

settings = get_settings()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api_v1_prefix}/auth/token")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    token_service = TokenService()
    user_id = token_service.decode_access_token(token)
    user = db.scalar(
        select(User).where(
            User.id == user_id,
            User.status == UserStatus.ACTIVE,
        )
    )
    if user is None:
        raise AppException(code=1002, message="unauthorized", status_code=401)
    return user
