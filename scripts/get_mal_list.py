import requests
from dotenv import load_dotenv
import json
import os
load_dotenv()

access_token = os.getenv("ACCESS_TOKEN")

import requests
from dotenv import load_dotenv
import json
import os

load_dotenv()

access_token = os.getenv("ACCESS_TOKEN")

def get_mal_list(content_type: str, total: int, ranking_type: str) -> json:
    """
    Retrieve a list of anime or manga from the MyAnimeList API and save it to a JSON file.
    """
    
    if content_type not in ['anime', 'manga']:
        raise ValueError("content_type must be either 'anime' or 'manga'")
    
    url = f'https://api.myanimelist.net/v2/{content_type}/ranking'
    all_items = []
    offset = 0
    
    while offset < total:
        params = {
            "ranking_type": ranking_type,
            "limit": "500",
            "offset": offset
        }

        response = requests.get(
            url, 
            headers={'Authorization': f'Bearer {access_token}'}, 
            params=params
        )
        
        response.raise_for_status()
        
        data = response.json()
        all_items.extend(data.get('data', []))
        print(f"Added 500 more {content_type}")
        
        offset += 500

    return all_items