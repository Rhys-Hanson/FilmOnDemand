How to get the API Key

1. Go to https://trakt.tv and create a free account

2. Head to https://trakt.tv/oauth/applications and click "New Application"

3. Fill in any name (e.g. "FilmOnDemand") and put urn:ietf:wg:oauth:2.0:oob in the Redirect URI field

4. Hit save — you'll get a Client ID, that's your API key

5. Copy it and replace "YOUR_TRAKT_API_KEY_HERE" in the script with it

You now need to run:
pip install requests