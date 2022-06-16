FROM python:3.9.7-slim-buster

WORKDIR /usr/src/app
ENV FLASK_APP=app

COPY /app/requirements.txt ./

RUN pip install --upgrade pip \
&& pip install -r requirements.txt \
&& apt-get update -y --no-install-recommends \
&& apt-get install -y --no-install-recommends poppler-utils
