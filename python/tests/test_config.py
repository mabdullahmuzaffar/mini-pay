import os
from unittest.mock import patch
from python.config import Config

def test_reads_from_env():
    with patch.dict(os.environ, {"MINIPAY_API_URL": "http://test:9000"}):
        c = Config()
        assert c.api_url == "http://test:9000"

def test_defaults():
    c = Config()
    assert "http://localhost:8080" in c.api_url
    assert c.timeout == 10
