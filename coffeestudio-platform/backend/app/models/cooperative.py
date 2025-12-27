from sqlalchemy import String, Text, Float, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.db.session import Base
from app.models.common import TimestampMixin


class Cooperative(Base, TimestampMixin):
    __tablename__ = "cooperatives"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    region: Mapped[str | None] = mapped_column(String(255), nullable=True)
    altitude_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    varieties: Mapped[str | None] = mapped_column(String(255), nullable=True)
    certifications: Mapped[str | None] = mapped_column(String(255), nullable=True)
    contact_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Workflow / CRM-ish fields
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="active")  # active|watch|blocked|archived
    next_action: Mapped[str | None] = mapped_column(String(255), nullable=True)
    requested_data: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_verified_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    quality_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reliability_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    economics_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    total_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)

    last_scored_at: Mapped[DateTime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    meta: Mapped[dict | None] = mapped_column(JSON, nullable=True)
