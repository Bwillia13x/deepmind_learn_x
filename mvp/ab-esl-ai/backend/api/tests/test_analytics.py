"""Tests for Analytics API endpoints."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def session_with_results():
    """Create a session with reading results for testing analytics."""
    # Create a session
    create_response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "Analytics Teacher",
            "grade_level": "Grade 4",
            "settings": {},
        },
    )
    session_data = create_response.json()
    session_id = session_data["session_id"]
    class_code = session_data["class_code"]
    
    # Join a participant
    join_response = client.post(
        "/auth/join",
        json={
            "class_code": class_code,
            "nickname": "AnalyticsStudent",
            "l1": "ar",
        },
    )
    participant_id = join_response.json()["participant_id"]
    
    # Add some reading results via the reading score endpoint
    for wpm in [45, 52, 58, 65, 72]:
        client.post(
            "/v1/reading/score",
            json={
                "expected_text": "The cat sat on the mat by the tree",
                "transcript": "The cat sat on the mat by the tree",
                "duration": 60.0 / wpm * 8,  # Calculate duration from desired WPM
            },
        )
    
    return {
        "session_id": session_id,
        "class_code": class_code,
        "participant_id": participant_id,
    }


def test_class_summary_empty_session():
    """Test class summary for a session with no results."""
    # Create a new empty session
    create_response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "Empty Session Teacher",
            "grade_level": "Grade 3",
            "settings": {},
        },
    )
    session_id = create_response.json()["session_id"]
    
    # Get summary
    response = client.get(f"/v1/analytics/class/{session_id}/summary")
    assert response.status_code == 200
    data = response.json()
    
    assert data["session_id"] == session_id
    assert data["total_assessments"] == 0
    assert data["avg_wpm"] == 0
    assert data["participants_count"] == 0


def test_class_summary_endpoint():
    """Test class summary endpoint returns expected structure."""
    # Create a session first
    create_response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "Summary Test Teacher",
            "grade_level": "Grade 5",
            "settings": {},
        },
    )
    session_id = create_response.json()["session_id"]
    
    response = client.get(f"/v1/analytics/class/{session_id}/summary")
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields exist
    assert "session_id" in data
    assert "total_assessments" in data
    assert "avg_wpm" in data
    assert "avg_wcpm" in data
    assert "avg_accuracy" in data
    assert "participants_count" in data


def test_student_progress_endpoint():
    """Test student progress endpoint."""
    # Create session and join
    create_response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "Progress Test Teacher",
            "grade_level": "Grade 4",
            "settings": {},
        },
    )
    class_code = create_response.json()["class_code"]
    
    join_response = client.post(
        "/auth/join",
        json={
            "class_code": class_code,
            "nickname": "ProgressStudent",
            "l1": "es",
        },
    )
    participant_id = join_response.json()["participant_id"]
    
    # Get progress
    response = client.get(f"/v1/analytics/student/{participant_id}/progress")
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields exist
    assert "participant_id" in data
    assert "total_readings" in data
    assert "current_wpm" in data
    assert "wpm_trend" in data
    assert "growth_rate" in data
    assert data["participant_id"] == participant_id


def test_student_progress_no_readings():
    """Test student progress with no reading results."""
    # Create session and join
    create_response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "No Readings Teacher",
            "grade_level": "Grade 2",
            "settings": {},
        },
    )
    class_code = create_response.json()["class_code"]
    
    join_response = client.post(
        "/auth/join",
        json={
            "class_code": class_code,
            "nickname": "NoReadingsStudent",
            "l1": "zh",
        },
    )
    participant_id = join_response.json()["participant_id"]
    
    # Get progress for student with no readings
    response = client.get(f"/v1/analytics/student/{participant_id}/progress")
    assert response.status_code == 200
    data = response.json()
    
    assert data["total_readings"] == 0
    assert data["current_wpm"] == 0
    assert data["wpm_trend"] == []
    assert data["growth_rate"] == 0


def test_interventions_endpoint():
    """Test interventions endpoint."""
    # Create a session
    create_response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "Intervention Teacher",
            "grade_level": "Grade 3",
            "settings": {},
        },
    )
    session_id = create_response.json()["session_id"]
    
    # Get interventions
    response = client.get(f"/v1/analytics/class/{session_id}/interventions")
    assert response.status_code == 200
    data = response.json()
    
    assert "session_id" in data
    assert "interventions" in data
    assert isinstance(data["interventions"], list)


def test_interventions_with_threshold():
    """Test interventions endpoint with custom threshold."""
    # Create a session
    create_response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "Threshold Teacher",
            "grade_level": "Grade 4",
            "settings": {},
        },
    )
    session_id = create_response.json()["session_id"]
    
    # Get interventions with custom threshold
    response = client.get(
        f"/v1/analytics/class/{session_id}/interventions",
        params={"threshold_wpm": 80.0}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert data["session_id"] == session_id
    assert "interventions" in data


def test_class_trends_endpoint():
    """Test class trends endpoint."""
    # Create a session
    create_response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "Trends Teacher",
            "grade_level": "Grade 5",
            "settings": {},
        },
    )
    session_id = create_response.json()["session_id"]
    
    # Get trends
    response = client.get(f"/v1/analytics/class/{session_id}/trends")
    assert response.status_code == 200
    data = response.json()
    
    assert "trend" in data


def test_class_trends_with_days_param():
    """Test class trends endpoint with custom days parameter."""
    # Create a session
    create_response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "Days Param Teacher",
            "grade_level": "Grade 6",
            "settings": {},
        },
    )
    session_id = create_response.json()["session_id"]
    
    # Get trends for 7 days
    response = client.get(
        f"/v1/analytics/class/{session_id}/trends",
        params={"days": 7}
    )
    assert response.status_code == 200
    data = response.json()
    
    assert "trend" in data
