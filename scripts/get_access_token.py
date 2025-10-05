import requests

class AccessTokenManager:
    def __init__(self, client_id, client_secret, token_url):
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = token_url
        self.access_token = None
        self.expires_in = 0
        self.token_acquired_time = 0

    def get_access_token(self):
        if self.access_token is None or self.is_token_expired():
            self.refresh_access_token()
        return self.access_token

    def refresh_access_token(self):
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'client_credentials'
        }
        response = requests.post(self.token_url, data=payload)
        response.raise_for_status()
        data = response.json()
        self.access_token = data['access_token']
        self.expires_in = data['expires_in']
        self.token_acquired_time = self._current_time()

    def is_token_expired(self):
        return self._current_time() > self.token_acquired_time + self.expires_in - 60

    def _current_time(self):
        import time
        return int(time.time())
