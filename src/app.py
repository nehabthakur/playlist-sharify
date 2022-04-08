import logging
from time import perf_counter

from flask import Flask, Response, request, g as app_context
from flask_httpauth import HTTPBasicAuth
from gevent.pywsgi import WSGIHandler
from pymongo.errors import PyMongoError

from src.models.playlist import get_playlist, put_playlist, post_playlist, delete_playlist
from src.models.song import get_song
from src.models.user import validate_user, sign_up_user

app = Flask(__name__)
auth = HTTPBasicAuth()


@app.errorhandler(PyMongoError)
def handle_mongo_error(pme):
    logging.info(f"{pme.code} - {pme.name} - {pme.description}")
    return Response("INTERNAL SERVER ERROR", 503)


@app.before_request
def log_request():
    app_context.start_time = perf_counter()
    logging.info(f"{request.remote_addr} {request.method} {request.scheme} {request.full_path}")


@app.after_request
def log_response(response: WSGIHandler) -> WSGIHandler:
    time_taken = (perf_counter() - app_context.start_time) * 1000
    logging.info(
        "%s %s %s %s - %s with %s took %ss",
        request.remote_addr,
        request.method,
        request.scheme,
        request.full_path,
        response.status,
        response.content_length,
        time_taken
    )

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
