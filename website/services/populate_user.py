import requests
from .. import db
from ..models import User, UserAnime, Anime
import json
from scripts.get_details import get_details

class MALClient:
    def __init__(self, current_user):
        self.access_token = current_user.mal_access_token
        self.user_id = current_user.id
        self.headers = {'Authorization': f'Bearer {self.access_token}'}
        self.base_url = "https://api.myanimelist.net/v2/users/@me"

    def get_anime_list(self):
        """Fetch user anime list"""
        url = f'{self.base_url}/animelist'
        params = {
        "fields": "list_status",
        "sort": "list_score"
        }
        all_data = {"data": []}

        while url:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            all_data["data"].extend(data.get("data"))
            
            url = data.get("paging", {}).get("next")
        return all_data['data']
    
    def get_manga_list(self):
        """Fetch user anime list"""
        url = f'{self.base_url}/mangalist'
        params = {
        "fields": "list_status",
        "sort": "list_score"
        }
        all_data = {"data": []}

        while url:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            all_data["data"].extend(data.get("data"))
            
            url = data.get("paging", {}).get("next")
        return all_data['data']
    
    def update_user_lists(self):
        UserAnime.query.filter_by(user_id=self.user_id).delete()
        
        db.session.commit()

        anime_data = self.get_anime_list()
        for item in anime_data:
            anime = Anime.query.filter_by(mal_id=item['node']['id']).first()
            if not anime:
                details = get_details("anime", [item['node']['id']])[0]['node']
                print(details.get('genres'))
                print(details.get('studios'))
                print(details.get('related_anime'))
                anime = Anime(
                    mal_id=details['id'],
                    title=details.get('title'),
                    synopsis=details.get('synopsis'),
                    mean=details.get('mean'),
                    studio=process_studio(details.get('studios')),
                    num_list_users=details.get('num_list_users', 0),
                    genres=process_genres(details.get('genres')),
                    related_anime=process_related_anime(details.get('related_anime')),
                    picture=details.get('main_picture', {}).get('medium'),
                    start_date=details.get('start_date')
                    )
                db.session.add(anime)
                db.session.flush()

            new_user_anime = UserAnime(
                user_id=self.user_id,
                anime_id=anime.id,
                status=item['list_status']['status'],
                updated_at = item['list_status']['updated_at'],
                score=item['list_status']['score']
            )
            
            db.session.add(new_user_anime)

            
        
        # manga_data = self.get_manga_list()
        # for item in manga_data:
        #     manga = Manga.query.filter_by(mal_id=item['node']['id']).first()
        #     if not manga:
        #         manga = Manga(
        #             mal_id=item['node']['id'],
        #             title=item['node']['title'], 
        #             picture=item['node']['main_picture']['medium'])
        #         db.session.add(manga)
        #         db.session.flush()

        #     new_user_manga = UserManga(
        #         user_id=self.user_id,
        #         manga_id=manga.id,
        #         status=item['list_status']['status'],
        #         score=item['list_status']['score']
        #     )
        #     db.session.add(new_user_manga)
        db.session.commit()

def process_studio(studio_list: list[dict]) -> str:
        """
        Extract primary studio name from the given list of studios.

        Args:
            studio_list (List[Dict]): A list of dictionaries, where each dictionary
                represents a studio and contains the keys 'id' and 'name'.

        Returns:
            str: The name of the primary studio, or None if the list is empty.
        """
        if not studio_list:
            return None
        return studio_list[0].get('name')

def process_genres(genres: list[dict]) -> list[str]:
        """Extract genre names from genres list."""
        return [genre['name'] for genre in genres] if genres else []

def process_related_anime(related: list[dict]) -> list[int]:
        """Extract related anime IDs."""
        if not related:
            return []
        return [anime['node']['id'] for anime in related]

def process_related_manga(related: list[dict]) -> list[int]:
        """Extract related anime IDs."""
        if not related:
            return []
        return [manga['node']['id'] for manga in related]
