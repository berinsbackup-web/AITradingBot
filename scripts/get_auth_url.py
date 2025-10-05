import upstox_client
from upstox_client.rest import ApiException

def print_auth_url(client_id, redirect_uri):
    configuration = upstox_client.Configuration()
    api_client = upstox_client.ApiClient(configuration)
    login_api = upstox_client.LoginApi(api_client)

    try:
        auth_response = login_api.authorize(
            client_id=client_id,
            redirect_uri=redirect_uri,
            api_version="v3"
        )
        print(f"Visit this URL to authorize:")
        print(auth_response.data.authorization_url)
    except ApiException as e:
        print(f"API Exception: {e}")

if __name__ == "__main__":
    CLIENT_ID = "your_client_id_here"
    REDIRECT_URI = "http://localhost:8000/callback"
    print_auth_url(CLIENT_ID, REDIRECT_URI)
