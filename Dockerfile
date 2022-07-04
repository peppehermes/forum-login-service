FROM python:3.8.10-slim-buster

# Install dependencies
RUN apt-get update && apt-get install -y python-pip

# Set work directory
WORKDIR /usr/src/app

# https://docs.python.org/3/using/cmdline.html#envvar-PYTHONDONTWRITEBYTECODE
# Prevents Python from writing .pyc files to disk
ENV PYTHONDONTWRITEBYTECODE 1

# Ensures that the python output is sent straight to terminal (container log)
# without being first buffered so that we can see the output of the application
# in real time. Equivalent to `python -u`: https://docs.python.org/3/using/cmdline.html#cmdoption-u
ENV PYTHONUNBUFFERED 1
ENV ENVIRONMENT prod
ENV TESTING 0

# Install python dependencies
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip && pip install -r ./requirements.txt

# Copy project
COPY . /usr/src/app

ENV PYTHONPATH=/usr/src/app
