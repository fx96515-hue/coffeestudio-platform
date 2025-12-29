"""Cooperative Sourcing Analyzer for buyer-side intelligence."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.cooperative import Cooperative
from app.models.region import Region
from app.services.data_sources.peru_data_sources import fetch_ico_price_data


@dataclass
class SupplyCapacityCheck:
    """Supply capacity assessment data."""
    
    score: float
    volume_score: float
    farmer_count_score: float
    storage_score: float
    processing_score: float
    experience_score: float
    details: dict


@dataclass
class ExportReadinessCheck:
    """Export readiness assessment data."""
    
    score: float
    license_valid: bool
    senasa_registered: bool
    certifications_score: float
    customs_history_score: float
    document_coordinator: bool
    details: dict


@dataclass
class PriceBenchmark:
    """Price competitiveness benchmark."""
    
    cooperative_price: Optional[float]
    regional_benchmark: Optional[float]
    difference_pct: Optional[float]
    score: float
    details: dict


@dataclass
class RiskAssessment:
    """Risk assessment for sourcing decision."""
    
    risk_score: float
    financial_risk: float
    quality_risk: float
    delivery_risk: float
    geographic_risk: float
    communication_risk: float
    risk_factors: list


@dataclass
class SourcingAnalysis:
    """Complete sourcing analysis for a cooperative."""
    
    cooperative_id: int
    cooperative_name: str
    supply_capacity: SupplyCapacityCheck
    export_readiness: ExportReadinessCheck
    communication_score: float
    price_benchmark: PriceBenchmark
    risk_assessment: RiskAssessment
    total_score: float
    recommendation: str


class CooperativeSourcingAnalyzer:
    """Analyzer for cooperative sourcing decisions from buyer perspective."""

    def __init__(self, db: Session):
        self.db = db

    def analyze_for_sourcing(self, cooperative_id: int) -> Optional[SourcingAnalysis]:
        """Perform comprehensive sourcing analysis for a cooperative.
        
        Args:
            cooperative_id: ID of the cooperative to analyze
            
        Returns:
            SourcingAnalysis object or None if cooperative not found
        """
        coop = self.db.query(Cooperative).filter(Cooperative.id == cooperative_id).first()
        if not coop:
            return None
        
        # Perform all checks
        supply_capacity = self.check_supply_capacity(coop)
        export_readiness = self.check_export_readiness(coop)
        communication_score = self.assess_communication_quality(coop)
        
        # Get region for price benchmarking
        region = None
        if coop.region:
            region = self.db.query(Region).filter(Region.name == coop.region).first()
        
        price_benchmark = self.benchmark_pricing(coop, region, coop.quality_score)
        risk_assessment = self.calculate_sourcing_risk(coop)
        
        # Calculate total score (weighted average)
        total_score = (
            supply_capacity.score * 0.30 +
            (coop.quality_score or 50.0) * 0.25 +
            export_readiness.score * 0.20 +
            price_benchmark.score * 0.15 +
            communication_score * 0.10
        )
        
        recommendation = self.generate_recommendation(
            {
                "supply": supply_capacity.score,
                "quality": coop.quality_score or 50.0,
                "export": export_readiness.score,
                "price": price_benchmark.score,
                "communication": communication_score,
                "total": total_score
            },
            risk_assessment
        )
        
        # Store sourcing scores
        coop.sourcing_scores = {
            "supply_capacity_score": supply_capacity.score,
            "quality_track_record_score": coop.quality_score or 50.0,
            "export_readiness_score": export_readiness.score,
            "price_competitiveness_score": price_benchmark.score,
            "communication_quality_score": communication_score,
            "total_score": total_score,
            "risk_score": risk_assessment.risk_score,
            "recommendation": recommendation
        }
        self.db.add(coop)
        self.db.commit()
        
        return SourcingAnalysis(
            cooperative_id=coop.id,
            cooperative_name=coop.name,
            supply_capacity=supply_capacity,
            export_readiness=export_readiness,
            communication_score=communication_score,
            price_benchmark=price_benchmark,
            risk_assessment=risk_assessment,
            total_score=total_score,
            recommendation=recommendation
        )

    def check_supply_capacity(self, cooperative: Cooperative) -> SupplyCapacityCheck:
        """Check supply capacity of cooperative.
        
        Scoring breakdown:
        - Volume: 30 points
        - Farmer count: 20 points
        - Storage capacity: 20 points
        - Processing facilities: 15 points
        - Export experience: 15 points
        
        Args:
            cooperative: Cooperative object
            
        Returns:
            SupplyCapacityCheck object
        """
        op_data = cooperative.operational_data or {}
        export_data = cooperative.export_readiness or {}
        financial_data = cooperative.financial_data or {}
        
        # Volume score (30 points)
        volume_kg = financial_data.get("export_volume_kg_last_year", 0)
        if volume_kg >= 100000:
            volume_score = 30.0
        elif volume_kg >= 50000:
            volume_score = 25.0
        elif volume_kg >= 25000:
            volume_score = 20.0
        elif volume_kg >= 10000:
            volume_score = 15.0
        else:
            volume_score = 5.0
        
        # Farmer count score (20 points)
        farmer_count = op_data.get("farmer_count", 0)
        if farmer_count >= 500:
            farmer_count_score = 20.0
        elif farmer_count >= 200:
            farmer_count_score = 17.0
        elif farmer_count >= 100:
            farmer_count_score = 14.0
        elif farmer_count >= 50:
            farmer_count_score = 10.0
        else:
            farmer_count_score = 5.0
        
        # Storage capacity score (20 points)
        storage_kg = op_data.get("storage_capacity_kg", 0)
        if storage_kg >= 200000:
            storage_score = 20.0
        elif storage_kg >= 100000:
            storage_score = 17.0
        elif storage_kg >= 50000:
            storage_score = 14.0
        elif storage_kg >= 25000:
            storage_score = 10.0
        else:
            storage_score = 5.0
        
        # Processing facilities score (15 points)
        processing_score = 0.0
        if op_data.get("has_wet_mill"):
            processing_score += 8.0
        if op_data.get("has_dry_mill"):
            processing_score += 7.0
        
        # Export experience score (15 points)
        export_years = export_data.get("export_experience_years", 0)
        if export_years >= 10:
            experience_score = 15.0
        elif export_years >= 5:
            experience_score = 12.0
        elif export_years >= 3:
            experience_score = 9.0
        elif export_years >= 1:
            experience_score = 6.0
        else:
            experience_score = 2.0
        
        total_score = volume_score + farmer_count_score + storage_score + processing_score + experience_score
        
        return SupplyCapacityCheck(
            score=min(100.0, total_score),
            volume_score=volume_score,
            farmer_count_score=farmer_count_score,
            storage_score=storage_score,
            processing_score=processing_score,
            experience_score=experience_score,
            details={
                "volume_kg": volume_kg,
                "farmer_count": farmer_count,
                "storage_capacity_kg": storage_kg,
                "has_wet_mill": op_data.get("has_wet_mill", False),
                "has_dry_mill": op_data.get("has_dry_mill", False),
                "export_experience_years": export_years
            }
        )

    def check_export_readiness(self, cooperative: Cooperative) -> ExportReadinessCheck:
        """Check export readiness of cooperative.
        
        Scoring breakdown:
        - Export license valid: 25 points
        - SENASA registered: 25 points
        - Certifications: 25 points
        - Customs history: 15 points
        - Document coordinator: 10 points
        
        Args:
            cooperative: Cooperative object
            
        Returns:
            ExportReadinessCheck object
        """
        export_data = cooperative.export_readiness or {}
        
        # Export license (25 points)
        license_valid = bool(export_data.get("export_license_number")) and bool(export_data.get("export_license_expiry"))
        license_score = 25.0 if license_valid else 0.0
        
        # SENASA registered (25 points)
        senasa_registered = export_data.get("senasa_registered", False)
        senasa_score = 25.0 if senasa_registered else 0.0
        
        # Certifications (25 points)
        certs = cooperative.certifications or ""
        cert_list = [c.strip().lower() for c in certs.split(",") if c.strip()]
        if len(cert_list) >= 3:
            cert_score = 25.0
        elif len(cert_list) == 2:
            cert_score = 20.0
        elif len(cert_list) == 1:
            cert_score = 15.0
        else:
            cert_score = 5.0
        
        # Customs history (15 points)
        customs_issues = export_data.get("customs_clearance_issues_count", 0)
        if customs_issues == 0:
            customs_score = 15.0
        elif customs_issues <= 2:
            customs_score = 10.0
        elif customs_issues <= 5:
            customs_score = 5.0
        else:
            customs_score = 0.0
        
        # Document coordinator (10 points)
        has_coordinator = export_data.get("has_document_coordinator", False)
        coordinator_score = 10.0 if has_coordinator else 0.0
        
        total_score = license_score + senasa_score + cert_score + customs_score + coordinator_score
        
        return ExportReadinessCheck(
            score=min(100.0, total_score),
            license_valid=license_valid,
            senasa_registered=senasa_registered,
            certifications_score=cert_score,
            customs_history_score=customs_score,
            document_coordinator=has_coordinator,
            details={
                "export_license": export_data.get("export_license_number"),
                "senasa_registered": senasa_registered,
                "certifications": cert_list,
                "customs_issues": customs_issues,
                "has_document_coordinator": has_coordinator,
                "containers_exported": export_data.get("containers_exported_lifetime", 0)
            }
        )

    def assess_communication_quality(self, cooperative: Cooperative) -> float:
        """Assess communication quality of cooperative.
        
        Scoring breakdown:
        - Response time: 25 points (≤24h = 25, ≤48h = 20, ≤72h = 10)
        - Language skills: 25 points (English +15, German +10)
        - Digital presence: 20 points
        - Documentation quality: 15 points
        - Meeting reliability: 15 points
        
        Args:
            cooperative: Cooperative object
            
        Returns:
            Score from 0-100
        """
        comm_data = cooperative.communication_metrics or {}
        digital_data = cooperative.digital_footprint or {}
        
        # Response time (25 points)
        response_hours = comm_data.get("avg_email_response_time_hours", 999)
        if response_hours <= 24:
            response_score = 25.0
        elif response_hours <= 48:
            response_score = 20.0
        elif response_hours <= 72:
            response_score = 10.0
        else:
            response_score = 5.0
        
        # Language skills (25 points)
        languages = comm_data.get("languages_spoken", [])
        language_score = 0.0
        if "english" in [l.lower() for l in languages]:
            language_score += 15.0
        if "german" in [l.lower() for l in languages]:
            language_score += 10.0
        if language_score == 0:
            language_score = 5.0  # Base score for Spanish
        
        # Digital presence (20 points)
        digital_score = 0.0
        if cooperative.website:
            digital_score += 8.0
        if digital_data.get("facebook_url"):
            digital_score += 4.0
        if digital_data.get("instagram_url"):
            digital_score += 4.0
        if comm_data.get("whatsapp_business"):
            digital_score += 4.0
        
        # Documentation quality (15 points)
        doc_score = 0.0
        if comm_data.get("provides_photos_regularly"):
            doc_score += 8.0
        if comm_data.get("provides_cupping_scores"):
            doc_score += 7.0
        
        # Meeting reliability (15 points)
        missed_meetings = comm_data.get("missed_meetings_count", 0)
        if missed_meetings == 0:
            meeting_score = 15.0
        elif missed_meetings <= 1:
            meeting_score = 12.0
        elif missed_meetings <= 3:
            meeting_score = 8.0
        else:
            meeting_score = 3.0
        
        return min(100.0, response_score + language_score + digital_score + doc_score + meeting_score)

    def benchmark_pricing(
        self,
        cooperative: Cooperative,
        region: Optional[Region],
        quality_level: Optional[float]
    ) -> PriceBenchmark:
        """Benchmark cooperative pricing against regional averages.
        
        Score: 100 - (abs(diff_pct) * 2)
        
        Args:
            cooperative: Cooperative object
            region: Region object (optional)
            quality_level: Quality score (optional)
            
        Returns:
            PriceBenchmark object
        """
        financial_data = cooperative.financial_data or {}
        coop_price = financial_data.get("avg_price_achieved_usd_per_kg")
        
        # Get regional benchmark
        regional_benchmark = None
        if region and region.economic_data:
            regional_benchmark = region.economic_data.get("avg_fob_price")
        
        # Fallback to ICO data
        if not regional_benchmark:
            ico_data = fetch_ico_price_data()
            regional_benchmark = ico_data.get("data", {}).get("peru_fob_avg_usd_per_kg", 5.10)
        
        # Calculate difference and score
        if coop_price and regional_benchmark:
            difference_pct = ((coop_price - regional_benchmark) / regional_benchmark) * 100
            score = max(0.0, min(100.0, 100.0 - (abs(difference_pct) * 2)))
        else:
            difference_pct = None
            score = 50.0  # Neutral score if no data
        
        return PriceBenchmark(
            cooperative_price=coop_price,
            regional_benchmark=regional_benchmark,
            difference_pct=difference_pct,
            score=score,
            details={
                "cooperative_price": coop_price,
                "regional_benchmark": regional_benchmark,
                "difference_pct": difference_pct,
                "quality_adjusted": quality_level
            }
        )

    def calculate_sourcing_risk(self, cooperative: Cooperative) -> RiskAssessment:
        """Calculate overall sourcing risk.
        
        Risk components (lower is better):
        - Financial stability: 25 points max risk
        - Quality consistency: 20 points max risk
        - Delivery reliability: 25 points max risk
        - Geographic factors: 15 points max risk
        - Communication: 15 points max risk
        
        Args:
            cooperative: Cooperative object
            
        Returns:
            RiskAssessment object
        """
        financial_data = cooperative.financial_data or {}
        export_data = cooperative.export_readiness or {}
        
        risk_factors = []
        
        # Financial stability risk (25 points max)
        annual_revenue = financial_data.get("annual_revenue_usd", 0)
        if annual_revenue < 100000:
            financial_risk = 25.0
            risk_factors.append("Low annual revenue (<$100k)")
        elif annual_revenue < 300000:
            financial_risk = 15.0
            risk_factors.append("Moderate annual revenue ($100k-$300k)")
        elif annual_revenue < 500000:
            financial_risk = 8.0
        else:
            financial_risk = 2.0
        
        # Quality consistency risk (20 points max)
        quality_score = cooperative.quality_score or 50.0
        if quality_score < 60:
            quality_risk = 20.0
            risk_factors.append("Low quality score (<60)")
        elif quality_score < 75:
            quality_risk = 12.0
            risk_factors.append("Moderate quality score (60-75)")
        elif quality_score < 85:
            quality_risk = 6.0
        else:
            quality_risk = 2.0
        
        # Delivery reliability risk (25 points max)
        export_years = export_data.get("export_experience_years", 0)
        customs_issues = export_data.get("customs_clearance_issues_count", 0)
        
        delivery_risk = 0.0
        if export_years < 2:
            delivery_risk += 15.0
            risk_factors.append("Limited export experience (<2 years)")
        elif export_years < 5:
            delivery_risk += 8.0
        
        if customs_issues > 3:
            delivery_risk += 10.0
            risk_factors.append(f"Multiple customs issues ({customs_issues})")
        elif customs_issues > 0:
            delivery_risk += 5.0
        
        # Geographic factors risk (15 points max)
        altitude = cooperative.altitude_m or 0
        if altitude > 2200 or altitude < 800:
            geographic_risk = 12.0
            risk_factors.append("Extreme altitude (logistics challenges)")
        elif altitude > 2000 or altitude < 1000:
            geographic_risk = 6.0
        else:
            geographic_risk = 2.0
        
        # Communication risk (15 points max)
        comm_data = cooperative.communication_metrics or {}
        response_hours = comm_data.get("avg_email_response_time_hours", 999)
        missed_meetings = comm_data.get("missed_meetings_count", 0)
        
        communication_risk = 0.0
        if response_hours > 72:
            communication_risk += 8.0
            risk_factors.append("Slow response time (>72h)")
        elif response_hours > 48:
            communication_risk += 4.0
        
        if missed_meetings > 2:
            communication_risk += 7.0
            risk_factors.append(f"Multiple missed meetings ({missed_meetings})")
        elif missed_meetings > 0:
            communication_risk += 3.0
        
        total_risk = financial_risk + quality_risk + delivery_risk + geographic_risk + communication_risk
        
        return RiskAssessment(
            risk_score=min(100.0, total_risk),
            financial_risk=financial_risk,
            quality_risk=quality_risk,
            delivery_risk=delivery_risk,
            geographic_risk=geographic_risk,
            communication_risk=communication_risk,
            risk_factors=risk_factors
        )

    def generate_recommendation(self, scores: dict, risk: RiskAssessment) -> str:
        """Generate sourcing recommendation based on scores and risk.
        
        Args:
            scores: Dictionary of all scores
            risk: RiskAssessment object
            
        Returns:
            Recommendation string
        """
        total_score = scores.get("total", 0)
        risk_score = risk.risk_score
        
        # High score, low risk
        if total_score >= 80 and risk_score < 30:
            return "HIGHLY RECOMMENDED"
        
        # Good score, acceptable risk
        if total_score >= 70 and risk_score < 40:
            return "RECOMMENDED"
        
        # Moderate score, moderate risk
        if total_score >= 60 and risk_score < 50:
            return "CONSIDER WITH CAUTION"
        
        # Low score or high risk
        if total_score < 60 or risk_score >= 60:
            return "NOT RECOMMENDED"
        
        # Default moderate
        return "MONITOR CLOSELY"
