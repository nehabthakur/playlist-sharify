from hashlib import md5

from flask import Response, jsonify

from src.models.song import get_song
from src.utils.mongo import MongoHelper


def get_playlist(body: dict[str, str], mongo_creds: dict[str, str]) -> Response:
    """
         Gets the playlist based on the name as input in the request body
         1. Name shouldn't be empty, it will throw 400 Bad Request, if it does
         2. It checks if the playlist exists in the mongodb `playlists` collection using the hashed id
         3. If it doesn't exist, it will throw 400 Bad Request
         4. If it does, the response will be in a json format
    """
    name = body.get("name", "")

    if name == "":
        return Response("name should be non-empty", 400)

    helper = MongoHelper(mongo_creds)
    result = helper.get_doc("playlist_db", "playlists", {"_id": md5(name.encode('utf-8')).hexdigest()})

    if result is None:
        return Response("Playlist doesn't exist", 400)

    helper.close()
    return jsonify(result)


def put_playlist(body: dict[str, str], mongo_creds: dict[str, str]) -> Response:
    """
        Creates a playlist using the name provided as input in the request body
        1. Name shouldn't be empty, it will throw 400 Bad Request, if it does
        2. It checks if the playlist exists in the mongodb `playlists` collection using the hashed id
        3. If it does exist, it will throw 409 Conflict
        4. If it does, the playlist is inserted to mongodb and response will be with status 200
    """
    name = body.get("name", "")

    if name == "":
        return Response("name should be non-empty", 400)

    helper = MongoHelper(mongo_creds)
    result = helper.get_doc("playlist_db", "playlists", {"_id": md5(name.encode('utf-8')).hexdigest()})

    if result:
        return Response("Playlist already exists", 409)

    record = {
        "_id": md5(name.encode('utf-8')).hexdigest(),
        "name": name,
        "songs": []
    }

    helper.insert_doc("playlist_db", "playlists", record)

    helper.close()
    return Response(status=200)


def post_playlist(body: dict[str, str], mongo_creds: dict[str, str], api_creds: dict[str, str]) -> Response:
    """
        Updates a playlist using name, track, song, operation type as input in the request body
        1. Name, track, song, op_type shouldn't be empty, it will throw 400 Bad Request, if it does
        2. op_type should be only `ADD` or `DELETE`, it will throw 400 Bad Request, if it doesn't
        3. Check if the song exists in the songs collection or the external last.fm api
        4. If it doesn't exist, it will throw 400 Bad Request
        5. It checks if the playlist exists in the mongodb `playlists` collection using the hashed id
        6. If it doesn't exist, it will throw 400 Bad Request
        7. If the op_type is ADD, the song shouldn't exist in the playlist, else it will throw 409 conflict
        8. If the op_type is DELETE, the song should exist in the playlist, else it will throw 400 Bad request
        9. The final record with removed or added songs will be updated in mongodb playlists collection
    """
    name = body.get("name", "")
    track = body.get("track", "")
    artist = body.get("artist", "")
    op_type = body.get("op_type", "").upper()

    if "" in (name, track, artist, op_type):
        return Response("name, track, artist, op_type should be non-empty", 400)
    elif op_type not in ("ADD", "DELETE"):
        return Response("op_type should be ADD or DELETE", 400)

    helper = MongoHelper(mongo_creds)
    response = get_song(body, mongo_creds, api_creds)

    if response.status_code != 200:
        return response

    song_details = response.get_json()

    result = helper.get_doc("playlist_db", "playlists", {"_id": md5(name.encode('utf-8')).hexdigest()})

    if result is None:
        return Response("Invalid Playlist name", 400)

    song_record = [song_details["_id"], song_details["track"], song_details["artist"]]

    if op_type == "ADD":
        if song_record not in result["songs"]:
            result["songs"].append(song_record)
        else:
            return Response("Song already exists in playlist", 409)
    else:
        if song_record in result["songs"]:
            result["songs"].remove(song_record)
        else:
            return Response("Song doesn't exist in playlist", 400)

    helper.insert_doc("playlist_db", "playlists", result)
    helper.close()
    return Response(status=200)


def delete_playlist(body: dict[str, str], mongo_creds: dict[str, str]) -> Response:
    """
         DELETE the playlist based on the name as input in the request body
         1. Name shouldn't be empty, it will throw 400 Bad Request, if it does
         2. It checks if the playlist exists in the mongodb `playlists` collection using the hashed id
         3. If it doesn't exist, it will throw 400 Bad Request
         4. If it does, deletes the playlist, the response will be with status_code 200.
    """
    name = body.get("name", "")

    if name == "":
        return Response("name should be non-empty", 400)

    helper = MongoHelper(mongo_creds)
    result = helper.get_doc("playlist_db", "playlists", {"_id": md5(name.encode('utf-8')).hexdigest()})

    if result is None:
        return Response("Invalid Playlist name", 400)

    helper.delete_doc("playlist_db", "playlists", {"_id": md5(name.encode('utf-8')).hexdigest()})

    helper.close()
    return Response(status=200)
