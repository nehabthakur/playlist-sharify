import json
from hashlib import md5

from flask import Response, jsonify

from src.utils.api_utils import get_track_info
from src.utils.mongo import MongoHelper


def get_song(body: str, mongo_creds: dict[str, str], api_creds: dict[str, str]) -> Response:
    body = json.loads(body)
    track = body.get("track", "").encode('utf-8')
    artist = body.get("artist", "").encode('utf-8')

    if track == "" or artist == "":
        return Response("Bad Request: track, artist should be non-empty", 400)

    helper = MongoHelper(mongo_creds)
    song_id = md5(f"{track} - {artist}").hexdigest()

    song_details = helper.get_doc("playlist_db", "song", {"_id": song_id})
    if song_details:
        return jsonify(song_details)

    track_info = json.loads(get_track_info(api_creds["api_key"], track, artist))

    if "error" in track_info:
        return Response(f"Bad Request: {track_info['message']}", 400)

    record = {
        "_id": song_id,
        "track": track_info["track"]["name"],
        "artist": track_info["track"]["artist"]["name"],
        "album": track_info["track"]["album"],
        "wiki": track_info["track"]["wiki"]
    }

    helper.insert_doc("playlist_db", "song", record)
    return jsonify(record)

