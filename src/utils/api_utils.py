import requests

URL = "https://ws.audioscrobbler.com/2.0/?method=track.getInfo"


def get_track_info(api_key: str, track: str, artist: str) -> dict[str, any]:
    """
        This method will fetch the song details from the last.fm external api
    """
    track = track.replace(' ', '%20')
    artist = artist.replace(' ', '%20')

    full_url = f"{URL}&api_key={api_key}&track={track}&artist={artist}&format=json"
    response = requests.get(full_url)
    return response.json()
