from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.exceptions import AppException
from app.core.security import PasswordService, TokenService
from app.models.user import User


class AuthService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.password_service = PasswordService()
        self.token_service = TokenService()

    def register(self, email: str, password: str) -> User:
        normalized_email = email.strip().lower()
        existing_user = self.db.scalar(select(User).where(User.email == normalized_email))
        if existing_user is not None:
            raise AppException(
                code=1005,
                message="email already registered",
                status_code=409,
            )

        user = User(
            email=normalized_email,
            password_hash=self.password_service.hash_password(password),
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login(self, email: str, password: str) -> dict[str, object]:
        normalized_email = email.strip().lower()
        user = self.db.scalar(select(User).where(User.email == normalized_email))
        if user is None or not self.password_service.verify_password(
            password, user.password_hash
        ):
            raise AppException(
                code=1002,
                message="invalid email or password",
                status_code=401,
            )

        access_token = self.token_service.create_access_token(user.id)
        return {
            "access_token": access_token,
            "user": user,
        }
