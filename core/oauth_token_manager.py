import time

class OAuthTokenManager:
    def __init__(self, auth_api):
        self.auth_api = auth_api
        self.token = None
        self.expires_at = 0

    def get_token(self):
        if not self.token or self.is_expired():
            self.refresh_token()
        return self.token

    def refresh_token(self):
        new_token, expires_in = self.auth_api.get_new_token()
        self.token = new_token
        self.expires_at = time.time() + expires_in - 60  # Refresh 1 min early

    def is_expired(self):
        return time.time() >= self.expires_at
