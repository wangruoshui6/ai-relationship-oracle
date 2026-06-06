from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class UserBrief(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    status: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserBrief


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str
