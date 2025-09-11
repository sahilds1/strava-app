
from fastapi import FastAPI
from pydantic import BaseModel
from stravalib import Client

app = FastAPI()

class RequestBody(BaseModel):
    state: str | None = None
    code: str
    error: str | None = None

@app.get("/")
def login():
    c = Client()
    url = c.authorization_url(
        client_id = #STRAVA_CLIENT_ID,
        redirect_uri = #logged_in,
        approval_prompt="auto"
    )

    return #login.html

@app.post("/strava-oauth")
def logged_in(request_body: RequestBody):
    if request_body.error:
        return # login_error.html
    else:
        client = Client()
        access_token = client.exchange_code_for_token(
            client_id=#"STRAVA_CLIENT_ID",
            client_secret=#"STRAVA_CLIENT_SECRET",
            code=request_body.code,
        )

        # Probably here you'd want to store this somewhere -- e.g. in a database.
        strava_athlete = client.get_athlete()

        return #login_results.html
