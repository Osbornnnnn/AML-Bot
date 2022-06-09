FROM python:3.10-slim-buster AS builder

RUN mkdir -p /opt/AML-Bot/bot/src

RUN apt-get update \
    && apt-get -yy install libmariadb-dev \
    && apt-get -yy install gcc

WORKDIR /opt/AML-Bot/bot

COPY requirements.txt .

RUN pip install --upgrade pip \
  && pip install --upgrade setuptools \
  && pip install -r requirements.txt

COPY src /opt/AML-Bot/bot/src

CMD python -m src
