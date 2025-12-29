from datetime import datetime
from sqlalchemy import String, Float, Integer, JSON, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from app.db.session import Base


class Region(Base):
    """Region model for comprehensive sourcing intelligence."""

    __tablename__ = "regions"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True, unique=True, nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False, default="Peru")
    
    # Geographic and environmental data
    polygon: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    elevation_range: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    climate_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    soil_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    growing_conditions_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    
    # Production and economic data
    production_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    economic_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    quality_profile: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Infrastructure and logistics
    infrastructure_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    harvest_season: Mapped[str | None] = mapped_column(String(100), nullable=True)
    
    # Cooperative-related data
    cooperatives_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    certifications_pct: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    risk_factors: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default="now()"
    )
