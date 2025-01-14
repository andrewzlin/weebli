from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from .models import User
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .services.populate_user import MALClient
from dotenv import load_dotenv
import requests
import secrets
import os
from datetime import datetime
load_dotenv()

auth = Blueprint('auth', __name__)

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URL = "http://127.0.0.1:5000/mal/callback"

AUTH_URL = 'https://myanimelist.net/v1/oauth2/authorize'
TOKEN_URL = 'https://myanimelist.net/v1/oauth2/token'

def generate_code_verifier():
    """Generate a code verifier matching MAL's requirements"""
    token = secrets.token_urlsafe(100)
    return token[:128]

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if current_user.is_authenticated:
            return redirect(url_for('views.home'))
        
        code_verifier = generate_code_verifier()
        session['code_verifier'] = code_verifier

        params = {
            'response_type': 'code',
            'client_id': CLIENT_ID,
            'code_challenge': code_verifier
        }

        session['oauth_state'] = secrets.token_urlsafe(16)
        params['state'] = session['oauth_state']

        auth_url = f"{AUTH_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        return redirect(auth_url)
    return render_template("login.html")

@auth.route('/mal/callback')
def mal_callback():
    """Handles the MyAnimeList OAuth callback and updates user data"""
    error = request.args.get('error')
    if error:
        flash(f'Authentication error: {error}', category='error')
        return redirect(url_for('auth.login'))
    
    if request.args.get('state') != session.get('oauth_state'):
        flash('Invalid state parameter', category='error')
        return redirect(url_for('auth.login'))
    
    code = request.args.get('code')
    token_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': code,
        'code_verifier': session.get('code_verifier'),
        'grant_type': 'authorization_code',
    }
    
    try:
        response = requests.post(TOKEN_URL, data=token_data)
        response.raise_for_status()
        tokens = response.json()
        
        headers = {'Authorization': f'Bearer {tokens["access_token"]}'}
        user_response = requests.get('https://api.myanimelist.net/v2/users/@me?fields=anime_statistics', headers=headers)
        user_response.raise_for_status()
        mal_user_data = user_response.json()
        
        user = User.query.filter_by(mal_username=mal_user_data['name']).first()
        if not user:
            user = User(
                mal_username=mal_user_data['name'],
                mal_access_token=tokens['access_token'],
                mal_refresh_token=tokens['refresh_token'],
                picture=mal_user_data['picture'],
                mal_joined_at=datetime.fromisoformat(mal_user_data['joined_at']),
                mean_score=mal_user_data['anime_statistics']['mean_score'],
                num_days=mal_user_data['anime_statistics']['num_days']
            )
            db.session.add(user)

        db.session.commit()

        MALClient(current_user).update_user_lists() 
        
        login_user(user, remember=True)
        return redirect(url_for('views.home'))
        
    except requests.exceptions.RequestException as e:
        flash(f'Authentication failed: {str(e)}', category='error')
        return redirect(url_for('auth.login'))


@auth.route('/logout')
@login_required
def logout(): 
    User.query.filter_by(id=current_user.id).delete()
    logout_user()
    session.clear()
    flash("Successfully logged out", category='success')
    return redirect(url_for('auth.login'))


