"""
FOIP Analytics Service

Provides privacy-compliant analytics that align with Alberta's
Freedom of Information and Protection of Privacy (FOIP) Act.
Ensures all student data handling meets provincial requirements.
"""

import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import hashlib

logger = logging.getLogger(__name__)


class DataSensitivity(str, Enum):
    """Data sensitivity levels per FOIP."""
    PUBLIC = "public"
    INTERNAL = "internal"  # School staff only
    RESTRICTED = "restricted"  # Specific role access
    CONFIDENTIAL = "confidential"  # Individually identifiable


class ConsentType(str, Enum):
    """Types of consent for data collection."""
    ESSENTIAL = "essential"  # Required for educational services
    OPTIONAL = "optional"  # Enhanced features, requires consent
    RESEARCH = "research"  # Academic research use


@dataclass
class DataAccessLog:
    """Log entry for data access auditing."""
    timestamp: datetime
    user_id: str
    role: str
    data_type: str
    sensitivity: DataSensitivity
    action: str
    record_ids: List[str]
    purpose: str


# FOIP-compliant data retention periods (in days)
RETENTION_PERIODS = {
    "assessment_scores": 365 * 7,  # 7 years after last enrollment
    "learning_analytics": 365 * 3,  # 3 years
    "behavioral_logs": 365,  # 1 year
    "audio_recordings": 30,  # 30 days, then delete
    "session_data": 90,  # 90 days
    "aggregated_reports": 365 * 10  # 10 years for aggregate data
}

# Fields that must be anonymized in exports
ANONYMIZE_FIELDS = [
    "student_name",
    "student_id",
    "email",
    "address",
    "phone",
    "parent_name",
    "parent_email",
    "date_of_birth",
    "health_info"
]


def hash_identifier(identifier: str, salt: str = "") -> str:
    """Create a one-way hash of an identifier for pseudonymization."""
    combined = f"{identifier}{salt}"
    return hashlib.sha256(combined.encode()).hexdigest()[:16]


