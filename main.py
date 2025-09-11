
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from stravalib import Client
import configparser

app = FastAPI()

# Load configuration
config = configparser.ConfigParser()
config.read('settings.cfg')

STRAVA_CLIENT_ID = config.get('DEFAULT', 'STRAVA_CLIENT_ID')
STRAVA_CLIENT_SECRET = config.get('DEFAULT', 'STRAVA_CLIENT_SECRET')

@app.get("/")
def login():
    c = Client()
    url = c.authorization_url(
        client_id=STRAVA_CLIENT_ID,
        redirect_uri="http://localhost:8000/strava-oauth",
        approval_prompt="auto"
    )

    html_content = f"""
    <html>
        <head>
            <title>Strava OAuth Login</title>
        </head>
        <body>
            <h1>Connect to Strava</h1>
            <p>Click the link below to authorize this application with Strava:</p>
            <a href="{url}">Authorize with Strava</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/strava-oauth")
def logged_in(request: Request):
    error = request.query_params.get("error")
    code = request.query_params.get("code")
    state = request.query_params.get("state")

    if error:
        error_html = f"""
        <html>
            <head>
                <title>OAuth Error</title>
            </head>
            <body>
                <h1>OAuth Error</h1>
                <p>Error: {error}</p>
                <a href="/">Try Again</a>
            </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=400)

    if not code:
        return HTMLResponse(content="<html><body><h1>Error</h1><p>Authorization code not provided</p></body></html>", status_code=400)

    try:
        client = Client()
        access_token = client.exchange_code_for_token(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            code=code
        )

        # Get athlete information
        strava_athlete = client.get_athlete()

        success_html = f"""
        <html>
            <head>
                <title>OAuth Success</title>
            </head>
            <body>
                <h1>Successfully Connected to Strava!</h1>
                <h2>Athlete Information:</h2>
                <p><strong>Name:</strong> {strava_athlete.firstname} {strava_athlete.lastname}</p>
                <p><strong>ID:</strong> {strava_athlete.id}</p>
                <p><strong>City:</strong> {strava_athlete.city or 'Not specified'}</p>
                <p><strong>State:</strong> {strava_athlete.state or 'Not specified'}</p>
                <p><strong>Country:</strong> {strava_athlete.country or 'Not specified'}</p>
                <h2>Access Token Info:</h2>
                <p><strong>Access Token:</strong> {access_token['access_token'][:20]}...</p>
                <p><strong>Expires At:</strong> {access_token['expires_at']}</p>
                <a href="/">Start Over</a>
            </body>
        </html>
        """
        return HTMLResponse(content=success_html)

    except Exception as e:
        error_html = f"""
        <html>
            <head>
                <title>OAuth Error</title>
            </head>
            <body>
                <h1>OAuth Error</h1>
                <p>Error exchanging code for token: {str(e)}</p>
                <a href="/">Try Again</a>
            </body>
        </html>
        """
        return HTMLResponse(content=error_html, status_code=500)
