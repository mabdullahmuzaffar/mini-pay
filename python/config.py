import os
import json

class Config:
    def __init__(self, config_file=None):
        if config_file and os.path.exists(config_file):
            with open(config_file) as f:
                data = json.load(f)
        else:
            data = {}

        self.api_url = data.get("api_url") or os.environ.get("MINIPAY_API_URL", "http://localhost:8080")
        self.api_key = data.get("api_key") or os.environ.get("MINIPAY_API_KEY", "dev-local-key")
        self.timeout = int(data.get("timeout") or os.environ.get("MINIPAY_TIMEOUT", "10"))
