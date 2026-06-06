from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import get_settings
from app.core.exceptions import AppException

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class PasswordService:
    def hash_password(self, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)


class TokenService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def create_access_token(self, subject: str) -> str:
        expire_at = datetime.now(timezone.utc) + timedelta(
            minutes=self.settings.jwt_expire_minutes
        )
        payload = {
            "sub": subject,
            "exp": expire_at,
        }
        return jwt.encode(
            payload,
            self.settings.jwt_secret,
            algorithm=self.settings.jwt_algorithm,
        )

    def decode_access_token(self, token: str) -> str:
        try:
            payload = jwt.decode(
                token,
                self.settings.jwt_secret,
                algorithms=[self.settings.jwt_algorithm],
            )
        except JWTError as exc:
            raise AppException(code=1002, message="unauthorized", status_code=401) from exc

        subject = payload.get("sub")
        if not subject:
            raise AppException(code=1002, message="unauthorized", status_code=401)
        return subject
