#/tests/tests.py

from fastapi.testclient import TestClient
from app import app

class TestAuthentication:

    def setup_method(self):
        self.client = TestClient(app)

    def test_generate_token_valid_credentials(self):
        username = "test"
        password = "test"
        response = self.client.post("/token", data={"username": username, "password": password})
        assert response.status_code == 200
        assert "access_token" in response.json()
        assert "token_type" in response.json() and response.json()["token_type"] == "bearer"
