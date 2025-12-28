from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime


class CooperativeCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    region: Optional[str] = Field(None, max_length=255)
    altitude_m: Optional[float] = Field(None, ge=0, le=6000)
    varieties: Optional[str] = Field(None, max_length=255)
    certifications: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    status: Optional[str] = Field("active", max_length=32)
    next_action: Optional[str] = Field(None, max_length=255)
    requested_data: Optional[str] = None
    meta: Optional[dict] = None
    
    @field_validator('name')
    @classmethod
    def name_safe(cls, v: str) -> str:
        """Prevent potentially dangerous input in names."""
        if not v:
            raise ValueError('Name darf nicht leer sein')
        dangerous = ['drop', 'delete', 'insert', 'update', '--', ';', '<script>', '<iframe>']
        v_lower = v.lower()
        for kw in dangerous:
            if kw in v_lower:
                raise ValueError(f'Ungültige Zeichen im Namen: "{kw}" ist nicht erlaubt')
        return v
    
    @field_validator('website')
    @classmethod
    def website_valid(cls, v: Optional[str]) -> Optional[str]:
        """Basic website URL validation."""
        if v and v.strip():
            v = v.strip()
            # Must start with http:// or https://
            if not (v.startswith('http://') or v.startswith('https://')):
                # Auto-prepend https:// if missing
                v = 'https://' + v
        return v if v else None


class CooperativeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    region: Optional[str] = Field(None, max_length=255)
    altitude_m: Optional[float] = Field(None, ge=0, le=6000)
    varieties: Optional[str] = Field(None, max_length=255)
    certifications: Optional[str] = Field(None, max_length=255)
    contact_email: Optional[EmailStr] = None
    website: Optional[str] = Field(None, max_length=500)
    notes: Optional[str] = None
    status: Optional[str] = Field(None, max_length=32)
    next_action: Optional[str] = Field(None, max_length=255)
    requested_data: Optional[str] = None
    last_verified_at: Optional[datetime] = None
    meta: Optional[dict] = None
    
    @field_validator('name')
    @classmethod
    def name_safe(cls, v: Optional[str]) -> Optional[str]:
        """Prevent potentially dangerous input in names."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError('Name darf nicht leer sein')
        dangerous = ['drop', 'delete', 'insert', 'update', '--', ';', '<script>', '<iframe>']
        v_lower = v.lower()
        for kw in dangerous:
            if kw in v_lower:
                raise ValueError(f'Ungültige Zeichen im Namen: "{kw}" ist nicht erlaubt')
        return v
    
    @field_validator('website')
    @classmethod
    def website_valid(cls, v: Optional[str]) -> Optional[str]:
        """Basic website URL validation."""
        if v and v.strip():
            v = v.strip()
            # Must start with http:// or https://
            if not (v.startswith('http://') or v.startswith('https://')):
                # Auto-prepend https:// if missing
                v = 'https://' + v
        return v if v else None


class CooperativeOut(BaseModel):
    id: int
    name: str
    region: Optional[str] = None
    altitude_m: Optional[float] = None
    varieties: Optional[str] = None
    certifications: Optional[str] = None
    contact_email: Optional[str] = None
    website: Optional[str] = None
    notes: Optional[str] = None

    status: str
    next_action: Optional[str] = None
    requested_data: Optional[str] = None
    last_verified_at: Optional[datetime] = None

    quality_score: Optional[float] = None
    reliability_score: Optional[float] = None
    economics_score: Optional[float] = None
    total_score: Optional[float] = None
    confidence: Optional[float] = None
    last_scored_at: Optional[datetime] = None

    meta: Optional[dict] = None

    class Config:
        from_attributes = True
