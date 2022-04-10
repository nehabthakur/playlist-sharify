import re
from hashlib import md5

from flask import Response

from src.utils.mongo import MongoHelper

USERNAME_REGEX = re.compile(r"^[A-Za-z][A-Za-z0-9_]{7,29}$")
PASSWORD_REGEX = re.compile(r"^(?=.*[0-9])(?=.*[a-z])(?=.*[A-Z])(?=.*[*.!@$%^&(){}[]:;<>,.?/~_+-=|).{8,32}$")


def validate_user(username: str, password: str, mongo_creds: dict[str, str]) -> bool:
    """
        This method will check if the hashed username exists in mongodb members
        and also the hashed password matches the given input password
    """
    query = {"_id": md5(username.encode('utf-8')).hexdigest()}
    helper = MongoHelper(mongo_creds)
    result = helper.get_doc("playlist_db", "members", query)
    helper.close()
    return result is not None and result['password'] == md5(password.encode('utf-8')).hexdigest()


def sign_up_user(body: dict[str, str], mongo_creds: dict[str, str]) -> Response:
    """
        This method will sign up user using the below steps:
        1. Validates if username, password, name are empty
        2. Throws 400 bad request, if they are empty
        3. Checks if the username exists in the mongodb members collection
        4. If it does, throws 409 conflict
        5. If the username is invalid for ex. doesn't have between 7 and 29, throws and 400 Bad Request
        6. If the password is invalid for ex. doesn't have between 8 and 32, throws and 400 Bad Request
        7. Inserts the document with hashed username, hashed password, name and username and empty playlists.
    """
    username = body.get("username", "")
    password = body.get("password", "")
    name = body.get("name", "")

    if "" in (username, password, name):
        return Response("Username, password and name should be non-empty", 400)

    helper = MongoHelper(mongo_creds)
    query = {"_id": md5(username.encode('utf-8')).hexdigest()}

    if helper.get_doc("playlist_db", "members", query) is not None:
        return Response("Username already exists", 409)

    if not USERNAME_REGEX.match(username):
        return Response("Invalid Username", 400)

    if not PASSWORD_REGEX.match(password):
        return Response("Invalid Password", 400)

    member_doc = {
        "_id": md5(username.encode('utf-8')).hexdigest(),
        "name": name,
        "username": username,
        "password": md5(password.encode('utf-8')).hexdigest(),
        "playlists": []
    }

    helper.insert_doc("playlist_db", "members", member_doc)
    helper.close()
    return Response(status=200)
