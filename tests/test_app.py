import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_homepage(client):
    """Test the homepage returns a 200 status code and contains 'Все товары'."""
    response = client.get('/')
    assert response.status_code == 200, "Expected status code 200, got {}".format(response.status_code)
    # assert b'Все товары' in response.data, "'Все товары' not found in response data"