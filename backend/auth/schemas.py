from pydantic import BaseModel, EmailStr, Field, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email")
    @classmethod
    def normalized_email(cls, value):
        return value.lower()


class LoginRequest(RegisterRequest):
    pass


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class DeleteAccountRequest(BaseModel):
    password: str = Field(min_length=8, max_length=128)
