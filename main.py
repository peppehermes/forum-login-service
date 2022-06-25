from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World!"}


@app.post("/signup/")
async def signup(username: str = Form(), password: str = Form(), two_factor_enabled: bool = Form()):
    response = {"username": username, "password": password, "two_factor_enabled": two_factor_enabled}

    return response


@app.post("/login/")
async def login(username: str = Form(), password: str = Form()):
    response = {"username": username, "password": password}

    # If 2FA is enabled for this user, redirect to 2FA endpoint
    # response = RedirectResponse(url='/redirected')

    return response


@app.post("/two_factor_auth/")
async def two_factor_auth(one_time_password: str = Form()):
    response = {"one_time_password": one_time_password}

    return response
