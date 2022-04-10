import logging
from time import perf_counter

from flask import Flask, Response, request, g as app_context
from flask_httpauth import HTTPBasicAuth
from gevent.pywsgi import WSGIHandler
from pymongo.errors import PyMongoError

from src.models.playlist import get_playlist, put_playlist, post_playlist, delete_playlist
from src.models.song import get_song
from src.models.user import validate_user, sign_up_user

# Initializing the flask application & basic authentication
app = Flask(__name__)
auth = HTTPBasicAuth()


@app.errorhandler(PyMongoError)
def handle_mongo_error(pme) -> Response:
    """
        This method is for logging and handling any errors when communicating with MongoDB.

    :param pme: PyMongoError
    :return: Response object with 503 Resource unavailable
    """
    logging.info(f"{pme.code} - {pme.name} - {pme.description}")
    return Response("INTERNAL SERVER ERROR", 503)


@app.before_request
def log_request():
    """
        This method is for logging every request made to the api
    """
    app_context.start_time = perf_counter()
    logging.info(f"{request.remote_addr} {request.method} {request.scheme} {request.full_path}")


@app.after_request
def log_response(response: WSGIHandler) -> WSGIHandler:
    """
        This method is for logging every response made to the request to the api

    :param response: WSGI Handler
    :return: WSGI Handler
    """
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
    """
        This method will act as a decorator to authenticate user before the user's request is fulfilled.
    """
    return validate_user(username, password, app.config['MONGO_CREDS'])


@app.route("/sign-up", methods=["PUT"])
def sign_up() -> Response:
    """
        This method handles user signup process by calling the `sign_up_user` method
    """
    return sign_up_user(request.get_json(), app.config['MONGO_CREDS'])


@auth.login_required
@app.route("/playlist", methods=["GET", "PUT", "POST", "DELETE"])
def playlist() -> Response:
    """
        This method calls the below functions for the respective input rest methods for /playlist api call
        - GET -> get_playlist
        - PUT -> put_playlist
        - POST -> post_playlist
        - DELETE -> delete_playlist
    """
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
    """
        This method calls get_song method when a get request is made to \song
    """
    return get_song(request.get_json(), app.config['MONGO_CREDS'], app.config["API_CREDS"])
