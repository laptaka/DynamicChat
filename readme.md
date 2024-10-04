# Dynamic Chat

Dynamic Chat is an application intended to be used as a fully featured OBS web source used by streamers.\
This app integrates Twitch chat, various Twitch emote providers, Spotify, and Ko-Fi donations to give the viewers a stream interface that responds to the viewers' actions.\
It features real-time chat message processing with emotes from popular platforms, donation handling through Ko-Fi, a Spotify widget, and a dynamic lava lamp styled background.\
When there are too many messages in chat to be shown in a reasonable amount of time, the app uses AI to determine the most interesting message from the Twitch chat that is then shown on stream, pushing the viewers to write more engaging messages.\
The app also features a Spotify widget that shows the currently playing song on stream, and if the artist or song name is in Russian, it will show the transliteration of the names.\
Donations are handled through Ko-Fi, and when a donation is made, the app will show the donation message on stream and play the message as a TTS audio through AWS Polly.\
A big part of Dynamic Chat is the dynamic lava lamp effect that can be used as a background for the stream and responds to the music that is playing.\
The app is built using Flask and Socket.IO for the main logic, and Node.js and Three.JS for the GLSL background.

## Prerequisites

- Python 3.x
- Node.js
- pip
- npm

- Hookdeck
- An AWS account with a set-up CLI
- A Twitch application
- A Spotify application
- An OpenAI/Deepseek API key
- A Kofi account

## Installation

### Python Components

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/yourproject.git
    cd yourproject
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv .venv

    .venv\Scripts\activate  # On Windows
    source .venv/bin/activate  # On macOS/Linux
    ```

3. Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory and add your environment variables:
   ```
   TWITCH_CLIENT_ID=<your twitch client id>
   TWITCH_OAUTH_TOKEN=<your twitch oauth token>
   DEEPSEEK_API_KEY=<your deepseek api key>
   KOFI_TOKEN=<your kofi verification token>
   SPOTIPY_CLIENT_ID=<your spotify client id>
   SPOTIPY_CLIENT_SECRET=<your spotify client secret>
   WEBHOOK_URL=<your webhook url>
   ```

### Node.js Components

1. Navigate to the `lavalamp` directory:
    ```sh
    cd lavalamp
    ```

2. Install the required Node.js packages:
    ```sh
    npm install
    ```

## Running the Project
### Node.js Server

1. Navigate to the `lavalamp` directory if not already there:
    ```sh
    cd lavalamp
    ```

2. Start the Node.js server:
    ```sh
    node index.js
    ```
3. Open your browser and go to `http://localhost:3000` to see the dynamic lava lamp effect.

### Python Server

1. Run the Flask server:
    ```sh
    python page.py
    ```
2. Open your browser and go to `http://localhost:3001` to see the dynamic chat.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.