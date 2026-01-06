"""
Testing module for SmartLensOCR backend.
Run with: pytest
"""

import pytest
import json
from fastapi.testclient import TestClient
from main import app
import os

client = TestClient(app)


class TestHealth:
    """Health check endpoint tests"""
    
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestUserManagement:
    """User management endpoint tests"""
    
    def test_create_user(self):
        """Test creating a new user"""
        response = client.post(
            "/api/users",
            json={"email": "test@example.com"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["credits"] == 5
        assert data["isPro"] == False
        self.user_id = data["id"]
    
    def test_get_existing_user(self):
        """Test retrieving an existing user returns same data"""
        # Create first
        response1 = client.post(
            "/api/users",
            json={"email": "test2@example.com"}
        )
        user_id = response1.json()["id"]
        
        # Retrieve
        response2 = client.get(f"/api/users/{user_id}")
        assert response2.status_code == 200
        assert response2.json()["email"] == "test2@example.com"
    
    def test_get_user_not_found(self):
        """Test retrieving non-existent user"""
        response = client.get("/api/users/nonexistent")
        assert response.status_code == 404


class TestCreditSystem:
    """Credit management tests"""
    
    def test_update_credits_positive(self):
        """Test adding credits to user"""
        # Create user
        create_response = client.post(
            "/api/users",
            json={"email": "credits@example.com"}
        )
        user_id = create_response.json()["id"]
        initial_credits = create_response.json()["credits"]
        
        # Update credits
        response = client.post(
            f"/api/users/{user_id}/credits",
            json={"amount": 10}
        )
        assert response.status_code == 200
        assert response.json()["credits"] == initial_credits + 10
    
    def test_update_credits_negative(self):
        """Test deducting credits from user"""
        # Create user
        create_response = client.post(
            "/api/users",
            json={"email": "debit@example.com"}
        )
        user_id = create_response.json()["id"]
        initial_credits = create_response.json()["credits"]
        
        # Deduct credits
        response = client.post(
            f"/api/users/{user_id}/credits",
            json={"amount": -2}
        )
        assert response.status_code == 200
        assert response.json()["credits"] == initial_credits - 2
    
    def test_credits_never_negative(self):
        """Test that credits cannot go below zero"""
        # Create user
        create_response = client.post(
            "/api/users",
            json={"email": "zero@example.com"}
        )
        user_id = create_response.json()["id"]
        
        # Try to deduct more than available
        response = client.post(
            f"/api/users/{user_id}/credits",
            json={"amount": -100}
        )
        assert response.status_code == 200
        assert response.json()["credits"] == 0


class TestRoot:
    """Root endpoint tests"""
    
    def test_root_endpoint(self):
        """Test root API information endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "SmartLensOCR Backend API"
        assert "version" in data
        assert "endpoints" in data


# Integration test examples (require valid Gemini API key)
@pytest.mark.skipif(
    not os.getenv("GEMINI_API_KEY"),
    reason="GEMINI_API_KEY not set"
)
class TestOCRIntegration:
    """OCR endpoint integration tests"""
    
    @pytest.fixture
    def sample_image(self):
        """Provide a sample image for testing"""
        # In a real test, you'd provide an actual image
        # For now, we'll skip actual image tests
        pass
    
    def test_detect_regions_requires_api_key(self):
        """Test that detect regions endpoint requires API key"""
        # This test verifies the endpoint exists
        response = client.post(
            "/api/detect-regions",
            json={"imageBase64": "invalid"}
        )
        # Should be 500 (API error) or 400 (bad request)
        assert response.status_code in [400, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
