from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for, session
from flask_login import login_required, current_user
from . import db
import requests
from .services.recommender import Recommender
from .services.exploration_score import ExplorationScore
from .services.populate_user import MALClient

views = Blueprint('views', __name__)

@views.route('/', methods=['GET', 'POST', 'DELETE'])
@login_required
def home():
    anime_list = [(ua.anime.mal_id, ua.anime.title) for ua in current_user.anime_list]
    
    eda = ExplorationScore(current_user)
    favorite_genres = eda.favorite_anime_genres()
    release_date_frequency = eda.release_date_frequency()
    least_popular = eda.least_popular_anime()

    return render_template("home.html", user=current_user, anime_list=anime_list, least_popular=least_popular, 
                           favorite_genres=favorite_genres, release_date_frequency=release_date_frequency)

@views.route('/', methods=['POST'])
@login_required
def refresh_user_data():
    current_user = session.get('current_user')

@views.route('/get-recommendations', methods=['POST'])
@login_required
def get_recommendations():
    
    selected_anime_mal_id = request.form.get('anime_mal_Id')

    if selected_anime_mal_id:
        recommender = Recommender(current_user)
        selected_anime = next((ua.anime for ua in current_user.anime_list 
                             if ua.anime.mal_id == int(selected_anime_mal_id)), None)
        if selected_anime:
            recommendations = recommender.get_recommendations(selected_anime.title, "anime")
            return jsonify({
                'recommendations': recommendations,
                'selected_anime': selected_anime.title
            })
    return jsonify({'error': 'No anime selected'})

@views.route('/add_to_plan', methods=['POST'])
@login_required
def add_to_plan():
    selected_anime_mal_id = request.form.get('anime_mal_Id')
    current_user = session.get('current_user')

    if selected_anime_mal_id:
        params = {
        "status" : "plan_to_watch",
        "comments" : "Updated with Anime Critic"
        }

        url = f'https://api.myanimelist.net/v2/anime/{selected_anime_mal_id}/my_list_status'
        response = requests.put(url, headers={
                        'Authorization': f'Bearer {current_user.mal_access_token}'}, params=params 
        )
        if response.status_code == 200:
            print(f'{selected_anime_mal_id} has been added to your anime plan_to_watch list')

