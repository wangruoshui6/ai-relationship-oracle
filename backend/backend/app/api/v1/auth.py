from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.auth import (
    AccessTokenResponse,
    LoginRequest,
    TokenResponse,
    UserBrief,
    UserRegisterRequest,
)
from app.schemas.common import ApiResponse, success_response
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=ApiResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegisterRequest,
    db: Session = Depends(get_db),
) -> dict:
    user = AuthService(db).register(payload.email, payload.password)
    return success_response(UserBrief.model_validate(user).model_dump())


@router.post("/login", response_model=ApiResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> dict:
    data = AuthService(db).login(payload.email, payload.password)
    response = TokenResponse(
        access_token=data["access_token"],
        token_type="bearer",
        user=UserBrief.model_validate(data["user"]),
    )
    return success_response(response.model_dump())


@router.post("/token", response_model=AccessTokenResponse)
def token_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> AccessTokenResponse:
    data = AuthService(db).login(form_data.username, form_data.password)
    return AccessTokenResponse(
        access_token=data["access_token"],
        token_type="bearer",
    )


@router.get("/me", response_model=ApiResponse)
def me(current_user: User = Depends(get_current_user)) -> dict:
    return success_response(UserBrief.model_validate(current_user).model_dump())
