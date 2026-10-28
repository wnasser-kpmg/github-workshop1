def test_root_redirects_to_activity_page(client):
    # Arrange
    # The client fixture disables automatic redirect following.

    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_data(client, activity_store):
    # Arrange
    expected_activities = activity_store.copy()

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activity_store):
    # Arrange
    activity_name = "Test Activity"
    email = "student@example.com"
    activity_store[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 5,
        "participants": [],
    }

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert activity_store[activity_name]["participants"] == [email]


def test_duplicate_signup_is_rejected(client, activity_store):
    # Arrange
    activity_name = "Test Activity"
    email = "duplicate@example.com"
    activity_store[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 5,
        "participants": [email],
    }

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"
    assert activity_store[activity_name]["participants"] == [email]


def test_signup_for_unknown_activity_returns_not_found(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_participant_can_be_unregistered(client, activity_store):
    # Arrange
    activity_name = "Test Activity"
    email = "student@example.com"
    activity_store[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 5,
        "participants": [email],
    }

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert activity_store[activity_name]["participants"] == []


def test_unregister_from_unknown_activity_returns_not_found(client):
    # Arrange
    activity_name = "Unknown Activity"

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": "student@example.com"},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_unregistered_participant_returns_not_found(client, activity_store):
    # Arrange
    activity_name = "Test Activity"
    email = "missing@example.com"
    existing_participant = "registered@example.com"
    activity_store[activity_name] = {
        "description": "Temporary test activity",
        "schedule": "Mondays, 3:00 PM",
        "max_participants": 5,
        "participants": [existing_participant],
    }

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert activity_store[activity_name]["participants"] == [existing_participant]
