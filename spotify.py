import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv
from colorthief import ColorThief
import requests
from io import BytesIO
import websocket
import json
from translitua import translit, RussianISO9SystemB
from colorsys import rgb_to_hls, hls_to_rgb

load_dotenv()

sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri="http://localhost:5000/callback",
        scope="user-read-currently-playing user-modify-playback-state user-read-playback-state",
    )
)

ws = None

last_track_id = None
last_track_energy = 0.6


def connect_websocket():
    global ws
    try:
        ws = websocket.WebSocket()
        ws.connect("ws://localhost:3000")
    except Exception as e:
        print(f"Failed to connect to WebSocket: {e}")
        ws = None


connect_websocket()


def color_difference(color1, color2):
    return sum(abs(a - b) for a, b in zip(color1, color2))


def increase_saturation(color, factor=1.5):
    r, g, b = [x / 255.0 for x in color]
    h, l, s = rgb_to_hls(r, g, b)
    s = min(1, s * factor)
    r, g, b = hls_to_rgb(h, l, s)
    return int(r * 255), int(g * 255), int(b * 255)


def get_dominant_color(image_url):
    response = requests.get(image_url)
    img = BytesIO(response.content)
    color_thief = ColorThief(img)
    palette = color_thief.get_palette(color_count=4, quality=1)
    dominant_color = increase_saturation(palette[0])

    complementary_color = None
    for color in palette[1:]:
        if 100 < color_difference(dominant_color, color) < 500:
            complementary_color = increase_saturation(color)
            break

    if complementary_color is None:
        complementary_color = increase_saturation(palette[1])

    return dominant_color, complementary_color


def send_dominant_color(dominant_color, complementary_color, energy):
    global ws
    if ws is None:
        print("WebSocket connection is None. Attempting to reconnect...")
        connect_websocket()

    if ws is not None:
        try:
            ws.send(
                json.dumps(
                    {"dominant_color": dominant_color, "complementary_color": complementary_color, "energy": energy}
                )
            )
        except (websocket.WebSocketConnectionClosedException, ConnectionResetError, AttributeError) as e:
            print(f"WebSocket connection error: {e}")
            connect_websocket()
            if ws:
                try:
                    ws.send(
                        json.dumps(
                            {
                                "dominant_color": dominant_color,
                                "complementary_color": complementary_color,
                                "energy": energy,
                            }
                        )
                    )
                except Exception as e:
                    print(f"Failed to send data after reconnecting: {e}")
    else:
        print("Failed to establish WebSocket connection. Unable to send colors.")


def get_current_spotify_track():
    global last_track_id, last_track_energy
    try:
        current_track = sp.current_user_playing_track()
        energy = last_track_energy
        if current_track and current_track["is_playing"]:
            album_cover = (
                current_track["item"]["album"]["images"][0]["url"]
                if len(current_track["item"]["album"]["images"]) > 0
                else None
            )
            if album_cover:
                dominant_color, complementary_color = get_dominant_color(album_cover)
            else:
                dominant_color, complementary_color = (54, 53, 55), (245, 230, 99)

            track_id = current_track["item"]["id"]
            if track_id != last_track_id:
                try:
                    audio_features = sp.audio_features(track_id)
                    if audio_features and len(audio_features) > 0:
                        energy = audio_features[0]["energy"]
                except Exception as e:
                    print(f"Error getting audio features: {e}")
                    energy = last_track_energy
                last_track_id = track_id
                last_track_energy = energy

            track_info = {
                "name": (
                    "None"
                    if current_track["item"]["name"] == ""
                    else translit(current_track["item"]["name"], RussianISO9SystemB)
                ),
                "artist": (
                    "None"
                    if len(current_track["item"]["artists"]) == 0
                    else ", ".join(
                        translit(artist["name"], RussianISO9SystemB) for artist in current_track["item"]["artists"]
                    )
                ),
                "album_cover": "None" if album_cover is None else album_cover,
            }
            send_dominant_color(dominant_color, complementary_color, energy)
            return track_info
        send_dominant_color((54, 53, 55), (245, 230, 99), 0.6)
        return None
    except Exception as e:
        print(f"Connection error: {e}")
        return None


def set_spotify_volume(volume):
    if sp.current_playback() is not None:
        sp.volume(volume)


def get_spotify_volume():
    if sp.current_playback() is not None:
        playback_info = sp.current_playback()
        if playback_info and "device" in playback_info:
            return playback_info["device"]["volume_percent"]
    return 50
