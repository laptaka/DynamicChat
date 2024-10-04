# Dynamic Chat

...

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