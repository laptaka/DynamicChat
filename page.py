import asyncio
import logging
import subprocess
import threading

import determinefeatured
import getchatmessages
import donation
import message_updates
from emotes import fetch_emote
import spotify

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
from dotenv import load_dotenv


last_track_info = {
    "track_id": None,
    "dominant_color": (54, 53, 55),
    "complementary_color": (245, 230, 99),
    "energy": 0.004,
}

load_dotenv()

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
socketio = SocketIO(app)

log = logging.getLogger("werkzeug")
log.setLevel(logging.ERROR)


@app.route("/")
def home():
    return render_template("page.html")


@app.route("/kofi-webhook", methods=["POST"])
def kofi_webhook():
    if request.is_json:
        data = request.json
    else:
        data = request.form.to_dict()

    if not data or "data" not in data:
        return "", 400

    return donation.handle_donation(data)


@app.route("/emote-info")
async def emote_info():
    emote_names = request.args.get("emotes", "").split(",")
    results = [fetch_emote(emote_name) for emote_name in emote_names]
    return jsonify(results)


@socketio.on("connect")
def handle_connect():
    print("Client connected")
    socketio.emit(
        "message_update",
        {
            "message": determinefeatured.last_message,
            "username": determinefeatured.username,
            "color": determinefeatured.color,
        },
    )
    track_info = spotify.get_current_spotify_track()
    if track_info:
        socketio.emit("spotify_update", track_info)


@socketio.on("skip_message")
def handle_skip_message():
    if message_updates.donation_active:
        message_updates.donation_active = False
        message_updates.donation_end_time = 0


def check_spotify_track():
    while True:
        try:
            track_info = spotify.get_current_spotify_track()

            if track_info:
                socketio.emit("spotify_update", track_info)
            else:
                socketio.emit("paused")
            socketio.sleep(3)
        except Exception as e:
            print(f"Error in check_spotify_track: {e}")
            socketio.sleep(3)


def run_bot():
    asyncio.run(getchatmessages.main())


def run_determinefeatured():
    asyncio.run(determinefeatured.main())


if __name__ == "__main__":
    subprocess.Popen(
        ["hookdeck", "listen", "3001", "Ko-Fi", "--cli-path", "/kofi-webhook"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )  # Hookdeck is used to listen to Ko-Fi webhooks from localhost

    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    determinefeatured_thread = threading.Thread(
        target=run_determinefeatured, daemon=True
    )
    determinefeatured_thread.start()
    socketio.start_background_task(message_updates.send_message_updates, socketio)
    socketio.start_background_task(check_spotify_track)

    socketio.run(app, debug=False, port=3001, allow_unsafe_werkzeug=True)
