#!/usr/bin/env python3

from google_auth_oauthlib.flow import InstalledAppFlow
from dotenv import load_dotenv
import os

load_dotenv()


def main():
    """
    Script to prompt an interactive login (browser) to obtain a refresh token.
    1. Login with the channel owner account
    2. Copy refresh token into .env
    """
    client_config = {
        "installed": {
            "client_id": os.getenv("OAUTH_CLIENT_ID"),
            "client_secret": os.getenv("OAUTH_CLIENT_SECRET"),
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
        }
    }
    scopes = [s.strip() for s in os.getenv("OAUTH_SCOPES", "").split(",") if s.strip()]
    flow = InstalledAppFlow.from_client_config(client_config, scopes=scopes)

    # Opens a local server, launches the browser, and captures the auth redirect automatically.
    creds = flow.run_local_server(port=0, prompt="consent", access_type="offline")

    print("COPY YOUR REFRESH_TOKEN INTO .env:\n", creds.refresh_token)


if __name__ == "__main__":
    main()
