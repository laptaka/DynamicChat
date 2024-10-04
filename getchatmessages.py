import asyncio
import os
import re

from twitchAPI.oauth import UserAuthenticationStorageHelper
from twitchAPI.twitch import Twitch
from twitchAPI.chat import Chat, EventData, ChatMessage
from twitchAPI.type import ChatEvent, AuthScope
from dotenv import load_dotenv

load_dotenv()

CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
CLIENT_SECRET = os.getenv("TWITCH_OAUTH_TOKEN")
TARGET_CHANNEL = "laptaka"  # Change this to the channel you want to monitor

message_count = 0
new_messages = []


async def on_ready(msg: EventData):
    await msg.chat.join_room(TARGET_CHANNEL)
    print("Scanning for chat messages!")


async def on_message(msg: ChatMessage):
    global message_count, new_messages
    message_count += 1
    filtered_message = re.sub(r"\b(?:http|https|www\.)\S+\b", "", msg.text).strip()
    if filtered_message:
        new_messages.append(
            {
                "username": msg.user.name,
                "color": msg.user.color,
                "message": filtered_message,
            }
        )


async def main():
    twitch = await Twitch(CLIENT_ID, CLIENT_SECRET)
    auth = UserAuthenticationStorageHelper(twitch, [AuthScope.CHAT_READ])
    await auth.bind()

    chat = await Chat(twitch)
    chat.register_event(ChatEvent.READY, on_ready)
    chat.register_event(ChatEvent.MESSAGE, on_message)

    chat.start()


if __name__ == "__main__":
    asyncio.run(main())
