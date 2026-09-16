from unittest.mock import patch, Mock
from python.config import Config
from python.client import MiniPayClient

def test_get_health_returns_json():
    config = Config()
    client = MiniPayClient(config)
    mock_response = Mock()
    mock_response.json.return_value = {"status": "ok"}
    mock_response.raise_for_status = Mock()
    with patch.object(client.session, "get", return_value=mock_response):
        result = client.get_health()
    assert result["status"] == "ok"
