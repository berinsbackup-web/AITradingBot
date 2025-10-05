import os
import requests
from dotenv import load_dotenv
from cryptography.fernet import Fernet
import json

load_dotenv()

CLIENT_ID = os.getenv("UPSTOX_CLIENT_ID")
CLIENT_SECRET = os.getenv("UPSTOX_CLIENT_SECRET")
REDIRECT_URI = os.getenv("UPSTOX_REDIRECT_URI")

TOKEN_DIR = os.getenv("TOKEN_DIR", ".secure")
TOKEN_PATH = os.path.join(TOKEN_DIR, "token.enc")
KEY_PATH = os.path.join(TOKEN_DIR, "token.key")

os.makedirs(TOKEN_DIR, exist_ok=True)

def _get_key() -> bytes:
    if os.path.exists(KEY_PATH):
        return open(KEY_PATH, "rb").read()
    key = Fernet.generate_key()
    with open(KEY_PATH, "wb") as f:
        f.write(key)
    return key

def save_token(token_dict: dict):
    f = Fernet(_get_key())
    data = json.dumps(token_dict).encode("utf-8")
    enc = f.encrypt(data)
    with open(TOKEN_PATH, "wb") as fh:
        fh.write(enc)

def load_token() -> dict | None:
    if not os.path.exists(TOKEN_PATH):
        return None
    f = Fernet(_get_key())
    enc = open(TOKEN_PATH, "rb").read()
    try:
        data = f.decrypt(enc)
        return json.loads(data.decode("utf-8"))
    except Exception:
        return None

def generate_oauth_url(state="state123"):
    return (
        "https://api.upstox.com/v2/login/authorization/dialog?"
        f"response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&state={state}"
    )

def exchange_code_for_token(auth_code: str) -> dict | None:
    token_url = "https://api.upstox.com/v2/login/authorization/token"
    data = {
        "code": auth_code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    headers = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    resp = requests.post(token_url, data=data, headers=headers)
    if resp.status_code == 200:
        token_data = resp.json()
        save_token(token_data)
        return token_data
    else:
        print(f"Token exchange failed: {resp.status_code} {resp.text}")
        return None
