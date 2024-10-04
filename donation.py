import io
import json
import os
import queue
import re
import threading

import inflect
from boto3 import Session
from pydub import AudioSegment

from spotify import set_spotify_volume, get_spotify_volume

aws_session = Session(profile_name="default")
tts_client = aws_session.client("polly")
inflect = inflect.engine()
donation_queue = queue.Queue()


def generate_tts(text, username, amount, donation_type, tier):
    try:
        prefix = generate_prefix_text(donation_type, username, amount, tier)
        ssml_text = f'<speak><prosody rate="x-slow">{prefix}{" <break time=\"0.7s\"/>" + text if text else ""}</prosody></speak>'

        response = tts_client.synthesize_speech(
            OutputFormat="mp3",
            VoiceId="Hans",
            Engine="standard",
            TextType="ssml",
            Text=ssml_text,
        )
        audio_data = response["AudioStream"].read()
        duration = get_audio_duration(audio_data)

        return audio_data, duration
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None, 0


def get_audio_duration(audio_data):
    audio = AudioSegment.from_mp3(io.BytesIO(audio_data))
    duration = len(audio) / 1000.0
    return duration


def generate_prefix_text(donation_type, username, amount, tier):
    amount_int = int(float(amount))
    amount_words = inflect.number_to_words(amount_int)
    if donation_type == "Subscription":
        prefix = (
            f'{username} subscribed to the {tier} tier for {amount_words} {"dollars" if amount_int > 1 else "dollar"}'
        )
    else:
        prefix = f'{username} donated {amount_words} {"dollars" if amount_int > 1 else "dollar"}'
    return prefix


def handle_donation(data):
    if isinstance(data["data"], str):
        kofi_data = json.loads(data["data"])
    else:
        kofi_data = data["data"]

    expected_token = os.getenv("KOFI_TOKEN")
    if kofi_data.get("verification_token") != expected_token:
        print("Verification token mismatch ", kofi_data)
        return "", 403

    print("Received verified Kofi webhook data:", kofi_data)

    if not kofi_data.get("is_public"):
        return "", 200

    donation_type = kofi_data.get("type")

    username = kofi_data.get("from_name", "Anonymous")
    amount = kofi_data.get("amount", "1")
    tier = kofi_data.get("tier_name", None)
    message = kofi_data.get("message", None)
    filtered_message = re.sub(r"\b(?:http|https|www\.)\S+\b", "", message).strip() if message else None

    audio_data, duration = generate_tts(filtered_message, username, amount, donation_type, tier)

    if not filtered_message or filtered_message == "":
        filtered_message = generate_prefix_text(donation_type, username, amount, tier)

    donation_queue.put(
        {
            "message": filtered_message,
            "username": username,
            "audio": audio_data.decode("latin-1") if audio_data else None,
            "audioDuration": duration,
            "isDonation": True,
            "amount": amount,
        }
    )

    previous_volume = get_spotify_volume()
    if previous_volume > 25:
        set_spotify_volume(25)
        threading.Timer(duration, set_spotify_volume, args=[previous_volume]).start()

    return "", 200
