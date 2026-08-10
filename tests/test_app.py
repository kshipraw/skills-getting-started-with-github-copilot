import copy

from fastapi.testclient import TestClient

from src.app import activities, app

client = TestClient(app)


def reset_activities_state():
    original = copy.deepcopy(activities)

    def restore():
        activities.clear()
        activities.update(original)

    return restore


def test_get_activities_returns_current_activities():
    response = client.get("/activities")

    assert response.status_code == 200
    json_data = response.json()
    assert isinstance(json_data, dict)
    assert "Chess Club" in json_data
    assert json_data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert json_data["Chess Club"]["participants"] == ["michael@mergington.edu", "daniel@mergington.edu"]


def test_signup_for_activity_adds_participant_and_updates_state():
    restore = reset_activities_state()
    try:
        response = client.post(
            "/activities/Chess%20Club/signup?email=teststudent@mergington.edu"
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Signed up teststudent@mergington.edu for Chess Club"

        activities_response = client.get("/activities")
        assert activities_response.status_code == 200
        participants = activities_response.json()["Chess Club"]["participants"]
        assert "teststudent@mergington.edu" in participants
    finally:
        restore()


def test_signup_for_existing_participant_returns_400():
    restore = reset_activities_state()
    try:
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert response.json()["detail"] == "Student already signed up for this activity"
    finally:
        restore()


def test_signup_for_missing_activity_returns_404():
    response = client.post(
        "/activities/Nonexistent%20Club/signup?email=teststudent@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_removes_student_and_updates_state():
    restore = reset_activities_state()
    try:
        response = client.delete(
            "/activities/Chess%20Club/participants?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        assert response.json()["message"] == "Removed michael@mergington.edu from Chess Club"

        activities_response = client.get("/activities")
        assert activities_response.status_code == 200
        participants = activities_response.json()["Chess Club"]["participants"]
        assert "michael@mergington.edu" not in participants
    finally:
        restore()


def test_remove_participant_from_missing_activity_returns_404():
    response = client.delete(
        "/activities/Nonexistent%20Club/participants?email=teststudent@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
