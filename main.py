import json
import logging
import os
import sys

from gevent.pywsgi import WSGIServer

from src.app import app


def init_logger():
    logging.basicConfig(
        stream=sys.stdout,
        format="%(asctime)s %(levelname)-8s %(message)s",
        level="INFO",
        datefmt="%Y-%m-%d %H:%M:%S"
    )


def main():
    logging.info("Pushing environment variables to app context")
    app.config["MONGO_CREDS"] = json.loads(os.environ["MONGO_CREDS"])
    app.config["API_CREDS"] = json.loads(os.environ["API_CREDS"])

    logging.info("Starting Rest API server")
    http_server = WSGIServer(("0.0.0.0", 5000), app)
    http_server.serve_forever()


if __name__ == '__main__':
    init_logger()
    main()
