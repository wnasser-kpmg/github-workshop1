from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app


@pytest.fixture
def activity_store():
    original_activities = deepcopy(activities)
    try:
        yield activities
    finally:
        activities.clear()
        activities.update(original_activities)


@pytest.fixture
def client(activity_store):
    with TestClient(app, follow_redirects=False) as test_client:
        yield test_client