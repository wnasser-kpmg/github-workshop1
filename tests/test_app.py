from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


def test_duplicate_signup_is_rejected():
    activity_name = "Test Activity"
    email = "duplicate@example.com"
    activities[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 5,
        "participants": [],
    }

    try:
        first = client.post(f"/activities/{activity_name}/signup?email={email}")
        second = client.post(f"/activities/{activity_name}/signup?email={email}")

        assert first.status_code == 200
        assert second.status_code == 400
        assert activities[activity_name]["participants"] == [email]
        assert second.json()["detail"] == "Student is already signed up for this activity"
    finally:
        activities.pop(activity_name, None)


def test_participant_can_be_unregistered():
    activity_name = "Test Activity"
    email = "student@example.com"
    activities[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 5,
        "participants": [email],
    }

    try:
        response = client.delete(
            f"/activities/{activity_name}/participants?email={email}"
        )

        assert response.status_code == 200
        assert activities[activity_name]["participants"] == []
        assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    finally:
        activities.pop(activity_name, None)
