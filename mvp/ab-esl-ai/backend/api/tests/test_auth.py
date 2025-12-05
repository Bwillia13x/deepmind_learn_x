"""Tests for authentication and session management API."""

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_session():
    """Test creating a new class session."""
    response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "Test Teacher",
            "grade_level": "Grade 5",
            "settings": {},
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "class_code" in data
    assert "session_id" in data
    assert "token" in data
    assert len(data["class_code"]) == 6  # Should be 6-character code
    assert data["class_code"].isalnum()


def test_create_session_missing_fields():
    """Test that missing required fields returns an error."""
    response = client.post(
        "/auth/create-session",
        json={"grade_level": "Grade 5"},  # Missing teacher_name
    )
    assert response.status_code == 422


def test_join_session():
    """Test joining an existing session."""
    # First create a session
    create_response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "Test Teacher",
            "grade_level": "Grade 5",
            "settings": {},
        },
    )
    class_code = create_response.json()["class_code"]

    # Now join it
    join_response = client.post(
        "/auth/join",
        json={
            "class_code": class_code,
            "nickname": "Student1",
            "l1": "es",
        },
    )
    assert join_response.status_code == 200
    data = join_response.json()
    assert "participant_id" in data
    assert "token" in data
    assert "session_id" in data


def test_join_invalid_code():
    """Test joining with an invalid class code."""
    response = client.post(
        "/auth/join",
        json={
            "class_code": "XXXX99",  # Non-existent code
            "nickname": "Student1",
            "l1": "es",
        },
    )
    assert response.status_code == 404


def test_get_session_participants():
    """Test retrieving participants for a session."""
    # Create session and add participants
    create_response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "Test Teacher",
            "grade_level": "Grade 5",
            "settings": {},
        },
    )
    session_id = create_response.json()["session_id"]
    class_code = create_response.json()["class_code"]

    # Add two participants
    client.post(
        "/auth/join",
        json={"class_code": class_code, "nickname": "Student1", "l1": "es"},
    )
    client.post(
        "/auth/join",
        json={"class_code": class_code, "nickname": "Student2", "l1": "ar"},
    )

    # Get participants
    response = client.get(f"/auth/session/{session_id}/participants")
    assert response.status_code == 200
    data = response.json()
    assert "participants" in data
    assert len(data["participants"]) == 2
    assert data["participants"][0]["nickname"] in ["Student1", "Student2"]


def test_close_session():
    """Test closing a session."""
    # Create session
    create_response = client.post(
        "/auth/create-session",
        json={
            "teacher_name": "Test Teacher",
            "grade_level": "Grade 5",
            "settings": {},
        },
    )
    session_id = create_response.json()["session_id"]

    # Close it
    response = client.post(f"/auth/session/{session_id}/close")
    assert response.status_code == 200

    # Try to join after closing - should fail
    class_code = create_response.json()["class_code"]
    join_response = client.post(
        "/auth/join",
        json={"class_code": class_code, "nickname": "LateStudent", "l1": "es"},
    )
    assert join_response.status_code == 404  # Session closed (inactive)
