from website.models import db, User
import requests
from website import create_app
import os 
from dotenv import load_dotenv


def refresh_access_tokens():
    load_dotenv()
    CLIENT_SECRET = os.getenv("CLIENT_SECRET")
    CLIENT_ID = os.getenv("CLIENT_ID")
    app = create_app()
    with app.app_context():
        url = "https://myanimelist.net/v1/oauth2/token"
        users = User.query.all()
        for user in users:
            data = {
                "client_id" : CLIENT_ID,
                "client_secret" : CLIENT_SECRET,
                "grant_type" : "refresh_token",
                "refresh_token" : user.mal_refresh_token
            }

            response = requests.post(url, data=data)

            if response.status_code == 200:
                new_tokens = response.json()
                user.access_token = new_tokens["access_token"]
                user.refresh_token = new_tokens["refresh_token"]
                db.session.commit()
                print("Token refreshed successfully!")
            else:
                print("Failed to refresh token:", response.json())
