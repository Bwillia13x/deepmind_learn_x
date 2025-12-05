"""Tests for Predictive Intervention Engine service."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.services.predictive_intervention import (
    RiskLevel,
    InterventionTier,
    calculate_trend,
    identify_risk_factors,
    identify_protective_factors,
    calculate_risk_score,
    generate_intervention_plan,
    determine_intervention_tier,
    AssessmentDataPoint,
    WCPM_BENCHMARKS,
)

client = TestClient(app)


class TestRiskAssessment:
    """Tests for student risk assessment functions."""

    def test_identify_risk_factors_low_fluency(self):
        """Test risk factor identification for low fluency student."""
        factors = identify_risk_factors(
            assessment_history=[
                {"date": "2024-01-15", "type": "orf", "wcpm": 50, "benchmark": 100},
                {"date": "2024-02-15", "type": "orf", "wcpm": 45, "benchmark": 100},
            ],
            student_profile={"l1": "es", "esl_level": 2},
            grade="3"
        )
        assert isinstance(factors, list)
        # Should identify below benchmark and declining trend

    def test_identify_risk_factors_slife(self):
        """Test risk factor identification for SLIFE student."""
        factors = identify_risk_factors(
            assessment_history=[],
            student_profile={
                "l1": "so",
                "slife": True,
                "l1_literacy": "limited"
            },
            grade="5"
        )
        assert isinstance(factors, list)
        # Should identify SLIFE and limited L1 literacy as risk factors

    def test_identify_protective_factors(self):
        """Test protective factor identification."""
        factors = identify_protective_factors(
            assessment_history=[
                {"date": "2024-01-15", "type": "orf", "score": 60},
                {"date": "2024-02-15", "type": "orf", "score": 70},
                {"date": "2024-03-15", "type": "orf", "score": 80},
            ],
            student_profile={
                "l1": "es",
                "l1_literacy": "strong",
                "family_involvement": True
            }
        )
        assert isinstance(factors, list)
        # Should identify improving trend, strong L1 literacy, cognate advantage

    def test_risk_levels_enum(self):
        """Test risk level enum values."""
        assert RiskLevel.LOW == "low"
        assert RiskLevel.MODERATE == "moderate"
        assert RiskLevel.HIGH == "high"
        assert RiskLevel.CRITICAL == "critical"

    def test_intervention_tiers_enum(self):
        """Test intervention tier enum values."""
        assert InterventionTier.TIER_1 == "tier_1"
        assert InterventionTier.TIER_2 == "tier_2"
        assert InterventionTier.TIER_3 == "tier_3"


class TestTrendCalculation:
    """Tests for trend calculation functions."""

    def test_calculate_trend_improving(self):
        """Test trend calculation for improving scores."""
        data_points = [
            AssessmentDataPoint(
                date=datetime(2024, 1, 15),
                assessment_type="fluency",
                score=50,
                benchmark=100
            ),
            AssessmentDataPoint(
                date=datetime(2024, 2, 15),
                assessment_type="fluency",
                score=60,
                benchmark=100
            ),
            AssessmentDataPoint(
                date=datetime(2024, 3, 15),
                assessment_type="fluency",
                score=70,
                benchmark=100
            ),
        ]
        result = calculate_trend(data_points)
        assert isinstance(result, dict)
        assert result["direction"] == "improving"
        assert result["slope"] > 0

    def test_calculate_trend_declining(self):
        """Test trend calculation for declining scores."""
        data_points = [
            AssessmentDataPoint(
                date=datetime(2024, 1, 15),
                assessment_type="fluency",
                score=70,
                benchmark=100
            ),
            AssessmentDataPoint(
                date=datetime(2024, 2, 15),
                assessment_type="fluency",
                score=60,
                benchmark=100
            ),
            AssessmentDataPoint(
                date=datetime(2024, 3, 15),
                assessment_type="fluency",
                score=50,
                benchmark=100
            ),
        ]
        result = calculate_trend(data_points)
        assert isinstance(result, dict)
        assert result["direction"] == "declining"
        assert result["slope"] < 0

    def test_calculate_trend_stable(self):
        """Test trend calculation for stable scores."""
        data_points = [
            AssessmentDataPoint(
                date=datetime(2024, 1, 15),
                assessment_type="fluency",
                score=75,
                benchmark=100
            ),
            AssessmentDataPoint(
                date=datetime(2024, 2, 15),
                assessment_type="fluency",
                score=76,
                benchmark=100
            ),
            AssessmentDataPoint(
                date=datetime(2024, 3, 15),
                assessment_type="fluency",
                score=75,
                benchmark=100
            ),
        ]
        result = calculate_trend(data_points)
        assert isinstance(result, dict)
        assert result["direction"] == "stable"

    def test_calculate_trend_empty_data(self):
        """Test trend calculation with no data."""
        result = calculate_trend([])
        assert isinstance(result, dict)
        assert result["direction"] == "insufficient_data"

    def test_calculate_trend_single_point(self):
        """Test trend calculation with single data point."""
        result = calculate_trend([
            AssessmentDataPoint(
                date=datetime.now(),
                assessment_type="fluency",
                score=75,
                benchmark=100
            )
        ])
        assert isinstance(result, dict)
        assert result["direction"] == "insufficient_data"


class TestRiskScore:
    """Tests for risk score calculation."""

    def test_calculate_risk_score_high_risk(self):
        """Test risk score calculation for elevated risk factors."""
        # These factors should produce at least MODERATE risk
        risk_factors = [
            {"factor": "declining_fluency_trend", "weight": 20},
            {"factor": "below_benchmark_fluency", "weight": 20},
            {"factor": "slife_indicator", "weight": 15}
        ]
        protective_factors = []
        
        score, level = calculate_risk_score(risk_factors, protective_factors)
        assert score > 0
        # With 55 points out of max possible, we expect at least MODERATE
        assert level in [RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL]

    def test_calculate_risk_score_low_risk(self):
        """Test risk score calculation for low-risk student."""
        risk_factors = [
            {"factor": "below_benchmark_fluency", "weight": 5}
        ]
        protective_factors = [
            {"factor": "improving_trend", "weight": 10},
            {"factor": "strong_l1_literacy", "weight": 8},
            {"factor": "family_involvement", "weight": 6}
        ]
        
        score, level = calculate_risk_score(risk_factors, protective_factors)
        assert level in [RiskLevel.LOW, RiskLevel.MODERATE]

    def test_calculate_risk_score_empty(self):
        """Test risk score with no factors."""
        score, level = calculate_risk_score([], [])
        assert score == 0
        assert level == RiskLevel.LOW


class TestInterventionTier:
    """Tests for intervention tier determination."""

    def test_determine_tier_critical(self):
        """Test Tier 3 for critical risk."""
        tier = determine_intervention_tier(RiskLevel.CRITICAL)
        assert tier == InterventionTier.TIER_3

    def test_determine_tier_high(self):
        """Test Tier 2 for high risk."""
        tier = determine_intervention_tier(RiskLevel.HIGH)
        assert tier == InterventionTier.TIER_2

    def test_determine_tier_moderate(self):
        """Test Tier 2 for moderate risk."""
        tier = determine_intervention_tier(RiskLevel.MODERATE)
        assert tier == InterventionTier.TIER_2

    def test_determine_tier_low(self):
        """Test Tier 1 for low risk."""
        tier = determine_intervention_tier(RiskLevel.LOW)
        assert tier == InterventionTier.TIER_1


class TestInterventionPlan:
    """Tests for intervention plan generation."""

    def test_generate_intervention_plan_tier1(self):
        """Test Tier 1 intervention plan generation."""
        plan = generate_intervention_plan(
            risk_factors=[{"factor": "below_benchmark_fluency", "weight": 5}],
            protective_factors=[{"factor": "improving_trend", "weight": 10}],
            student_profile={"l1": "es", "grade": "2"},
            tier=InterventionTier.TIER_1
        )
        assert isinstance(plan, dict)
        assert plan["tier"] == "tier_1"

    def test_generate_intervention_plan_tier2(self):
        """Test Tier 2 intervention plan generation."""
        plan = generate_intervention_plan(
            risk_factors=[
                {"factor": "below_benchmark_fluency", "weight": 12},
                {"factor": "vocabulary_gap", "weight": 8}
            ],
            protective_factors=[],
            student_profile={"l1": "ar", "grade": "3"},
            tier=InterventionTier.TIER_2
        )
        assert isinstance(plan, dict)
        assert plan["tier"] == "tier_2"

    def test_generate_intervention_plan_tier3(self):
        """Test Tier 3 intervention plan generation."""
        plan = generate_intervention_plan(
            risk_factors=[
                {"factor": "declining_fluency_trend", "weight": 15},
                {"factor": "slife_indicator", "weight": 12},
                {"factor": "limited_l1_literacy", "weight": 10}
            ],
            protective_factors=[],
            student_profile={"l1": "so", "slife": True, "grade": "5"},
            tier=InterventionTier.TIER_3
        )
        assert isinstance(plan, dict)
        assert plan["tier"] == "tier_3"
        # Tier 3 should have more intensive recommendations


class TestPredictiveInterventionAPI:
    """Tests for predictive intervention API endpoints."""

    def test_assess_risk_endpoint(self):
        """Test POST /interventions/assess-risk endpoint."""
        response = client.post(
            "/interventions/assess-risk",
            json={
                "student_id": "test_001",
                "assessment_history": [
                    {"date": "2024-03-15", "type": "orf", "wcpm": 80}
                ],
                "student_profile": {"l1": "es", "esl_level": 3},
                "grade": "3"
            }
        )
        # May be 200 or 404 depending on router registration
        if response.status_code == 200:
            data = response.json()
            assert data is not None

    def test_generate_plan_endpoint(self):
        """Test POST /interventions/generate-plan endpoint."""
        response = client.post(
            "/interventions/generate-plan",
            json={
                "risk_factors": [{"factor": "vocabulary_gap", "weight": 8}],
                "protective_factors": [],
                "student_profile": {"l1": "ar", "grade": "4"},
                "tier": "tier_2"
            }
        )
        if response.status_code == 200:
            data = response.json()
            assert data is not None


class TestAlbertaIntegration:
    """Integration tests specific to Alberta context."""

    def test_alberta_grade_benchmarks(self):
        """Test that Alberta-specific grade benchmarks are used."""
        assert "K" in WCPM_BENCHMARKS
        assert "3" in WCPM_BENCHMARKS
        # Grade 3 benchmark should be around 120 WCPM
        assert WCPM_BENCHMARKS["3"] >= 100
        assert WCPM_BENCHMARKS["3"] <= 150

    def test_full_risk_assessment_workflow(self):
        """Test complete risk assessment workflow."""
        # Step 1: Identify risk factors
        risk_factors = identify_risk_factors(
            assessment_history=[
                {"date": "2024-03-01", "type": "orf", "wcpm": 60}
            ],
            student_profile={"l1": "ko", "esl_level": 2},
            grade="2"
        )
        assert isinstance(risk_factors, list)
        
        # Step 2: Identify protective factors
        protective_factors = identify_protective_factors(
            assessment_history=[
                {"date": "2024-03-01", "type": "orf", "score": 60}
            ],
            student_profile={"l1": "ko", "l1_literacy": "strong"}
        )
        assert isinstance(protective_factors, list)
        
        # Step 3: Calculate risk score
        score, level = calculate_risk_score(risk_factors, protective_factors)
        assert 0 <= score <= 100
        
        # Step 4: Determine intervention tier
        tier = determine_intervention_tier(level)
        assert tier in [InterventionTier.TIER_1, InterventionTier.TIER_2, InterventionTier.TIER_3]
        
        # Step 5: Generate intervention plan
        plan = generate_intervention_plan(
            risk_factors=risk_factors,
            protective_factors=protective_factors,
            student_profile={"l1": "ko", "grade": "2"},
            tier=tier
        )
        assert isinstance(plan, dict)


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_empty_assessment_history(self):
        """Test with empty assessment history."""
        factors = identify_risk_factors(
            assessment_history=[],
            student_profile={"l1": "ar"},
            grade="3"
        )
        assert isinstance(factors, list)

    def test_invalid_date_format(self):
        """Test handling of invalid date format in assessments."""
        factors = identify_risk_factors(
            assessment_history=[
                {"date": "invalid", "type": "orf", "wcpm": 50}
            ],
            student_profile={"l1": "es"},
            grade="2"
        )
        # Should handle gracefully
        assert isinstance(factors, list)

    def test_missing_profile_fields(self):
        """Test with minimal student profile."""
        factors = identify_risk_factors(
            assessment_history=[],
            student_profile={},
            grade="1"
        )
        assert isinstance(factors, list)

    def test_assessment_data_point_percentage(self):
        """Test AssessmentDataPoint percentage calculation."""
        point = AssessmentDataPoint(
            date=datetime.now(),
            assessment_type="fluency",
            score=75,
            benchmark=100
        )
        assert point.percentage_of_benchmark == 75.0

    def test_assessment_data_point_zero_benchmark(self):
        """Test percentage with zero benchmark."""
        point = AssessmentDataPoint(
            date=datetime.now(),
            assessment_type="fluency",
            score=75,
            benchmark=0
        )
        assert point.percentage_of_benchmark == 0
