import requests

class MiniPayClient:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        # Add the authentication key directly to default tracking headers
        self.session.headers.update({"X-API-Key": self.config.api_key})

    def get_health(self):
        r = self.session.get(
            f"{self.config.api_url}/health",
            timeout=self.config.timeout
        )
        r.raise_for_status()
        return r.json()

    def search_transaction(self, ref: str):
        r = self.session.get(
            f"{self.config.api_url}/api/payments/search/transactions",
            params={"ref": ref},
            timeout=self.config.timeout
        )
        r.raise_for_status()
        return r.json()
