
            
import requests
import os
from .. import db
from ..models import Anime

from pinecone import Pinecone
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
index_name = os.getenv("PINECONE_INDEX_NAME")

ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
BASE_URL = "https://api.myanimelist.net/v2"

ANIME_FIELDS = [
    "id", "title", "main_picture", "start_date", "end_date",
    "synopsis", "mean", "rank", "popularity", "num_list_users",
    "num_scoring_users", "nsfw", "media_type", "status", "genres",
    "num_episodes", "source", "average_episode_duration", "rating",
    "background", "related_anime", "related_manga", "studios",
    "created_at", "updated_at"
]

MANGA_FIELDS = [
    "id", "title", "main_picture", "start_date", "end_date",
    "synopsis", "mean", "rank", "popularity", "num_list_users",
    "num_scoring_users", "nsfw", "created_at", "updated_at",
    "media_type", "status", "genres", "num_volumes", "num_chapters",
    "authors", "background", "related_anime", "related_manga",
    "serialization"
]

class Recommender:
    def __init__(self, user):
        self.index = pinecone.Index(index_name)
        self.client = client
        self.base_url = BASE_URL

        self.access_token = ACCESS_TOKEN
        self.user = user
        self.user_list = [ua.anime.title for ua in user.anime_list]

        self.anime_fields = ANIME_FIELDS
        self.manga_fields = MANGA_FIELDS

    def make_request(self, endpoint: str, params: dict[str, str]) -> dict[str, any]:
        """Gets json with title details"""
        try:
            url = f"{self.base_url}/{endpoint}" # endpoint is manga or anime 
            response = requests.get(
                url, 
                headers={'Authorization': f'Bearer {self.access_token}'},
                params=params,
                timeout=3
            )
            response.raise_for_status()
            data = response.json()
            response.close()
            return data
        
        except requests.exceptions.Timeout:
            print("Request timed out")

        except requests.exceptions.RequestException as e:
            print (f'Request failed: {e}')

    def get_details(self, id, namespace):
        """Assembles endpoint and sends request with fields"""
        fields = self.anime_fields if namespace == "anime" else self.manga_fields
        search_data = self.make_request(
            f"{namespace}/{id}",
            {"fields": ",".join(fields)}
        )
        return search_data

    def search_index(self, filter, query_embedding, namespace, max_res=5, threshold=0.3, max=0.8):
        """Search index with filter and embedding, returning filtered results."""

        raw_results = self.index.query(
            namespace=namespace,
            vector=query_embedding, 
            top_k=max_res, 
            include_metadata=True,
            filter=filter
        )

        return [match["metadata"] for match in raw_results["matches"]
                if threshold <= match["score"] <= max] or []
    
    def get_recommendations(self, title : str, namespace : str):
        """Return recommendations based on title and namespace, filtering to remove related titles"""

        if namespace not in {"anime", "manga"}:
            print('Invalid namespace')
            return
        
        vector_data = self.index.fetch(ids=[title], namespace=namespace).get('vectors', {}).get(title, None)
        
        if vector_data:
            query_embeddings = vector_data.get('values')
            vector_metadata = vector_data.get('metadata', {})
            related_titles = vector_metadata.get('related_anime', []) + vector_metadata.get('related_manga', [])
    
        else: 
            content = Anime.query.filter_by(title=title).first()
            if content:
                id = content.mal_id
                search_data = self.get_details(id, namespace)

                related_titles = [anime['node']['title'] for anime in search_data.get('related_anime', [])]

                genres = " ".join(genre['name'] for genre in search_data.get('genres', []))

                embedding_text = f"Genres: {genres} {search_data.get('synopsis', '')}"

                query_embeddings = (
                client.embeddings.create(
                    input=embedding_text, 
                    model="text-embedding-3-small"
                )
                .data[0]
                .embedding
            )
                
            else: 
                print("Anime not found in database")
                return
            
        filter = {
                "title": {"$nin": list(set(self.user_list) | set(related_titles) | {title})},
                "popularity" : {"$lte" : 500},
                "mean" : {"$gte" : 7.5}
            }
        
        return self.search_index(filter, query_embedding=query_embeddings, namespace=namespace)