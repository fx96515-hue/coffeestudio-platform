from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("password")
    @classmethod
    def password_not_common(cls, v: str) -> str:
        """Check password strength - basic common password rejection.

        For production: integrate with HaveIBeenPwned API or similar service.
        Current check is intentionally minimal as a starting point.
        """
        common = ["password", "12345678", "admin123", "qwerty", "letmein"]
        if v.lower() in common:
            raise ValueError("Passwort ist zu schwach und leicht zu erraten")
        # TODO: Add more comprehensive checks in future (uppercase, lowercase, numbers, special chars)
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: str
    is_active: bool

    class Config:
        from_attributes = True
