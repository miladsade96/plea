# pull official base image
FROM python:3.9-slim-buster

LABEL maintainer="Milad.Sadeghi.DM@OutLook.com"

# set work directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /app/

# install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt


# copy project
COPY . /app/
