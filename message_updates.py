import time

from flask_socketio import SocketIO

import determinefeatured
import donation

donation_active = False
donation_end_time = 0
client_reachable = False


def send_message_updates(socketio: SocketIO):
    global donation_active, donation_end_time, client_reachable
    last_emitted_message = None
    last_emitted_username = None

    while True:
        current_time = time.time()

        if not donation_active and not donation.donation_queue.empty():
            socketio.emit("ping", callback=lambda: set_client_reachable(True))
            socketio.sleep(1)
            if client_reachable:
                donation_item = donation.donation_queue.get()
                audio_duration = donation_item["audioDuration"]
                socketio.emit("message_update", donation_item)
                donation_active = True
                donation_end_time = current_time + audio_duration + 2
                set_client_reachable(False)
            else:
                print("Client not reachable")
                socketio.sleep(5)

        elif donation_active and current_time >= donation_end_time:
            donation_active = False

        if not donation_active and donation.donation_queue.empty() and current_time >= donation_end_time:
            current_message = determinefeatured.last_message
            current_username = determinefeatured.username
            current_color = determinefeatured.color
            if current_message != last_emitted_message or current_username != last_emitted_username:
                socketio.emit(
                    "message_update",
                    {
                        "message": current_message,
                        "username": current_username,
                        "color": current_color,
                        "changed": True,
                    },
                )
                last_emitted_message = current_message
                last_emitted_username = current_username

        socketio.sleep(1)


def set_client_reachable(status: bool):
    global client_reachable
    client_reachable = status
