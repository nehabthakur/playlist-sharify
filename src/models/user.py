import json
import re
from hashlib import md5

from flask import Response

from src.utils.mongo import MongoHelper

USERNAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z0-9_]{7,29}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[*.!@$%^&(){}[]:;<>,.?/~_+-=|).{8,32}$")


def validate_user(username: str, password: str, mongo_creds: dict[str, str]) -> bool:
    query = {"_id": md5(username).hexdigest()}
    helper = MongoHelper(mongo_creds)
    result = helper.get_doc("playlist_db", "members", query)
    return result is not None and result['password'] == md5(password).hexdigest()


def sign_up_user(body: str, mongo_creds: dict[str, str]) -> Response:
    body = json.loads(body)
    username = body.get("username", "").encode('utf-8')
    password = body.get("password", "").encode('utf-8')
    name = body.get("name", "").encode('utf-8')

    if "" in (username, password, name):
        return Response("Bad Request: Username, password and name should be non-empty", 400)

    helper = MongoHelper(mongo_creds)
    query = {"_id": md5(username).hexdigest()}

    if helper.get_doc("playlist_db", "members", query) is not None:
        return Response("Conflict: username already exists", 409)

    if not USERNAME_REGEX.match(username):
        return Response("Bad Request: Invalid Username", 400)

    if not PASSWORD_REGEX.match(password):
        return Response("Bad Request: Invalid Password", 400)

    member_doc = {
        "_id": md5(username).hexdigest(),
        "name": name,
        "username": username,
        "password": md5(password).hexdigest(),
        "playlists": []
    }

    helper.insert_doc("playlist_db", "members", member_doc)
    return Response(status=200)
