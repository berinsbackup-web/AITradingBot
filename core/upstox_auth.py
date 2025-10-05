import time
import requests

class UpstoxAuth:
    def __init__(self, client_id, client_secret, redirect_uri, refresh_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.refresh_token = refresh_token
        self.access_token = None
        self.access_token_expiry = 0

    def refresh_access_token(self):
        url = "https://api.upstox.com/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token,
            'redirect_uri': self.redirect_uri,
        }
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        self.access_token = data['access_token']
        self.refresh_token = data['refresh_token']
        self.access_token_expiry = time.time() + data['expires_in'] - 60  # Renew 1 min early
        return self.access_token

    def get_access_token(self):
        if self.access_token is None or time.time() > self.access_token_expiry:
            return self.refresh_access_token()
        return self.access_token
