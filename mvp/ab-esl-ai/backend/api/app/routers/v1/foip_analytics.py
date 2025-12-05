"""
FOIP Analytics API Endpoints

Provides privacy-compliant analytics and data management
aligned with Alberta's FOIP Act requirements.
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.services.foip_analytics import (
    anonymize_record,
    get_retention_period,
    check_consent_required,
    generate_privacy_report,
    get_data_export_format,
    validate_data_request,
    DataSensitivity,
    ConsentType,
    RETENTION_PERIODS
)

router = APIRouter(prefix="/v1/foip")


# Request/Response Models
class DataRequestValidation(BaseModel):
    """Request to validate data access."""
    requester_role: str = Field(..., description="Role of the requester")
    data_sensitivity: str = Field(..., description="Sensitivity level of requested data")
    purpose: str = Field(..., description="Purpose for the data request")


class AnonymizationRequest(BaseModel):
    """Request to anonymize records."""
    records: List[Dict[str, Any]] = Field(..., description="Records to anonymize")


class ConsentCheckRequest(BaseModel):
    """Request to check consent requirements."""
    data_category: str = Field(..., description="Category of data")


class PrivacyReportRequest(BaseModel):
    """Request for privacy compliance report."""
    school_id: str = Field(..., description="School identifier")
    start_date: str = Field(..., description="Report start date (ISO format)")
    end_date: str = Field(..., description="Report end date (ISO format)")


class ExportFormatRequest(BaseModel):
    """Request for export format specification."""
    include_pii: bool = Field(False, description="Whether PII can be included")
    purpose: str = Field("internal", description="Export purpose")


# Endpoints
@router.get("/retention-periods")
async def get_retention_periods():
    """Get FOIP-compliant data retention periods."""
    return {
        "periods": RETENTION_PERIODS,
        "unit": "days",
        "legal_reference": "Alberta FOIP Act, Regulation 200/95"
    }


@router.get("/retention/{data_type}")
async def get_data_retention(data_type: str):
    """Get retention period for a specific data type."""
    period = get_retention_period(data_type)
    return {
        "data_type": data_type,
        "retention_days": period,
        "retention_years": round(period / 365, 1)
    }


@router.post("/consent/check")
async def check_consent(request: ConsentCheckRequest):
    """Check consent requirements for a data category."""
    return check_consent_required(request.data_category)


@router.post("/anonymize")
async def anonymize_records(request: AnonymizationRequest):
    """Anonymize records by removing/hashing PII."""
    anonymized = [anonymize_record(r) for r in request.records]
    return {
        "original_count": len(request.records),
        "anonymized_count": len(anonymized),
        "anonymized_records": anonymized
    }


@router.post("/validate-access")
async def validate_access(request: DataRequestValidation):
    """Validate a data access request against FOIP requirements."""
    try:
        sensitivity = DataSensitivity(request.data_sensitivity)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sensitivity level. Must be one of: {[s.value for s in DataSensitivity]}"
        )
    
    return validate_data_request(
        requester_role=request.requester_role,
        data_sensitivity=sensitivity,
        purpose=request.purpose
    )


@router.post("/privacy-report")
async def create_privacy_report(request: PrivacyReportRequest):
    """Generate a privacy compliance report."""
    try:
        start = datetime.fromisoformat(request.start_date)
        end = datetime.fromisoformat(request.end_date)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format. Use ISO format (YYYY-MM-DD)"
        )
    
    return generate_privacy_report(
        school_id=request.school_id,
        start_date=start,
        end_date=end
    )


@router.post("/export-format")
async def get_export_format(request: ExportFormatRequest):
    """Get appropriate data export format based on purpose."""
    if request.purpose not in ["internal", "research", "transfer"]:
        raise HTTPException(
            status_code=400,
            detail="Purpose must be one of: internal, research, transfer"
        )
    
    return get_data_export_format(
        include_pii=request.include_pii,
        purpose=request.purpose
    )


@router.get("/sensitivity-levels")
async def get_sensitivity_levels():
    """Get available data sensitivity levels."""
    return {
        "levels": [
            {
                "code": s.value,
                "name": s.name,
                "description": get_sensitivity_description(s)
            }
            for s in DataSensitivity
        ]
    }


def get_sensitivity_description(sensitivity: DataSensitivity) -> str:
    """Get description for a sensitivity level."""
    descriptions = {
        DataSensitivity.PUBLIC: "Information that can be shared publicly",
        DataSensitivity.INTERNAL: "Information accessible to school staff only",
        DataSensitivity.RESTRICTED: "Information with specific role-based access",
        DataSensitivity.CONFIDENTIAL: "Individually identifiable sensitive information"
    }
    return descriptions.get(sensitivity, "")


@router.get("/consent-types")
async def get_consent_types():
    """Get available consent types."""
    return {
        "types": [
            {
                "code": c.value,
                "name": c.name,
                "description": get_consent_description(c)
            }
            for c in ConsentType
        ]
    }


def get_consent_description(consent: ConsentType) -> str:
    """Get description for a consent type."""
    descriptions = {
        ConsentType.ESSENTIAL: "Required for educational services - no explicit consent needed",
        ConsentType.OPTIONAL: "Enhanced features - requires explicit consent",
        ConsentType.RESEARCH: "Academic research use - requires explicit research consent"
    }
    return descriptions.get(consent, "")
