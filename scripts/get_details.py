import requests
import time
import json
import os
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BASE_URL = "https://api.myanimelist.net/v2"

ANIME_FIELDS = [
    "id", "title", "main_picture", "start_date",
    "synopsis", "mean",
    "num_list_users", "genres",
    "related_anime", "studios", "media_type"
]

MANGA_FIELDS = [
    "id", "title", "main_picture", "start_date", 
    "synopsis", "mean", 
    "num_list_users", 
    "genres", 
    "related_manga"
]

def countdown_timer(seconds: int) -> None:
    """Display a countdown timer for the specified number of seconds."""
    for remaining in range(seconds, 0, -1):
        print(f"{remaining} seconds left", end='\r')
        time.sleep(1)

def make_request(endpoint: str, params: Dict[str, str]) -> Dict[str, Any]:
    """Make an API request with retry logic for timeouts."""
    while True:
        try:
            url = f"{BASE_URL}/{endpoint}"
            response = requests.get(
                url,
                headers={'Authorization': f'Bearer {ACCESS_TOKEN}'},
                params=params,
                timeout=3
            )
            response.raise_for_status()
            data = response.json()
            response.close()
            return data
        except requests.exceptions.Timeout:
            print("Request timed out, retrying in 5 minutes")
            countdown_timer(300)

def get_details(content_type: str, id_list: List[int]) -> List[Dict]:
    """Fetch details for anime or manga."""
    fields = ANIME_FIELDS if content_type == "anime" else MANGA_FIELDS
    descriptions = []
    
    for counter, item_id in enumerate(id_list, 1):
        data = make_request(
            f"{content_type}/{item_id}",
            {"fields": ",".join(fields)}
        )
        
        if "synopsis" in data:
            data["synopsis"] = data.get("synopsis", "").replace("\u2014", "-").replace("\n\n", " ")
        
        descriptions.append({
            "node": {key: data.get(key) for key in fields}
        })
        print(f"Number of {content_type} descriptions added: {counter}")
        
    return descriptions