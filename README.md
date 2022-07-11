# Forum Login Service in FastAPI
Login service for general forum/blog.  
This is a simple example of how to authenticate a user with time-based OTP.

## Setup

For local startup purposes, a `docker-compose.yml` file is provided.
Simply do a 
```
$ docker-compose up
```
and that will start the **Gunicorn** server locally at port 5000.

The docker image is based on **Python 3.8**.  
The database used is **PostgreSQL** for deployment purposes, while for local development
a **SQLite** database can be used instead.

You can check out the provided Swagger documentation by going to
`http://localhost:5000/docs`.

## How it works

First, an account should be created providing your preferred credentials, e.g.:

*Email*: walterwhite@save.com

*Password*: savewalterwhite

Then, the provided API can be tested by making HTTP calls to the following endpoints:

- `http://localhost:5000/auth/signup`: used to create a new user, providing email, 
password and if the user wants to enable or not 2FA;


- `http://localhost:5000/auth/login`: used to log a registered user in, given its
email and password;


- `http://localhost:5000/auth/two_factor`: used to authenticate the user
if it has 2FA enabled.

You can issue a signup request as follows:
```shell
$ curl -X 'POST' \
  'http://localhost:5000/auth/signup/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "walterwhite@save.com",
  "two_factor_enabled": true,
  "password": "savewalterwhite"
}'

HTTP/1.1 200 OK
content-length: 51
content-type: application/json
date: Mon,04 Jul 2022 14:48:32 GMT
server: uvicorn 

{
  "email": "walterwhite@save.com",
  "two_factor_enabled": true,
  "id": 1
}
```
Now the created user can make a login attempt:
```shell
$ curl -X 'POST' \
  'http://localhost:5000/auth/login/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "walterwhite@save.com",
  "password": "savewalterwhite"
}'

HTTP/1.1 200 OK
content-length: 125 
content-type: application/json
date: Mon,04 Jul 2022 14:48:43 GMT 
server: uvicorn 

{
  "email": "walterwhite@save.com",
  "two_factor_enabled": true,
  "id": 1,
  "login_identifier": "1372c333fd8c3e54abd528a56208cb40",
  "otp_code": "254992"
}
```

You will get a login session identifier for the next request, together with the
OTP code; it is provided in this response for simplicity purposes, and it is also
logged in the command line.

Finally, check the received OTP. It will be valid for 5 minutes:

```shell
$ curl -X 'POST' \
  'http://localhost:5000/auth/two_factor/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "identifier": "1372c333fd8c3e54abd528a56208cb40",
  "otp_code": "254992"
}'

HTTP/1.1 200 OK
content-length: 65 
content-type: application/json
date: Mon,04 Jul 2022 14:49:01 GMT 
server: uvicorn

{
  "status": "OK",
  "access_token": "2c6b88309972e86b1ed01d408c29bd1d"
}
```
As you can see, an access token has been sent back,
meaning that the user is now authenticated and should include
that token for further requests.

## Development

The project utilizes **pip** as the package management tool.
Ensure you have the dev dependencies installed by running

```
$ pip install -r ./requirements.txt
```

Run tests using the `pytest` command:
```
$ pytest main
```

The command to execute the backend service locally is the following:

```
uvicorn main:app --reload --log-level debug
```

Basic code style is enforced via [Black](https://pypi.org/project/black/).
Consider running `$ black .` before pushing contributions.
