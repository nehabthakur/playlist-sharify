FROM python:3.10-slim-buster

WORKDIR app/

COPY . app/

RUN cd app/ && \
    ls -latr . && \
    pip install -r requirements.txt
