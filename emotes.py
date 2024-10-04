import os
from functools import lru_cache

import requests
from dotenv import load_dotenv

load_dotenv()


def fetch_7tv_emote_url(emote_name):
    url = "https://7tv.io/v3/gql"
    query = {
        "query": """
        query($emoteSetId: ObjectID!) {
            emoteSet(id: $emoteSetId) {
                emotes {
                    id
                    name
                }
            }
            namedEmoteSet(name: GLOBAL) {
                emotes {
                    id
                    name
                }
            }
        }
        """,
        "variables": {"emoteSetId": "66c62d6ec6d977e3d585243c"},
    }  # Change the emoteSetId to the channel's emote set ID
    response = requests.post(url, json=query)
    data = response.json()

    # Check the channel emote set first
    channel_emotes = data["data"]["emoteSet"]["emotes"]
    for emote in channel_emotes:
        if emote["name"] == emote_name:
            return f"https://cdn.7tv.app/emote/{emote['id']}/1x.webp"

    # If not found, check global emotes
    global_emotes = data["data"]["namedEmoteSet"]["emotes"]
    for emote in global_emotes:
        if emote["name"] == emote_name:
            return f"https://cdn.7tv.app/emote/{emote['id']}/1x.webp"

    return None


def fetch_betterttv_emote_url(emote_name):
    url = "https://api.betterttv.net/3/cached/emotes/global"
    response = requests.get(url)
    if response.status_code == 200:
        emotes = response.json()
        for emote in emotes:
            if emote["code"] == emote_name:
                return f"https://cdn.betterttv.net/emote/{emote['id']}/1x"
    return None


def fetch_twitch_emote_url(emote_name):
    client_id = os.getenv("TWITCH_CLIENT_ID")
    user_token = requests.post(
        f"https://id.twitch.tv/oauth2/token?client_id={client_id}&client_secret={os.getenv('TWITCH_OAUTH_TOKEN')}&grant_type=client_credentials"
    ).json()["access_token"]
    url = "https://api.twitch.tv/helix/chat/emotes/global"

    headers = {"Client-ID": client_id, "Authorization": f"Bearer {user_token}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        emotes = response.json()["data"]
        for emote in emotes:
            if emote["name"].lower() == emote_name.lower():
                return emote["images"]["url_1x"]
    else:
        print(f"Error fetching Twitch emotes: {response.status_code} - {response.text}")
    return None


@lru_cache(maxsize=1000)
def fetch_emote_url(emote_name):
    # Check 7TV
    emote_url = fetch_7tv_emote_url(emote_name)
    if emote_url:
        return emote_url

    # Check BetterTTV
    emote_url = fetch_betterttv_emote_url(emote_name)
    if emote_url:
        return emote_url

    # Check Twitch
    emote_url = fetch_twitch_emote_url(emote_name)
    if emote_url:
        return emote_url

    return None


def fetch_emote(emote_name):
    emote_url = fetch_emote_url(emote_name)
    if emote_url:
        return {"name": emote_name, "url": emote_url}
    else:
        return None
