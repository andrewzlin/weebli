# allows user to add anime to plan to watch, once added to plan to watch, can no longer use the button
# update using MALClient(current_user).update_user_lists() after adding information 
# add updateUser info button. prevent abuse 

from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
load_dotenv()

access_token = os.getenv("ACCESS_TOKEN")
index_name = os.getenv("PINECONE_INDEX_NAME")
pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pinecone.Index(index_name)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
 
def edit_item(mal_id : str, status : str, content_type="anime"):
    """
    Potential status:
        - watching
        - completed
        - on_hold
        - dropped
        - plan_to_watch
    """

    if content_type not in ['anime', 'manga']:
        raise ValueError("content_type must be either 'anime' or 'manga'")
    
    params = {
        "status" : status,
        "comments" : "Updated with Anime Critic"
        }

    url = f'https://api.myanimelist.net/v2/{content_type}/{mal_id}/my_list_status'
    response = requests.put(url, headers={
                    'Authorization': f'Bearer {access_token}'}, params=params 
    )

    response.raise_for_status()
    
    print(f'{mal_id} has been added to your {content_type} {status} list')

def delete_item(mal_id : str, content_type="anime"):
    if content_type not in ['anime', 'manga']:
        raise ValueError("content_type must be either 'anime' or 'manga'")
    

    url = f'https://api.myanimelist.net/v2/{content_type}/{mal_id}/my_list_status'
    response = requests.delete(url, headers={
                    'Authorization': f'Bearer {access_token}'}
    )
    response.raise_for_status()

    print(f'{mal_id} has been deleted from your list')