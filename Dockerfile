FROM python:3.8.10-slim-buster

# Install dependencies
RUN apt-get update && apt-get install -y \
    python-pip

# set work directory
WORKDIR /usr/src/app

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# ensures that the python output is sent straight to terminal (e.g. your container log)
# without being first buffered and that you can see the output of your application (e.g. django logs)
# in real time. Equivalent to python -u: https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT prod
ENV TESTING 0

# Instlal dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip && pip install -r ./requirements.txt

# Copy project
COPY . /usr/src/app

ENV PYTHONPATH=/usr/src/app
