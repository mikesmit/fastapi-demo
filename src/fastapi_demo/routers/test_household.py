from .test_common import createApi
from fastapi.testclient import TestClient
from .household import router
import pytest

@pytest.fixture
def client()->TestClient:
    api = createApi(router)
    return TestClient(api)

def test_create_household(client:TestClient):
    response = client.post("/household", json={})
    assert response.status_code == 200
    assert response.json() == {
        'id': 1
    }

def test_get_household(client:TestClient):
    create_response = client.post("/household", json={})
    id = create_response.json()['id']
    response = client.get(f"/household/{id}")
    assert response.status_code == 200
    assert response.json() == {
        'id': 1
    }

def test_get_household_404(client:TestClient):
    response = client.get(f"/household/1")
    assert response.status_code == 404

def test_delete_household(client:TestClient):
    create_response = client.post("/household", json={})
    id = create_response.json()['id']
    response = client.delete(f"/household/{id}")
    assert response.status_code == 200
    get_response = client.get(f"/household/{id}")
    assert get_response.status_code == 404

def test_delete_household_404(client:TestClient):
    response = client.delete(f"/household/1")
    assert response.status_code == 404
