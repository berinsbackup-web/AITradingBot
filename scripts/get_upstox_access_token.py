import requests

class UpstoxTokenManager:
    def __init__(self, api_key, api_secret, redirect_uri):
        self.api_key = api_key
        self.api_secret = api_secret
        self.redirect_uri = redirect_uri
        self.access_token = None

    def get_auth_url(self):
        return f"https://upstox.com/auth?api_key={self.api_key}&redirect_uri={self.redirect_uri}"

    def get_access_token(self, auth_code):
        url = "https://upstox.com/api/token"
        headers = {'Content-Type': 'application/json'}
        payload = {
            'api_key': self.api_key,
            'api_secret': self.api_secret,
            'code': auth_code,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code'
        }
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        data = response.json()
        self.access_token = data['access_token']
        return self.access_token
