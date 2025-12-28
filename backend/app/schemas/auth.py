from pydantic import BaseModel, EmailStr, Field, field_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    
    @field_validator('password')
    @classmethod
    def password_not_common(cls, v: str) -> str:
        """Reject common weak passwords."""
        common = ['password', '12345678', 'admin123', 'qwerty', 'letmein']
        if v.lower() in common:
            raise ValueError('Passwort ist zu schwach und leicht zu erraten')
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
