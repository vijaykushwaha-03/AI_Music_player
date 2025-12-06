# Microsoft Teams Integration Guide

This guide explains how to connect your AI Office Jukebox to a Microsoft Teams channel, allowing it to post updates about songs being played.

## Prerequisites

1.  A Microsoft Teams account.
2.  Permissions to add connectors/apps to a channel.

## Step 1: Create an Incoming Webhook

1.  Navigate to the **Teams channel** where you want notifications.
2.  Click the **three dots (...)** next to the channel name -> **Connectors**.
    *   *Note: If you are on the new Teams, you might need to go to "Manage channel" > "Connectors" or search for "Incoming Webhook" in the Apps store and add it to the team.*
3.  Search for **"Incoming Webhook"** and click **Add**.
4.  Click **Configure**.
5.  Give it a name (e.g., "Office Jukebox").
6.  (Optional) Upload an icon (like a musical note).
7.  Click **Create**.
8.  **Copy the Webhook URL** that is generated. It will look like:
    `https://outlook.office.com/webhook/....`

## Step 2: Configure the Jukebox

1.  Open your `.env` file in the `ai_office_jukebox` directory.
2.  Add the webhook URL (feature coming soon to main config, currently requires custom implementation in `main.py` or a notification service).

    *Current implementation status*: The core codebase is ready for integration. To enable it, you would typically add a function like this to your `services/ai_service.py` or `main.py`:

    ```python
    import requests
    
    TEAMS_WEBHOOK_URL = "YOUR_WEBHOOK_URL_HERE"

    def post_to_teams(song_title, artist):
        payload = {
            "title": "Now Playing",
            "text": f"🎶 **{song_title}** - {artist}"
        }
        requests.post(TEAMS_WEBHOOK_URL, json=payload)
    ```

## Usage

Once configured, the system can send POST requests to this URL whenever a new song starts playing.
