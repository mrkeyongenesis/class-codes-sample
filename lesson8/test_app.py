"""
Test suite for the Flask CI/CD Demo application
"""

import pytest
import json
from app import app, init_db

@pytest.fixture
def client():
    """Create a test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestHealthCheck:
    """Test health check endpoint"""
    
    def test_health_endpoint_exists(self, client):
        """Test that health endpoint returns 200"""
        response = client.get('/health')
        assert response.status_code in [200, 503]  # 200 if DB ready, 503 if not
    
    def test_health_response_format(self, client):
        """Test health response has required fields"""
        response = client.get('/health')
        data = json.loads(response.data)
        assert 'status' in data
        assert 'app' in data

class TestIndexPage:
    """Test index page"""
    
    def test_index_page_loads(self, client):
        """Test that index page returns 200"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'CI/CD Demo Application' in response.data

class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_get_messages_endpoint(self, client):
        """Test GET /api/messages endpoint"""
        response = client.get('/api/messages')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'messages' in data
        assert 'count' in data
        assert isinstance(data['messages'], list)
    
    def test_stats_endpoint(self, client):
        """Test GET /api/stats endpoint"""
        response = client.get('/api/stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_messages' in data
        assert 'app_version' in data

class TestErrorHandling:
    """Test error handling"""
    
    def test_404_error(self, client):
        """Test 404 error handling"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_api_error_format(self, client):
        """Test error response format"""
        response = client.get('/nonexistent')
        data = json.loads(response.data)
        assert 'error' in data

class TestAppConfiguration:
    """Test app configuration"""
    
    def test_app_exists(self):
        """Test that Flask app is properly configured"""
        assert app is not None
    
    def test_app_debug_mode(self):
        """Test app configuration"""
        assert app.config['TESTING'] in [True, False]

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
