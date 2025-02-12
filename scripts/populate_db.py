from flask import Flask
from website import create_app
import website
from .get_details import get_details
from .get_mal_list import get_mal_list
from typing import List, Dict
from website.models import db, User, UserAnime, Anime, Manga, UserManga
import json
import os

app = create_app()

def process_studio(studio_list: List[Dict]) -> str:
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

def process_genres(genres: List[Dict]) -> List[str]:
    """Extract genre names from genres list."""
    return [genre['name'] for genre in genres] if genres else []

def process_related_anime(related: List[Dict]) -> List[int]:
    """Extract related anime IDs."""
    if not related:
        return []
    return [anime['node']['id'] for anime in related]

def process_related_manga(related: List[Dict]) -> List[int]:
    """Extract related anime IDs."""
    if not related:
        return []
    return [manga['node']['id'] for manga in related]

def fetch_details(content_type : str, limit: int = 5) -> List[Dict]:
    """
    Fetch anime data from MAL API and return processed results.
    """
    # First get the list of anime
    all_items = get_mal_list(content_type, limit, 'all')
    
    # Get detailed information for each anime
    return get_details(content_type, set(item['node']['id'] for item in all_items))

def populate_anime_database(limit: int = 500) -> None:
    """
    Populate the database with anime data from MAL.
    """

    anime_data_file = 'anime_data.json'
    if os.path.exists(anime_data_file):
        print("Using existing data file")
        with open(anime_data_file, 'r') as f:
            anime_data = json.load(f)
    else:
        print("Fetching data from MAL API...")
        anime_data = fetch_details("anime", limit)
        with open('anime_data.json', 'w') as f:
            json.dump(anime_data, f, indent=4)
            
    with app.app_context():
        print(f"Processing {len(anime_data)} anime entries...")
        existing_anime_ids = {anime.mal_id for anime in Anime.query.with_entities(Anime.mal_id).all()}
        new_animes = []

        for entry in anime_data:
            node = entry['node']
            if node['id'] in existing_anime_ids:
                print(f"Skipping duplicate anime: {node.get('title')}")
                continue

            anime = Anime(
                mal_id=node['id'],
                title=node.get('title'),
                synopsis=node.get('synopsis'),
                mean=node.get('mean'),
                studio=process_studio(node.get('studios', [])),
                num_list_users=node.get('num_list_users', 0),
                genres=process_genres(node.get('genres', [])),
                related_anime=process_related_anime(node.get('related_anime', [])),
                picture=node.get('main_picture', {}).get('medium'),
                start_date=node.get('start_date'),
                media_type=node.get('media_type'),
            )
            new_animes.append(anime)

        db.session.bulk_save_objects(new_animes)
        db.session.commit()
        print(f"Added {len(new_animes)} new anime entries.")

def populate_manga_database(limit: int = 500) -> None:
    """
    Populate the database with anime data from MAL.
    """
    print("Fetching data from MAL API...")

    
    manga_data = fetch_details("manga", limit)
    
    print(f"Processing {len(manga_data)} manga entries...")
    existing_manga_ids = {manga.mal_id for manga in Manga.query.with_entities(Manga.mal_id).all()}
    new_mangas = []

    for entry in manga_data:
        node = entry['node']
        if node['id'] in existing_manga_ids:
            print(f"Skipping duplicate anime: {node.get('title')}")
            continue

        manga = Manga(
            mal_id=node['id'],
            title=node.get('title'),
            synopsis=node.get('synopsis'),
            mean=node.get('mean'),
            num_list_users=node.get('num_list_users', 0),
            genres=process_genres(node.get('genres', [])),
            related_manga=process_related_manga(node.get('related_manga', [])),
            picture=node.get('main_picture', {}).get('medium'),
            start_date=node.get('start_date')
        )
        new_mangas.append(manga)

    db.session.bulk_save_objects(new_mangas)
    db.session.commit()
    print(f"Added {len(new_mangas)} new manga entries.")