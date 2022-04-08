import json

from flask import Flask, Response, request
from flask_httpauth import HTTPBasicAuth
from pymongo.errors import PyMongoError

from src.models.playlist import get_playlist, put_playlist, post_playlist, delete_playlist
from src.models.song import get_song
from src.models.user import validate_user, sign_up_user

app = Flask(__name__)
auth = HTTPBasicAuth()


@app.errorhandler(PyMongoError)
def handle_mongo_error(pme):
    response = pme.get_response()
    response.data = json.dumps(
        {
            "code": pme.code,
            "name": pme.name,
            "description": pme.description
        }
    )
    response.content_type = "application/json"
    return response


@auth.verify_password
def verify_password(username: str, password: str) -> bool:
    return validate_user(username, password, app.config['MONGO_CREDS'])


@app.route("/sign-up", methods=["PUT"])
def sign_up() -> Response:
    return sign_up_user(request.get_json(), app.config['MONGO_CREDS'])


@auth.login_required
@app.route("/playlist", methods=["GET", "PUT", "POST", "DELETE"])
def playlist() -> Response:
    match request.method:
        case "GET":
            return get_playlist(request.get_json(), app.config['MONGO_CREDS'])
        case "PUT":
            return put_playlist(request.get_json(), app.config['MONGO_CREDS'])
        case "POST":
            return post_playlist(request.get_json(), app.config['MONGO_CREDS'], app.config["API_CREDS"])
        case "DELETE":
            return delete_playlist(request.get_json(), app.config['MONGO_CREDS'])


@auth.login_required
@app.route("/song", methods=["GET"])
def song() -> Response:
    return get_song(request.get_json(), app.config['MONGO_CREDS'], app.config["API_CREDS"])
