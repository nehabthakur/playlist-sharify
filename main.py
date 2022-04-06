import json
import logging
import os

from gevent.pywsgi import WSGIServer

from src.app import app


def main():
    logging.info("Pushing environment variables to app context")
    app.config["MONGO_CREDS"] = json.loads(os.environ["MONGO_CREDS"])
    app.config["API_CREDS"] = json.loads(os.environ["API_CREDS"])

    logging.info("Starting Rest API server")
    http_server = WSGIServer(("0.0.0.0", 5000), app)
    http_server.serve_forever()


if __name__ == '__main__':
    main()
