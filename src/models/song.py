from hashlib import md5

from flask import Response, jsonify

from src.utils.api_utils import get_track_info
from src.utils.mongo import MongoHelper


def get_song(body: dict[str, str], mongo_creds: dict[str, str], api_creds: dict[str, str]) -> Response:
    """
        This method will return the song details either from last.fm external api or the mongodb songs collection
        1. If the input doesn't contain track, artist, throws 400 Bad Request
        2. If the song already exists in mongodb songs collection, returns the document
        3. Else Gets the song details from last.fm external api
        4. If the song doesn't exist, it will throw a 400 Bad Request error
        5. Else inserts the transformed record in songs collection
    """
    track = body.get("track", "")
    artist = body.get("artist", "")

    if "" in (track, artist):
        return Response("track, artist should be non-empty", 400)

    helper = MongoHelper(mongo_creds)
    song_id = md5(f"{track} - {artist}".encode('utf-8')).hexdigest()

    song_details = helper.get_doc("playlist_db", "songs", {"_id": song_id})
    if song_details:
        return jsonify(song_details)

    track_info = get_track_info(api_creds["api_key"], track, artist)

    if "error" in track_info:
        return Response(f"{track_info['message']}", 400)

    record = {
        "_id": song_id,
        "track": track_info["track"]["name"],
        "artist": track_info["track"]["artist"]["name"],
        "album": track_info["track"].get("album", {}),
        "wiki": track_info["track"].get("wiki", {})
    }

    helper.insert_doc("playlist_db", "songs", record)
    helper.close()
    return jsonify(record)
