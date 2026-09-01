from app import app
import pytest
import json

@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_check_safe_hash(client):
    """Test checking a hash that is NOT in the known hashes."""
    response = client.post('/check',
                          data=json.dumps({"hash": "unknown_hash"}),
                          content_type='application/json')
    assert response.status_code == 200
    assert response.get_json() == {"compromised": False}

def test_check_missing_hash_field(client):
    """Test that missing 'hash' field returns 400."""
    response = client.post('/check',
                          data=json.dumps({}),
                          content_type='application/json')
    assert response.status_code == 400
    assert response.get_json() == {"error": "missing 'hash' field"}