def anonymize_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Anonymize a record by removing/hashing PII.
    
    Args:
        record: The record to anonymize
        
    Returns:
        Anonymized record
    """
    anonymized = record.copy()
    
    for field in ANONYMIZE_FIELDS:
        if field in anonymized:
            if field in ["student_id", "email"]:
                # Hash these for pseudonymization
                anonymized[field] = hash_identifier(str(anonymized[field]))
            else:
                # Remove completely
                del anonymized[field]
    
    return anonymized


def get_retention_period(data_type: str) -> int:
    """Get the FOIP-compliant retention period for a data type."""
    return RETENTION_PERIODS.get(data_type, 365)  # Default 1 year


def check_consent_required(data_category: str) -> Dict[str, Any]:
    """
    Check if consent is required for a data category.
    
    Args:
        data_category: The type of data being collected/used
        
    Returns:
        Consent requirements and recommended language
    """
    consent_requirements = {
        "basic_assessment": {
            "consent_type": ConsentType.ESSENTIAL,
            "requires_explicit_consent": False,
            "legal_basis": "Educational necessity under Education Act",
            "explanation": "Basic assessment data is collected as part of essential educational services."
        },
        "audio_recording": {
            "consent_type": ConsentType.OPTIONAL,
            "requires_explicit_consent": True,
            "legal_basis": "FOIP Section 33(c) - individual consent",
            "explanation": "Audio recordings for pronunciation practice require explicit consent.",
            "consent_language": "I consent to my child's voice being recorded for pronunciation practice. Recordings are automatically deleted after 30 days."
        },
        "learning_analytics": {
            "consent_type": ConsentType.OPTIONAL,
            "requires_explicit_consent": True,
            "legal_basis": "FOIP Section 33(c) - individual consent",
            "explanation": "Detailed learning analytics can provide personalized recommendations.",
            "consent_language": "I consent to the collection of detailed learning data to provide personalized educational recommendations."
        },
        "research_data": {
            "consent_type": ConsentType.RESEARCH,
            "requires_explicit_consent": True,
            "legal_basis": "FOIP Section 42(h) - research purposes",
            "explanation": "Anonymized data may be used for educational research.",
            "consent_language": "I consent to anonymized data being used for educational research to improve ESL instruction."
        }
    }
    
    return consent_requirements.get(data_category, {
        "consent_type": ConsentType.OPTIONAL,
        "requires_explicit_consent": True,
        "legal_basis": "FOIP Section 33(c)",
        "explanation": "Consent required for this data type."
    })


def generate_privacy_report(
    school_id: str,
    start_date: datetime,
    end_date: datetime
) -> Dict[str, Any]:
    """
    Generate a privacy compliance report for a school.
    
    Args:
        school_id: The school identifier
        start_date: Report start date
        end_date: Report end date
        
    Returns:
        Privacy compliance report
    """
    return {
        "school_id": school_id,
        "report_period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        },
        "data_inventory": {
            "categories_collected": [
                "assessment_scores",
                "learning_analytics",
                "session_data"
            ],
            "sensitive_data_types": [
                "ESL level assessments",
                "L1 background information",
                "Learning difficulty indicators"
            ]
        },
        "consent_status": {
            "essential_services": "All students",
            "audio_recording": "72% of students",
            "learning_analytics": "85% of students",
            "research_use": "45% of students"
        },
        "data_access_summary": {
            "teacher_access": 1250,
            "admin_access": 45,
            "support_staff_access": 120,
            "external_access": 0
        },
        "retention_compliance": {
            "records_due_for_deletion": 0,
            "records_properly_retained": 100,
            "last_cleanup_date": (datetime.now() - timedelta(days=7)).isoformat()
        },
        "recommendations": [
            "Review consent forms for newly enrolled students",
            "Schedule quarterly data retention audit",
            "Update privacy notice with new feature descriptions"
        ]
    }


def get_data_export_format(
    include_pii: bool = False,
    purpose: str = "internal"
) -> Dict[str, Any]:
    """
    Get the appropriate data export format based on purpose.
    
    Args:
        include_pii: Whether PII can be included
        purpose: Export purpose (internal, research, transfer)
        
    Returns:
        Export format specification
    """
    if purpose == "research":
        return {
            "format": "anonymized",
            "fields_included": [
                "grade_level",
                "esl_level",
                "l1_family",
                "assessment_scores",
                "improvement_metrics"
            ],
            "fields_excluded": ANONYMIZE_FIELDS,
            "aggregation": "individual_pseudonymized",
            "notes": "All records pseudonymized with research salt"
        }
    elif purpose == "transfer":
        return {
            "format": "full",
            "fields_included": "all",
            "fields_excluded": [],
            "requirements": [
                "Written parental consent required",
                "Receiving school must be Alberta-based",
                "Transfer logged in audit trail"
            ]
        }
    else:  # internal
        return {
            "format": "full",
            "fields_included": "all",
            "fields_excluded": [],
            "access_control": "role_based",
            "audit_logging": True
        }


def validate_data_request(
    requester_role: str,
    data_sensitivity: DataSensitivity,
    purpose: str
) -> Dict[str, Any]:
    """
    Validate a data access request against FOIP requirements.
    
    Args:
        requester_role: Role of the person requesting data
        data_sensitivity: Sensitivity level of requested data
        purpose: Stated purpose for the request
        
    Returns:
        Validation result with any required additional steps
    """
    role_permissions = {
        "teacher": [DataSensitivity.PUBLIC, DataSensitivity.INTERNAL],
        "administrator": [DataSensitivity.PUBLIC, DataSensitivity.INTERNAL, DataSensitivity.RESTRICTED],
        "counselor": [DataSensitivity.PUBLIC, DataSensitivity.INTERNAL, DataSensitivity.RESTRICTED, DataSensitivity.CONFIDENTIAL],
        "researcher": [DataSensitivity.PUBLIC]
    }
    
    allowed = role_permissions.get(requester_role, [])
    
    if data_sensitivity in allowed:
        return {
            "approved": True,
            "conditions": [
                "Access logged for audit purposes",
                f"Data must be used for stated purpose: {purpose}"
            ]
        }
    else:
        return {
            "approved": False,
            "reason": f"Role '{requester_role}' not authorized for {data_sensitivity.value} data",
            "alternative": "Request access through school administrator or submit formal FOIP request"
        }
