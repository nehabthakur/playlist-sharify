import json
from hashlib import md5

from flask import Response, jsonify

from src.models.song import get_song
from src.utils.mongo import MongoHelper


def get_playlist(body: str, mongo_creds: dict[str, str]) -> Response:
    body = json.loads(body)
    name = body.get("name", "").encode('utf-8')

    if name == "":
        return Response("Bad Request: name should be non-empty", 400)

    helper = MongoHelper(mongo_creds)
    result = helper.get_doc("playlist_db", "playlist", {"_id": md5(name).hexdigest()})

    if result is None:
        return Response("Bad Request: Invalid Playlist name", 400)

    return jsonify(result)


def put_playlist(body: str, mongo_creds: dict[str, str]) -> Response:
    body = json.loads(body)
    name = body.get("name", "").encode('utf-8')

    if name == "":
        return Response("Bad Request: name should be non-empty", 400)

    helper = MongoHelper(mongo_creds)
    result = helper.get_doc("playlist_db", "playlist", {"_id": md5(name).hexdigest()})

    if result:
        return Response("Conflict: Playlist already exists", 409)

    record = {
        "_id": md5(name).hexdigest(),
        "name": name,
        "songs": []
    }

    helper.insert_doc("playlist_db", "playlist", record)
    return Response(status=200)


def post_playlist(body: str, mongo_creds: dict[str, str]) -> Response:
    body = json.loads(body)
    name = body.get("name", "").encode('utf-8')
    track = body.get("track", "").encode('utf-8')
    artist = body.get("artist", "").encode('utf-8')
    op_type = body.get("op_type", "").encode('utf-8').upper()

    if "" in (name, track, artist, op_type):
        return Response("Bad Request: name, track, artist, op_type should be non-empty", 400)
    elif op_type not in ("ADD", "DELETE"):
        return Response("Bad Request: op_type should be ADD or DELETE", 400)

    helper = MongoHelper(mongo_creds)
    response = get_song(body, mongo_creds)

    if response.status_code != 200:
        return response

    song_details = response.get_json()

    result = helper.get_doc("playlist_db", "playlist", {"_id": md5(name).hexdigest()})

    if result is None:
        return Response("Bad Request: Invalid Playlist name", 400)

    if op_type == "ADD":
        result["songs"].append((song_details["_id"], song_details["track"], song_details["artist"]))
    else:
        result["songs"].remove((song_details["_id"], song_details["track"], song_details["artist"]))

    return Response(status=200)


def delete_playlist(body: str, mongo_creds: dict[str, str]) -> Response:
    body = json.loads(body)
    name = body.get("name", "").encode('utf-8')

    if name == "":
        return Response("Bad Request: name should be non-empty", 400)

    helper = MongoHelper(mongo_creds)
    result = helper.get_doc("playlist_db", "playlist", {"_id": md5(name).hexdigest()})

    if result is None:
        return Response("Bad Request: Invalid Playlist name", 400)

    helper.delete_doc("playlist_db", "playlist", {"_id": md5(name).hexdigest()})
    return Response(status=200)
