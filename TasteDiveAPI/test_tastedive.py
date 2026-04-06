import pytest
from unittest.mock import patch, MagicMock
from TasteDiveAPI.main import TasteDiveAPI
import requests

@pytest.fixture
def api():
    """Fixture to initialize the TasteDiveAPI with a mocked environment."""
    with patch('TasteDiveAPI.main.load_dotenv'), patch('os.getenv') as mock_getenv:
        mock_getenv.return_value = "fake_api_key"
        return TasteDiveAPI()

def test_successful_fetch(api):
    """Verify correct title extraction from a valid JSON response."""
    mock_data = {
        "similar": {
            "results": [
                {"name": "The Dark Knight"},
                {"name": "Inception"}
            ]
        }
    }
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        results = api.run("Batman")
        
        assert len(results) == 2
        assert results[0] == "The Dark Knight"
        assert results[1] == "Inception"

def test_empty_results(api):
    """Verify that the API returns an empty list (not None) when no results are found."""
    mock_data = {
        "similar": {
            "results": []
        }
    }
    
    with patch('requests.get') as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        results = api.run("SomeObscureMovie")
        
        # This asserts that BUG TD-01 is fixed (used to return None)
        assert isinstance(results, list)
        assert len(results) == 0

def test_api_error_handling(api):
    """Verify that network errors result in an empty list gracefully."""
    with patch('requests.get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("API Down")

        results = api.run("Batman")
        
        # This asserts that BUG TD-03 is handled
        assert isinstance(results, list)
        assert len(results) == 0

def test_invalid_query_validation(api):
    """Verify that calling run with an empty string returns [] immediately."""
    results = api.run("")
    
    # This asserts that BUG TD-02 is fixed
    assert results == []
